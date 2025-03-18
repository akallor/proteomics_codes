# Install and configure AWS CLI
pip install awscli

aws configure  # Enter your AWS credentials when prompted 

#AWS Access ID: AKIAU6GDYU554DIVROMT
#Secret Access ID: ELwi+GmPOwgBC1PBFwfVCXsyRQHjBrGBZ2OMBrfT
#Default region name [ap-southeast-2]: ap-southeast-2
#Default output format [json]: json

#Create S3 Bucket for Data Lake Storage

aws s3 mb s3://proteomics-datalake-pride
