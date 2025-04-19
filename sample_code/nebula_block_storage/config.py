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