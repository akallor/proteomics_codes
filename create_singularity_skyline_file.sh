#!/usr/bin bash

#Create a working directory for your Apptainer build
mkdir -p ~/skyline-apptainer
cd ~/skyline-apptainer

#Create the skyline definition file
nano skyline.def

#Copy your Skyline files to this same directory:
#Copy your entire Skyline folder to ~/skyline-apptainer/Skyline
#Copy the SkylineRunner.exe to ~/skyline-apptainer/SkylineRunner.exe

#Build the container from this directory

cd ~/skyline-apptainer
apptainer build skyline.sif skyline.def

#Run the container
apptainer run skyline.sif --help
