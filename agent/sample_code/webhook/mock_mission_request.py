import requests
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def send_mock_request():
    # Webhook URL
    url = "http://localhost:8000/webhook/verify-user"
    
    # Get access token from environment or use default
    access_token = os.getenv("ACCESS_TOKEN", "demo-access-token")
    
    # Headers
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json"
    }
    
    # Mock request data
    data = {
        "user_id": "user_12345",
        "username": "alice.eth",
        "quest_id": "quest_abc123"
    }
    
    try:
        # Send POST request
        response = requests.post(url, json=data, headers=headers)
        
        # Print response
        print(f"Status Code: {response.status_code}")
        print("Response:")
        print(response.json())
        
    except requests.exceptions.ConnectionError:
        print("Error: Could not connect to the webhook server.")
        print("Make sure the server is running on http://localhost:8000")
    except Exception as e:
        print(f"Error: {str(e)}")

if __name__ == "__main__":
    send_mock_request() 