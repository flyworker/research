# Nebula Block Storage Access Guide for Mac Silicon

This guide demonstrates how to access Nebula Block object storage using Python on Mac Silicon (Apple Silicon) machines.

## Overview

Nebula Block provides S3-compatible object storage that can be accessed using the AWS SDK for Python (boto3). This guide will walk you through setting up and using Nebula Block storage on your Mac Silicon machine.

## Prerequisites

- Python 3.8+ installed on your Mac Silicon machine
- Nebula Block account with access credentials
- Nebula Block storage deployment created

## Installation

1. Create a virtual environment (recommended):

```bash
python -m venv venv
source venv/bin/activate
```

2. Install required packages:

```bash
pip install boto3 python-dotenv
```

## Configuration

1. Create a `.env` file in your project directory:

```
NEBULA_ACCESS_KEY=your_access_key
NEBULA_SECRET_KEY=your_secret_key
NEBULA_ENDPOINT=s3-us-east.nebulablock.com
NEBULA_REGION=US
NEBULA_BUCKET=your_bucket_name
```

2. Create a configuration script (`config.py`):

```python
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Nebula Block configuration
NEBULA_CONFIG = {
    'aws_access_key_id': os.getenv('NEBULA_ACCESS_KEY'),
    'aws_secret_access_key': os.getenv('NEBULA_SECRET_KEY'),
    'endpoint_url': f"https://{os.getenv('NEBULA_ENDPOINT')}",
    'region_name': os.getenv('NEBULA_REGION'),
    'bucket_name': os.getenv('NEBULA_BUCKET')
}
```

## Basic Operations

### Connecting to Nebula Block Storage

```python
import boto3
from config import NEBULA_CONFIG

# Create an S3 client
s3_client = boto3.client(
    's3',
    aws_access_key_id=NEBULA_CONFIG['aws_access_key_id'],
    aws_secret_access_key=NEBULA_CONFIG['aws_secret_access_key'],
    endpoint_url=NEBULA_CONFIG['endpoint_url'],
    region_name=NEBULA_CONFIG['region_name']
)

# Test connection
try:
    s3_client.list_buckets()
    print("Successfully connected to Nebula Block storage!")
except Exception as e:
    print(f"Error connecting to Nebula Block: {e}")
```

### Creating a Bucket

```python
def create_bucket(bucket_name):
    try:
        s3_client.create_bucket(Bucket=bucket_name)
        print(f"Bucket '{bucket_name}' created successfully!")
    except Exception as e:
        print(f"Error creating bucket: {e}")

# Create a bucket
create_bucket(NEBULA_CONFIG['bucket_name'])
```

### Uploading Files

```python
def upload_file(file_path, object_name=None):
    """
    Upload a file to Nebula Block storage
    
    Args:
        file_path (str): Path to the file to upload
        object_name (str, optional): Name to give the object in storage. 
                                   If not provided, uses the file name.
    """
    if object_name is None:
        object_name = os.path.basename(file_path)
    
    try:
        s3_client.upload_file(file_path, NEBULA_CONFIG['bucket_name'], object_name)
        print(f"File '{file_path}' uploaded successfully as '{object_name}'!")
    except Exception as e:
        print(f"Error uploading file: {e}")

# Example usage
upload_file('path/to/your/file.txt', 'custom_name.txt')
```

### Downloading Files

```python
def download_file(object_name, file_path=None):
    """
    Download a file from Nebula Block storage
    
    Args:
        object_name (str): Name of the object in storage
        file_path (str, optional): Path to save the file to. 
                                 If not provided, uses the object name.
    """
    if file_path is None:
        file_path = object_name
    
    try:
        s3_client.download_file(NEBULA_CONFIG['bucket_name'], object_name, file_path)
        print(f"File '{object_name}' downloaded successfully to '{file_path}'!")
    except Exception as e:
        print(f"Error downloading file: {e}")

# Example usage
download_file('custom_name.txt', 'downloaded_file.txt')
```

### Listing Objects in a Bucket

```python
def list_objects(prefix=None):
    """
    List objects in a bucket
    
    Args:
        prefix (str, optional): Filter objects by prefix
    """
    try:
        if prefix:
            response = s3_client.list_objects_v2(
                Bucket=NEBULA_CONFIG['bucket_name'],
                Prefix=prefix
            )
        else:
            response = s3_client.list_objects_v2(
                Bucket=NEBULA_CONFIG['bucket_name']
            )
        
        if 'Contents' in response:
            print(f"Objects in bucket '{NEBULA_CONFIG['bucket_name']}':")
            for obj in response['Contents']:
                print(f"  - {obj['Key']} ({obj['Size']} bytes)")
        else:
            print(f"No objects found in bucket '{NEBULA_CONFIG['bucket_name']}'")
    except Exception as e:
        print(f"Error listing objects: {e}")

# Example usage
list_objects()
list_objects(prefix='images/')
```

### Deleting Objects

```python
def delete_object(object_name):
    """
    Delete an object from storage
    
    Args:
        object_name (str): Name of the object to delete
    """
    try:
        s3_client.delete_object(
            Bucket=NEBULA_CONFIG['bucket_name'],
            Key=object_name
        )
        print(f"Object '{object_name}' deleted successfully!")
    except Exception as e:
        print(f"Error deleting object: {e}")

# Example usage
delete_object('custom_name.txt')
```

## Complete Example Script

Here's a complete example script that demonstrates all the basic operations:

```python
import os
import boto3
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Nebula Block configuration
NEBULA_CONFIG = {
    'aws_access_key_id': os.getenv('NEBULA_ACCESS_KEY'),
    'aws_secret_access_key': os.getenv('NEBULA_SECRET_KEY'),
    'endpoint_url': f"https://{os.getenv('NEBULA_ENDPOINT')}",
    'region_name': os.getenv('NEBULA_REGION'),
    'bucket_name': os.getenv('NEBULA_BUCKET')
}

def main():
    # Create an S3 client
    s3_client = boto3.client(
        's3',
        aws_access_key_id=NEBULA_CONFIG['aws_access_key_id'],
        aws_secret_access_key=NEBULA_CONFIG['aws_secret_access_key'],
        endpoint_url=NEBULA_CONFIG['endpoint_url'],
        region_name=NEBULA_CONFIG['region_name']
    )
    
    # Test connection
    try:
        s3_client.list_buckets()
        print("Successfully connected to Nebula Block storage!")
    except Exception as e:
        print(f"Error connecting to Nebula Block: {e}")
        return
    
    # Create a test file
    with open('test_file.txt', 'w') as f:
        f.write('This is a test file for Nebula Block storage.')
    
    # Upload the file
    try:
        s3_client.upload_file('test_file.txt', NEBULA_CONFIG['bucket_name'], 'test_file.txt')
        print("File uploaded successfully!")
    except Exception as e:
        print(f"Error uploading file: {e}")
    
    # List objects in the bucket
    try:
        response = s3_client.list_objects_v2(Bucket=NEBULA_CONFIG['bucket_name'])
        if 'Contents' in response:
            print("Objects in bucket:")
            for obj in response['Contents']:
                print(f"  - {obj['Key']} ({obj['Size']} bytes)")
    except Exception as e:
        print(f"Error listing objects: {e}")
    
    # Download the file
    try:
        s3_client.download_file(NEBULA_CONFIG['bucket_name'], 'test_file.txt', 'downloaded_test_file.txt')
        print("File downloaded successfully!")
    except Exception as e:
        print(f"Error downloading file: {e}")
    
    # Delete the file
    try:
        s3_client.delete_object(Bucket=NEBULA_CONFIG['bucket_name'], Key='test_file.txt')
        print("File deleted successfully!")
    except Exception as e:
        print(f"Error deleting file: {e}")
    
    # Clean up local files
    if os.path.exists('test_file.txt'):
        os.remove('test_file.txt')
    if os.path.exists('downloaded_test_file.txt'):
        os.remove('downloaded_test_file.txt')

if __name__ == "__main__":
    main()
```

## Advanced Usage

### Working with Large Files

For large files, you can use multipart uploads:

```python
def upload_large_file(file_path, object_name=None):
    """
    Upload a large file using multipart upload
    
    Args:
        file_path (str): Path to the file to upload
        object_name (str, optional): Name to give the object in storage
    """
    if object_name is None:
        object_name = os.path.basename(file_path)
    
    try:
        # Create a multipart upload
        response = s3_client.create_multipart_upload(
            Bucket=NEBULA_CONFIG['bucket_name'],
            Key=object_name
        )
        upload_id = response['UploadId']
        
        # Get file size
        file_size = os.path.getsize(file_path)
        
        # Calculate part size (5MB minimum)
        part_size = 5 * 1024 * 1024  # 5MB
        parts = []
        
        # Upload parts
        with open(file_path, 'rb') as f:
            part_number = 1
            while True:
                data = f.read(part_size)
                if not data:
                    break
                
                response = s3_client.upload_part(
                    Bucket=NEBULA_CONFIG['bucket_name'],
                    Key=object_name,
                    PartNumber=part_number,
                    UploadId=upload_id,
                    Body=data
                )
                
                parts.append({
                    'PartNumber': part_number,
                    'ETag': response['ETag']
                })
                
                part_number += 1
        
        # Complete multipart upload
        s3_client.complete_multipart_upload(
            Bucket=NEBULA_CONFIG['bucket_name'],
            Key=object_name,
            UploadId=upload_id,
            MultipartUpload={'Parts': parts}
        )
        
        print(f"Large file '{file_path}' uploaded successfully as '{object_name}'!")
    except Exception as e:
        print(f"Error uploading large file: {e}")
        # Abort multipart upload if it exists
        try:
            s3_client.abort_multipart_upload(
                Bucket=NEBULA_CONFIG['bucket_name'],
                Key=object_name,
                UploadId=upload_id
            )
        except:
            pass
```

### Generating Presigned URLs

You can generate presigned URLs for temporary access to objects:

```python
def generate_presigned_url(object_name, expiration=3600):
    """
    Generate a presigned URL for temporary access to an object
    
    Args:
        object_name (str): Name of the object
        expiration (int): URL expiration time in seconds (default: 1 hour)
    
    Returns:
        str: Presigned URL
    """
    try:
        url = s3_client.generate_presigned_url(
            'get_object',
            Params={
                'Bucket': NEBULA_CONFIG['bucket_name'],
                'Key': object_name
            },
            ExpiresIn=expiration
        )
        return url
    except Exception as e:
        print(f"Error generating presigned URL: {e}")
        return None

# Example usage
url = generate_presigned_url('custom_name.txt', expiration=7200)  # 2 hours
if url:
    print(f"Presigned URL: {url}")
```

## Troubleshooting

### Common Issues

1. **Authentication Errors**: Verify your access key and secret key are correct
2. **Connection Errors**: Check your internet connection and ensure the endpoint URL is correct
3. **Permission Errors**: Ensure your account has the necessary permissions for the operations you're trying to perform
4. **Bucket Not Found**: Verify the bucket name exists and is correctly specified

### Debugging

Enable debug mode for more detailed error information:

```python
import logging

# Configure logging
logging.basicConfig(level=logging.DEBUG)
```

## Resources

- [Nebula Block Documentation](https://docs.nebulablock.com/)
- [AWS SDK for Python (boto3) Documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/index.html)
- [S3 API Reference](https://docs.aws.amazon.com/AmazonS3/latest/API/Welcome.html) 