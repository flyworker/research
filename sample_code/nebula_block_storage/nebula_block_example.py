#!/usr/bin/env python3
"""
Nebula Block Storage Example for Mac Silicon

This script demonstrates how to use Nebula Block object storage on Mac Silicon
using the AWS SDK for Python (boto3).
"""

import os
import sys
import logging
import boto3
from dotenv import load_dotenv

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

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

# Validate configuration
def validate_config():
    """Validate that all required configuration values are set."""
    missing_vars = []
    for key, value in NEBULA_CONFIG.items():
        if value is None:
            missing_vars.append(key)
    
    if missing_vars:
        logger.error(f"Missing configuration values: {', '.join(missing_vars)}")
        logger.error("Please set the required environment variables in your .env file.")
        return False
    
    return True

# Create an S3 client
def create_s3_client():
    """Create and return an S3 client for Nebula Block."""
    try:
        s3_client = boto3.client(
            's3',
            aws_access_key_id=NEBULA_CONFIG['aws_access_key_id'],
            aws_secret_access_key=NEBULA_CONFIG['aws_secret_access_key'],
            endpoint_url=NEBULA_CONFIG['endpoint_url'],
            region_name=NEBULA_CONFIG['region_name']
        )
        return s3_client
    except Exception as e:
        logger.error(f"Error creating S3 client: {e}")
        return None

# Test connection
def test_connection(s3_client):
    """Test the connection to Nebula Block storage."""
    try:
        s3_client.list_buckets()
        logger.info("Successfully connected to Nebula Block storage!")
        return True
    except Exception as e:
        logger.error(f"Error connecting to Nebula Block: {e}")
        return False

# Create a bucket
def create_bucket(s3_client, bucket_name):
    """Create a bucket in Nebula Block storage."""
    try:
        s3_client.create_bucket(Bucket=bucket_name)
        logger.info(f"Bucket '{bucket_name}' created successfully!")
        return True
    except Exception as e:
        logger.error(f"Error creating bucket: {e}")
        return False

# Create a bucket if it doesn't exist
def create_bucket_if_not_exists(s3_client, bucket_name):
    """Create a bucket if it doesn't exist."""
    try:
        s3_client.head_bucket(Bucket=bucket_name)
        logger.info(f"Bucket '{bucket_name}' already exists.")
        return True
    except:
        try:
            s3_client.create_bucket(Bucket=bucket_name)
            logger.info(f"Bucket '{bucket_name}' created successfully.")
            return True
        except Exception as e:
            logger.error(f"Error creating bucket: {e}")
            return False

# Upload a file
def upload_file(s3_client, file_path, object_name=None):
    """
    Upload a file to Nebula Block storage.
    
    Args:
        s3_client: The S3 client
        file_path (str): Path to the file to upload
        object_name (str, optional): Name to give the object in storage.
                                   If not provided, uses the file name.
    """
    if object_name is None:
        object_name = os.path.basename(file_path)
    
    try:
        s3_client.upload_file(file_path, NEBULA_CONFIG['bucket_name'], object_name)
        logger.info(f"File '{file_path}' uploaded successfully as '{object_name}'!")
        return True
    except Exception as e:
        logger.error(f"Error uploading file: {e}")
        return False

# Download a file
def download_file(s3_client, object_name, file_path=None):
    """
    Download a file from Nebula Block storage.
    
    Args:
        s3_client: The S3 client
        object_name (str): Name of the object in storage
        file_path (str, optional): Path to save the file to.
                                 If not provided, uses the object name.
    """
    if file_path is None:
        file_path = object_name
    
    try:
        s3_client.download_file(NEBULA_CONFIG['bucket_name'], object_name, file_path)
        logger.info(f"File '{object_name}' downloaded successfully to '{file_path}'!")
        return True
    except Exception as e:
        logger.error(f"Error downloading file: {e}")
        return False

# List objects in a bucket
def list_objects(s3_client, prefix=None):
    """
    List objects in a bucket.
    
    Args:
        s3_client: The S3 client
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
            logger.info(f"Objects in bucket '{NEBULA_CONFIG['bucket_name']}':")
            for obj in response['Contents']:
                logger.info(f"  - {obj['Key']} ({obj['Size']} bytes)")
            return response['Contents']
        else:
            logger.info(f"No objects found in bucket '{NEBULA_CONFIG['bucket_name']}'")
            return []
    except Exception as e:
        logger.error(f"Error listing objects: {e}")
        return []

# Delete an object
def delete_object(s3_client, object_name):
    """
    Delete an object from storage.
    
    Args:
        s3_client: The S3 client
        object_name (str): Name of the object to delete
    """
    try:
        s3_client.delete_object(
            Bucket=NEBULA_CONFIG['bucket_name'],
            Key=object_name
        )
        logger.info(f"Object '{object_name}' deleted successfully!")
        return True
    except Exception as e:
        logger.error(f"Error deleting object: {e}")
        return False

# Generate a presigned URL
def generate_presigned_url(s3_client, object_name, expiration=3600):
    """
    Generate a presigned URL for temporary access to an object.
    
    Args:
        s3_client: The S3 client
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
        logger.error(f"Error generating presigned URL: {e}")
        return None

# Main function
def main():
    """Main function to demonstrate Nebula Block storage usage."""
    # Validate configuration
    if not validate_config():
        sys.exit(1)
    
    # Create an S3 client
    s3_client = create_s3_client()
    if not s3_client:
        sys.exit(1)
    
    # Test connection
    if not test_connection(s3_client):
        sys.exit(1)
    
    # Create bucket if it doesn't exist
    if not create_bucket_if_not_exists(s3_client, NEBULA_CONFIG['bucket_name']):
        sys.exit(1)
    
    # Create a test file
    test_file_path = 'test_file.txt'
    with open(test_file_path, 'w') as f:
        f.write('This is a test file for Nebula Block storage on Mac Silicon.')
    
    # Upload the file
    if not upload_file(s3_client, test_file_path, 'test_file.txt'):
        os.remove(test_file_path)
        sys.exit(1)
    
    # List objects in the bucket
    list_objects(s3_client)
    
    # Generate a presigned URL
    url = generate_presigned_url(s3_client, 'test_file.txt', expiration=3600)
    if url:
        logger.info(f"Presigned URL (valid for 1 hour): {url}")
    
    # Download the file
    if not download_file(s3_client, 'test_file.txt', 'downloaded_test_file.txt'):
        os.remove(test_file_path)
        sys.exit(1)
    
    # Delete the file
    if not delete_object(s3_client, 'test_file.txt'):
        os.remove(test_file_path)
        os.remove('downloaded_test_file.txt')
        sys.exit(1)
    
    # Clean up local files
    if os.path.exists(test_file_path):
        os.remove(test_file_path)
    if os.path.exists('downloaded_test_file.txt'):
        os.remove('downloaded_test_file.txt')
    
    logger.info("Nebula Block storage example completed successfully!")

if __name__ == "__main__":
    main() 