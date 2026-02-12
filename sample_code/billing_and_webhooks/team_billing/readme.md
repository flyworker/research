# Nebula Block – Team Access, Member Tracking & Invoicing System

## 🚀 Quickstart

### 1. Run with Docker
```sh

# Build the Docker image
docker build -t team-billing-app .
# Run the app (uses SQLite by default)
docker run -p 8000:8000 --env-file .env team-billing-app
```

### 2. Run Tests
```sh
cd sample_code/billing_and_webhooks/team_billing
pip install -r requirements.txt
pytest test_server.py -v
```

### 3. Tech Stack
- **FastAPI** (Python web framework)
- **SQLModel** (ORM, built on SQLAlchemy)
- **SQLite** (default, file-based DB for local/dev)
- **Docker** (containerization)
- **Pytest** (testing)

---

## Features Overview

### ✅ Team Functionality
- Create and manage teams
- Invite and onboard team members
- Role-based access control (Owner, Admin, Member)
- Shared usage of inference & storage APIs
- Team-level API key

### 🧑‍💼 Individual Member Usage Tracking
- Monitor API usage per member within a team
- Track token usage, storage consumption, and cost per user
- Include breakdown in monthly invoice and admin dashboards

### 💳 Billing & Invoicing
- Track team-level and user-level API usage
- Monthly invoice generation (team-level billing)
- PDF invoice delivery to billing contact
- Optional payment integration (Stripe, crypto)

---

## 📦 Team API Endpoints

### 1. Create a Team
```http
POST /teams/create
```
**Payload:**
```json
{
  "team_name": "Research Team Alpha",
  "owner_user_id": "user_123"
}
```

---

### 2. Invite Team Member
```http
POST /teams/invite
```
**Payload:**
```json
{
  "team_id": "team_abc",
  "email": "newuser@example.com",
  "role": "Member",
  "inviter_id": "user_123"
}
```

---

### 3. Join Team via Invite
```http
POST /teams/join
```
**Payload:**
```json
{
  "invitation_token": "token_xyz",
  "user_id": "user_456"
}
```

---

### 4. Get Team API Key
```http
GET /teams/{team_id}/apikey
```

---

## 🧠 Inference API Usage (Team Context with User Tracking)
To log requests per team member, include both the API key and the user ID in headers:
```bash
curl -X POST https://api.nebulablock.ai/v1/inference \
  -H "Authorization: Bearer <team_api_key>" \
  -H "X-User-ID: user_123" \
  -d '{ "model": "llama3", "prompt": "Translate to French: Hello" }'
```

---

## 📊 Usage Tracking Schema
```sql
CREATE TABLE usage_records (
  id UUID PRIMARY KEY,
  team_id UUID,
  user_id UUID,        -- Per-user tracking
  usage_type TEXT,     -- 'inference', 'storage'
  amount NUMERIC,
  unit TEXT,           -- 'tokens', 'GB'
  cost NUMERIC,
  recorded_at TIMESTAMP
);
```
> You can index on `(team_id, user_id, recorded_at)` for fast lookups and analytics.

---

## 🧾 Invoicing API

### Generate Invoice
```http
POST /billing/invoice/generate
```
**Payload:**
```json
{
  "team_id": "team_abc"
}
```
**Output Example:**
```json
{
  "invoice_id": "inv_001",
  "team_id": "team_abc",
  "period_start": "2025-05-01",
  "period_end": "2025-05-31",
  "line_items": [...],
  "total": 7.5,
  "status": "pending",
  "created_at": "2025-06-01",
  "member_breakdown": [
    { "user_id": "user_123", "tokens_used": 2000000, "cost": 1.0 },
    { "user_id": "user_456", "tokens_used": 3000000, "cost": 1.5 }
  ]
}
```

---

### Download Invoice PDF
```http
GET /billing/invoice/{invoice_id}/pdf
```

---

### Pay Invoice
```http
POST /billing/invoice/{invoice_id}/pay
```
**Payload:**
```json
{
  "method": "stripe"
}
```

---

## 📤 Email Invoice
On invoice generation, the PDF is emailed to:
* Team Owner
* Optional: `billing_email` field on team profile

---

## (Optional) Payment Integration
```http
POST /billing/invoice/{invoice_id}/pay
```
Support Stripe, PayPal, or crypto.

---

## 🔐 Role Permissions
| Role   | Invite Members | Access API | View Usage | Generate Invoice |
| ------ | -------------- | ---------- | ---------- | ---------------- |
| Owner  | ✅              | ✅          | ✅          | ✅                |
| Admin  | ✅              | ✅          | ✅          | ❌                |
| Member | ❌              | ✅          | ❌          | ❌                |

---

## 👥 Example User Flow
1. User A creates a team and invites User B.
2. Team API key is issued.
3. Each user includes their `user_id` via `X-User-ID` header on requests.
4. System logs both team-level and individual usage.
5. Admins view usage reports per member.
6. Invoice is generated monthly with usage breakdown.

---

## 📩 Contact
For implementation support, reach out to the Nebula Block developer team at [support@nebulablock.ai]

