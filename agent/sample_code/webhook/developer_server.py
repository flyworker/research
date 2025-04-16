from fastapi import FastAPI, HTTPException, Header, Depends, Query, Path
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
import os
from dotenv import load_dotenv
import time
import uuid

# Load environment variables
load_dotenv()

app = FastAPI(title="Mission Verification Service API")

# Verification request model
class VerificationRequest(BaseModel):
    user_id: str
    username: str
    quest_id: str
    verification_data: Dict[str, Any] = Field(default_factory=dict, description="Additional verification data")
    timestamp: int = Field(default_factory=lambda: int(time.time()), description="Unix timestamp of verification")

# Verification response model
class VerificationResponse(BaseModel):
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

@app.post("/api/verify", response_model=VerificationResponse)
async def verify_user(
    request: VerificationRequest, 
    token: str = Depends(verify_token),
    debug: bool = Query(False, description="Enable debug mode for more detailed responses")
):
    """
    Verify if a user has completed a quest.
    This endpoint provides verification functionality for the webhook server.
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
        "verification_method": "verification_service",
        "verification_timestamp": request.timestamp
    }
    
    # Add debug information if requested
    if debug:
        details["debug_info"] = {
            "request_data": request.verification_data,
            "server_time": int(time.time()),
            "processing_time_ms": 42
        }
    
    return VerificationResponse(
        success=success,
        message=message,
        verification_id=verification_id,
        timestamp=int(time.time()),
        details=details
    )

@app.get("/api/status/{verification_id}")
async def verification_status(
    verification_id: str = Path(..., description="The verification ID to check"),
    token: str = Depends(verify_token)
):
    """
    Check the status of a previous verification.
    """
    # In a real implementation, you would look up the verification in your database
    # For demo purposes, we'll return a mock status
    return {
        "verification_id": verification_id,
        "status": "completed",
        "timestamp": int(time.time()),
        "details": {
            "user_id": "user_12345",
            "quest_id": "quest_abc123",
            "completion_time": int(time.time()) - 3600
        }
    }

@app.get("/api/health")
async def health_check():
    """
    Health check endpoint to verify the service is running.
    """
    return {
        "status": "healthy",
        "timestamp": int(time.time()),
        "version": "1.0.0"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001) 