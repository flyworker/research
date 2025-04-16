from fastapi import FastAPI, HTTPException, Header, Depends, Query, Path
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
import os
from dotenv import load_dotenv
import time
import uuid
import requests
import json

# Load environment variables
load_dotenv()

app = FastAPI(title="Mission Quest Verification Webhook")

# Request model
class VerificationRequest(BaseModel):
    user_id: str
    username: str
    quest_id: str

# Response model
class VerificationResponse(BaseModel):
    success: bool
    message: str

# Developer verification request model
class DeveloperVerificationRequest(BaseModel):
    user_id: str
    username: str
    quest_id: str
    verification_data: Dict[str, Any] = Field(default_factory=dict, description="Additional verification data")
    timestamp: int = Field(default_factory=lambda: int(time.time()), description="Unix timestamp of verification")

# Developer verification response model
class DeveloperVerificationResponse(BaseModel):
    success: bool
    message: str
    verification_id: str
    timestamp: int
    details: Dict[str, Any] = Field(default_factory=dict)

# Verify access token
async def verify_token(authorization: str = Header(...)):
    if not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Invalid authorization header")
    
    token = authorization.split(" ")[1]
    expected_token = os.getenv("ACCESS_TOKEN", "demo-access-token")
    
    if token != expected_token:
        raise HTTPException(status_code=401, detail="Invalid access token")
    
    return token

@app.post("/webhook/verify-user", response_model=VerificationResponse)
async def verify_user(request: VerificationRequest, token: str = Depends(verify_token)):
    """
    Verify if a user has completed a quest by forwarding the request to the verification service.
    """
    # Verification service URL
    verification_url = "http://localhost:8001/api/verify"
    
    # Prepare the request to the verification service
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    # Create the verification data
    verification_data = {
        "user_id": request.user_id,
        "username": request.username,
        "quest_id": request.quest_id,
        "verification_data": {
            "source": "webhook_server",
            "verification_timestamp": int(time.time())
        },
        "timestamp": int(time.time())
    }
    
    try:
        # Forward the request to the verification service
        response = requests.post(verification_url, json=verification_data, headers=headers)
        
        if response.status_code == 200:
            verification_response = response.json()
            return VerificationResponse(
                success=verification_response["success"],
                message=verification_response["message"]
            )
        else:
            raise HTTPException(
                status_code=response.status_code,
                detail=f"Verification service error: {response.text}"
            )
            
    except requests.exceptions.RequestException as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error connecting to verification service: {str(e)}"
        )

@app.post("/webhook/developer/verify", response_model=DeveloperVerificationResponse)
async def developer_verify(
    request: DeveloperVerificationRequest, 
    token: str = Depends(verify_token),
    debug: bool = Query(False, description="Enable debug mode for more detailed responses")
):
    """
    Developer verification endpoint with enhanced capabilities.
    This endpoint provides more detailed verification and tracking.
    """
    # Generate a unique verification ID
    verification_id = str(uuid.uuid4())
    
    # In a real implementation, you would:
    # 1. Validate the verification data
    # 2. Check your database for user completion
    # 3. Verify against external services
    # 4. Log the verification attempt
    
    # For demo purposes, we'll simulate a verification process
    success = True
    message = "User completed the task"
    
    # Create detailed response
    details = {
        "user_id": request.user_id,
        "username": request.username,
        "quest_id": request.quest_id,
        "verification_method": "developer_api",
        "verification_timestamp": request.timestamp
    }
    
    # Add debug information if requested
    if debug:
        details["debug_info"] = {
            "request_data": request.verification_data,
            "server_time": int(time.time()),
            "processing_time_ms": 42
        }
    
    return DeveloperVerificationResponse(
        success=success,
        message=message,
        verification_id=verification_id,
        timestamp=int(time.time()),
        details=details
    )

@app.get("/webhook/status/{verification_id}")
async def verification_status(
    verification_id: str = Path(..., description="The verification ID to check"),
    token: str = Depends(verify_token)
):
    """
    Check the status of a previous verification by forwarding the request to the verification service.
    """
    # Verification service URL
    status_url = f"http://localhost:8001/api/status/{verification_id}"
    
    # Prepare the request to the verification service
    headers = {
        "Authorization": f"Bearer {token}"
    }
    
    try:
        # Forward the request to the verification service
        response = requests.get(status_url, headers=headers)
        
        if response.status_code == 200:
            return response.json()
        else:
            raise HTTPException(
                status_code=response.status_code,
                detail=f"Verification service error: {response.text}"
            )
            
    except requests.exceptions.RequestException as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error connecting to verification service: {str(e)}"
        )

@app.get("/webhook/health")
async def health_check():
    """
    Health check endpoint to verify the webhook server is running.
    """
    return {
        "status": "healthy",
        "timestamp": int(time.time()),
        "version": "1.0.0"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 