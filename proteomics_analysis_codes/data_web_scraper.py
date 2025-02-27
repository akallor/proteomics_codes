#!/usr/bin python

import os
import json
import requests
import asyncio
import aiohttp
from concurrent.futures import ThreadPoolExecutor
from multiprocessing import cpu_count

# Load keywords
with open("keywords.json", "r") as f:
    keywords = json.load(f)

BASE_URLS = {
    "PRIDE": "https://www.ebi.ac.uk/pride/ws/archive/",
    "MASSIVE": "https://massive.ucsd.edu/ProteoSAFe/proxi/v0.1/datasets"
}

# Define valid API fields
valid_pride_fields = ["accession", "title", "species", "instrument", "experimentType", "publicationDate"]
valid_massive_fields = ["id", "title", "organism", "instrument", "date", "description"]

# Define possible mappings for user-friendly keywords
field_mappings = {
    "species": ["organism", "taxonomy"],
    "experimentType": ["experiment", "type"],
    "instrument": ["machine", "mass spec"],
}

# Validate and map keywords
for key in list(keywords.keys()):
    if key not in valid_pride_fields and key not in valid_massive_fields:
        mapped = False
        for correct_field, alternatives in field_mappings.items():
            if key in alternatives:
                print(f"Mapping '{key}' to '{correct_field}'")
                keywords[correct_field] = keywords.pop(key)
                mapped = True
                break
        if not mapped:
            print(f"Warning: '{key}' is not a recognized field in PRIDE or MASSIVE.")

# Function to fetch dataset IDs from PRIDE API
def fetch_pride_projects():
    url = f"{BASE_URLS['PRIDE']}project/search"
    params = {"q": keywords.get("species", ""), "experimentType": keywords.get("experimentType", "")}
    response = requests.get(url, params=params)
    return [proj["accession"] for proj in response.json().get("projects", [])]

# Function to fetch RAW file URLs from PRIDE
def fetch_pride_files(project_id):
    url = f"{BASE_URLS['PRIDE']}file/list/project/{project_id}"
    response = requests.get(url)
    return [f['downloadLink'] for f in response.json() if f['fileName'].endswith('.raw')]

# Asynchronous downloader
async def download_file(session, url, dest_folder):
    os.makedirs(dest_folder, exist_ok=True)
    local_filename = os.path.join(dest_folder, url.split("/")[-1])
    async with session.get(url) as response:
        with open(local_filename, "wb") as f:
            while chunk := await response.content.read(8192):
                f.write(chunk)
    print(f"Downloaded: {local_filename}")

async def batch_download(urls, dest_folder):
    async with aiohttp.ClientSession() as session:
        tasks = [download_file(session, url, dest_folder) for url in urls]
        await asyncio.gather(*tasks)

if __name__ == "__main__":
    print("Fetching datasets...")
    project_ids = fetch_pride_projects()
    print(f"Found {len(project_ids)} projects")

    # Use ThreadPoolExecutor to fetch file URLs in parallel
    with ThreadPoolExecutor(max_workers=cpu_count() * 2) as executor:
        raw_file_urls = list(executor.map(fetch_pride_files, project_ids))
    
    raw_file_urls = [url for sublist in raw_file_urls for url in sublist]  # Flatten list
    print(f"Found {len(raw_file_urls)} RAW files")

    # Download in parallel using asyncio
    asyncio.run(batch_download(raw_file_urls, "downloads"))

