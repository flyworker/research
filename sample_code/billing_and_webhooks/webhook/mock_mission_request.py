import requests
import json
import time
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configuration
WEBHOOK_URL = "http://localhost:8000/webhook/verify-user"
ACCESS_TOKEN = os.getenv("ACCESS_TOKEN", "demo-access-token")

def send_verification_request():
    """
    Send a mock mission verification request to the webhook server.
    """
    # Mock user data
    user_data = {
        "user_id": "user123",
        "username": "testuser",
        "quest_id": "quest456"
    }
    
    # Headers with access token
    headers = {
        "Authorization": f"Bearer {ACCESS_TOKEN}",
        "Content-Type": "application/json"
    }
    
    try:
        # Send the request to the webhook server
        response = requests.post(WEBHOOK_URL, json=user_data, headers=headers)
        
        # Print the response
        print(f"Status Code: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
        
        # If successful, check the verification status
        if response.status_code == 200:
            verification_id = response.json().get("verification_id")
            if verification_id:
                check_verification_status(verification_id)
                
    except requests.exceptions.RequestException as e:
        print(f"Error sending request: {str(e)}")

def check_verification_status(verification_id):
    """
    Check the status of a verification request.
    """
    status_url = f"http://localhost:8000/webhook/status/{verification_id}"
    headers = {
        "Authorization": f"Bearer {ACCESS_TOKEN}"
    }
    
    try:
        # Wait a moment before checking status
        time.sleep(1)
        
        # Send the status check request
        response = requests.get(status_url, headers=headers)
        
        # Print the status response
        print(f"\nStatus Check:")
        print(f"Status Code: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
        
    except requests.exceptions.RequestException as e:
        print(f"Error checking status: {str(e)}")

if __name__ == "__main__":
    print("Sending mock mission verification request...")
    send_verification_request() 