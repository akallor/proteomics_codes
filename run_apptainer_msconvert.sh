#!/usr/bin bash
#Run the apptainer on the msconvert container (msconvert.sif) to convert raw files to mzml
#Basic version

apptainer exec --bind /data/teamgdansk/ashwin1988/raw_files:/raw_files,/data/teamgdansk/ashwin1988/mzml_output:/output msconvert.sif wine msconvert /raw_files/120608_ARDK_RCC792_Benign_W_10_1sDynExl_Rep1_msms7.RAW --mzML -o /output 2>/dev/null
