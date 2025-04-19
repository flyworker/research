# Nebula Block Storage Example for Mac Silicon

This example demonstrates how to use Nebula Block object storage on Mac Silicon (Apple Silicon) machines using Python.

## Installation

1. Make sure you have Python 3.8+ installed on your Mac Silicon machine.

2. Create and activate a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate
   ```

3. Install the required packages from requirements.txt:
   ```bash
   pip install -r requirements.txt
   ```

## Configuration

1. Copy the sample environment file to create your .env file:
   ```bash
   cp sample_env .env
   ```

2. Edit the `.env` file and replace the placeholder values with your actual Nebula Block credentials:
   ```
   NEBULA_ACCESS_KEY=your_actual_access_key
   NEBULA_SECRET_KEY=your_actual_secret_key
   NEBULA_ENDPOINT=your_actual_endpoint
   NEBULA_REGION=your_actual_region
   NEBULA_BUCKET=your_actual_bucket_name
   ```

   You can find these credentials in your Nebula Block account dashboard.

## Running the Example

Run the example script:
```bash
python nebula_block_example.py
```

The script will:
1. Connect to your Nebula Block storage
2. Create a bucket if it doesn't exist
3. Create a test file
4. Upload the file to your bucket
5. List objects in the bucket
6. Generate a presigned URL for the file
7. Download the file
8. Delete the file from the bucket
9. Clean up local files

## Troubleshooting

If you encounter any issues:

1. Make sure your Nebula Block credentials are correct
2. Check that your bucket exists and is accessible
3. Verify your internet connection
4. Enable debug logging by changing the logging level in the script:
   ```python
   logging.basicConfig(level=logging.DEBUG)
   ```

## Additional Resources

- [Nebula Block Documentation](https://docs.nebulablock.com/object-storage/tutorials/linuxmac)
- [AWS SDK for Python (boto3) Documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/index.html)
- [S3 API Reference](https://docs.aws.amazon.com/AmazonS3/latest/API/Welcome.html) 