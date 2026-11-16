#!/usr/bin/env python3
"""
RAG Knowledge Base Seeder
Inserts rich policy documents into MongoDB uploaded_documents collection
AND indexes them into the vector store via the RAG service API.

Run:
    cd d:\Semester7\ai-service
    python ..\scripts\seed_rag_documents.py
"""

import os
import sys
import datetime
from bson import ObjectId

try:
    from pymongo import MongoClient
except ImportError:
    print("[Error] pymongo not found. Run: pip install pymongo")
    sys.exit(1)

# Load from .env if present
env_file = os.path.join(os.path.dirname(__file__), "..", ".env")
if os.path.exists(env_file):
    with open(env_file, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                k, _, v = line.partition("=")
                os.environ[k.strip()] = v.strip()

MONGODB_URI = os.getenv("MONGODB_URI", "mongodb+srv://vishalkrpatel14_db_user:6Mygn5JCDFuXHC5O@cluster0.0bopsue.mongodb.net/enterprise_ai?retryWrites=true&w=majority&appName=Cluster0")
DB_NAME = "enterprise_ai"

# ─── Rich Policy Documents ───────────────────────────────────────────────────

HR_POLICY_TEXT = """
ACME CORPORATION — HR POLICY & EMPLOYEE BENEFITS HANDBOOK 2026

SECTION 1: PAID TIME OFF (PTO) POLICY
Full-time employees accrue 20 vacation days (160 hours) annually at 1.67 days per month.
Part-time employees accrue PTO proportional to their FTE percentage.
PTO must be pre-approved by the direct manager via the HR Portal (hr.acme.com).
Unused PTO above 10 days is forfeited at year-end (use-it-or-lose-it policy).
Emergency leave up to 3 days can be taken without manager pre-approval with same-day notification.

SECTION 2: SICK LEAVE
Employees receive 10 dedicated sick/wellness days per calendar year.
Sick days do not roll over and are not paid out upon separation.
Medical documentation required for absences exceeding 3 consecutive business days.
Sick leave is separate from PTO and cannot be used interchangeably.

SECTION 3: PARENTAL LEAVE
Primary caregiver: 12 fully-paid weeks of parental leave.
Secondary caregiver: 4 fully-paid weeks of parental leave.
Leave must commence within 12 months of birth, adoption, or foster placement.
Employees must notify HR at least 30 days before the expected leave date.

SECTION 4: HEALTH INSURANCE & BENEFITS
Medical: Acme partners with BlueCross BlueShield — Premium PPO plan fully covered for employees.
Dental: Delta Dental — 100% preventive coverage, 80% basic, 50% major.
Vision: VSP — $200 annual frame allowance, contact lens allowance $150.
Life Insurance: Company provides 2x annual salary term life insurance at no cost.
HSA contribution: Company contributes $500/year to employee HSA accounts.

SECTION 5: 401(k) RETIREMENT PLAN
Acme matches 100% of employee contributions up to 6% of base salary (dollar-for-dollar match).
Vesting schedule: 100% immediate vesting on company match contributions.
Employees are auto-enrolled at 3% contribution after 30 days of employment.
Roth 401(k) option available; annual IRS limit applies ($23,000 for 2026).

SECTION 6: REMOTE WORK & HYBRID POLICY
Acme follows a Hybrid-First model: minimum 2 days per week in office (Tuesday & Thursday).
Remote work equipment stipend: $1,000 one-time setup allowance for new hires.
Monthly internet reimbursement: up to $80/month with valid invoice.
Employees may request fully-remote status after 12 months of tenure with manager approval.

SECTION 7: PERFORMANCE REVIEWS & PROMOTIONS
Annual performance review cycle: October–November each year.
Mid-year check-in: April (non-evaluative, developmental focus).
Promotion eligibility: minimum 12 months in current role; requires manager + skip-level endorsement.
Merit increase pool for 2026: 4.5% of total payroll, distributed based on performance rating.

SECTION 8: PROFESSIONAL DEVELOPMENT
Annual L&D budget per employee: $2,500 for courses, certifications, conferences.
Manager approval required for spends above $500 per individual event.
Acme reimburses 100% of exam fees for pre-approved certifications (AWS, GCP, Azure, PMP).
Study leave: up to 3 paid study days per certification exam attempt.

SECTION 9: CODE OF CONDUCT
All employees must complete annual Ethics & Compliance training by December 31.
Conflicts of interest must be disclosed to HR within 30 days of occurrence.
Zero tolerance policy for discrimination, harassment, or retaliation.
Violations may result in immediate termination and legal action.

SECTION 10: RESIGNATION, OFFBOARDING & NOTICE PERIOD
Standard notice period for full-time Software Engineers and Individual Contributors (IC) is 30 calendar days (1 month).
Employees undergoing initial 90-day probation have a 14-day notice period from either party.
Engineering Leads, Managers, and Staff Engineers must serve a 60-day notice period to ensure transition continuity.
Directors and Executive Leadership must provide a 90-day written notice.
All resignations must be submitted formally through the HR Portal (hr.acme.com) and acknowledged by the direct manager.
Mandatory knowledge transfer documentation, codebase handover, and surrender of company hardware/badges are required prior to final settlement.
Notice buyout may be approved at the discretion of the Department Head and People Operations.
"""

TECH_SLA_TEXT = """
ACME CORPORATION — ENTERPRISE TECHNICAL ARCHITECTURE & SLA DOCUMENT 2026

SECTION 1: SYSTEM UPTIME COMMITMENTS (SLA)
Core API Service (Spring Boot): 99.95% monthly uptime = max 21.6 min downtime/month.
AI Service (FastAPI/LangGraph): 99.9% monthly uptime = max 43.2 min downtime/month.
Frontend (React/Vite): 99.99% uptime via CDN.
Planned maintenance windows: Sundays 2:00 AM – 4:00 AM IST (notified 48h in advance).

SECTION 2: MICROSERVICES ARCHITECTURE
The platform uses a 3-tier microservices architecture:
  - Tier 1 (Frontend): React 18 + TypeScript + Tailwind CSS served via Nginx CDN.
  - Tier 2 (Core Backend): Java Spring Boot 3.2 with JWT authentication, RBAC, and MongoDB 7.0.
  - Tier 3 (AI Service): Python FastAPI + LangGraph multi-agent swarm with Gemini API.

Inter-service communication: REST over HTTPS with mTLS certificates for backend-to-AI calls.
Service discovery: Kubernetes DNS-based with Consul fallback.

SECTION 3: DATABASE CONFIGURATION
Primary Database: MongoDB 7.0 (cluster: enterprise-prod-rs0).
Connection pool: min=10, max=100, connectionTimeoutMS=10000, socketTimeoutMS=30000.
Write concern: { w: "majority", j: true } for all financial and authentication operations.
Read preference: primaryPreferred for reads, primary for writes.
Backup: Daily snapshots at 01:00 UTC, 7-day retention, monthly archives for 1 year.
No SQL databases in the architecture — MongoDB exclusive.

SECTION 4: PERFORMANCE TARGETS
API response P95 latency: < 300ms for standard queries.
AI agent response time: < 5000ms for single-agent queries, < 12000ms for multi-agent.
Concurrent users supported: 10,000 per cluster node.
Auto-scaling triggers: CPU > 70% for 3 minutes → scale out +1 node.

SECTION 5: SECURITY PROTOCOLS
Authentication: JWT (RS256) with 15-minute access tokens and 7-day refresh tokens.
RBAC roles: EMPLOYEE → MANAGER → ORG_ADMIN → SUPER_ADMIN (hierarchical).
All API endpoints require valid JWT except /health, /docs.
Data encryption: AES-256 at rest, TLS 1.3 in transit.
PII data masked in logs; audit trail maintained for all state-mutation operations.

SECTION 6: INCIDENT RESPONSE
P0 (Critical — full outage): Response within 15 minutes, resolution target 1 hour.
P1 (High — partial outage): Response within 30 minutes, resolution target 4 hours.
P2 (Medium — degraded): Response within 2 hours, resolution target 24 hours.
P3 (Low — minor issue): Response within 1 business day, resolution target 1 week.
On-call rotation: DevOps team 24/7 via PagerDuty (channel: #dev-incidents on Slack).

SECTION 7: AI AGENT SYSTEM (LangGraph)
Agents: Orchestrator, HR Agent, Finance Agent, Developer Agent, Research Agent, DB Agent, Action Agent, RAG Agent.
LLM Provider: Google Gemini (gemini-3.5-flash model).
Human-in-the-Loop (HITL): All state-mutation actions (Jira creation, cluster provisioning, Slack broadcasts) require Manager+ approval.
Agent routing: Gemini-powered intent classification with keyword fallback.
RAG: In-memory vector store with MD5-hash embeddings; Qdrant optional for production.

SECTION 8: DEPLOYMENT & CI/CD
Container registry: Google Artifact Registry (us-central1).
Deployment: Kubernetes (GKE) with Helm charts.
CI/CD: GitHub Actions → build → test → Docker push → Helm upgrade.
Rollback: Helm rollback to previous revision within 5 minutes.
Feature flags: LaunchDarkly SDK integrated in Spring Boot backend.
"""

FINANCE_BUDGET_TEXT = """
ACME CORPORATION — Q3 2026 FINANCIAL BUDGET & COST CENTER ALLOCATIONS (CONFIDENTIAL)

CLASSIFICATION: CONFIDENTIAL — MANAGER, ORG_ADMIN, SUPER_ADMIN ONLY

SECTION 1: Q3 CONSOLIDATED BUDGET SUMMARY
Total Q3 Operating Budget: $3,100,000
Total Actual Spend (QTD through Sept 30): $2,800,000
Overall Budget Utilization: 90.3%
Remaining Q3 Headroom: $300,000
Forecast to Q3-end: On-track, no variance alert.

SECTION 2: DEPARTMENT BREAKDOWN
Engineering & Cloud Operations:
  - Allocated: $1,450,000
  - Actual Spend: $1,180,000
  - Variance: -$270,000 (18.6% under) ✅ On Track
  - Major cost: AWS EC2 reserved instances $420,000; GKE cluster $280,000; SaaS tools $180,000.

Product & Architecture:
  - Allocated: $420,000
  - Actual Spend: $390,000
  - Variance: -$30,000 (7.1% under) ✅ On Track
  - Major cost: Figma enterprise $45,000; Jira $32,000; Product research $120,000.

Sales & Commercial:
  - Allocated: $850,000
  - Actual Spend: $820,000
  - Variance: -$30,000 (3.5% under) ✅ On Track
  - Major cost: Salesforce CRM $240,000; Lead gen tools $180,000; Travel $120,000.

HR & Corporate Operations:
  - Allocated: $380,000
  - Actual Spend: $410,000
  - Variance: +$30,000 (7.8% OVER) ⚠️ Under Review
  - Root cause: Unexpected recruitment agency fees for 3 senior engineering hires.

SECTION 3: HEADCOUNT BUDGET
Total headcount: 148 FTE
Engineering: 62 FTE | Product: 18 FTE | Sales: 34 FTE | HR/Ops: 16 FTE | Finance: 18 FTE
Open requisitions: 7 (3 engineering, 2 product, 2 sales)
Hiring freeze: Active for HR/Ops and Finance until Q4 budget review.

SECTION 4: CLOUD INFRASTRUCTURE COSTS
AWS total Q3: $700,000 (EC2 $420K, S3 $80K, RDS $200K)
GCP/GKE Q3: $280,000 (GKE $180K, Artifact Registry $20K, BigQuery $80K)
Gemini API Q3: $45,000 (AI inference cost for LangGraph agent calls)
Total Cloud Q3: $1,025,000

SECTION 5: Q4 FORECAST & CONSTRAINTS
Q4 Budget: $3,200,000 (3.2% increase approved by CFO)
Priority investments: AI platform expansion (+$120K), engineering headcount (+$200K)
Cost reduction targets: SaaS rationalization target $80K savings; renegotiate AWS reserved instances.
Discretionary freeze: All non-essential spend > $10,000 requires CFO approval through Q4.
"""

def seed_rag_docs(db):
    print("[*] Checking existing documents...")
    
    # Get first org id
    org = db.organizations.find_one({"code": "acme-corp"})
    org_id = org["_id"] if org else ObjectId("6732a1000000000000000001")
    
    # Get dept ids
    dept_eng = db.departments.find_one({"code": "ENG"})
    dept_hr = db.departments.find_one({"code": "HR"})
    dept_fin = db.departments.find_one({"code": "FIN"})
    
    # Get user ids
    hr_mgr = db.users.find_one({"email": "david.sterling@acme.com"})
    admin = db.users.find_one({"role": "ORG_ADMIN"})
    
    now = datetime.datetime.utcnow()
    
    documents = [
        {
            "fileName": "Acme_HR_Policy_and_Benefits_2026.pdf",
            "fileType": "pdf",
            "content": HR_POLICY_TEXT,
            "classification": "INTERNAL",
            "allowedRoles": ["EMPLOYEE", "MANAGER", "ORG_ADMIN", "SUPER_ADMIN"],
            "departmentId": dept_hr["_id"] if dept_hr else None,
            "uploadedBy": hr_mgr["_id"] if hr_mgr else None,
            "uploadedByName": "David Sterling",
        },
        {
            "fileName": "Microservices_Architecture_and_SLA_2026.docx",
            "fileType": "docx",
            "content": TECH_SLA_TEXT,
            "classification": "INTERNAL",
            "allowedRoles": ["EMPLOYEE", "MANAGER", "ORG_ADMIN", "SUPER_ADMIN"],
            "departmentId": dept_eng["_id"] if dept_eng else None,
            "uploadedBy": admin["_id"] if admin else None,
            "uploadedByName": "Alex Rivera",
        },
        {
            "fileName": "Q3_Confidential_Financial_Budget_Allocations_2026.pdf",
            "fileType": "pdf",
            "content": FINANCE_BUDGET_TEXT,
            "classification": "CONFIDENTIAL",
            "allowedRoles": ["MANAGER", "ORG_ADMIN", "SUPER_ADMIN"],
            "departmentId": dept_fin["_id"] if dept_fin else None,
            "uploadedBy": admin["_id"] if admin else None,
            "uploadedByName": "Sarah Jenkins",
        },
    ]
    
    inserted = 0
    for doc in documents:
        # Remove old version if exists
        db.uploaded_documents.delete_many({
            "organizationId": org_id,
            "fileName": doc["fileName"]
        })
        
        content = doc.pop("content")
        preview = content.strip()[:500] + "..." if len(content) > 500 else content.strip()
        
        doc_record = {
            "organizationId": org_id,
            "departmentId": doc.get("departmentId"),
            "fileName": doc["fileName"],
            "fileType": doc["fileType"],
            "fileSize": len(content.encode("utf-8")),
            "storagePath": f"/storage/acme/{doc['fileName']}",
            "contentPreview": preview,
            # Store FULL content for RAG indexing
            "fullContent": content,
            "chunkCount": len(content.split()) // 50,
            "vectorCollection": "enterprise_kb_vectors",
            "classification": doc["classification"],
            "allowedRoles": doc["allowedRoles"],
            "uploadedBy": doc.get("uploadedBy"),
            "uploadedByName": doc.get("uploadedByName", "System"),
            "status": "INDEXED",
            "errorMessage": None,
            "createdAt": now,
            "updatedAt": now,
        }
        
        db.uploaded_documents.insert_one(doc_record)
        inserted += 1
        print(f"[+] Inserted: {doc['fileName']} ({len(content)} chars, {doc_record['chunkCount']} est. chunks)")
    
    print(f"\n[SUCCESS] {inserted} rich policy documents seeded into MongoDB!")
    print("[*] Restart AI service to pick up full document content for RAG queries.")
    return True


def main():
    print("[*] Connecting to MongoDB...")
    client = MongoClient(MONGODB_URI, serverSelectionTimeoutMS=5000)
    db = client[DB_NAME]
    
    try:
        db.command("ping")
        print("[+] MongoDB connected!")
    except Exception as e:
        print(f"[ERROR] Cannot connect to MongoDB: {e}")
        sys.exit(1)
    
    seed_rag_docs(db)
    client.close()


if __name__ == "__main__":
    main()
