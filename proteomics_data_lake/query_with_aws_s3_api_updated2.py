import boto3
import re
from datetime import datetime

def query_by_tags(bucket_name, tag_filters, match_types=None, match_all=False):
    """
    Query S3 objects by their tags with flexible matching options.
    
    Parameters:
    - bucket_name (str): Name of the S3 bucket
    - tag_filters (dict): Dictionary of tag key-value pairs to match
    - match_types (dict): Dictionary specifying match type for each tag key
    - match_all (bool): If True, all tag filters must match. If False, at least one must match.
    
    Returns:
    - list: Keys of matching S3 objects with metadata
    """
    s3_client = boto3.client('s3')
    paginator = s3_client.get_paginator("list_objects_v2")
    response = paginator.paginate(Bucket=bucket_name)
    matching_objects = []
    match_types = match_types or {}
    
    # Remove empty filter values if not using match_all
    if not match_all:
        tag_filters = {k: v for k, v in tag_filters.items() if v}
    
    # Handle case where no filters are provided
    if not tag_filters:
        return []
    
    for page in response:
        for obj in page.get('Contents', []):
            # Get tags for this object
            tags_response = s3_client.get_object_tagging(
                Bucket=bucket_name,
                Key=obj['Key']
            )
            
            # Convert tags to a dictionary
            tags_dict = {tag['Key']: tag['Value'] for tag in tags_response['TagSet']}
            
            # Track matches for each tag filter
            matches = []
            
            for key, value in tag_filters.items():
                # Skip empty filter values
                if not value:
                    continue
                
                # If the tag doesn't exist on the object
                if key not in tags_dict:
                    matches.append(False)
                    continue
                
                tag_value = tags_dict[key]
                match_type = match_types.get(key, 'exact')
                match_found = False
                
                if match_type == 'exact':
                    match_found = (tag_value == value)
                
                elif match_type == 'prefix':
                    match_found = tag_value.startswith(value)
                
                elif match_type == 'contains':
                    match_found = (value in tag_value)
                
                elif match_type == 'regex':
                    match_found = bool(re.match(value, tag_value))
                
                elif match_type == 'date_range':
                    # Expects value to be a tuple of (start_date, end_date)
                    start_date, end_date = value
                    try:
                        tag_date = datetime.strptime(tag_value, "%Y-%m-%d")
                        start = datetime.strptime(start_date, "%Y-%m-%d") if start_date else datetime.min
                        end = datetime.strptime(end_date, "%Y-%m-%d") if end_date else datetime.max
                        match_found = (start <= tag_date <= end)
                    except ValueError:
                        match_found = False
                
                matches.append(match_found)
            
            # Determine if the object matches based on match_all flag
            if match_all:
                # All filters must match
                if all(matches) and len(matches) > 0:
                    matching_objects.append({
                        'Key': obj['Key'],
                        'LastModified': obj['LastModified'],
                        'Size': obj['Size'],
                        'Tags': tags_dict
                    })
            else:
                # At least one filter must match
                if any(matches) and len(matches) > 0:
                    matching_objects.append({
                        'Key': obj['Key'],
                        'LastModified': obj['LastModified'],
                        'Size': obj['Size'],
                        'Tags': tags_dict
                    })
    
    return matching_objects

def filter_results(results, file_extensions=None, min_size=None, max_size=None, sort_by=None, limit=None):
    """
    Filter and sort the results from query_by_tags.
    
    Parameters:
    - results: The list of results from query_by_tags
    - file_extensions: List of file extensions to include (e.g., ['.raw', '.mzML'])
    - min_size: Minimum file size in bytes
    - max_size: Maximum file size in bytes
    - sort_by: Field to sort by ('Key', 'LastModified', 'Size')
    - limit: Maximum number of results to return
    
    Returns:
    - list: Filtered and sorted results
    """
    filtered = results[:]
    
    # Filter by file extension
    if file_extensions:
        filtered = [r for r in filtered if any(r['Key'].lower().endswith(ext.lower()) for ext in file_extensions)]
    
    # Filter by size
    if min_size is not None:
        filtered = [r for r in filtered if r['Size'] >= min_size]
    if max_size is not None:
        filtered = [r for r in filtered if r['Size'] <= max_size]
    
    # Sort results
    if sort_by:
        filtered.sort(key=lambda x: x[sort_by])
    
    # Limit results
    if limit:
        filtered = filtered[:limit]
    
    return filtered

# Example usage
if __name__ == "__main__":
    # Example 1: Get files matching ANY of the provided criteria
    results = query_by_tags(
        'proteomics-datalake-pride',
        {
            'publicationDate': '2025',
            'instruments': '',  # Empty string will be ignored
            'diseases': 'neuroblastoma'
        },
        match_types={
            'publicationDate': 'prefix',
            'instruments': 'contains',
            'diseases': 'contains'
        },
        match_all=False  # Match ANY of the provided criteria
    )
    
    print(f"Found {len(results)} files matching ANY criteria")
    
    # Filter for RAW files only
    raw_files = filter_results(results, file_extensions=['.raw'])
    for item in raw_files[:5]:  # Show first 5 results
        print(f"{item['Key']} - {item['Size']} bytes - Published: {item['Tags'].get('publicationDate', 'unknown')}")
        print(f"  Diseases: {item['Tags'].get('diseases', 'N/A')}")
        print(f"  Instruments: {item['Tags'].get('instruments', 'N/A')}")
    
    # Example 2: Get files matching ALL of the provided criteria
    strict_results = query_by_tags(
        'proteomics-datalake-pride',
        {
            'publicationDate': '2025',
            'diseases': 'Brain cancer'
        },
        match_types={
            'publicationDate': 'prefix',
            'diseases': 'contains'
        },
        match_all=True  # Match ALL of the provided criteria
    )
    
    print(f"\nFound {len(strict_results)} files matching ALL criteria")
    
    # Example 3: Search with multiple optional fields (up to 10)
    multi_tag_results = query_by_tags(
        'proteomics-datalake-pride',
        {
            'publicationDate': '2025',
            'diseases': 'lymphoma',
            'instruments': '',
            'species': 'Homo sapiens',
            'cellType': 'bone marrow',
            'tissueType': '',
            'proteinConcentration': '',
            'experimentType': 'DDA',
            'sampleType': '',
            'institutionName': ''
        },
        match_types={
            'publicationDate': 'prefix',
            'diseases': 'contains',
            'instruments': 'contains',
            'species': 'exact',
            'cellType': 'contains',
            'tissueType': 'contains',
            'proteinConcentration': 'contains',
            'experimentType': 'exact',
            'sampleType': 'contains',
            'institutionName': 'contains'
        },
        match_all=False  # Match ANY of the provided criteria
    )
    
    print(f"\nFound {len(multi_tag_results)} files matching any of the 10 criteria")
