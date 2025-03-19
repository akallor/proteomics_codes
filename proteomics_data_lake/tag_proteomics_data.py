import json
import boto3
import requests
import os
import re
from typing import Dict, Any, List

def get_project_metadata(accession: str) -> Dict[str, Any]:
    """Fetch metadata for a specific PRIDE project by accession number."""
    url = f"https://www.ebi.ac.uk/pride/ws/archive/v3/projects/{accession}"
    headers = {"accept": "application/json"}
    
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        return response.json()
    else:
        print(f"Failed to fetch metadata for {accession}: {response.status_code}")
        return {}

def sanitize_tag_value(value: str) -> str:
    """Sanitize tag value to comply with S3 tag restrictions."""
    if not value:
        return "unknown"
    
    # Remove control characters and non-printable characters
    value = ''.join(c for c in value if ord(c) >= 32 and ord(c) <= 126)
    
    # Replace problematic characters with spaces
    value = re.sub(r'[^\w\s,.:-]', ' ', value)
    
    # Collapse multiple spaces
    value = re.sub(r'\s+', ' ', value)
    
    # Trim leading/trailing spaces
    value = value.strip()
    
    # Truncate to 255 characters (S3 limit)
    value = value[:255]
    
    # Handle empty values after sanitization
    if not value:
        return "unknown"
    
    return value

def extract_tags(metadata: Dict[str, Any]) -> Dict[str, str]:
    """Extract the desired tags from project metadata."""
    tags = {}
    
    # Extract simple fields
    simple_fields = ["accession", "title", "submissionType", "publicationDate"]
    for field in simple_fields:
        if field in metadata and metadata[field]:
            tags[field] = sanitize_tag_value(str(metadata[field]))
    
    # Handle submitters
    if "submitters" in metadata and metadata["submitters"]:
        submitters = []
        for s in metadata["submitters"]:
            name_parts = []
            if s.get("firstName"):
                name_parts.append(s.get("firstName"))
            if s.get("lastName"):
                name_parts.append(s.get("lastName"))
            if name_parts:
                submitters.append(" ".join(name_parts))
        if submitters:
            tags["submitters"] = sanitize_tag_value(", ".join(submitters))
    
    # Handle affiliations
    if "affiliations" in metadata and metadata["affiliations"]:
        tags["affiliations"] = sanitize_tag_value(", ".join(str(a) for a in metadata["affiliations"]))
    
    # Handle lists of objects with name fields
    for field in ["instruments", "softwares", "organisms", "organismsPart", "diseases"]:
        if field in metadata and metadata[field]:
            names = [str(item.get("name", "")) for item in metadata[field] if item.get("name")]
            if names:
                tags[field] = sanitize_tag_value(", ".join(names))
    
    # Handle references
    if "references" in metadata and metadata["references"]:
        refs = []
        for ref in metadata["references"]:
            if ref.get("doi"):
                refs.append(f"DOI:{ref.get('doi')}")
            elif ref.get("pubmedId"):
                refs.append(f"PMID:{ref.get('pubmedId')}")
        if refs:
            tags["references"] = sanitize_tag_value(", ".join(refs))
    
    # Handle highlights
    if "highlights" in metadata and metadata["highlights"]:
        tags["highlights"] = sanitize_tag_value(", ".join(str(h) for h in metadata["highlights"]))
    
    # Debug output
    print("\nTags to be applied:")
    for k, v in tags.items():
        print(f"  {k}: {v}")
    
    return tags

def tag_s3_object(bucket_name: str, object_key: str, tags: Dict[str, str]):
    """Apply tags to an S3 object."""
    s3_client = boto3.client('s3')
    
    # Convert tags to S3 format and ensure they're valid
    tag_set = []
    for k, v in tags.items():
        if v:  # Only add tags with non-empty values
            tag_set.append({"Key": k, "Value": v})
    
    try:
        # Validate we don't exceed the 10 tag limit
        if len(tag_set) > 10:
            print(f"Warning: Trimming tags for {object_key} to 10 (from {len(tag_set)})")
            tag_set = tag_set[:10]
        
        s3_client.put_object_tagging(
            Bucket=bucket_name,
            Key=object_key,
            Tagging={'TagSet': tag_set}
        )
        print(f"Successfully tagged {object_key}")
    except Exception as e:
        print(f"Error tagging {object_key}: {e}")
        print(f"Problematic tags: {tag_set}")

def tag_pride_datasets(bucket_name: str, prefix: str = ""):
    """
    Find all PRIDE datasets in the S3 bucket and tag them with metadata.
    """
    s3_client = boto3.client('s3')
    
    # List objects with the given prefix
    paginator = s3_client.get_paginator('list_objects_v2')
    pages = paginator.paginate(Bucket=bucket_name, Prefix=prefix, Delimiter="/")
    
    # Process each page of results
    for page in pages:
        # Process each dataset folder in this page
        for common_prefix in page.get('CommonPrefixes', []):
            folder_path = common_prefix.get('Prefix')
            
            # Extract accession from the folder path
            path_parts = folder_path.rstrip('/').split('/')
            accession = path_parts[-1]
            
            # Check if this looks like a PRIDE accession
            if not accession.startswith('PXD'):
                print(f"Folder {folder_path} doesn't appear to be a PRIDE dataset, skipping")
                continue
            
            print(f"Processing dataset {accession}")
            
            # Get metadata for this accession
            metadata = get_project_metadata(accession)
            if not metadata:
                print(f"No metadata found for {accession}")
                continue
            
            # Extract tags from metadata
            tags = extract_tags(metadata)
            
            # Get all objects in this dataset folder
            objects_paginator = s3_client.get_paginator('list_objects_v2')
            objects_pages = objects_paginator.paginate(Bucket=bucket_name, Prefix=folder_path)
            
            # Tag each object in the dataset folder
            for objects_page in objects_pages:
                for obj in objects_page.get('Contents', []):
                    key = obj['Key']
                    tag_s3_object(bucket_name, key, tags)

if __name__ == "__main__":
    # Use your actual bucket name
    BUCKET_NAME = "proteomics-datalake-pride"
    
    # Tag data folders
    PREFIX = "data/"
    
    tag_pride_datasets(BUCKET_NAME, PREFIX)
