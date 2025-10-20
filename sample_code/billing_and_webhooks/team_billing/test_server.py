import os
import pytest
from fastapi.testclient import TestClient
from server import app, SQLModel, get_session
from sqlmodel import Session, create_engine
from contextlib import contextmanager
import tempfile
import uuid

# Use in-memory SQLite for testing, with shared connection
TEST_DB_URL = "sqlite:///:memory:"
engine = create_engine(TEST_DB_URL, echo=False, connect_args={"check_same_thread": False})
connection = engine.connect()

# Override the get_session dependency to use the shared connection
@contextmanager
def override_get_session():
    with Session(bind=connection) as session:
        yield session

app.dependency_overrides[get_session] = override_get_session

@pytest.fixture(scope="module", autouse=True)
def setup_db():
    SQLModel.metadata.create_all(connection)
    yield
    SQLModel.metadata.drop_all(connection)

@pytest.fixture(scope="module")
def test_client():
    with TestClient(app) as client:
        yield client

@pytest.fixture(scope="module")
def team_info(test_client):
    response = test_client.post(
        "/teams/create",
        json={"team_name": "Test Team", "owner_user_id": "user_123"}
    )
    assert response.status_code == 200
    data = response.json()
    return {"team_id": data["team_id"], "api_key": data["api_key"]}

@pytest.fixture(scope="module")
def invoice_id(test_client, team_info):
    # Invite and join a member
    response = test_client.post(
        "/teams/invite",
        json={"team_id": team_info["team_id"], "email": "newuser@example.com", "role": "Member", "inviter_id": "user_123"}
    )
    assert response.status_code == 200
    token = response.json()["invitation_token"]
    join_response = test_client.post(
        "/teams/join",
        json={"invitation_token": token, "user_id": "user_456"}
    )
    assert join_response.status_code == 200
    # Log usage for both users
    for user_id, amount, cost in [("user_123", 1000, 1.0), ("user_456", 2000, 2.0)]:
        resp = test_client.post(
            "/usage/log",
            json={
                "team_id": team_info["team_id"],
                "user_id": user_id,
                "usage_type": "inference",
                "amount": amount,
                "unit": "tokens",
                "cost": cost
            }
        )
        assert resp.status_code == 200
    # Generate invoice
    invoice_resp = test_client.post(
        "/billing/invoice/generate",
        json={"team_id": team_info["team_id"]}
    )
    assert invoice_resp.status_code == 200
    data = invoice_resp.json()
    return data["invoice_id"]

def test_create_team(team_info):
    assert "team_id" in team_info
    assert "api_key" in team_info

def test_invite_and_join(test_client, team_info):
    response = test_client.post(
        "/teams/invite",
        json={"team_id": team_info["team_id"], "email": "anotheruser@example.com", "role": "Member", "inviter_id": "user_123"}
    )
    assert response.status_code == 200
    token = response.json()["invitation_token"]
    join_response = test_client.post(
        "/teams/join",
        json={"invitation_token": token, "user_id": "user_789"}
    )
    assert join_response.status_code == 200
    assert "Joined team successfully" in join_response.json()["message"]

def test_get_team_api_key(test_client, team_info):
    response = test_client.get(
        f"/teams/{team_info['team_id']}/apikey",
        headers={"X-User-ID": "user_123"}
    )
    assert response.status_code == 200
    assert "api_key" in response.json()

def test_log_usage_and_generate_invoice(test_client, team_info):
    # Log usage for a new user
    resp = test_client.post(
        "/usage/log",
        json={
            "team_id": team_info["team_id"],
            "user_id": "user_789",
            "usage_type": "inference",
            "amount": 500,
            "unit": "tokens",
            "cost": 0.5
        }
    )
    assert resp.status_code == 200
    # Generate invoice
    invoice_resp = test_client.post(
        "/billing/invoice/generate",
        json={"team_id": team_info["team_id"]}
    )
    assert invoice_resp.status_code == 200
    data = invoice_resp.json()
    assert "invoice_id" in data
    assert "member_breakdown" in data
    assert any(mb["user_id"] == "user_789" for mb in data["member_breakdown"])

def test_invoice_pdf_and_payment(test_client, invoice_id):
    # Download PDF
    pdf_resp = test_client.get(f"/billing/invoice/{invoice_id}/pdf")
    assert pdf_resp.status_code == 200
    assert "pdf_url" in pdf_resp.json()
    # Pay invoice
    pay_resp = test_client.post(f"/billing/invoice/{invoice_id}/pay", json={"method": "stripe"})
    assert pay_resp.status_code == 200
    assert pay_resp.json()["status"] == "paid"

# Add more test cases for other endpoints...
