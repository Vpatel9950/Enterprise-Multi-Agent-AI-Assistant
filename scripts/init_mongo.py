#!/usr/bin/env python3
"""
Enterprise Multi-Agent AI Assistant - MongoDB Setup & Seed Utility
Connects to local MongoDB or MongoDB Atlas using MONGODB_URI and applies:
1. Database creation (enterprise_ai)
2. Collections & Schema Validation
3. Compound, Unique, and Text Indexes
4. Default Seed Data (Orgs, Departments, Roles, Users, Agents, Docs, Workflows)
"""

import os
import sys
import datetime
from bson import ObjectId

try:
    from pymongo import MongoClient, ASCENDING, DESCENDING, TEXT
    import bcrypt
except ImportError:
    print("[Error] Required packages not found. Run: pip install pymongo bcrypt")
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
DB_NAME = os.getenv("MONGODB_DB_NAME", "enterprise_ai")

def get_db():
    print(f"[*] Connecting to MongoDB at: {MONGODB_URI.split('@')[-1] if '@' in MONGODB_URI else MONGODB_URI}")
    client = MongoClient(MONGODB_URI, serverSelectionTimeoutMS=5000)
    return client, client[DB_NAME]

def setup_indexes(db):
    print("[*] Creating indexes and unique constraints...")
    
    # Organizations
    db.organizations.create_index([("code", ASCENDING)], unique=True)
    db.organizations.create_index([("domain", ASCENDING)], unique=True)
    
    # Departments
    db.departments.create_index([("organizationId", ASCENDING), ("code", ASCENDING)], unique=True)
    db.departments.create_index([("organizationId", ASCENDING), ("name", ASCENDING)])
    
    # Roles
    db.roles.create_index([("organizationId", ASCENDING), ("name", ASCENDING)], unique=True)
    
    # Users
    db.users.create_index([("organizationId", ASCENDING), ("email", ASCENDING)], unique=True)
    db.users.create_index([("email", ASCENDING)], unique=True)
    db.users.create_index([("organizationId", ASCENDING), ("role", ASCENDING)])
    db.users.create_index([("organizationId", ASCENDING), ("departmentId", ASCENDING)])
    
    # AI Agents
    db.ai_agents.create_index([("organizationId", ASCENDING), ("code", ASCENDING)], unique=True)
    
    # Conversations
    db.conversations.create_index([("organizationId", ASCENDING), ("userId", ASCENDING), ("updatedAt", DESCENDING)])
    db.conversations.create_index([("organizationId", ASCENDING), ("status", ASCENDING)])
    
    # Messages
    db.messages.create_index([("conversationId", ASCENDING), ("createdAt", ASCENDING)])
    db.messages.create_index([("organizationId", ASCENDING), ("createdAt", DESCENDING)])
    
    # Agent Execution Logs
    db.agent_execution_logs.create_index([("organizationId", ASCENDING), ("agentCode", ASCENDING), ("createdAt", DESCENDING)])
    db.agent_execution_logs.create_index([("organizationId", ASCENDING), ("userId", ASCENDING), ("createdAt", DESCENDING)])
    
    # Uploaded Documents
    db.uploaded_documents.create_index([("organizationId", ASCENDING), ("departmentId", ASCENDING)])
    db.uploaded_documents.create_index([("organizationId", ASCENDING), ("classification", ASCENDING)])
    db.uploaded_documents.create_index([("fileName", TEXT), ("contentPreview", TEXT)])
    
    # Workflows
    db.workflows.create_index([("organizationId", ASCENDING), ("triggerType", ASCENDING)])
    db.workflows.create_index([("organizationId", ASCENDING), ("status", ASCENDING)])
    
    # Approval Requests
    db.approval_requests.create_index([("organizationId", ASCENDING), ("status", ASCENDING), ("createdAt", DESCENDING)])
    db.approval_requests.create_index([("organizationId", ASCENDING), ("requestedBy", ASCENDING)])
    
    # Audit Logs
    db.audit_logs.create_index([("organizationId", ASCENDING), ("timestamp", DESCENDING)])
    db.audit_logs.create_index([("organizationId", ASCENDING), ("action", ASCENDING)])
    
    print("[+] All collection indexes successfully verified.")

def seed_data(db):
    print("[*] Seeding default organizations, users, and AI agents...")
    now = datetime.datetime.utcnow()
    
    # Check if data already exists
    if db.users.count_documents({}) > 0:
        print("[!] Existing users found in MongoDB. Skipping initial overwrite.")
        return

    # 1. Organizations
    acme_org_id = ObjectId("6732a1000000000000000001")
    global_org_id = ObjectId("6732a1000000000000000002")
    
    db.organizations.insert_many([
        {
            "_id": acme_org_id,
            "name": "Acme Global Enterprises",
            "code": "acme-corp",
            "domain": "acme.com",
            "status": "ACTIVE",
            "subscriptionTier": "ENTERPRISE",
            "settings": {"enforceMFA": True, "allowedLLMs": ["gpt-4o", "claude-3-5-sonnet"]},
            "createdAt": now,
            "updatedAt": now
        },
        {
            "_id": global_org_id,
            "name": "Global Enterprise Cloud Systems",
            "code": "global-ai",
            "domain": "enterprise.ai",
            "status": "ACTIVE",
            "subscriptionTier": "ENTERPRISE",
            "settings": {"enforceMFA": True, "allowedLLMs": ["gpt-4o", "claude-3-5-sonnet"]},
            "createdAt": now,
            "updatedAt": now
        }
    ])

    # 2. Departments
    dept_eng_id = ObjectId()
    dept_hr_id = ObjectId()
    dept_fin_id = ObjectId()
    dept_exec_id = ObjectId()
    
    db.departments.insert_many([
        {
            "_id": dept_eng_id,
            "organizationId": acme_org_id,
            "name": "Engineering & Architecture",
            "code": "ENG",
            "description": "Software development & cloud infrastructure",
            "managerId": None,
            "createdAt": now,
            "updatedAt": now
        },
        {
            "_id": dept_hr_id,
            "organizationId": acme_org_id,
            "name": "Human Resources & Talent",
            "code": "HR",
            "description": "Workforce policies, benefits, and employee relations",
            "managerId": None,
            "createdAt": now,
            "updatedAt": now
        },
        {
            "_id": dept_fin_id,
            "organizationId": acme_org_id,
            "name": "Finance & Procurement",
            "code": "FIN",
            "description": "Corporate budgets and spend control",
            "managerId": None,
            "createdAt": now,
            "updatedAt": now
        },
        {
            "_id": dept_exec_id,
            "organizationId": acme_org_id,
            "name": "Executive Operations",
            "code": "EXEC",
            "description": "Governance and enterprise management",
            "managerId": None,
            "createdAt": now,
            "updatedAt": now
        }
    ])

    # 3. Roles
    db.roles.insert_many([
        {
            "organizationId": None,
            "name": "SUPER_ADMIN",
            "description": "Global administration across all tenants",
            "permissions": ["SYS_ALL", "ORG_ALL", "USER_ALL", "DOC_ALL", "AUDIT_ALL", "HITL_OVERRIDE"],
            "isSystemRole": True,
            "createdAt": now
        },
        {
            "organizationId": None,
            "name": "ORG_ADMIN",
            "description": "Tenant-level admin management",
            "permissions": ["ORG_READ", "DEPT_ALL", "USER_MANAGE", "DOC_ALL", "AUDIT_READ", "HITL_APPROVE"],
            "isSystemRole": True,
            "createdAt": now
        },
        {
            "organizationId": None,
            "name": "MANAGER",
            "description": "Department management and confidential documents",
            "permissions": ["USER_READ", "DEPT_READ", "DOC_READ_CONFIDENTIAL", "HITL_APPROVE"],
            "isSystemRole": True,
            "createdAt": now
        },
        {
            "organizationId": None,
            "name": "EMPLOYEE",
            "description": "Standard workforce user",
            "permissions": ["USER_READ_SELF", "DOC_READ_INTERNAL", "CHAT_USE"],
            "isSystemRole": True,
            "createdAt": now
        }
    ])

    # 4. Users (Bcrypt hash of 'Password123!')
    salt = bcrypt.gensalt(10)
    pwd_hash = bcrypt.hashpw(b"Password123!", salt).decode('utf-8')

    super_admin_id = ObjectId("6732a1000000000000000010")
    org_admin_id = ObjectId("6732a1000000000000000002")
    hr_mgr_id = ObjectId("6732a1000000000000000003")
    emp_id = ObjectId("6732a1000000000000000004")

    db.users.insert_many([
        {
            "_id": super_admin_id,
            "organizationId": global_org_id,
            "departmentId": dept_exec_id,
            "email": "superadmin@enterprise.ai",
            "passwordHash": pwd_hash,
            "fullName": "Victoria Vance (Super Admin)",
            "role": "SUPER_ADMIN",
            "department": "Executive Operations",
            "isActive": True,
            "lastLoginAt": now,
            "createdAt": now,
            "updatedAt": now
        },
        {
            "_id": org_admin_id,
            "organizationId": acme_org_id,
            "departmentId": dept_exec_id,
            "email": "admin@acme.com",
            "passwordHash": pwd_hash,
            "fullName": "Sarah Jenkins (Org Admin)",
            "role": "ORG_ADMIN",
            "department": "Executive Operations",
            "isActive": True,
            "lastLoginAt": now,
            "createdAt": now,
            "updatedAt": now
        },
        {
            "_id": hr_mgr_id,
            "organizationId": acme_org_id,
            "departmentId": dept_hr_id,
            "email": "hr.manager@acme.com",
            "passwordHash": pwd_hash,
            "fullName": "David Sterling (HR Manager)",
            "role": "MANAGER",
            "department": "Human Resources & Talent",
            "isActive": True,
            "lastLoginAt": now,
            "createdAt": now,
            "updatedAt": now
        },
        {
            "_id": emp_id,
            "organizationId": acme_org_id,
            "departmentId": dept_eng_id,
            "email": "alex.rivera@acme.com",
            "passwordHash": pwd_hash,
            "fullName": "Alex Rivera (Staff Engineer)",
            "role": "EMPLOYEE",
            "department": "Engineering & Architecture",
            "isActive": True,
            "lastLoginAt": now,
            "createdAt": now,
            "updatedAt": now
        }
    ])

    # 5. AI Agents
    agents = [
        {
            "organizationId": None,
            "code": "orchestrator",
            "name": "Centralized Orchestrator Agent",
            "roleDescription": "Main supervisor agent. Analyzes natural language intent, creates DAG task breakdown, delegates subtasks, and synthesizes answers.",
            "systemPrompt": "You are the Centralized Orchestrator of the Enterprise Multi-Agent AI System. Break down user queries, delegate subtasks to specialized agents (RAG, HR, Finance, Developer, Research, Database, Action), enforce organizational access control, and combine sub-agent findings into a cohesive, executive-grade response.",
            "modelName": "gpt-4o",
            "temperature": 0.2,
            "tools": ["delegate_agent", "aggregate_responses", "check_permission", "hitl_approval_gate"],
            "requiredPermission": "CHAT_USE",
            "isSystem": True,
            "isActive": True,
            "createdAt": now,
            "updatedAt": now
        },
        {
            "organizationId": None,
            "code": "rag_agent",
            "name": "Knowledge & RAG Agent",
            "roleDescription": "Retrieves facts and answers from uploaded company handbooks, architecture specs, and internal policies with precise citations.",
            "systemPrompt": "You are the Knowledge/RAG Agent. Search the company document vector index with security ACL filters. Always cite the document name, page number, and section whenever answering.",
            "modelName": "gpt-4o-mini",
            "temperature": 0.1,
            "tools": ["vector_search", "extract_citation", "summarize_document"],
            "requiredPermission": "DOC_READ_INTERNAL",
            "isSystem": True,
            "isActive": True,
            "createdAt": now,
            "updatedAt": now
        },
        {
            "organizationId": None,
            "code": "hr_agent",
            "name": "HR & Employee Agent",
            "roleDescription": "Handles employee leave balances, PTO policies, healthcare benefits, and corporate onboarding workflows.",
            "systemPrompt": "You are the Enterprise HR Agent. Help employees with PTO policy, benefits enrollment, maternity/paternity leave, and onboarding steps. Mask sensitive PII and ensure responses adhere to company HR directives.",
            "modelName": "gpt-4o-mini",
            "temperature": 0.3,
            "tools": ["pto_calculator", "handbook_retriever", "benefits_navigator"],
            "requiredPermission": "CHAT_USE",
            "isSystem": True,
            "isActive": True,
            "createdAt": now,
            "updatedAt": now
        },
        {
            "organizationId": None,
            "code": "finance_agent",
            "name": "Finance & Procurement Agent",
            "roleDescription": "Analyzes department budgets, reports spending variance, tracks invoice approvals, and queries cost centers.",
            "systemPrompt": "You are the Enterprise Finance Agent. Provide department spending summaries, cost center breakdowns, and procurement approval policies. Do not authorize disbursements directly; route payment requests through the Action Agent.",
            "modelName": "gpt-4o",
            "temperature": 0.1,
            "tools": ["budget_lookup", "spend_variance_analyzer", "procurement_matrix"],
            "requiredPermission": "FINANCE_READ",
            "isSystem": True,
            "isActive": True,
            "createdAt": now,
            "updatedAt": now
        },
        {
            "organizationId": None,
            "code": "dev_agent",
            "name": "Developer & Architecture Agent",
            "roleDescription": "Provides software architecture guidance, API code generation, stack trace debugging, and infrastructure diagnostics.",
            "systemPrompt": "You are the Senior Technical Architecture Agent. Diagnose system errors, provide clean code snippets, generate Swagger/OpenAPI contracts, and explain cloud infrastructure setups.",
            "modelName": "gpt-4o",
            "temperature": 0.2,
            "tools": ["code_analyzer", "log_debugger", "architecture_diagrammer"],
            "requiredPermission": "CHAT_USE",
            "isSystem": True,
            "isActive": True,
            "createdAt": now,
            "updatedAt": now
        },
        {
            "organizationId": None,
            "code": "research_agent",
            "name": "Research & Synthesis Agent",
            "roleDescription": "Synthesizes information across multiple internal records and external industry benchmarks into structured executive briefs.",
            "systemPrompt": "You are the Enterprise Research Agent. Gather information across internal knowledge and industry trends, verify factual accuracy, and formulate clear, well-referenced executive summaries.",
            "modelName": "gpt-4o",
            "temperature": 0.4,
            "tools": ["multi_doc_synthesizer", "competitive_benchmarker", "executive_briefer"],
            "requiredPermission": "CHAT_USE",
            "isSystem": True,
            "isActive": True,
            "createdAt": now,
            "updatedAt": now
        },
        {
            "organizationId": None,
            "code": "db_agent",
            "name": "Database Query Agent",
            "roleDescription": "Executes secure, permission-validated read-only MongoDB aggregation queries without modifying or deleting data.",
            "systemPrompt": "You are the Read-Only Database Query Agent. Translate natural language queries into MongoDB aggregation pipelines. You strictly NEVER execute update, delete, drop, or destructive operations. Only find() and aggregate() are permitted.",
            "modelName": "gpt-4o",
            "temperature": 0.0,
            "tools": ["mongo_aggregate_readonly", "schema_inspector", "query_validator"],
            "requiredPermission": "DB_QUERY_READ",
            "isSystem": True,
            "isActive": True,
            "createdAt": now,
            "updatedAt": now
        },
        {
            "organizationId": None,
            "code": "action_agent",
            "name": "Action & Execution Agent",
            "roleDescription": "Executes authorized operations (creating records, filing tickets, triggering webhooks) with mandatory Human-in-the-Loop approval.",
            "systemPrompt": "You are the Enterprise Action Agent. Whenever an operation modifies state, issues external notifications, or affects business records, you must pause execution and request explicit Human-in-the-Loop (HITL) approval.",
            "modelName": "gpt-4o",
            "temperature": 0.1,
            "tools": ["create_jira_issue", "dispatch_slack_alert", "sync_crm_lead", "submit_procurement_request"],
            "requiredPermission": "ACTION_EXECUTE",
            "isSystem": True,
            "isActive": True,
            "createdAt": now,
            "updatedAt": now
        }
    ]
    db.ai_agents.insert_many(agents)

    # 6. Uploaded Knowledge Base Documents
    doc_hr_id = ObjectId()
    doc_tech_id = ObjectId()
    doc_fin_id = ObjectId()

    db.uploaded_documents.insert_many([
        {
            "_id": doc_hr_id,
            "organizationId": acme_org_id,
            "departmentId": dept_hr_id,
            "fileName": "Acme_HR_Policy_and_Benefits_2026.pdf",
            "fileType": "pdf",
            "fileSize": 245000,
            "storagePath": "/storage/acme/hr/Acme_HR_Policy_and_Benefits_2026.pdf",
            "contentPreview": "Acme Corporation Paid Time Off (PTO) Policy: Full-time employees accrue 20 vacation days annually. Primary caregiver parental leave covers 12 fully paid weeks. Standard 401(k) match is 6% dollar-for-dollar.",
            "chunkCount": 14,
            "vectorCollection": "acme_kb_vectors",
            "classification": "INTERNAL",
            "allowedRoles": ["EMPLOYEE", "MANAGER", "ORG_ADMIN", "SUPER_ADMIN"],
            "uploadedBy": hr_mgr_id,
            "uploadedByName": "David Sterling",
            "status": "INDEXED",
            "errorMessage": None,
            "createdAt": now,
            "updatedAt": now
        },
        {
            "_id": doc_tech_id,
            "organizationId": acme_org_id,
            "departmentId": dept_eng_id,
            "fileName": "Microservices_Architecture_and_SLA.docx",
            "fileType": "docx",
            "fileSize": 512000,
            "storagePath": "/storage/acme/eng/Microservices_Architecture_and_SLA.docx",
            "contentPreview": "Enterprise Cloud System SLA: Target uptime 99.95%. Core Spring Boot backend communicates with Python LangGraph AI service over mTLS. Database connection pool max_size=30, timeout=10s. Redis cache TTL=3600s.",
            "chunkCount": 28,
            "vectorCollection": "acme_kb_vectors",
            "classification": "INTERNAL",
            "allowedRoles": ["EMPLOYEE", "MANAGER", "ORG_ADMIN", "SUPER_ADMIN"],
            "uploadedBy": emp_id,
            "uploadedByName": "Alex Rivera",
            "status": "INDEXED",
            "errorMessage": None,
            "createdAt": now,
            "updatedAt": now
        },
        {
            "_id": doc_fin_id,
            "organizationId": acme_org_id,
            "departmentId": dept_fin_id,
            "fileName": "Q3_Confidential_Financial_Budget_Allocations.pdf",
            "fileType": "pdf",
            "fileSize": 840000,
            "storagePath": "/storage/acme/fin/Q3_Confidential_Financial_Budget_Allocations.pdf",
            "contentPreview": "Confidential Finance Allocations: Engineering Q3 Operating Budget: $1,450,000. Cloud Infrastructure Compute: $320,000. Discretionary hiring freeze enforced until Q4 review.",
            "chunkCount": 35,
            "vectorCollection": "acme_kb_vectors",
            "classification": "CONFIDENTIAL",
            "allowedRoles": ["MANAGER", "ORG_ADMIN", "SUPER_ADMIN"],
            "uploadedBy": org_admin_id,
            "uploadedByName": "Sarah Jenkins",
            "status": "INDEXED",
            "errorMessage": None,
            "createdAt": now,
            "updatedAt": now
        }
    ])

    # 7. Workflows
    db.workflows.insert_many([
        {
            "organizationId": acme_org_id,
            "name": "High-Priority System Incident Auto-Escalation",
            "description": "When a critical API error occurs, notify Technical Support Agent, generate a Jira issue, and broadcast an alert to #dev-incidents.",
            "triggerType": "ON_TICKET_CREATED",
            "targetAgentCode": "action_agent",
            "ruleConfig": {"severity": "CRITICAL", "targetService": "jira", "alertChannel": "slack"},
            "status": "ACTIVE",
            "createdById": org_admin_id,
            "runCount": 8,
            "lastRunAt": now,
            "createdAt": now,
            "updatedAt": now
        }
    ])

    # 8. Sample Approval Request
    db.approval_requests.insert_one({
        "organizationId": acme_org_id,
        "conversationId": None,
        "workflowId": None,
        "requestedBy": emp_id,
        "requestedByName": "Alex Rivera",
        "actionType": "PROVISION_CLOUD_CLUSTER",
        "targetSystem": "AWS EKS",
        "actionPayload": {
            "clusterName": "staging-ai-swarm",
            "nodeCount": 3,
            "instanceType": "m5.large",
            "estimatedMonthlyCost": "$450.00"
        },
        "riskLevel": "HIGH",
        "status": "PENDING",
        "reviewedBy": None,
        "reviewedByName": None,
        "reviewNotes": None,
        "reviewedAt": None,
        "createdAt": now,
        "expiresAt": now + datetime.timedelta(days=3)
    })

    print("[+] Successfully seeded default Multi-Tenant Enterprise data into MongoDB!")

def main():
    try:
        client, db = get_db()
        setup_indexes(db)
        seed_data(db)
        client.close()
        print("\n[SUCCESS] MongoDB enterprise_ai database initialization complete!")
    except Exception as e:
        print(f"\n[!] Note: If MongoDB server is not running locally, make sure to start it via docker or update MONGODB_URI to your MongoDB Atlas connection string.")
        print(f"Details: {e}")

if __name__ == "__main__":
    main()
