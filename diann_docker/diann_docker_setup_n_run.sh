
#Install wsl and then Debian if unavailable
apt install wsl

wsl --install -d Debian

#Install docker for linux and start

sudo apt update && sudo apt install docker.io -y
sudo service docker start

#Naviagate to the DIA-NN directory

cd DIA-NN-2.0.1-Academia-Linux

#Build the docker container

docker build --no-cache -t diann_docker .

#Save docker image for reuse on a different Linux system
docker save -o diann_docker.tar diann_docker

#Load saved docker image on a different Linux system
docker load -i diann_docker.tar

#Run docker image
docker run -it diann_docker

#After entering docker run as above, then naviagate to the diann folder
cd diann-2.0.1

#Run DIA-NN inside the docker image
./diann-linux

#Mount directory onto docker image
docker run -it -v /root/DIA-NN-2.0.1-Academia-Linux/diann-2.0.1:/data diann_docker bash

#Copy files to container after mounting
docker cp /root/DIA-NN-2.0.1-Academia-Linux/diann-2.0.1 diann_container:/data

##Running DIA-NN and msconvert using pre-prepared images

#Load msconvert image (prepared previously)

docker load -i msconvert.tar

#Run the conversion of one example file

docker run --rm -v "$(pwd)":/data msconvert /data/HLM_DIA_Pool1.wiff --mzML

#Copy the converted mzML file to the docker container (diann_container2)

docker cp *.mzML diann_container2:/diann-2.0.1/

#Start the docker DIA-NN container in detached mode (if the container already exists)

docker start -ai diann_container2

#Run DIA-NN on the mzML file with the library and number of thread specified (in quick mode to save memory)

./diann-linux --f HLM_DIA_Pool1-HLM#1.mzML --lib K562-spin-column-lib.tsv --out result.tsv --threads 4 --predictor quick
