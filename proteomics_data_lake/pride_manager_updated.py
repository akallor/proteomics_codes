<<<<<<< HEAD
=======
"""
Download datasets from the PRIDE url: https://www.ebi.ac.uk/pride/ws/archive/v3/webjars/swagger-ui/index.html#/projects/projects based on querying the /search/projects API
Then upload them to the existing AWS S3 bucket (need to install boto3 to work between the local machine and the S3 bucket).
"""

>>>>>>> 9875bb40d42f6f5a541d7b86756af500b20d3efc
import requests
import json
import os
import argparse
import time
import boto3
import urllib.parse
import urllib.request
import sys
from tqdm import tqdm

print("This is the merged version that includes both changes")

class PrideDatasetManager:
    def __init__(self, output_dir="./pride_data", s3_bucket=None):
        self.base_url = "https://www.ebi.ac.uk/pride/ws/archive/v3"
        self.output_dir = output_dir
        self.s3_bucket = s3_bucket

        # Create output directory if it doesn't exist
        os.makedirs(output_dir, exist_ok=True)

        # Initialize S3 client if bucket is provided
        self.s3_client = boto3.client('s3') if s3_bucket else None

    def search_datasets(self, keyword, page_size=100, page=0, filters=None,
                       sort_direction="DESC", sort_fields="submissionDate"):
        """
        Search for datasets in PRIDE using the v3 API
        """
        # Construct the query URL
        encoded_keyword = urllib.parse.quote(keyword)
        url = f"{self.base_url}/search/projects?keyword={encoded_keyword}&pageSize={page_size}&page={page}&sortDirection={sort_direction}&sortFields={sort_fields}"

        # Add filters if provided
        if filters:
            url += f"&filter={urllib.parse.quote(filters)}"

        print(f"Searching PRIDE with URL: {url}")

        # Make the request
        response = requests.get(url, headers={"Accept": "application/json"})

        if response.status_code == 200:
            result = response.json()
            print(f"Found {len(result)} datasets matching the search criteria")
            return result
        else:
            print(f"Error searching PRIDE: {response.status_code}")
            print(response.text)
            return []

    def get_dataset_files(self, accession):
        """
        Get the list of files for a specific dataset
        """
        url = f"{self.base_url}/projects/{accession}/files"
        response = requests.get(url, headers={"Accept": "application/json"})

        if response.status_code == 200:
            files = response.json()
            return files
        else:
            print(f"Error getting files for dataset {accession}: {response.status_code}")
            return []

    def download_file(self, url, output_path):
        """
        Download a file from a URL to a specified path
        """
        try:
            if url.startswith('ftp://'):
                # Handle FTP URLs using urllib
                with urllib.request.urlopen(url) as response, open(output_path, 'wb') as out_file:
                    total_size = int(response.headers.get('Content-Length', -1))
                    
                    with tqdm(
                        desc=os.path.basename(output_path),
                        total=total_size if total_size != -1 else None,
                        unit='B',
                        unit_scale=True,
                        unit_divisor=1024,
                    ) as pbar:
                        while True:
                            chunk = response.read(8192)
                            if not chunk:
                                break
                            out_file.write(chunk)
                            pbar.update(len(chunk))
                return True
            else:
                # Use requests for HTTP/HTTPS
                with requests.get(url, stream=True) as r:
                    r.raise_for_status()
                    total_size = int(r.headers.get('content-length', 0))

                    with open(output_path, 'wb') as f, tqdm(
                        desc=os.path.basename(output_path),
                        total=total_size,
                        unit='B',
                        unit_scale=True,
                        unit_divisor=1024,
                    ) as pbar:
                        for chunk in r.iter_content(chunk_size=8192):
                            if chunk:  # filter out keep-alive chunks
                                f.write(chunk)
                                pbar.update(len(chunk))
                return True
        except Exception as e:
            print(f"Error downloading {url}: {str(e)}")
            return False

    def download_dataset(self, accession, max_files=None, file_types=None):
        """
        Download all files for a specific dataset

        Parameters:
        - accession: PRIDE dataset accession ID
        - max_files: Maximum number of files to download (None for all)
        - file_types: List of file extensions to download (None for all)
        """
        # Get dataset files
        files = self.get_dataset_files(accession)

        if not files:
            print(f"No files found for dataset {accession}")
            return False

        # Filter files by type if specified
        if file_types:
            files = [f for f in files if any(f['fileName'].lower().endswith(ext.lower()) for ext in file_types)]

        # Limit the number of files if specified
        if max_files and len(files) > max_files:
            print(f"Limiting download to {max_files} of {len(files)} files")
            files = files[:max_files]

        # Create dataset directory
        dataset_dir = os.path.join(self.output_dir, accession)
        os.makedirs(dataset_dir, exist_ok=True)

        # Download each file
        success_count = 0
        for file in files:
            file_url = file.get('publicFileLocations', [{}])[0].get('value', None)
            if not file_url:
                print(f"No download URL for file {file['fileName']}")
                continue

            output_path = os.path.join(dataset_dir, file['fileName'])

            # Skip if file already exists
            if os.path.exists(output_path) and os.path.getsize(output_path) > 0:
                print(f"File already exists, skipping: {output_path}")
                success_count += 1
                continue

            print(f"Downloading {file['fileName']}...")
            if self.download_file(file_url, output_path):
                success_count += 1

                # Upload to S3 if bucket is specified
                if self.s3_bucket:
                    s3_key = f"data/{accession}/{file['fileName']}"
                    print(f"Uploading to S3: {s3_key}")
                    try:
                        self.s3_client.upload_file(output_path, self.s3_bucket, s3_key)
                    except Exception as e:
                        print(f"Error uploading to S3: {str(e)}")

        print(f"Downloaded {success_count} of {len(files)} files for dataset {accession}")
        return success_count > 0

    def get_project_details(self, accession):
        """
        Get detailed information about a project
        """
        url = f"{self.base_url}/projects/{accession}"
        response = requests.get(url, headers={"Accept": "application/json"})

        if response.status_code == 200:
            return response.json()
        else:
            print(f"Error getting details for dataset {accession}: {response.status_code}")
            return {}

    def extract_metadata(self, project_details):
        """
        Extract metadata from project details in the format required for the data lake
        """
        metadata = {
            "Data_access": "Public",  # Assuming all datasets from PRIDE are public
            "Dataset_ID": project_details.get('accession', ''),
            "Dataset_size_in_Gbs": 0,  # Will be calculated later
            "Experiment_type": "Proteomics",  # Default
            "MS_type": "DDA",  # Default
            "Enzyme": "Trypsin",  # Default
            "Disease": "Normal",  # Default
            "Disease_subtype": "Normal",  # Default
            "Sample_type": "Tissue",  # Default
            "Sample_details": "",
            "Year_of_publication": str(project_details.get('publicationDate', '').split('-')[0]) if project_details.get('publicationDate') else '',
            "DOI": project_details.get('doi', '')
        }

        # Try to extract more specific information from project details
        description = project_details.get('projectDescription', '').lower()
        title = project_details.get('title', '').lower()

        # Attempt to detect experiment type
        if 'immunopeptidom' in description or 'immunopeptidom' in title:
            metadata['Experiment_type'] = 'Immunopeptidomcs'

        # Attempt to detect MS type
        ms_types = {
            'dda': 'DDA',
            'dia': 'DIA',
            'wwa': 'WWA',
            'prm': 'PRM',
            'srm': 'SRM',
            'mrm': 'MRM'
        }
        for ms_key, ms_value in ms_types.items():
            if ms_key in description or ms_key in title:
                metadata['MS_type'] = ms_value
                break

        # Attempt to detect enzyme
        enzymes = {
            'trypsin': 'Trypsin',
            'chymotrypsin': 'Chymotrypsin',
            'lysc': 'LysC',
            'no enzyme': 'None'
        }
        for enz_key, enz_value in enzymes.items():
            if enz_key in description or enz_key in title:
                metadata['Enzyme'] = enz_value
                break

        # Attempt to detect disease
        if 'cancer' in description or 'cancer' in title or 'tumor' in description or 'tumor' in title:
            metadata['Disease'] = 'Cancer'

            # Try to detect cancer type
            cancer_types = ['breast', 'lung', 'liver', 'colon', 'prostate', 'ovarian', 'pancreatic', 'melanoma', 'leukemia']
            for cancer_type in cancer_types:
                if cancer_type in description or cancer_type in title:
                    metadata['Disease_subtype'] = f"{cancer_type.capitalize()} cancer"
                    break
        elif 'benign' in description or 'benign' in title:
            metadata['Disease'] = 'Benign'

        # Attempt to detect sample type
        sample_types = {
            'tissue': 'Tissue',
            'cell line': 'Cell line',
            'primary cell': 'Primary cell',
            'organoid': 'Organoid',
            'xenograft': 'Xenograft'
        }
        for sample_key, sample_value in sample_types.items():
            if sample_key in description or sample_key in title:
                metadata['Sample_type'] = sample_value
                break

        # Try to extract sample details
        if metadata['Sample_type'] == 'Cell line':
            cell_lines = ['hela', 'mcf7', 'mcf-7', 'hek293', 'hek-293', 'hct116', 'hct-116']
            for cell_line in cell_lines:
                if cell_line in description or cell_line in title:
                    metadata['Sample_details'] = cell_line.upper()
                    break

        # Extract keywords
        keywords = project_details.get('keywords', [])
        metadata['Keywords'] = ', '.join(keywords) if keywords else ''

        return metadata

    def calculate_directory_size_gb(self, directory):
        """Calculate the size of a directory in GB"""
        total_size = 0
        for dirpath, dirnames, filenames in os.walk(directory):
            for f in filenames:
                fp = os.path.join(dirpath, f)
                total_size += os.path.getsize(fp)
        return total_size / (1024 * 1024 * 1024)  # Convert bytes to GB

    def process_dataset(self, accession, override_metadata=None, max_files=None, file_types=None):
        """
        Process a single dataset: download files, extract metadata, upload to S3

        Parameters:
        - accession: PRIDE dataset accession ID
        - override_metadata: Dict of metadata values to override the automatically extracted ones
        - max_files: Maximum number of files to download
        - file_types: List of file extensions to download
        """
        print(f"Processing dataset {accession}...")

        # Get project details
        project_details = self.get_project_details(accession)
        if not project_details:
            print(f"Failed to get details for dataset {accession}")
            return False

        # Extract metadata
        metadata = self.extract_metadata(project_details)

        # Override metadata if provided
        if override_metadata:
            for key, value in override_metadata.items():
                if key in metadata:
                    metadata[key] = value

        # Download dataset files
        dataset_dir = os.path.join(self.output_dir, accession)
        success = self.download_dataset(accession, max_files, file_types)

        if success:
            # Calculate dataset size
            metadata['Dataset_size_in_Gbs'] = self.calculate_directory_size_gb(dataset_dir)

            # Save metadata to file
            metadata_file = os.path.join(dataset_dir, f"{accession}_metadata.json")
            with open(metadata_file, 'w') as f:
                json.dump(metadata, f, indent=2)

            # Upload metadata to S3 if bucket is specified
            if self.s3_bucket:
                metadata_key = f"metadata/{accession}/{accession}_metadata.json"
                try:
                    self.s3_client.upload_file(metadata_file, self.s3_bucket, metadata_key)
                    print(f"Uploaded metadata to S3: {metadata_key}")
                except Exception as e:
                    print(f"Error uploading metadata to S3: {str(e)}")

            print(f"Dataset {accession} processed successfully")
            return True
        else:
            print(f"Failed to download dataset {accession}")
            return False

def main():
    parser = argparse.ArgumentParser(description='Search and download datasets from PRIDE')
    parser.add_argument('--keyword', required=True, help='Search keyword')
    parser.add_argument('--output-dir', default='./pride_data', help='Output directory for downloaded files')
    parser.add_argument('--s3-bucket', help='S3 bucket for uploading files')
    parser.add_argument('--max-datasets', type=int, default=5, help='Maximum number of datasets to process')
    parser.add_argument('--max-files-per-dataset', type=int, help='Maximum number of files to download per dataset')
    parser.add_argument('--file-types', nargs='+', help='File types to download (e.g., RAW mzML)')
    parser.add_argument('--page-size', type=int, default=100, help='Number of results per page')
    parser.add_argument('--filter', help='Filter string in the format field1==value1,field2==value2')
    parser.add_argument('--sort-direction', default='DESC', choices=['ASC', 'DESC'], help='Sort direction')
    parser.add_argument('--sort-fields', default='submissionDate', help='Fields to sort by')

    args = parser.parse_args()

    manager = PrideDatasetManager(output_dir=args.output_dir, s3_bucket=args.s3_bucket)

    # Search for datasets
    datasets = manager.search_datasets(
        keyword=args.keyword,
        page_size=args.page_size,
        filters=args.filter,
        sort_direction=args.sort_direction,
        sort_fields=args.sort_fields
    )

    # Limit the number of datasets if specified
    if args.max_datasets and len(datasets) > args.max_datasets:
        print(f"Limiting to {args.max_datasets} of {len(datasets)} datasets")
        datasets = datasets[:args.max_datasets]

    # Process each dataset
    for dataset in datasets:
        accession = dataset.get('accession')
        if not accession:
            continue

        manager.process_dataset(
            accession=accession,
            max_files=args.max_files_per_dataset,
            file_types=args.file_types
        )

        # Add a small delay to avoid overwhelming the PRIDE API
        time.sleep(1)

if __name__ == "__main__":
    main()
