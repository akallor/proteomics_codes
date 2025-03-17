
#!/bin/bash
# Script to create and build a Docker container for Skyline

# 1. Create a Dockerfile for Skyline
cat > Dockerfile << 'EOF'
FROM ubuntu:22.04

# Install dependencies
RUN apt-get update && apt-get install -y \
    wget \
    unzip \
    libgdiplus \
    libc6-dev \
    mono-complete \
    mono-devel \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /skyline

# Download and install Skyline command line tool
RUN wget https://skyline.ms/files/zips/SkylineCmd/SkylineCmd-21-2-x64.zip \
    && unzip SkylineCmd-21-2-x64.zip \
    && chmod +x SkylineCmd.exe \
    && rm SkylineCmd-21-2-x64.zip

# Create a wrapper script to make execution easier
RUN echo '#!/bin/bash\nmono /skyline/SkylineCmd.exe "$@"' > /usr/local/bin/skylinecmd \
    && chmod +x /usr/local/bin/skylinecmd

# Set environment variables
ENV PATH="/skyline:${PATH}"

# Set entrypoint
ENTRYPOINT ["skylinecmd"]
EOF

# 2. Build the Docker image
docker build -t skyline:latest .

# 3. Test the Docker image
docker run --rm skyline:latest --help

echo "Docker image for Skyline has been created successfully!"
echo "You can run it with: docker run --rm skyline:latest [commands]"
