// MongoDB Initialization Script for Enterprise Multi-Agent AI Assistant
// Database: enterprise_ai
// Strict schema validators, compound indexes, unique constraints, and organization-level isolation

const dbName = 'enterprise_ai';
const targetDb = db.getSiblingDB(dbName);

print(`[MongoDB Init] Initializing '${dbName}' database with schema validation & indexes...`);

// 1. ORGANIZATIONS
targetDb.createCollection('organizations', {
  validator: {
    $jsonSchema: {
      bsonType: 'object',
      required: ['name', 'code', 'domain', 'status', 'subscriptionTier', 'createdAt'],
      properties: {
        name: { bsonType: 'string', description: 'Organization full name' },
        code: { bsonType: 'string', description: 'Unique slug code (e.g. acme-corp)' },
        domain: { bsonType: 'string', description: 'Corporate email domain' },
        status: { enum: ['ACTIVE', 'SUSPENDED', 'PENDING'], description: 'Organization account status' },
        subscriptionTier: { enum: ['STARTER', 'PROFESSIONAL', 'ENTERPRISE'], description: 'Billing plan' },
        settings: { bsonType: 'object', description: 'Custom org configuration' },
        createdAt: { bsonType: 'date' },
        updatedAt: { bsonType: 'date' }
      }
    }
  }
});
targetDb.organizations.createIndex({ code: 1 }, { unique: true });
targetDb.organizations.createIndex({ domain: 1 }, { unique: true });

// 2. DEPARTMENTS
targetDb.createCollection('departments', {
  validator: {
    $jsonSchema: {
      bsonType: 'object',
      required: ['organizationId', 'name', 'code', 'createdAt'],
      properties: {
        organizationId: { bsonType: 'objectId' },
        name: { bsonType: 'string' },
        code: { bsonType: 'string' },
        description: { bsonType: 'string' },
        managerId: { bsonType: ['objectId', 'null'] },
        createdAt: { bsonType: 'date' },
        updatedAt: { bsonType: 'date' }
      }
    }
  }
});
targetDb.departments.createIndex({ organizationId: 1, code: 1 }, { unique: true });
targetDb.departments.createIndex({ organizationId: 1, name: 1 });

// 3. ROLES & PERMISSIONS
targetDb.createCollection('roles', {
  validator: {
    $jsonSchema: {
      bsonType: 'object',
      required: ['name', 'permissions', 'isSystemRole', 'createdAt'],
      properties: {
        organizationId: { bsonType: ['objectId', 'null'] },
        name: { enum: ['SUPER_ADMIN', 'ORG_ADMIN', 'MANAGER', 'EMPLOYEE'], description: 'Standard role hierarchy' },
        description: { bsonType: 'string' },
        permissions: { bsonType: 'array', items: { bsonType: 'string' } },
        isSystemRole: { bsonType: 'bool' },
        createdAt: { bsonType: 'date' }
      }
    }
  }
});
targetDb.roles.createIndex({ organizationId: 1, name: 1 }, { unique: true });

// 4. USERS
targetDb.createCollection('users', {
  validator: {
    $jsonSchema: {
      bsonType: 'object',
      required: ['organizationId', 'email', 'passwordHash', 'fullName', 'role', 'isActive', 'createdAt'],
      properties: {
        organizationId: { bsonType: 'objectId' },
        departmentId: { bsonType: ['objectId', 'null'] },
        email: { bsonType: 'string', pattern: '^\\S+@\\S+\\.\\S+$' },
        passwordHash: { bsonType: 'string' },
        fullName: { bsonType: 'string' },
        role: { enum: ['SUPER_ADMIN', 'ORG_ADMIN', 'MANAGER', 'EMPLOYEE'] },
        department: { bsonType: ['string', 'null'] },
        isActive: { bsonType: 'bool' },
        lastLoginAt: { bsonType: ['date', 'null'] },
        createdAt: { bsonType: 'date' },
        updatedAt: { bsonType: 'date' }
      }
    }
  }
});
targetDb.users.createIndex({ organizationId: 1, email: 1 }, { unique: true });
targetDb.users.createIndex({ email: 1 }, { unique: true });
targetDb.users.createIndex({ organizationId: 1, role: 1 });
targetDb.users.createIndex({ organizationId: 1, departmentId: 1 });

// 5. AI AGENTS CATALOG
targetDb.createCollection('ai_agents', {
  validator: {
    $jsonSchema: {
      bsonType: 'object',
      required: ['code', 'name', 'roleDescription', 'systemPrompt', 'modelName', 'isActive', 'createdAt'],
      properties: {
        organizationId: { bsonType: ['objectId', 'null'] },
        code: {
          enum: [
            'orchestrator',
            'rag_agent',
            'hr_agent',
            'finance_agent',
            'dev_agent',
            'research_agent',
            'db_agent',
            'action_agent'
          ]
        },
        name: { bsonType: 'string' },
        roleDescription: { bsonType: 'string' },
        systemPrompt: { bsonType: 'string' },
        modelName: { bsonType: 'string' },
        temperature: { bsonType: 'double' },
        tools: { bsonType: 'array', items: { bsonType: 'string' } },
        requiredPermission: { bsonType: 'string' },
        isSystem: { bsonType: 'bool' },
        isActive: { bsonType: 'bool' },
        createdAt: { bsonType: 'date' },
        updatedAt: { bsonType: 'date' }
      }
    }
  }
});
targetDb.ai_agents.createIndex({ organizationId: 1, code: 1 }, { unique: true });

// 6. CONVERSATIONS
targetDb.createCollection('conversations', {
  validator: {
    $jsonSchema: {
      bsonType: 'object',
      required: ['organizationId', 'userId', 'title', 'status', 'createdAt', 'updatedAt'],
      properties: {
        organizationId: { bsonType: 'objectId' },
        userId: { bsonType: 'objectId' },
        title: { bsonType: 'string' },
        assignedAgentCode: { bsonType: ['string', 'null'] },
        status: { enum: ['ACTIVE', 'ARCHIVED', 'DELETED'] },
        pinnedMessageIds: { bsonType: 'array', items: { bsonType: 'objectId' } },
        metadata: { bsonType: 'object' },
        createdAt: { bsonType: 'date' },
        updatedAt: { bsonType: 'date' }
      }
    }
  }
});
targetDb.conversations.createIndex({ organizationId: 1, userId: 1, updatedAt: -1 });
targetDb.conversations.createIndex({ organizationId: 1, status: 1 });

// 7. MESSAGES
targetDb.createCollection('messages', {
  validator: {
    $jsonSchema: {
      bsonType: 'object',
      required: ['conversationId', 'organizationId', 'senderType', 'senderName', 'content', 'createdAt'],
      properties: {
        conversationId: { bsonType: 'objectId' },
        organizationId: { bsonType: 'objectId' },
        senderType: { enum: ['USER', 'AGENT', 'SYSTEM', 'DELEGATE'] },
        senderId: { bsonType: ['objectId', 'string', 'null'] },
        senderName: { bsonType: 'string' },
        content: { bsonType: 'string' },
        citations: {
          bsonType: 'array',
          items: {
            bsonType: 'object',
            required: ['documentId', 'sourceName', 'relevanceScore', 'snippet'],
            properties: {
              documentId: { bsonType: 'objectId' },
              sourceName: { bsonType: 'string' },
              pageNumber: { bsonType: ['int', 'null'] },
              section: { bsonType: ['string', 'null'] },
              relevanceScore: { bsonType: 'double' },
              snippet: { bsonType: 'string' }
            }
          }
        },
        agentTraces: {
          bsonType: 'array',
          items: {
            bsonType: 'object',
            required: ['agentName', 'action', 'status', 'durationMs'],
            properties: {
              agentName: { bsonType: 'string' },
              action: { bsonType: 'string' },
              status: { enum: ['STARTED', 'COMPLETED', 'FAILED', 'PENDING_APPROVAL'] },
              durationMs: { bsonType: 'int' },
              details: { bsonType: ['string', 'null'] }
            }
          }
        },
        durationMs: { bsonType: ['int', 'null'] },
        tokensUsed: { bsonType: ['int', 'null'] },
        createdAt: { bsonType: 'date' }
      }
    }
  }
});
targetDb.messages.createIndex({ conversationId: 1, createdAt: 1 });
targetDb.messages.createIndex({ organizationId: 1, createdAt: -1 });

// 8. AGENT EXECUTION LOGS
targetDb.createCollection('agent_execution_logs', {
  validator: {
    $jsonSchema: {
      bsonType: 'object',
      required: ['organizationId', 'userId', 'agentCode', 'taskDescription', 'status', 'durationMs', 'createdAt'],
      properties: {
        organizationId: { bsonType: 'objectId' },
        conversationId: { bsonType: ['objectId', 'null'] },
        messageId: { bsonType: ['objectId', 'null'] },
        userId: { bsonType: 'objectId' },
        agentCode: { bsonType: 'string' },
        taskDescription: { bsonType: 'string' },
        inputStateSummary: { bsonType: 'string' },
        outputStateSummary: { bsonType: ['string', 'null'] },
        status: { enum: ['SUCCESS', 'FAILED', 'PAUSED_HITL', 'TIMEOUT'] },
        durationMs: { bsonType: 'int' },
        error: { bsonType: ['string', 'null'] },
        createdAt: { bsonType: 'date' }
      }
    }
  }
});
targetDb.agent_execution_logs.createIndex({ organizationId: 1, agentCode: 1, createdAt: -1 });
targetDb.agent_execution_logs.createIndex({ organizationId: 1, userId: 1, createdAt: -1 });

// 9. UPLOADED DOCUMENTS (KNOWLEDGE BASE)
targetDb.createCollection('uploaded_documents', {
  validator: {
    $jsonSchema: {
      bsonType: 'object',
      required: ['organizationId', 'fileName', 'fileType', 'fileSize', 'classification', 'allowedRoles', 'uploadedBy', 'status', 'createdAt'],
      properties: {
        organizationId: { bsonType: 'objectId' },
        departmentId: { bsonType: ['objectId', 'null'] },
        fileName: { bsonType: 'string' },
        fileType: { enum: ['pdf', 'docx', 'txt', 'csv', 'md'] },
        fileSize: { bsonType: 'int' },
        storagePath: { bsonType: 'string' },
        contentPreview: { bsonType: 'string' },
        chunkCount: { bsonType: 'int' },
        vectorCollection: { bsonType: 'string' },
        classification: { enum: ['PUBLIC', 'INTERNAL', 'CONFIDENTIAL', 'RESTRICTED'] },
        allowedRoles: { bsonType: 'array', items: { bsonType: 'string' } },
        uploadedBy: { bsonType: 'objectId' },
        uploadedByName: { bsonType: 'string' },
        status: { enum: ['PROCESSING', 'INDEXED', 'FAILED'] },
        errorMessage: { bsonType: ['string', 'null'] },
        createdAt: { bsonType: 'date' },
        updatedAt: { bsonType: 'date' }
      }
    }
  }
});
targetDb.uploaded_documents.createIndex({ organizationId: 1, departmentId: 1 });
targetDb.uploaded_documents.createIndex({ organizationId: 1, classification: 1 });
targetDb.uploaded_documents.createIndex({ organizationId: 1, fileName: 'text', contentPreview: 'text' });

// 10. WORKFLOWS
targetDb.createCollection('workflows', {
  validator: {
    $jsonSchema: {
      bsonType: 'object',
      required: ['organizationId', 'name', 'description', 'triggerType', 'targetAgentCode', 'status', 'createdById', 'createdAt'],
      properties: {
        organizationId: { bsonType: 'objectId' },
        name: { bsonType: 'string' },
        description: { bsonType: 'string' },
        triggerType: { enum: ['ON_TICKET_CREATED', 'ON_LEAD_RECEIVED', 'ON_DOCUMENT_UPLOADED', 'SCHEDULED_DAILY', 'MANUAL'] },
        targetAgentCode: { bsonType: 'string' },
        ruleConfig: { bsonType: 'object' },
        status: { enum: ['ACTIVE', 'PAUSED', 'DEPRECATED'] },
        createdById: { bsonType: 'objectId' },
        runCount: { bsonType: 'int' },
        lastRunAt: { bsonType: ['date', 'null'] },
        createdAt: { bsonType: 'date' },
        updatedAt: { bsonType: 'date' }
      }
    }
  }
});
targetDb.workflows.createIndex({ organizationId: 1, triggerType: 1 });
targetDb.workflows.createIndex({ organizationId: 1, status: 1 });

// 11. APPROVAL REQUESTS (HUMAN-IN-THE-LOOP)
targetDb.createCollection('approval_requests', {
  validator: {
    $jsonSchema: {
      bsonType: 'object',
      required: ['organizationId', 'requestedBy', 'actionType', 'targetSystem', 'actionPayload', 'riskLevel', 'status', 'createdAt'],
      properties: {
        organizationId: { bsonType: 'objectId' },
        conversationId: { bsonType: ['objectId', 'null'] },
        workflowId: { bsonType: ['objectId', 'null'] },
        requestedBy: { bsonType: 'objectId' },
        requestedByName: { bsonType: 'string' },
        actionType: { bsonType: 'string' },
        targetSystem: { bsonType: 'string' },
        actionPayload: { bsonType: 'object' },
        riskLevel: { enum: ['LOW', 'MEDIUM', 'HIGH', 'CRITICAL'] },
        status: { enum: ['PENDING', 'APPROVED', 'REJECTED', 'EXPIRED'] },
        reviewedBy: { bsonType: ['objectId', 'null'] },
        reviewedByName: { bsonType: ['string', 'null'] },
        reviewNotes: { bsonType: ['string', 'null'] },
        reviewedAt: { bsonType: ['date', 'null'] },
        createdAt: { bsonType: 'date' },
        expiresAt: { bsonType: ['date', 'null'] }
      }
    }
  }
});
targetDb.approval_requests.createIndex({ organizationId: 1, status: 1, createdAt: -1 });
targetDb.approval_requests.createIndex({ organizationId: 1, requestedBy: 1 });

// 12. AUDIT LOGS (TAMPER-EVIDENT COMPLIANCE)
targetDb.createCollection('audit_logs', {
  validator: {
    $jsonSchema: {
      bsonType: 'object',
      required: ['organizationId', 'action', 'resourceType', 'status', 'timestamp'],
      properties: {
        organizationId: { bsonType: 'objectId' },
        userId: { bsonType: ['objectId', 'null'] },
        userEmail: { bsonType: ['string', 'null'] },
        userRole: { bsonType: ['string', 'null'] },
        action: { bsonType: 'string' },
        resourceType: { bsonType: 'string' },
        resourceId: { bsonType: ['string', 'null'] },
        ipAddress: { bsonType: ['string', 'null'] },
        userAgent: { bsonType: ['string', 'null'] },
        status: { enum: ['SUCCESS', 'FAILURE', 'BLOCKED'] },
        details: { bsonType: 'object' },
        timestamp: { bsonType: 'date' }
      }
    }
  }
});
targetDb.audit_logs.createIndex({ organizationId: 1, timestamp: -1 });
targetDb.audit_logs.createIndex({ organizationId: 1, action: 1 });
targetDb.audit_logs.createIndex({ organizationId: 1, userId: 1 });

print(`[MongoDB Init] All 12 collections and compound indexes created successfully in '${dbName}'.`);
