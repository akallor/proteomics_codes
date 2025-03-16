#Convert multiple raw files to mzml output using msconvert (run a dockerized msconvert container through apptainer)
#TODO: customize the code to incorporate more options for filtering, threading, wavelet transform and peak picking.

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
#SBATCH --cpus-per-task=8
#SBATCH --mem=10G
#SBATCH --time=01:00:00

echo "Starting conversion of $filename at \$(date)"

apptainer exec --bind $RAW_DIR:/raw_files,$OUTPUT_DIR:/output \\
    msconvert.sif wine msconvert "/raw_files/$filename" \\
    --mzML -o /output --threads 16 2>/dev/null

echo "Finished conversion of $filename at \$(date)"
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
