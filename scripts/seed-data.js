// Seed Data Script for MongoDB Database: enterprise_ai
// Contains seed data for Multi-Tenant Organizations, Departments, Roles, Users,
// AI Agents, Uploaded Knowledge Documents, Workflows, and Sample Approval Requests.

const dbName = 'enterprise_ai';
const targetDb = db.getSiblingDB(dbName);

print(`[MongoDB Seed] Seeding default enterprise records into '${dbName}'...`);

// Clean existing data for clean setup
targetDb.organizations.deleteMany({});
targetDb.departments.deleteMany({});
targetDb.roles.deleteMany({});
targetDb.users.deleteMany({});
targetDb.ai_agents.deleteMany({});
targetDb.conversations.deleteMany({});
targetDb.messages.deleteMany({});
targetDb.uploaded_documents.deleteMany({});
targetDb.workflows.deleteMany({});
targetDb.approval_requests.deleteMany({});
targetDb.audit_logs.deleteMany({});

const now = new Date();

// 1. ORGANIZATIONS
const acmeOrgId = new ObjectId();
const globalOrgId = new ObjectId();

targetDb.organizations.insertMany([
  {
    _id: acmeOrgId,
    name: 'Acme Global Enterprises',
    code: 'acme-corp',
    domain: 'acme.com',
    status: 'ACTIVE',
    subscriptionTier: 'ENTERPRISE',
    settings: {
      enforceMFA: true,
      allowedLLMs: ['gpt-4o', 'claude-3-5-sonnet'],
      hitlAutoApprovalThreshold: 1000
    },
    createdAt: now,
    updatedAt: now
  },
  {
    _id: globalOrgId,
    name: 'Global Enterprise Cloud Systems',
    code: 'global-ai',
    domain: 'enterprise.ai',
    status: 'ACTIVE',
    subscriptionTier: 'ENTERPRISE',
    settings: {
      enforceMFA: true,
      allowedLLMs: ['gpt-4o', 'claude-3-5-sonnet']
    },
    createdAt: now,
    updatedAt: now
  }
]);

// 2. DEPARTMENTS
const deptEngineeringId = new ObjectId();
const deptHrId = new ObjectId();
const deptFinanceId = new ObjectId();
const deptExecId = new ObjectId();

targetDb.departments.insertMany([
  {
    _id: deptEngineeringId,
    organizationId: acmeOrgId,
    name: 'Engineering & Architecture',
    code: 'ENG',
    description: 'Software development, cloud infrastructure, and technical operations',
    managerId: null,
    createdAt: now,
    updatedAt: now
  },
  {
    _id: deptHrId,
    organizationId: acmeOrgId,
    name: 'Human Resources & Talent',
    code: 'HR',
    description: 'Workforce compliance, talent onboarding, employee benefits & leave management',
    managerId: null,
    createdAt: now,
    updatedAt: now
  },
  {
    _id: deptFinanceId,
    organizationId: acmeOrgId,
    name: 'Finance & Procurement',
    code: 'FIN',
    description: 'Corporate budgeting, expense auditing, and vendor contracts',
    managerId: null,
    createdAt: now,
    updatedAt: now
  },
  {
    _id: deptExecId,
    organizationId: acmeOrgId,
    name: 'Executive Operations',
    code: 'EXEC',
    description: 'Strategic planning, cross-tenant policies, and governance',
    managerId: null,
    createdAt: now,
    updatedAt: now
  }
]);

// 3. ROLES & PERMISSIONS
targetDb.roles.insertMany([
  {
    organizationId: null,
    name: 'SUPER_ADMIN',
    description: 'Global system administration across all organizations',
    permissions: [
      'SYS_ALL', 'ORG_CREATE', 'ORG_UPDATE', 'USER_ALL', 'AUDIT_READ',
      'DOC_ALL', 'AGENT_CONFIGURE', 'WORKFLOW_ALL', 'HITL_OVERRIDE'
    ],
    isSystemRole: true,
    createdAt: now
  },
  {
    organizationId: null,
    name: 'ORG_ADMIN',
    description: 'Tenant-level administrative control, departmental governance & policies',
    permissions: [
      'ORG_READ', 'DEPT_ALL', 'USER_READ', 'USER_MANAGE', 'DOC_ALL',
      'AGENT_CONFIGURE', 'WORKFLOW_ALL', 'AUDIT_READ', 'HITL_APPROVE'
    ],
    isSystemRole: true,
    createdAt: now
  },
  {
    organizationId: null,
    name: 'MANAGER',
    description: 'Departmental management, approval authority & confidential document access',
    permissions: [
      'USER_READ', 'DEPT_READ', 'DOC_READ_CONFIDENTIAL', 'WORKFLOW_TRIGGER',
      'HITL_APPROVE', 'AUDIT_DEPT_READ'
    ],
    isSystemRole: true,
    createdAt: now
  },
  {
    organizationId: null,
    name: 'EMPLOYEE',
    description: 'Standard employee chat, personal workflows, and public/internal documents',
    permissions: [
      'USER_READ_SELF', 'DOC_READ_INTERNAL', 'CHAT_USE', 'WORKFLOW_REQUEST'
    ],
    isSystemRole: true,
    createdAt: now
  }
]);

// 4. USERS (Bcrypt hash for password "Password123!")
const bcryptPasswordHash = '$2a$10$wT/t.95oYQ8PjG14x6qD..KxOqD5qX4yV4f1R3eLwU5.c7M9hV5O6';

const superAdminUserId = new ObjectId();
const orgAdminUserId = new ObjectId();
const hrManagerUserId = new ObjectId();
const employeeUserId = new ObjectId();

targetDb.users.insertMany([
  {
    _id: superAdminUserId,
    organizationId: globalOrgId,
    departmentId: deptExecId,
    email: 'superadmin@enterprise.ai',
    passwordHash: bcryptPasswordHash,
    fullName: 'Victoria Vance (Super Admin)',
    role: 'SUPER_ADMIN',
    department: 'Executive Operations',
    isActive: true,
    lastLoginAt: now,
    createdAt: now,
    updatedAt: now
  },
  {
    _id: orgAdminUserId,
    organizationId: acmeOrgId,
    departmentId: deptExecId,
    email: 'admin@acme.com',
    passwordHash: bcryptPasswordHash,
    fullName: 'Sarah Jenkins (Org Admin)',
    role: 'ORG_ADMIN',
    department: 'Executive Operations',
    isActive: true,
    lastLoginAt: now,
    createdAt: now,
    updatedAt: now
  },
  {
    _id: hrManagerUserId,
    organizationId: acmeOrgId,
    departmentId: deptHrId,
    email: 'hr.manager@acme.com',
    passwordHash: bcryptPasswordHash,
    fullName: 'David Sterling (HR Manager)',
    role: 'MANAGER',
    department: 'Human Resources & Talent',
    isActive: true,
    lastLoginAt: now,
    createdAt: now,
    updatedAt: now
  },
  {
    _id: employeeUserId,
    organizationId: acmeOrgId,
    departmentId: deptEngineeringId,
    email: 'alex.rivera@acme.com',
    passwordHash: bcryptPasswordHash,
    fullName: 'Alex Rivera (Staff Engineer)',
    role: 'EMPLOYEE',
    department: 'Engineering & Architecture',
    isActive: true,
    lastLoginAt: now,
    createdAt: now,
    updatedAt: now
  }
]);

// Update manager reference
targetDb.departments.updateOne({ _id: deptHrId }, { $set: { managerId: hrManagerUserId } });

// 5. AI AGENTS CATALOG
targetDb.ai_agents.insertMany([
  {
    organizationId: null,
    code: 'orchestrator',
    name: 'Centralized Orchestrator Agent',
    roleDescription: 'Main supervisor agent. Analyzes natural language intent, creates DAG task breakdown, delegates subtasks, and synthesizes answers.',
    systemPrompt: 'You are the Centralized Orchestrator of the Enterprise Multi-Agent AI System. Break down user queries, delegate subtasks to specialized agents (RAG, HR, Finance, Developer, Research, Database, Action), enforce organizational access control, and combine sub-agent findings into a cohesive, executive-grade response.',
    modelName: 'gpt-4o',
    temperature: 0.2,
    tools: ['delegate_agent', 'aggregate_responses', 'check_permission', 'hitl_approval_gate'],
    requiredPermission: 'CHAT_USE',
    isSystem: true,
    isActive: true,
    createdAt: now,
    updatedAt: now
  },
  {
    organizationId: null,
    code: 'rag_agent',
    name: 'Knowledge & RAG Agent',
    roleDescription: 'Retrieves facts and answers from uploaded company handbooks, architecture specs, and internal policies with precise citations.',
    systemPrompt: 'You are the Knowledge/RAG Agent. Search the company document vector index with security ACL filters. Always cite the document name, page number, and section whenever answering.',
    modelName: 'gpt-4o-mini',
    temperature: 0.1,
    tools: ['vector_search', 'extract_citation', 'summarize_document'],
    requiredPermission: 'DOC_READ_INTERNAL',
    isSystem: true,
    isActive: true,
    createdAt: now,
    updatedAt: now
  },
  {
    organizationId: null,
    code: 'hr_agent',
    name: 'HR & Employee Agent',
    roleDescription: 'Handles employee leave balances, PTO policies, healthcare benefits, and corporate onboarding workflows.',
    systemPrompt: 'You are the Enterprise HR Agent. Help employees with PTO policy, benefits enrollment, maternity/paternity leave, and onboarding steps. Mask sensitive PII and ensure responses adhere to company HR directives.',
    modelName: 'gpt-4o-mini',
    temperature: 0.3,
    tools: ['pto_calculator', 'handbook_retriever', 'benefits_navigator'],
    requiredPermission: 'CHAT_USE',
    isSystem: true,
    isActive: true,
    createdAt: now,
    updatedAt: now
  },
  {
    organizationId: null,
    code: 'finance_agent',
    name: 'Finance & Procurement Agent',
    roleDescription: 'Analyzes department budgets, reports spending variance, tracks invoice approvals, and queries cost centers.',
    systemPrompt: 'You are the Enterprise Finance Agent. Provide department spending summaries, cost center breakdowns, and procurement approval policies. Do not authorize disbursements directly; route payment requests through the Action Agent.',
    modelName: 'gpt-4o',
    temperature: 0.1,
    tools: ['budget_lookup', 'spend_variance_analyzer', 'procurement_matrix'],
    requiredPermission: 'FINANCE_READ',
    isSystem: true,
    isActive: true,
    createdAt: now,
    updatedAt: now
  },
  {
    organizationId: null,
    code: 'dev_agent',
    name: 'Developer & Architecture Agent',
    roleDescription: 'Provides software architecture guidance, API code generation, stack trace debugging, and infrastructure diagnostics.',
    systemPrompt: 'You are the Senior Technical Architecture Agent. Diagnose system errors, provide clean code snippets, generate Swagger/OpenAPI contracts, and explain cloud infrastructure setups.',
    modelName: 'gpt-4o',
    temperature: 0.2,
    tools: ['code_analyzer', 'log_debugger', 'architecture_diagrammer'],
    requiredPermission: 'CHAT_USE',
    isSystem: true,
    isActive: true,
    createdAt: now,
    updatedAt: now
  },
  {
    organizationId: null,
    code: 'research_agent',
    name: 'Research & Synthesis Agent',
    roleDescription: 'Synthesizes information across multiple internal records and external industry benchmarks into structured executive briefs.',
    systemPrompt: 'You are the Enterprise Research Agent. Gather information across internal knowledge and industry trends, verify factual accuracy, and formulate clear, well-referenced executive summaries.',
    modelName: 'gpt-4o',
    temperature: 0.4,
    tools: ['multi_doc_synthesizer', 'competitive_benchmarker', 'executive_briefer'],
    requiredPermission: 'CHAT_USE',
    isSystem: true,
    isActive: true,
    createdAt: now,
    updatedAt: now
  },
  {
    organizationId: null,
    code: 'db_agent',
    name: 'Database Query Agent',
    roleDescription: 'Executes secure, permission-validated read-only MongoDB aggregation queries without modifying or deleting data.',
    systemPrompt: 'You are the Read-Only Database Query Agent. Translate natural language queries into MongoDB aggregation pipelines. You strictly NEVER execute update, delete, drop, or destructive operations. Only find() and aggregate() are permitted.',
    modelName: 'gpt-4o',
    temperature: 0.0,
    tools: ['mongo_aggregate_readonly', 'schema_inspector', 'query_validator'],
    requiredPermission: 'DB_QUERY_READ',
    isSystem: true,
    isActive: true,
    createdAt: now,
    updatedAt: now
  },
  {
    organizationId: null,
    code: 'action_agent',
    name: 'Action & Execution Agent',
    roleDescription: 'Executes authorized operations (creating records, filing tickets, triggering webhooks) with mandatory Human-in-the-Loop approval.',
    systemPrompt: 'You are the Enterprise Action Agent. Whenever an operation modifies state, issues external notifications, or affects business records, you must pause execution and request explicit Human-in-the-Loop (HITL) approval.',
    modelName: 'gpt-4o',
    temperature: 0.1,
    tools: ['create_jira_issue', 'dispatch_slack_alert', 'sync_crm_lead', 'submit_procurement_request'],
    requiredPermission: 'ACTION_EXECUTE',
    isSystem: true,
    isActive: true,
    createdAt: now,
    updatedAt: now
  }
]);

// 6. UPLOADED DOCUMENTS (KNOWLEDGE BASE)
const docHrId = new ObjectId();
const docTechId = new ObjectId();
const docFinId = new ObjectId();

targetDb.uploaded_documents.insertMany([
  {
    _id: docHrId,
    organizationId: acmeOrgId,
    departmentId: deptHrId,
    fileName: 'Acme_HR_Policy_and_Benefits_2026.pdf',
    fileType: 'pdf',
    fileSize: 245000,
    storagePath: '/storage/acme/hr/Acme_HR_Policy_and_Benefits_2026.pdf',
    contentPreview: 'Acme Corporation Paid Time Off (PTO) Policy: Full-time employees accrue 20 vacation days annually. Primary caregiver parental leave covers 12 fully paid weeks. Standard 401(k) match is 6% dollar-for-dollar.',
    chunkCount: 14,
    vectorCollection: 'acme_kb_vectors',
    classification: 'INTERNAL',
    allowedRoles: ['EMPLOYEE', 'MANAGER', 'ORG_ADMIN', 'SUPER_ADMIN'],
    uploadedBy: hrManagerUserId,
    uploadedByName: 'David Sterling',
    status: 'INDEXED',
    errorMessage: null,
    createdAt: now,
    updatedAt: now
  },
  {
    _id: docTechId,
    organizationId: acmeOrgId,
    departmentId: deptEngineeringId,
    fileName: 'Microservices_Architecture_and_SLA.docx',
    fileType: 'docx',
    fileSize: 512000,
    storagePath: '/storage/acme/eng/Microservices_Architecture_and_SLA.docx',
    contentPreview: 'Enterprise Cloud System SLA: Target uptime 99.95%. Core Spring Boot backend communicates with Python LangGraph AI service over mTLS. Database connection pool max_size=30, timeout=10s. Redis cache TTL=3600s.',
    chunkCount: 28,
    vectorCollection: 'acme_kb_vectors',
    classification: 'INTERNAL',
    allowedRoles: ['EMPLOYEE', 'MANAGER', 'ORG_ADMIN', 'SUPER_ADMIN'],
    uploadedBy: employeeUserId,
    uploadedByName: 'Alex Rivera',
    status: 'INDEXED',
    errorMessage: null,
    createdAt: now,
    updatedAt: now
  },
  {
    _id: docFinId,
    organizationId: acmeOrgId,
    departmentId: deptFinanceId,
    fileName: 'Q3_Confidential_Financial_Budget_Allocations.pdf',
    fileType: 'pdf',
    fileSize: 840000,
    storagePath: '/storage/acme/fin/Q3_Confidential_Financial_Budget_Allocations.pdf',
    contentPreview: 'Confidential Finance Allocations: Engineering Q3 Operating Budget: $1,450,000. Cloud Infrastructure Compute: $320,000. Discretionary hiring freeze enforced until Q4 review.',
    chunkCount: 35,
    vectorCollection: 'acme_kb_vectors',
    classification: 'CONFIDENTIAL',
    allowedRoles: ['MANAGER', 'ORG_ADMIN', 'SUPER_ADMIN'], // Restricted from regular employees!
    uploadedBy: orgAdminUserId,
    uploadedByName: 'Sarah Jenkins',
    status: 'INDEXED',
    errorMessage: null,
    createdAt: now,
    updatedAt: now
  }
]);

// 7. WORKFLOWS
targetDb.workflows.insertMany([
  {
    organizationId: acmeOrgId,
    name: 'High-Priority System Incident Auto-Escalation',
    description: 'When a critical API error occurs, notify Technical Support Agent, generate a Jira issue, and broadcast an alert to #dev-incidents.',
    triggerType: 'ON_TICKET_CREATED',
    targetAgentCode: 'action_agent',
    ruleConfig: {
      severity: 'CRITICAL',
      targetService: 'jira',
      alertChannel: 'slack'
    },
    status: 'ACTIVE',
    createdById: orgAdminUserId,
    runCount: 8,
    lastRunAt: new Date(Date.now() - 3600000),
    createdAt: now,
    updatedAt: now
  },
  {
    organizationId: acmeOrgId,
    name: 'Weekly Department Budget Variance Digest',
    description: 'Weekly scheduled aggregation by Finance Agent analyzing expenditure variances above 10%.',
    triggerType: 'SCHEDULED_DAILY',
    targetAgentCode: 'finance_agent',
    ruleConfig: {
      schedule: '0 9 * * 1',
      notifyManagers: true
    },
    status: 'ACTIVE',
    createdById: orgAdminUserId,
    runCount: 14,
    lastRunAt: new Date(Date.now() - 86400000),
    createdAt: now,
    updatedAt: now
  }
]);

// 8. APPROVAL REQUESTS (HITL SAMPLES)
targetDb.approval_requests.insertMany([
  {
    organizationId: acmeOrgId,
    conversationId: null,
    workflowId: null,
    requestedBy: employeeUserId,
    requestedByName: 'Alex Rivera',
    actionType: 'PROVISION_CLOUD_CLUSTER',
    targetSystem: 'AWS EKS',
    actionPayload: {
      clusterName: 'staging-ai-swarm',
      nodeCount: 3,
      instanceType: 'm5.large',
      estimatedMonthlyCost: '$450.00'
    },
    riskLevel: 'HIGH',
    status: 'PENDING',
    reviewedBy: null,
    reviewedByName: null,
    reviewNotes: null,
    reviewedAt: null,
    createdAt: now,
    expiresAt: new Date(Date.now() + 86400000 * 3)
  }
]);

// 9. AUDIT LOGS
targetDb.audit_logs.insertMany([
  {
    organizationId: acmeOrgId,
    userId: orgAdminUserId,
    userEmail: 'admin@acme.com',
    userRole: 'ORG_ADMIN',
    action: 'ORGANIZATION_CONFIG_UPDATE',
    resourceType: 'ORGANIZATION',
    resourceId: acmeOrgId.toString(),
    ipAddress: '192.168.1.10',
    userAgent: 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)',
    status: 'SUCCESS',
    details: { change: 'Enabled MFA and configured GPT-4o model' },
    timestamp: new Date(Date.now() - 7200000)
  },
  {
    organizationId: acmeOrgId,
    userId: hrManagerUserId,
    userEmail: 'hr.manager@acme.com',
    userRole: 'MANAGER',
    action: 'DOCUMENT_UPLOAD',
    resourceType: 'UPLOADED_DOCUMENT',
    resourceId: docHrId.toString(),
    ipAddress: '192.168.1.15',
    userAgent: 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)',
    status: 'SUCCESS',
    details: { fileName: 'Acme_HR_Policy_and_Benefits_2026.pdf', classification: 'INTERNAL' },
    timestamp: new Date(Date.now() - 3600000)
  }
]);

print(`[MongoDB Seed] Successfully populated initial multi-tenant data into '${dbName}'!`);
