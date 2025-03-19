import boto3

def query_by_tags(bucket_name, tag_filters):
    s3_client = boto3.client('s3')

    # Get the paginator for listing objects
    paginator = s3_client.get_paginator("list_objects_v2")
    response = paginator.paginate(Bucket=bucket_name)

    matching_objects = []

    for page in response:
        for obj in page.get('Contents', []):
            # Get tags for this object
            tags_response = s3_client.get_object_tagging(
                Bucket=bucket_name,
                Key=obj['Key']
            )

            # Check if object matches all filter criteria
            tags_dict = {tag['Key']: tag['Value'] for tag in tags_response['TagSet']}

            if all(tags_dict.get(k) == v for k, v in tag_filters.items()):
                matching_objects.append(obj['Key'])

    return matching_objects

# Example query
results = query_by_tags('proteomics-datalake-pride', {
    'publicationDate': '2025-01-28',
    'instruments': 'Q Exactive HF',
    'diseases': 'Brain cancer'
})

for item in results:
    if item.endswith('.raw'):
        print(item)
