//By default, the pipeline considers paired-end reads (please see contra_single.nf for single-end reads).
// Define the parameters for the input and output directories
params.input_dir = "/path/to/input/dir"
params.output_dir = "/path/to/output/dir"

// Read quality control 
process FastQC {
    // Run FastQC on the input FASTQ files
    input:
    file pair from Channel.fromFilePairs("${params.input_dir}/*_{1,2}.fastq")
    output:
    file "*_fastqc.zip" into qc_raw
    script:
    """
    fastqc -o . ${pair[0]} ${pair[1]}
    """
}

//Adapter trimming
process Cutadapt {
    // Run Cutadapt on the FASTQ files to trim adapters
    input:
    file pair from Channel.fromFilePairs("${params.input_dir}/*_{1,2}.fastq")
    output:
    file "*_trimmed.fastq" into trimmed
    script:
    """
    cutadapt -a ADAPTER -A ADAPTER -o ${pair[0].baseName}_trimmed.fastq -p ${pair[1].baseName}_trimmed.fastq ${pair[0]} ${pair[1]}
    """
}

//Quality control second-round for trimmed reads (repeat as many times as required)
process FastQC_trimmed {
    // Run FastQC on the trimmed FASTQ files
    input:
    file pair from trimmed.collect()
    output:
    file "*_fastqc.zip" into qc_trimmed
    script:
    """
    fastqc -o . ${pair[0]} ${pair[1]}
    """
}

//Filter reads by Phred score to retain only the highest scoring reads
process Filter {
    // Filter the trimmed FASTQ files by Phred score
    input:
    file pair from trimmed.collect()
    output:
    file "*_filtered.fastq" into filtered
    script:
    """
    filter_fastq.py -i ${pair[0]} -o ${pair[0].baseName}_filtered.fastq -q 30
    filter_fastq.py -i ${pair[1]} -o ${pair[1].baseName}_filtered.fastq -q 30
    """
}

//Demultiplexing and UMI removal for each read
process MiGEC {
    // Run MiGEC on the filtered FASTQ files to perform demultiplexing and UMI removal
    input:
    file pair from filtered.collect()
    output:
    file "*_migec.fastq" into migec
    script:
    """
    migec Checkout -c CONFIG ${pair[0]} ${pair[1]} .
    migec Assemble -c CONFIG ${pair[0].baseName}_migec.fastq ${pair[1].baseName}_migec.fastq .
    """
}

//Read alignment and enumerating repertoires per sample
process MiXCR {
    // Run MiXCR on the demultiplexed FASTQ files to perform alignment
    input:
    file pair from migec.collect()
    output:
    file "*.vdjca" into vdjca
    script:
    """
    mixcr align -p rna-seq -s SPECIES -OallowPartialAlignments=true ${pair[0]} ${pair[1]} ${pair[0].baseName}.vdjca
    """
}

//Perform visualization and statistical analysis for the output of the previous alignment and enumeration steps
process VDJTOOLS {
    // Run VDJTOOLS on the aligned files to perform diversity analysis
    input:
    file vdjca_file from vdjca.collect()
    output:
    file "*.txt" into diversity
    script:
    """
    mixcr exportClones ${vdjca_file} ${vdjca_file.baseName}.txt
    vdjtools CalcDiversityStats -m METADATA -p ${vdjca_file.baseName}.txt .
    """
}

// Write the output files to the output directory
qc_raw.collect().set { qc_raw_files }
qc_trimmed.collect().set { qc_trimmed_files }
filtered.collect().set { filtered_files }
migec.collect().set { migec_files }
vdjca.collect().set { vdjca_files }
diversity.collect().set { diversity_files }

process Output {
    input:
    file qc_raw_file from qc_raw_files
    file qc_trimmed_file from qc_trimmed_files
    file filtered_file from filtered_files
    file migec_file from migec_files
    file vdjca_file from vdjca_files
    file diversity_file from diversity_files
    output:
    file "*" into output
    script:
    """
    cp ${qc_raw_file} ${params.output_dir}
    cp ${qc_trimmed_file} ${params.output_dir}
    cp ${filtered_file} ${params.output_dir}
    cp ${migec_file} ${params.output_dir}
    cp ${vdjca_file} ${params.output_dir}
    cp ${diversity_file} ${params.output_dir}
    """
}
