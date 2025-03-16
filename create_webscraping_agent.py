import requests
from bs4 import BeautifulSoup
import pandas as pd
import time
import smtplib
import imaplib
import email
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import re
import os
from datetime import datetime, timedelta
import logging
import schedule

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("proteome_monitor.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("ProteomeExchange Monitor")

# Configuration variables - replace with your actual values
EMAIL_ADDRESS = "your_email@example.com"  # Replace with your email
EMAIL_PASSWORD = "your_app_password"      # Use app password for Gmail
SMTP_SERVER = "smtp.gmail.com"            # Adjust based on your email provider
SMTP_PORT = 587                           # Standard TLS port
IMAP_SERVER = "imap.gmail.com"            # Adjust based on your email provider
CHECK_INTERVAL_HOURS = 24                 # How often to check for new datasets
TIME_WINDOW_HOURS = 48                    # Time window for considering datasets as "new"
DOWNLOAD_DIR = "datasets"                 # Directory to save downloaded datasets

# Create download directory if it doesn't exist
os.makedirs(DOWNLOAD_DIR, exist_ok=True)

# Store previously found datasets to avoid duplicate notifications
previous_datasets = set()

def get_proteome_exchange_datasets():
    """
    Scrape ProteomeExchange website for datasets related to pediatric cancer
    """
    # Base URL for ProteomeExchange
    base_url = "http://proteomecentral.proteomexchange.org/cgi/GetDataset"
    
    # Search terms
    search_terms = [
        "pediatric cancer", 
        "childhood cancer", 
        "pediatric tumor", 
        "pediatric oncology",
        "pediatric immunopeptidomics",
        "pediatric proteomics"
    ]
    
    all_datasets = []
    
    for term in search_terms:
        logger.info(f"Searching for term: {term}")
        
        # Parameters for the search
        params = {
            "action": "list",
            "test": "no",
            "keywords": term,
            "species": "",
            "instrument": "",
            "publicationdate": "",
            "maxhits": "100",  # Adjust as needed
            "format": "json"
        }
        
        try:
            response = requests.get(base_url, params=params)
            response.raise_for_status()
            
            if response.headers.get('content-type') == 'application/json':
                data = response.json()
                if 'datasets' in data:
                    all_datasets.extend(data['datasets'])
            else:
                logger.warning(f"Unexpected content type: {response.headers.get('content-type')}")
                
        except requests.exceptions.RequestException as e:
            logger.error(f"Error fetching data for term '{term}': {e}")
    
    # Remove duplicates
    unique_datasets = []
    seen_ids = set()
    
    for dataset in all_datasets:
        if dataset.get('id') not in seen_ids:
            seen_ids.add(dataset.get('id'))
            unique_datasets.append(dataset)
    
    return unique_datasets

def is_recent_dataset(dataset, hours):
    """
    Check if a dataset was published within the specified time window
    """
    if 'publicationDate' not in dataset:
        return False
    
    try:
        pub_date = datetime.strptime(dataset['publicationDate'], "%Y-%m-%d")
        cutoff_date = datetime.now() - timedelta(hours=hours)
        return pub_date >= cutoff_date.date()
    except (ValueError, KeyError):
        logger.warning(f"Could not parse publication date for dataset {dataset.get('id')}")
        return False

def is_pediatric_cancer_dataset(dataset):
    """
    Check if a dataset is related to pediatric cancer
    """
    keywords = ["pediatric", "childhood", "child", "children", "young", "infant"]
    cancer_terms = ["cancer", "tumor", "neoplasm", "oncology", "malignancy"]
    
    # Check title
    title = dataset.get('title', '').lower()
    description = dataset.get('description', '').lower()
    
    has_pediatric = any(keyword in title or keyword in description for keyword in keywords)
    has_cancer = any(term in title or term in description for term in cancer_terms)
    
    is_proteomics = "proteom" in title or "proteom" in description
    is_immunopeptidomics = "immunopeptid" in title or "immunopeptid" in description or "hla" in title or "hla" in description
    
    return (has_pediatric and has_cancer) and (is_proteomics or is_immunopeptidomics)

def send_email_notification(dataset):
    """
    Send an email notification about a new dataset
    """
    subject = f"New Pediatric Cancer Dataset Found: {dataset.get('id')}"
    
    body = f"""
    New pediatric cancer proteomics/immunopeptidomics dataset found on ProteomeExchange:
    
    Dataset ID: {dataset.get('id')}
    Title: {dataset.get('title')}
    Publication Date: {dataset.get('publicationDate')}
    Description: {dataset.get('description')}
    
    Would you like to download this dataset? Reply with 'Yes' or 'No'.
    """
    
    msg = MIMEMultipart()
    msg['From'] = EMAIL_ADDRESS
    msg['To'] = EMAIL_ADDRESS
    msg['Subject'] = subject
    
    msg.attach(MIMEText(body, 'plain'))
    
    try:
        server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
        server.starttls()
        server.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
        server.send_message(msg)
        server.quit()
        logger.info(f"Email notification sent for dataset {dataset.get('id')}")
        return True
    except Exception as e:
        logger.error(f"Failed to send email: {e}")
        return False

def download_dataset(dataset):
    """
    Download a dataset from ProteomeExchange
    """
    dataset_id = dataset.get('id')
    ftp_link = dataset.get('ftp_link')
    
    if not ftp_link:
        logger.error(f"No FTP link available for dataset {dataset_id}")
        return False
    
    try:
        # Create a directory for this dataset
        dataset_dir = os.path.join(DOWNLOAD_DIR, dataset_id)
        os.makedirs(dataset_dir, exist_ok=True)
        
        # Here we'd implement the actual download logic
        # This would depend on the exact structure of ProteomeExchange datasets
        # For now, log that we would download it
        logger.info(f"Downloading dataset {dataset_id} to {dataset_dir}")
        logger.info(f"Would download from: {ftp_link}")
        
        # For an actual implementation, you might use:
        # - requests for HTTP downloads
        # - ftplib for FTP downloads
        # - subprocess to call wget or curl
        
        # Simulation of download success
        with open(os.path.join(dataset_dir, "download_info.txt"), "w") as f:
            f.write(f"Dataset ID: {dataset_id}\n")
            f.write(f"Download URL: {ftp_link}\n")
            f.write(f"Download time: {datetime.now().isoformat()}\n")
        
        return True
    except Exception as e:
        logger.error(f"Error downloading dataset {dataset_id}: {e}")
        return False

def check_email_responses():
    """
    Check email inbox for responses to dataset notifications
    """
    try:
        mail = imaplib.IMAP4_SSL(IMAP_SERVER)
        mail.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
        mail.select('inbox')
        
        # Search for unread emails with specific subject pattern
        search_query = '(UNSEEN SUBJECT "Re: New Pediatric Cancer Dataset Found")'
        status, messages = mail.search(None, search_query)
        
        if status != 'OK':
            logger.warning("No messages found or error in search")
            return
        
        for num in messages[0].split():
            status, data = mail.fetch(num, '(RFC822)')
            if status != 'OK':
                continue
                
            msg = email.message_from_bytes(data[0][1])
            subject = msg['subject']
            
            # Extract the dataset ID from the subject
            dataset_id_match = re.search(r'New Pediatric Cancer Dataset Found: (PXD\d+)', subject)
            if not dataset_id_match:
                logger.warning(f"Could not extract dataset ID from subject: {subject}")
                continue
                
            dataset_id = dataset_id_match.group(1)
            
            # Get email body
            if msg.is_multipart():
                for part in msg.walk():
                    content_type = part.get_content_type()
                    content_disposition = str(part.get("Content-Disposition"))
                    
                    if content_type == "text/plain" and "attachment" not in content_disposition:
                        body = part.get_payload(decode=True).decode()
                        break
            else:
                body = msg.get_payload(decode=True).decode()
            
            # Check if the response is "Yes" or "No"
            if re.search(r'\byes\b', body, re.I):
                logger.info(f"User approved download of dataset {dataset_id}")
                
                # Find the dataset info
                datasets = get_proteome_exchange_datasets()
                for dataset in datasets:
                    if dataset.get('id') == dataset_id:
                        download_dataset(dataset)
                        break
                else:
                    logger.warning(f"Could not find dataset {dataset_id} for download")
            
            elif re.search(r'\bno\b', body, re.I):
                logger.info(f"User declined download of dataset {dataset_id}")
            
            # Mark email as read
            mail.store(num, '+FLAGS', '\\Seen')
        
        mail.close()
        mail.logout()
    
    except Exception as e:
        logger.error(f"Error checking email responses: {e}")

def check_for_new_datasets():
    """
    Main function to check for new datasets
    """
    global previous_datasets
    
    logger.info("Checking for new pediatric cancer datasets...")
    
    try:
        # Get all datasets
        datasets = get_proteome_exchange_datasets()
        logger.info(f"Found {len(datasets)} total datasets")
        
        # Filter for recent datasets related to pediatric cancer
        new_datasets = []
        for dataset in datasets:
            dataset_id = dataset.get('id')
            
            if (dataset_id not in previous_datasets and 
                is_recent_dataset(dataset, TIME_WINDOW_HOURS) and 
                is_pediatric_cancer_dataset(dataset)):
                
                new_datasets.append(dataset)
                previous_datasets.add(dataset_id)
        
        logger.info(f"Found {len(new_datasets)} new pediatric cancer datasets")
        
        # Send notifications for new datasets
        for dataset in new_datasets:
            send_email_notification(dataset)
        
        # Check for responses to previous notifications
        check_email_responses()
        
    except Exception as e:
        logger.error(f"Error in dataset check cycle: {e}")

def run_continuously():
    """
    Set up scheduler to run checks at regular intervals
    """
    logger.info(f"Setting up monitoring every {CHECK_INTERVAL_HOURS} hours")
    
    # Run immediately on startup
    check_for_new_datasets()
    
    # Schedule regular runs
    schedule.every(CHECK_INTERVAL_HOURS).hours.do(check_for_new_datasets)
    
    while True:
        schedule.run_pending()
        time.sleep(60)  # Check every minute if there are scheduled tasks to run

if __name__ == "__main__":
    logger.info("Starting ProteomeExchange pediatric cancer dataset monitor")
    run_continuously()
