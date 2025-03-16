#Submit the msconvert conversion process for multiple files by copying back and forth from $SCRATCH
#This saves I/O resources and speeds up the conversion process, in addition to other optimizations
#such as multi-threading within the msconvert process. We can also examine the runtime to optimize 
#further.


#!/bin/bash
#SBATCH --job-name=msconvert_launcher
#SBATCH --output=msconvert_launcher_%j.log
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --time=00:30:00

# Define directories
RAW_DIR="/data/teamgdansk/ashwin1988/raw_files"
OUTPUT_DIR="/data/teamgdansk/ashwin1988/mzml_output"

# Create output directory if it doesn't exist
mkdir -p $OUTPUT_DIR

# Function to create job script for each file
submit_conversion_job() {
    local raw_file=$1
    local filename=$(basename "$raw_file")
    local job_script="msconvert_${filename%.RAW}.sh"

    # Create a job script for this file
    cat > $job_script << EOL
#!/bin/bash
#SBATCH --job-name=msconv_${filename%.RAW}
#SBATCH --output=msconv_${filename%.RAW}_%j.log
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=16
#SBATCH --mem=10G
#SBATCH --time=01:00:00

# Record start time
START_TIME=\$(date +%s)
echo "Starting conversion of $filename at \$(date)"

# Optimize WINE settings
export WINEDEBUG=-all
export WINEPREFIX=/tmp/wine_\$SLURM_JOB_ID
export WINEARCH=win64

# Create unique scratch directory for this job
SCRATCH_DIR="/scratch/\$USER/\$SLURM_JOB_ID"
mkdir -p \$SCRATCH_DIR

echo "Copying RAW file to scratch space at \$(date)"
COPY_START=\$(date +%s)
cp $RAW_DIR/$filename \$SCRATCH_DIR/
COPY_END=\$(date +%s)
COPY_TIME=\$((COPY_END - COPY_START))
echo "Copy to scratch took \$COPY_TIME seconds"

echo "Starting conversion from scratch space at \$(date)"
CONVERT_START=\$(date +%s)
apptainer exec --bind \$SCRATCH_DIR:/scratch_data \
    msconvert.sif wine msconvert "/scratch_data/$filename" \
    --mzML --zlib --threads 16 \
    -o /scratch_data 2>/dev/null
CONVERT_END=\$(date +%s)
CONVERT_TIME=\$((CONVERT_END - CONVERT_START))
echo "Conversion took \$CONVERT_TIME seconds"

echo "Copying mzML result back to output directory at \$(date)"
COPY_BACK_START=\$(date +%s)
cp \$SCRATCH_DIR/${filename%.RAW}.mzML $OUTPUT_DIR/
COPY_BACK_END=\$(date +%s)
COPY_BACK_TIME=\$((COPY_BACK_END - COPY_BACK_START))
echo "Copy back took \$COPY_BACK_TIME seconds"

echo "Cleaning up scratch space at \$(date)"
rm -rf \$SCRATCH_DIR

# Calculate total runtime
END_TIME=\$(date +%s)
TOTAL_SECONDS=\$((END_TIME - START_TIME))
MINUTES=\$((TOTAL_SECONDS / 60))
SECONDS=\$((TOTAL_SECONDS % 60))

echo "Finished conversion of $filename at \$(date)"
echo "----------------------------------------"
echo "RUNTIME SUMMARY:"
echo "----------------------------------------"
echo "Total runtime: \$MINUTES minutes and \$SECONDS seconds (\$TOTAL_SECONDS seconds total)"
echo "Copy to scratch: \$COPY_TIME seconds"
echo "Conversion: \$CONVERT_TIME seconds"
echo "Copy back: \$COPY_BACK_TIME seconds"
echo "----------------------------------------"
EOL

    # Submit the job and record the job ID
    chmod +x $job_script
    sbatch $job_script
    echo "Submitted job for $filename"
}

# Loop through all RAW files and submit a job for each
for raw_file in $RAW_DIR/*.RAW; do
    submit_conversion_job "$raw_file"
done

echo "All conversion jobs have been submitted!"
