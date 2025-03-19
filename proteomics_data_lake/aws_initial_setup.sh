# Install and configure AWS CLI
#The key cannot be shown for security reasons.
pip install awscli
#The secret key cannot be added here due to security reasons
aws configure  # Enter your AWS credentials when prompted 

#AWS Access ID: AKIAU6GDYU554DIVROMT
#Default region name [ap-southeast-2]: ap-southeast-2
#Default output format [json]: json

#Create S3 Bucket for Data Lake Storage

aws s3 mb s3://proteomics-datalake-pride
