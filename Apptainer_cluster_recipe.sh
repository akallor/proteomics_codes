#!/usr/bin bash
#Download and install apptainer (and Golang, since apptainer requires Golang to run)
#For Red Hat and other Debian-based OS: use dnf
#For Ubuntu/other non-Debian-based OS: use apt

#Apt-recipe

# Install necessary build dependencies
sudo apt update
sudo apt install -y build-essential libseccomp-dev pkg-config squashfs-tools cryptsetup curl wget git

# Clone Apptainer repository
git clone https://github.com/apptainer/apptainer.git
cd apptainer

# Build Apptainer
./mconfig
cd builddir
make
sudo make install


# Set installation prefix to your home directory
./mconfig --prefix=$HOME/apptainer
cd builddir
make
make install
# Then add to your PATH
echo 'export PATH=$HOME/apptainer/bin:$PATH' >> ~/.bashrc
source ~/.bashrc

#Dnf-recipe

# Update package lists
sudo dnf update

# Install EPEL repository (Extra Packages for Enterprise Linux)
sudo dnf install -y epel-release

# Install dependencies
sudo dnf install -y wget git gcc make libseccomp-devel squashfs-tools cryptsetup

# Install Go (required for building Apptainer)
sudo dnf install -y golang

# Clone Apptainer repository
git clone https://github.com/apptainer/apptainer.git
cd apptainer

# Build Apptainer
./mconfig
cd builddir
make
sudo make install

#If you don't have sudo privileges, you can try installing it in your user space:

# Clone Apptainer repository
git clone https://github.com/apptainer/apptainer.git
cd apptainer

# Configure with prefix to your home directory
./mconfig --prefix=$HOME/.local
cd builddir
make
make install

# Add to your PATH
echo 'export PATH=$HOME/.local/bin:$PATH' >> ~/.bashrc
source ~/.bashrc




