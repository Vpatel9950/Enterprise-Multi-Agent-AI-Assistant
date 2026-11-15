# Enterprise Multi-Agent AI Assistant

A production-grade, distributed **Enterprise Multi-Agent AI Assistant** platform built with **Java Spring Boot 3**, **Python FastAPI (LangGraph)**, **React.js 18 (TypeScript + Vite + Tailwind CSS)**, and powered by **MongoDB 7.0** as the primary and exclusive application database.

---

## 🏛️ System Architecture

```text
┌────────────────────────────────────────────────────────────────────────┐
│                   React 18 + TypeScript + Vite UI                      │
│     (Streaming Chat, Agent Traces, RAG Citations, HITL Approvals)       │
└───────────────────▲────────────────────────────────▲───────────────────┘
                    │ REST / JWT                     │ SSE Stream / REST
┌───────────────────▼──────────────────────┐   ┌─────▼──────────────────────────────┐
│  Core Backend (Java Spring Boot 3.3)     │   │  AI Service (Python FastAPI)       │
│  - Spring Security 6 (JWT + RBAC)        │   │  - LangGraph Orchestrator Graph    │
│  - Spring Data MongoDB                   │◄─►│  - 7 Specialized Domain Agents     │
│  - Document ACL Metadata Permissions     │   │  - PyMongo & Multi-Tenant Isolated │
│  - Audit Logging & Rate Limiting         │   │  - Qdrant Vector Engine & RAG      │
└───────────────────▲──────────────────────┘   └─────▲──────────────────────────────┘
                    │                                │
                    └────────────────┬───────────────┘
                                     │
                    ┌────────────────▼────────────────┐
                    │     PRIMARY & EXCLUSIVE DB      │
                    │         MongoDB 7.0             │
                    │   (enterprise_ai Database)      │
                    └─────────────────────────────────┘
```

---

## 🗄️ MongoDB Exclusive Database Design

The system strictly stores and manages all enterprise application data in **MongoDB** (`enterprise_ai`). No relational database is used.

### Core Collections & Relationships

| Collection | Description | Key Indexes & Schema Validation |
| :--- | :--- | :--- |
| `organizations` | Multi-tenant tenant accounts & enterprise settings | Unique on `code` and `domain` |
| `departments` | Organizational departments (Engineering, HR, Finance) | Compound index `{ organizationId: 1, code: 1 }` |
| `roles` | System roles (`SUPER_ADMIN`, `ORG_ADMIN`, `MANAGER`, `EMPLOYEE`) | Unique `{ organizationId: 1, name: 1 }` |
| `users` | Employee records with Bcrypt password hashes & RBAC | Compound unique `{ organizationId: 1, email: 1 }` |
| `ai_agents` | AI Agent swarm catalog with system prompts & tools | Unique `{ organizationId: 1, code: 1 }` |
| `conversations` | Multi-turn chat sessions with assigned agents | Compound index `{ organizationId: 1, userId: 1, updatedAt: -1 }` |
| `messages` | Chat history, RAG citations, and agent execution traces | Compound index `{ conversationId: 1, createdAt: 1 }` |
| `agent_execution_logs` | Audit trail of sub-agent DAG execution steps | Compound index `{ organizationId: 1, agentCode: 1, createdAt: -1 }` |
| `uploaded_documents` | Ingested PDF/DOCX/TXT knowledge files with ACL tags | Compound index `{ organizationId: 1, departmentId: 1 }`, Text index on `fileName` |
| `workflows` | Automated event trigger rules and pipeline actions | Compound index `{ organizationId: 1, triggerType: 1 }` |
| `approval_requests` | Human-in-the-Loop (HITL) gate for sensitive operations | Compound index `{ organizationId: 1, status: 1, createdAt: -1 }` |
| `audit_logs` | Tamper-evident enterprise compliance logs | Compound index `{ organizationId: 1, timestamp: -1 }` |

---

## 🤖 The 7 Specialized AI Agents Swarm

1. **Centralized Orchestrator Agent (`orchestrator`)**:
   - Performs intent recognition and dynamic DAG task decomposition.
   - Delegates subtasks to specialized domain agents and synthesizes the final response.
2. **Knowledge & RAG Agent (`rag_agent`)**:
   - Performs dense vector searches against company handbooks, SLAs, and architecture specs.
   - Enforces strict document-level clearance (`allowedRoles`).
   - Appends verified source citations with document names, section headers, and page numbers.
3. **HR & Employee Agent (`hr_agent`)**:
   - Handles PTO vacation balances, parental leave policies, healthcare insurance, and onboarding milestones.
4. **Finance & Procurement Agent (`finance_agent`)**:
   - Analyzes departmental operating budgets and expenditure variance.
   - Restricts detailed financial ledgers to Manager and Admin roles.
5. **Developer & Architecture Agent (`dev_agent`)**:
   - Provides code snippets, stack trace error diagnostics, connection pool optimizations, and API contracts.
6. **Research & Synthesis Agent (`research_agent`)**:
   - Synthesizes findings across multiple documents into executive briefs.
7. **Database Query Agent (`db_agent`)**:
   - Executes permission-controlled read-only MongoDB aggregation pipelines.
   - Strictly blocks all write, update, delete, or drop operations.
8. **Action & Execution Agent (`action_agent`)**:
   - Interacts with external services (Jira, Slack, CRM, Cloud APIs).
   - **Enforces Human-in-the-Loop (HITL) Gate**: Pauses execution and registers an approval request before modifying any state.

---

## 🚀 Quick Start Guide

### Option A: Complete Docker Compose (Single Command)

```bash
# 1. Clone repository and navigate to root
cd d:\Semester7

# 2. Copy and configure environment variables
cp .env.example .env

# 3. Spin up MongoDB, Redis, Qdrant, Core Backend, AI Service, and Frontend
docker compose up -d
```

---

### Option B: Local Development (Service by Service)

#### 1. Initialize MongoDB Database & Seed Data
```bash
# Run the automated Python MongoDB setup & seed script
python scripts/init_mongo.py
```

#### 2. Start the Python AI Microservice (FastAPI + LangGraph)
```bash
cd ai-service
pip install -r requirements.txt
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
# Service runs at: http://localhost:8000
# OpenAPI Docs at: http://localhost:8000/docs
```

#### 3. Start the Java Spring Boot Core Backend
```bash
cd core-backend
mvn clean spring-boot:run
# Service runs at: http://localhost:8080
# Swagger UI at: http://localhost:8080/swagger-ui.html
```

#### 4. Start the React Frontend Web Client
```bash
cd frontend
npm install
npm run dev
# Web application running at: http://localhost:5173
```

---

## 🔑 Demo Enterprise Roles & Credentials

All default accounts use password: `Password123!`

| Role | Email | Organization | Clearance Scope |
| :--- | :--- | :--- | :--- |
| **Super Admin** | `superadmin@enterprise.ai` | Global Systems | Global multi-tenant administration, cross-org telemetry |
| **Org Admin** | `admin@acme.com` | Acme Corp | Tenant administration, user provisioning, document upload |
| **Manager** | `hr.manager@acme.com` | Acme Corp | Departmental management, HITL action approvals, confidential docs |
| **Employee** | `alex.rivera@acme.com` | Acme Corp | Standard chat, internal document search, workflow triggers |

> **Quick Switcher**: Click the **Role Switcher** buttons in the top Navbar of the web UI to instantly test permissions across all 4 clearance levels!

---

## 🌐 MongoDB Atlas Integration

To connect to a managed **MongoDB Atlas** cluster instead of local MongoDB:
1. Update `MONGODB_URI` in `.env`:
   ```env
   MONGODB_URI=mongodb+srv://<username>:<password>@cluster0.mongodb.net/enterprise_ai?retryWrites=true&w=majority
   ```
2. Run `python scripts/init_mongo.py` to automatically configure indexes and initial seed data in Atlas.
