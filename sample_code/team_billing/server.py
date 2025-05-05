import os
from fastapi import FastAPI, HTTPException, Depends, Header
from fastapi.middleware.cors import CORSMiddleware
from typing import Optional, List
from datetime import datetime, timedelta
import uuid
from dotenv import load_dotenv
from sqlmodel import SQLModel, Field, create_engine, Session, select, Relationship
from pydantic import BaseModel
from sqlalchemy import and_

# Load environment variables
load_dotenv()

app = FastAPI(
    title="Nebula Block Team Billing API",
    description="API for team management, usage tracking and invoicing",
    version="1.0.0"
)

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Database Configuration
DB_URL = os.getenv("DB_URL") or "sqlite:///./app.db"
engine = create_engine(DB_URL, echo=True)

# SQLModel ORM Models
class Team(SQLModel, table=True):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()), primary_key=True, index=True)
    name: str
    owner_id: str
    api_key: str = Field(default_factory=lambda: str(uuid.uuid4()), index=True)
    created_at: datetime = Field(default_factory=datetime.now)
    members: List["TeamMember"] = Relationship(back_populates="team")

class TeamMember(SQLModel, table=True):
    team_id: str = Field(foreign_key="team.id", primary_key=True)
    user_id: str = Field(primary_key=True)
    role: str
    joined_at: datetime = Field(default_factory=datetime.now)
    team: Optional[Team] = Relationship(back_populates="members")

class Invitation(SQLModel, table=True):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()), primary_key=True)
    team_id: str = Field(foreign_key="team.id")
    email: str
    role: str
    inviter_id: str
    token: str = Field(default_factory=lambda: str(uuid.uuid4()), index=True)
    created_at: datetime = Field(default_factory=datetime.now)
    accepted: bool = False

class UsageRecord(SQLModel, table=True):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()), primary_key=True)
    team_id: str = Field(foreign_key="team.id")
    user_id: str
    usage_type: str
    amount: float
    unit: str
    cost: float
    recorded_at: datetime = Field(default_factory=datetime.now)

class Invoice(SQLModel, table=True):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()), primary_key=True)
    team_id: str = Field(foreign_key="team.id")
    period_start: datetime
    period_end: datetime
    total: float
    status: str
    created_at: datetime = Field(default_factory=datetime.now)

class InvoiceLineItem(SQLModel, table=True):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()), primary_key=True)
    invoice_id: str = Field(foreign_key="invoice.id")
    user_id: Optional[str]
    tokens_used: Optional[float]
    cost: Optional[float]

class Payment(SQLModel, table=True):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()), primary_key=True)
    invoice_id: str = Field(foreign_key="invoice.id")
    method: Optional[str]
    amount: Optional[float]
    status: Optional[str]
    created_at: datetime = Field(default_factory=datetime.now)

class TeamCreateRequest(BaseModel):
    team_name: str
    owner_user_id: str

class TeamInviteRequest(BaseModel):
    team_id: str
    email: str
    role: str
    inviter_id: str

class UsageLogRequest(BaseModel):
    team_id: str
    user_id: str
    usage_type: str
    amount: float
    unit: str
    cost: float

class InvoiceGenerateRequest(BaseModel):
    team_id: str

class JoinTeamRequest(BaseModel):
    invitation_token: str
    user_id: str

class PayInvoiceRequest(BaseModel):
    method: str

# Create tables
SQLModel.metadata.create_all(engine)

# Dependency for session
from contextlib import contextmanager
@contextmanager
def get_session():
    with Session(engine) as session:
        yield session

# API Endpoints with SQLModel ORM
@app.post("/teams/create")
async def create_team(request: TeamCreateRequest):
    team_name = request.team_name
    owner_user_id = request.owner_user_id
    with get_session() as session:
        team = Team(name=team_name, owner_id=owner_user_id)
        session.add(team)
        session.flush()  # Ensure team.id is available
        owner_member = TeamMember(team_id=team.id, user_id=owner_user_id, role="Owner")
        session.add(owner_member)
        session.commit()
        session.refresh(team)
        return {"team_id": team.id, "api_key": team.api_key}

@app.post("/teams/invite")
async def invite_team_member(request: TeamInviteRequest):
    team_id = request.team_id
    email = request.email
    role = request.role
    inviter_id = request.inviter_id
    with get_session() as session:
        inviter = session.exec(select(TeamMember).where(and_(TeamMember.team_id == team_id, TeamMember.user_id == inviter_id))).first()
        if not inviter or inviter.role not in ('Owner', 'Admin'):
            raise HTTPException(status_code=403, detail="No permission to invite members.")
        invitation = Invitation(team_id=team_id, email=email, role=role, inviter_id=inviter_id)
        session.add(invitation)
        session.commit()
        session.refresh(invitation)
        return {"invitation_token": invitation.token}

@app.post("/teams/join")
async def join_team(request: JoinTeamRequest):
    invitation_token = request.invitation_token
    user_id = request.user_id
    with get_session() as session:
        # Validate invitation
        invitation = session.exec(select(Invitation).where(Invitation.token == invitation_token)).first()
        if not invitation:
            raise HTTPException(status_code=404, detail="Invalid invitation token.")
        if invitation.accepted:
            raise HTTPException(status_code=400, detail="Invitation already accepted.")
        # Add user to team_members
        member = TeamMember(team_id=invitation.team_id, user_id=user_id, role=invitation.role)
        session.add(member)
        # Mark invitation as accepted
        invitation.accepted = True
        session.commit()
        session.refresh(invitation)
        return {"message": "Joined team successfully."}

@app.get("/teams/{team_id}/apikey")
async def get_team_api_key(team_id: str, user_id: str = Header(..., alias="X-User-ID")):
    with get_session() as session:
        member = session.exec(select(TeamMember).where(and_(TeamMember.team_id == team_id, TeamMember.user_id == user_id))).first()
        if not member:
            raise HTTPException(status_code=403, detail="Not a team member.")
        team = session.exec(select(Team).where(Team.id == team_id)).first()
        if not team:
            raise HTTPException(status_code=404, detail="Team not found.")
        return {"api_key": team.api_key}

@app.post("/billing/invoice/generate")
async def generate_invoice(request: InvoiceGenerateRequest):
    team_id = request.team_id
    with get_session() as session:
        # Calculate current month period
        now = datetime.now()
        period_start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        if now.month == 12:
            next_month = now.replace(year=now.year+1, month=1, day=1)
        else:
            next_month = now.replace(month=now.month+1, day=1)
        period_end = next_month
        # Aggregate usage per user
        member_breakdown = session.exec(
            select(UsageRecord).where(
                (UsageRecord.team_id == team_id) &
                (UsageRecord.usage_type == 'inference') &
                (UsageRecord.recorded_at >= period_start) &
                (UsageRecord.recorded_at < period_end)
            ).group_by(UsageRecord.user_id)
        ).all()
        total = sum([m.cost or 0 for m in member_breakdown])
        invoice = Invoice(team_id=team_id, period_start=period_start, period_end=period_end, total=total, status="pending")
        session.add(invoice)
        for m in member_breakdown:
            line_item = InvoiceLineItem(invoice_id=invoice.id, user_id=m.user_id, tokens_used=m.amount, cost=m.cost)
            session.add(line_item)
        session.commit()
        session.refresh(invoice)
        return {
            "invoice_id": invoice.id,
            "team_id": team_id,
            "period_start": str(period_start.date()),
            "period_end": str((period_end - timedelta(days=1)).date()),
            "total": total,
            "status": invoice.status,
            "created_at": str(invoice.created_at),
            "member_breakdown": [
                {"user_id": m.user_id, "tokens_used": m.amount, "cost": m.cost} for m in member_breakdown
            ]
        }

@app.post("/usage/log")
async def log_usage(request: UsageLogRequest):
    with get_session() as session:
        usage = UsageRecord(
            team_id=request.team_id,
            user_id=request.user_id,
            usage_type=request.usage_type,
            amount=request.amount,
            unit=request.unit,
            cost=request.cost
        )
        session.add(usage)
        session.commit()
        return {"message": "Usage logged."}

@app.get("/billing/invoice/{invoice_id}/pdf")
async def download_invoice_pdf(invoice_id: str):
    # Stub: Return a placeholder PDF URL
    return {"pdf_url": f"https://example.com/invoices/{invoice_id}.pdf"}

@app.post("/billing/invoice/{invoice_id}/pay")
async def pay_invoice(invoice_id: str, request: PayInvoiceRequest):
    method = request.method
    with get_session() as session:
        invoice = session.exec(select(Invoice).where(Invoice.id == invoice_id)).first()
        if not invoice:
            raise HTTPException(status_code=404, detail="Invoice not found.")
        invoice.status = "paid"
        payment = Payment(invoice_id=invoice.id, method=method, amount=0, status="paid")
        session.add(invoice)
        session.add(payment)
        session.commit()
        session.refresh(invoice)
        session.refresh(payment)
        return {"status": "paid"}

# Add other endpoints with SQLModel ORM...

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
