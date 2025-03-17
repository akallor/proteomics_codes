#!/bin/bash
# Script to create a Singularity container for Skyline directly

# Create a Singularity definition file
cat > Singularity.def << 'EOF'
Bootstrap: docker
From: ubuntu:22.04

%post
    apt-get update && apt-get install -y \
        wget \
        unzip \
        libgdiplus \
        libc6-dev \
        mono-complete \
        mono-devel \
        && rm -rf /var/lib/apt/lists/*
    
    mkdir -p /skyline
    cd /skyline
    wget https://skyline.ms/files/zips/SkylineCmd/SkylineCmd-21-2-x64.zip
    unzip SkylineCmd-21-2-x64.zip
    chmod +x SkylineCmd.exe
    rm SkylineCmd-21-2-x64.zip
    
    echo '#!/bin/bash' > /usr/local/bin/skylinecmd
    echo 'mono /skyline/SkylineCmd.exe "$@"' >> /usr/local/bin/skylinecmd
    chmod +x /usr/local/bin/skylinecmd

%environment
    export PATH="/skyline:$PATH"

%runscript
    skylinecmd "$@"

%labels
    Author Researcher
    Version v1.0
    Description Skyline Command Line Tool Container
EOF

# Build Singularity container from definition file
echo "Building Singularity container directly..."
singularity build skyline.sif Singularity.def

echo "Singularity container created: skyline.sif"
echo "You can run it with: singularity run skyline.sif [commands]"
echo "Or: singularity exec skyline.sif skylinecmd [commands]"

# Example usage instructions
cat << 'EOF'
Example commands for using the Singularity container:

# Display help
singularity run skyline.sif --help

# Process a Skyline file (binding a local directory)
singularity exec --bind /path/to/data:/data skyline.sif skylinecmd --in=/data/analysis.sky --report-conflict-resolution=true

# For running on a cluster, transfer the skyline.sif file to your cluster and use similar commands
EOF
