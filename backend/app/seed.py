import json
import datetime
from app.database import engine, SessionLocal, Base
from app.models import User, Agent, KnowledgeDocument, Workflow, Integration, AnalyticsEvent, Conversation, Message
from app.auth import hash_password

def seed_database():
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()

    try:
        # 1. Seed Users
        if db.query(User).count() == 0:
            admin_user = User(
                email="admin@enterprise.ai",
                hashed_password=hash_password("AdminPassword123!"),
                full_name="Sarah Jenkins (Admin)",
                role="admin",
                department="Executive Operations"
            )
            standard_user = User(
                email="user@enterprise.ai",
                hashed_password=hash_password("UserPassword123!"),
                full_name="Michael Chen",
                role="user",
                department="Engineering"
            )
            db.add_all([admin_user, standard_user])
            db.commit()

        # 2. Seed Agents
        if db.query(Agent).count() == 0:
            agents = [
                Agent(
                    name="Customer Support Agent",
                    code="customer_support",
                    role_description="Resolves client tickets, handles service FAQs, and checks system SLA guarantees.",
                    system_prompt="You are an empathetic, precise Enterprise Customer Support Agent. Provide step-by-step help and refer to internal documentation.",
                    model_name="gpt-4o-mini",
                    temperature=0.6,
                    tools_enabled=json.dumps(["knowledge_search", "ticket_escalation", "sla_checker"])
                ),
                Agent(
                    name="HR & Compliance Agent",
                    code="hr_agent",
                    role_description="Assists employees with PTO policies, benefits enrollment, onboarding, and company handbook rules.",
                    system_prompt="You are an authoritative HR Specialist. Answer questions about leave balance, employee perks, and compliance accurately.",
                    model_name="gpt-4o-mini",
                    temperature=0.5,
                    tools_enabled=json.dumps(["pto_calculator", "handbook_retrieval", "benefits_portal"])
                ),
                Agent(
                    name="Sales & Pipeline Agent",
                    code="sales_agent",
                    role_description="Analyzes deal stages, scores incoming enterprise leads, generates proposals, and updates CRM records.",
                    system_prompt="You are a strategic Sales Lead. Provide concise pipeline metrics, lead scoring recommendations, and deal strategies.",
                    model_name="gpt-4o",
                    temperature=0.7,
                    tools_enabled=json.dumps(["crm_sync", "proposal_generator", "lead_scorer"])
                ),
                Agent(
                    name="Technical Support Agent",
                    code="tech_support",
                    role_description="Diagnoses code exceptions, analyzes infrastructure logs, troubleshoots API errors, and guides developers.",
                    system_prompt="You are a Senior Systems Architect. Diagnose technical errors with code snippets and clear remediation steps.",
                    model_name="gpt-4o",
                    temperature=0.3,
                    tools_enabled=json.dumps(["log_parser", "code_debugger", "jira_creator"])
                ),
                Agent(
                    name="Data Analyst Agent",
                    code="data_analyst",
                    role_description="Translates business queries to SQL, summarizes operational metrics, and generates visual insights.",
                    system_prompt="You are an Enterprise Data Analyst. Format query outputs in clean Markdown tables and SQL statements.",
                    model_name="gpt-4o-mini",
                    temperature=0.4,
                    tools_enabled=json.dumps(["sql_generator", "chart_builder", "export_csv"])
                ),
                Agent(
                    name="Workflow Automation Agent",
                    code="workflow_agent",
                    role_description="Orchestrates multi-agent tasks, coordinates cross-departmental automation, and executes trigger rules.",
                    system_prompt="You are an Automation Supervisor. Delegate subtasks to specialized agents and log execution progress.",
                    model_name="gpt-4o",
                    temperature=0.5,
                    tools_enabled=json.dumps(["workflow_trigger", "slack_dispatch", "multi_agent_router"])
                )
            ]
            db.add_all(agents)
            db.commit()

        # 3. Seed Knowledge Documents
        if db.query(KnowledgeDocument).count() == 0:
            docs = [
                KnowledgeDocument(
                    filename="Enterprise_HR_Policy_2026.txt",
                    file_type="txt",
                    content=(
                        "ENTERPRISE HR POLICY & BENEFIT DIRECTIVE (2026)\n"
                        "1. Paid Time Off (PTO): Full-time employees accrue 2.5 days of PTO per month, totaling 20 days annually. "
                        "Requests over 3 consecutive days require manager sign-off 5 business days in advance.\n"
                        "2. Health & Dental Insurance: Enterprise covers 85% of employee premiums and 65% of dependent coverage. "
                        "Open enrollment opens annually in October.\n"
                        "3. Parental Leave: 12 weeks of 100% paid parental leave for primary caregivers following birth or adoption."
                    ),
                    word_count=85,
                    chunk_count=2,
                    uploaded_by="Sarah Jenkins (Admin)",
                    category="HR & Compliance"
                ),
                KnowledgeDocument(
                    filename="Q3_Sales_Strategy_and_RFP.txt",
                    file_type="txt",
                    content=(
                        "ENTERPRISE SALES STRATEGY & RFP GUIDELINES (Q3 2026)\n"
                        "Target Deal Size: $100k - $500k ARR per enterprise account.\n"
                        "Lead Qualification Criteria: BANT (Budget, Authority, Need, Timeline under 90 days).\n"
                        "Discount Approval Matrix: VP Sales approval required for any contract discount exceeding 15%."
                    ),
                    word_count=52,
                    chunk_count=1,
                    uploaded_by="Sarah Jenkins (Admin)",
                    category="Sales"
                ),
                KnowledgeDocument(
                    filename="API_Architecture_and_SLA.txt",
                    file_type="txt",
                    content=(
                        "DEVELOPER API ARCHITECTURE & SLA GUARANTEES\n"
                        "Uptime Target: 99.95% availability for production REST APIs.\n"
                        "Rate Limits: 10,000 requests per hour per enterprise API key.\n"
                        "Authentication: Bearer JWT in Request Authorization Header (`Authorization: Bearer <token>`).\n"
                        "Database Connection Pool: SQLAlchemy recommended pool size 30 with max_overflow=20."
                    ),
                    word_count=55,
                    chunk_count=1,
                    uploaded_by="Sarah Jenkins (Admin)",
                    category="Technical"
                )
            ]
            db.add_all(docs)
            db.commit()

        # 4. Seed Workflows
        if db.query(Workflow).count() == 0:
            tech_agent = db.query(Agent).filter(Agent.code == "tech_support").first()
            sales_agent = db.query(Agent).filter(Agent.code == "sales_agent").first()
            admin = db.query(User).filter(User.role == "admin").first()

            workflows = [
                Workflow(
                    name="High-Priority Incident Auto-Escalation",
                    description="Automatically alerts Technical Support and logs a high priority Jira ticket on system failure.",
                    trigger_type="on_ticket_created",
                    target_agent_id=tech_agent.id if tech_agent else 1,
                    config_json=json.dumps({"target_service": "jira", "action_type": "create_ticket", "priority": "High"}),
                    status="active",
                    created_by_id=admin.id if admin else 1,
                    run_count=12,
                    last_run_at=datetime.datetime.utcnow() - datetime.timedelta(hours=2)
                ),
                Workflow(
                    name="Inbound Lead CRM Qualification Sync",
                    description="Scores new enterprise leads and pushes qualified profiles to Salesforce CRM.",
                    trigger_type="on_lead_received",
                    target_agent_id=sales_agent.id if sales_agent else 2,
                    config_json=json.dumps({"target_service": "crm", "action_type": "create_deal", "min_score": 80}),
                    status="active",
                    created_by_id=admin.id if admin else 1,
                    run_count=45,
                    last_run_at=datetime.datetime.utcnow() - datetime.timedelta(minutes=15)
                )
            ]
            db.add_all(workflows)
            db.commit()

        # 5. Seed Integrations
        if db.query(Integration).count() == 0:
            integrations = [
                Integration(name="Slack Workspace Connector", service_type="slack", status="connected", webhook_url="https://hooks.slack.com/services/T00/B00/XXXX"),
                Integration(name="Salesforce CRM Sync", service_type="crm", status="connected", webhook_url="https://crm.enterprise.com/api/v1/sync"),
                Integration(name="SAP ERP Enterprise Module", service_type="erp", status="connected", webhook_url="https://erp.enterprise.com/api/sap"),
                Integration(name="SendGrid Email Service", service_type="email", status="connected", webhook_url="https://api.sendgrid.com/v3/mail/send"),
                Integration(name="Jira Software Cloud", service_type="jira", status="connected", webhook_url="https://enterprise.atlassian.net/rest/api/3")
            ]
            db.add_all(integrations)
            db.commit()

        # 6. Seed Analytics Events
        if db.query(AnalyticsEvent).count() == 0:
            events = [
                AnalyticsEvent(action_type="chat_query", response_time_ms=180, tokens_used=140, satisfaction_score=5.0),
                AnalyticsEvent(action_type="chat_query", response_time_ms=220, tokens_used=210, satisfaction_score=4.8),
                AnalyticsEvent(action_type="rag_search", response_time_ms=95, tokens_used=80, satisfaction_score=5.0),
                AnalyticsEvent(action_type="workflow_trigger", response_time_ms=310, tokens_used=300, satisfaction_score=4.9)
            ]
            db.add_all(events)
            db.commit()

        print("Database seeded successfully!")

    finally:
        db.close()

if __name__ == "__main__":
    seed_database()
