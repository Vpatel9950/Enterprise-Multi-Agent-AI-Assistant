import React, { useState, useEffect } from "react";
import { api } from "../../services/api";
import { Share2, Zap, Send, CheckCircle2, RefreshCw, Terminal, Layers } from "lucide-react";

export const IntegrationsManager = () => {
  const [integrations, setIntegrations] = useState([]);
  const [testResult, setTestResult] = useState(null);
  const [testingId, setTestingId] = useState(null);

  useEffect(() => {
    loadIntegrations();
  }, []);

  const loadIntegrations = async () => {
    try {
      const data = await api.getIntegrations();
      setIntegrations(data);
    } catch (err) {
      console.error("Failed to load integrations", err);
    }
  };

  const handleTestIntegration = async (intItem) => {
    setTestingId(intItem.id);
    try {
      const res = await api.testIntegration(intItem.id, {
        channel: "#enterprise-ai-alerts",
        lead_name: "Acme Global Corp ($250k ARR)",
        summary: "Automated Jira issue created from agent diagnostic trace"
      });
      setTestResult({ integration: intItem, response: res });
      loadIntegrations();
    } catch (err) {
      console.error("Failed to test integration", err);
    } finally {
      setTestingId(null);
    }
  };

  const getServiceColor = (type) => {
    switch (type) {
      case "slack": return "#e01e5a";
      case "crm": return "#00a1e0";
      case "erp": return "#0567ad";
      case "email": return "#1a82e2";
      case "jira": return "#0052cc";
      default: return "var(--accent-primary)";
    }
  };

  return (
    <div className="page-container">
      <div className="page-header">
        <div>
          <h2 style={{ fontSize: 'clamp(1.2rem, 3.5vw, 1.5rem)', fontWeight: 700, display: 'flex', alignItems: 'center', gap: '0.6rem' }}>
            <Share2 className="gradient-text" size={26} /> External Enterprise Integrations
          </h2>
          <p style={{ fontSize: '0.85rem', color: 'var(--text-secondary)', marginTop: '0.25rem' }}>
            Connect AI agent actions with external tools: Slack, Salesforce CRM, SAP ERP, SendGrid Email, and Jira.
          </p>
        </div>
        <span className="badge badge-emerald" style={{ padding: '0.5rem 1rem', fontSize: '0.8rem' }}>
          5 Live Connectors Synced
        </span>
      </div>

      {/* Grid of Integrations */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(280px, 1fr))', gap: '1.25rem', marginBottom: '2rem' }}>
        {integrations.map((item) => (
          <div key={item.id} className="glass-card" style={{ padding: '1.5rem', display: 'flex', flexDirection: 'column', justifyContent: 'space-between' }}>
            <div>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: '0.85rem' }}>
                <div>
                  <h3 style={{ fontSize: '1.1rem', fontWeight: 700 }}>{item.name}</h3>
                  <span className="badge badge-cyan" style={{ fontSize: '0.65rem', marginTop: '0.2rem' }}>
                    Type: {item.service_type.toUpperCase()}
                  </span>
                </div>
                <span className="badge badge-emerald" style={{ fontSize: '0.7rem' }}>
                  <CheckCircle2 size={12} /> {item.status}
                </span>
              </div>

              <div style={{ background: 'var(--bg-primary)', padding: '0.75rem', borderRadius: '8px', border: '1px solid var(--border-color)', marginBottom: '1rem', fontSize: '0.78rem' }}>
                <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '0.25rem' }}>
                  <span style={{ color: 'var(--text-muted)' }}>Masked API Key:</span>
                  <span style={{ fontFamily: 'monospace' }}>{item.api_key_masked}</span>
                </div>
                <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '0.25rem' }}>
                  <span style={{ color: 'var(--text-muted)' }}>Webhook Endpoint:</span>
                  <span style={{ color: 'var(--accent-secondary)', whiteSpace: 'nowrap', overflow: 'hidden', textOverflow: 'ellipsis', maxWidth: '160px' }}>
                    {item.webhook_url || "Configured"}
                  </span>
                </div>
              </div>
            </div>

            <button
              onClick={() => handleTestIntegration(item)}
              disabled={testingId === item.id}
              className="btn-primary"
              style={{ width: '100%', justifyContent: 'center', fontSize: '0.85rem' }}
            >
              <Zap size={15} /> {testingId === item.id ? "Dispatching Webhook..." : "Test Webhook Dispatch"}
            </button>
          </div>
        ))}
      </div>

      {/* Webhook Response Tester Log */}
      {testResult && (
        <div className="glass-card" style={{ padding: '1.5rem', border: '1px solid var(--border-glow)' }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1rem' }}>
            <h3 style={{ fontSize: '1.1rem', fontWeight: 700, display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
              <Terminal size={18} color="var(--accent-secondary)" /> Live Webhook Payload Dispatch Log: {testResult.integration.name}
            </h3>
            <button onClick={() => setTestResult(null)} className="btn-secondary" style={{ padding: '0.25rem 0.65rem', fontSize: '0.78rem' }}>
              Close Log
            </button>
          </div>

          <pre style={{ background: '#080c14', padding: '1rem', borderRadius: '8px', fontSize: '0.85rem', color: '#38bdf8', overflowX: 'auto' }}>
            {JSON.stringify(testResult.response, null, 2)}
          </pre>
        </div>
      )}
    </div>
  );
};
