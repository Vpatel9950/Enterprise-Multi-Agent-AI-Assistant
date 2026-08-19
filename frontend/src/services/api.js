const API_BASE = "http://127.0.0.1:8000/api";

const getHeaders = () => {
  const token = localStorage.getItem("token");
  return {
    "Content-Type": "application/json",
    ...(token ? { Authorization: `Bearer ${token}` } : {}),
  };
};

export const api = {
  // Auth
  login: async (email, password) => {
    const res = await fetch(`${API_BASE}/auth/login`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ email, password }),
    });
    if (!res.ok) {
      const err = await res.json();
      throw new Error(err.detail || "Login failed");
    }
    return res.json();
  },

  register: async (userData) => {
    const res = await fetch(`${API_BASE}/auth/register`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(userData),
    });
    if (!res.ok) {
      const err = await res.json();
      throw new Error(err.detail || "Registration failed");
    }
    return res.json();
  },

  getMe: async () => {
    const res = await fetch(`${API_BASE}/auth/me`, {
      headers: getHeaders(),
    });
    if (!res.ok) throw new Error("Unauthorized");
    return res.json();
  },

  // Agents
  getAgents: async () => {
    const res = await fetch(`${API_BASE}/agents`, { headers: getHeaders() });
    if (!res.ok) throw new Error("Failed to fetch agents");
    return res.json();
  },

  updateAgent: async (id, data) => {
    const res = await fetch(`${API_BASE}/agents/${id}`, {
      method: "PUT",
      headers: getHeaders(),
      body: JSON.stringify(data),
    });
    if (!res.ok) throw new Error("Failed to update agent");
    return res.json();
  },

  // Chat & Conversations
  getConversations: async () => {
    const res = await fetch(`${API_BASE}/chat/conversations`, { headers: getHeaders() });
    if (!res.ok) throw new Error("Failed to fetch conversations");
    return res.json();
  },

  getConversation: async (id) => {
    const res = await fetch(`${API_BASE}/chat/conversations/${id}`, { headers: getHeaders() });
    if (!res.ok) throw new Error("Failed to fetch conversation detail");
    return res.json();
  },

  createConversation: async (title, agentId) => {
    const res = await fetch(`${API_BASE}/chat/conversations`, {
      method: "POST",
      headers: getHeaders(),
      body: JSON.stringify({ title, agent_id: agentId }),
    });
    if (!res.ok) throw new Error("Failed to create conversation");
    return res.json();
  },

  deleteConversation: async (id) => {
    const res = await fetch(`${API_BASE}/chat/conversations/${id}`, {
      method: "DELETE",
      headers: getHeaders(),
    });
    if (!res.ok) throw new Error("Failed to delete conversation");
    return res.json();
  },

  sendMessage: async (conversationId, agentId, content) => {
    const res = await fetch(`${API_BASE}/chat/send`, {
      method: "POST",
      headers: getHeaders(),
      body: JSON.stringify({
        conversation_id: conversationId,
        agent_id: agentId,
        content,
      }),
    });
    if (!res.ok) throw new Error("Failed to send message");
    return res.json();
  },

  // RAG & Knowledge Documents
  getDocuments: async () => {
    const res = await fetch(`${API_BASE}/rag/documents`, { headers: getHeaders() });
    if (!res.ok) throw new Error("Failed to fetch documents");
    return res.json();
  },

  createDocument: async (docData) => {
    const res = await fetch(`${API_BASE}/rag/documents`, {
      method: "POST",
      headers: getHeaders(),
      body: JSON.stringify(docData),
    });
    if (!res.ok) throw new Error("Failed to add document");
    return res.json();
  },

  deleteDocument: async (id) => {
    const res = await fetch(`${API_BASE}/rag/documents/${id}`, {
      method: "DELETE",
      headers: getHeaders(),
    });
    if (!res.ok) throw new Error("Failed to delete document");
    return res.json();
  },

  searchKnowledge: async (query) => {
    const res = await fetch(`${API_BASE}/rag/search`, {
      method: "POST",
      headers: getHeaders(),
      body: JSON.stringify({ query }),
    });
    if (!res.ok) throw new Error("Failed to search knowledge base");
    return res.json();
  },

  // Workflows
  getWorkflows: async () => {
    const res = await fetch(`${API_BASE}/workflows`, { headers: getHeaders() });
    if (!res.ok) throw new Error("Failed to fetch workflows");
    return res.json();
  },

  createWorkflow: async (wfData) => {
    const res = await fetch(`${API_BASE}/workflows`, {
      method: "POST",
      headers: getHeaders(),
      body: JSON.stringify(wfData),
    });
    if (!res.ok) throw new Error("Failed to create workflow");
    return res.json();
  },

  triggerWorkflow: async (id, payload = {}) => {
    const res = await fetch(`${API_BASE}/workflows/${id}/trigger`, {
      method: "POST",
      headers: getHeaders(),
      body: JSON.stringify(payload),
    });
    if (!res.ok) throw new Error("Failed to trigger workflow");
    return res.json();
  },

  getWorkflowRuns: async (id) => {
    const res = await fetch(`${API_BASE}/workflows/${id}/runs`, { headers: getHeaders() });
    if (!res.ok) throw new Error("Failed to fetch workflow runs");
    return res.json();
  },

  // Integrations
  getIntegrations: async () => {
    const res = await fetch(`${API_BASE}/integrations`, { headers: getHeaders() });
    if (!res.ok) throw new Error("Failed to fetch integrations");
    return res.json();
  },

  testIntegration: async (id, payload = {}) => {
    const res = await fetch(`${API_BASE}/integrations/${id}/test`, {
      method: "POST",
      headers: getHeaders(),
      body: JSON.stringify(payload),
    });
    if (!res.ok) throw new Error("Failed to test integration");
    return res.json();
  },

  // Admin
  getAnalytics: async () => {
    const res = await fetch(`${API_BASE}/admin/analytics`, { headers: getHeaders() });
    if (!res.ok) throw new Error("Failed to fetch admin analytics");
    return res.json();
  },

  getUsers: async () => {
    const res = await fetch(`${API_BASE}/admin/users`, { headers: getHeaders() });
    if (!res.ok) throw new Error("Failed to fetch users");
    return res.json();
  },

  updateUserRole: async (userId, role) => {
    const res = await fetch(`${API_BASE}/admin/users/${userId}/role?role=${role}`, {
      method: "PUT",
      headers: getHeaders(),
    });
    if (!res.ok) throw new Error("Failed to update user role");
    return res.json();
  },

  toggleUserStatus: async (userId, isActive) => {
    const res = await fetch(`${API_BASE}/admin/users/${userId}/status?is_active=${isActive}`, {
      method: "PUT",
      headers: getHeaders(),
    });
    if (!res.ok) throw new Error("Failed to toggle user status");
    return res.json();
  },
};
