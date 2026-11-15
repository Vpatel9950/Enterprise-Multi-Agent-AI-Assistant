import React, { useState, useEffect } from "react";
import { api } from "../../services/api";
import { useAuth } from "../../context/AuthContext";
import { Workflow, Play, Plus, Clock, CheckCircle2, AlertCircle, FileCode } from "lucide-react";

export const WorkflowBuilder = () => {
  const { isAdmin } = useAuth();
  const [workflows, setWorkflows] = useState([]);
  const [agents, setAgents] = useState([]);
  const [selectedWorkflowRuns, setSelectedWorkflowRuns] = useState(null);
  const [showCreateModal, setShowCreateModal] = useState(false);

  // Form state
  const [name, setName] = useState("");
  const [description, setDescription] = useState("");
  const [triggerType, setTriggerType] = useState("on_ticket_created");
  const [targetAgentId, setTargetAgentId] = useState("");
  const [runningId, setRunningId] = useState(null);

  useEffect(() => {
    loadWorkflows();
    loadAgents();
  }, []);

  const loadWorkflows = async () => {
    try {
      const data = await api.getWorkflows();
      setWorkflows(data);
    } catch (err) {
      console.error("Failed to load workflows", err);
    }
  };

  const loadAgents = async () => {
    try {
      const data = await api.getAgents();
      setAgents(data);
      if (data.length > 0) setTargetAgentId(data[0].id);
    } catch (err) {
      console.error("Failed to load agents", err);
    }
  };

  const handleTriggerManual = async (wf) => {
    setRunningId(wf.id);
    try {
      await api.triggerWorkflow(wf.id, { source: "Manual UI Trigger" });
      await loadWorkflows();
      const runs = await api.getWorkflowRuns(wf.id);
      setSelectedWorkflowRuns({ workflow: wf, runs });
    } catch (err) {
      console.error("Failed to trigger workflow", err);
    } finally {
      setRunningId(null);
    }
  };

  const handleViewRuns = async (wf) => {
    try {
      const runs = await api.getWorkflowRuns(wf.id);
      setSelectedWorkflowRuns({ workflow: wf, runs });
    } catch (err) {
      console.error("Failed to load runs", err);
    }
  };

  const handleCreateWorkflow = async (e) => {
    e.preventDefault();
    try {
      await api.createWorkflow({
        name,
        description,
        trigger_type: triggerType,
        target_agent_id: parseInt(targetAgentId),
        config_json: JSON.stringify({ target_service: "slack", action_type: "auto_escalate" })
      });
      setShowCreateModal(false);
      setName("");
      setDescription("");
      loadWorkflows();
    } catch (err) {
      console.error("Failed to create workflow", err);
    }
  };

  return (
    <div className="page-container">
      <div className="page-header">
        <div>
          <h2 style={{ fontSize: 'clamp(1.2rem, 3.5vw, 1.5rem)', fontWeight: 700, display: 'flex', alignItems: 'center', gap: '0.6rem' }}>
            <Workflow className="gradient-text" size={26} /> Workflow Automation Engine
          </h2>
          <p style={{ fontSize: '0.85rem', color: 'var(--text-secondary)', marginTop: '0.25rem' }}>
            Define business rules that trigger AI agent reasoning pipelines and external tool actions automatically.
          </p>
        </div>
        {isAdmin && (
          <button onClick={() => setShowCreateModal(true)} className="btn-primary">
            <Plus size={16} /> Create Automation Rule
          </button>
        )}
      </div>

      {/* Workflow Cards */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(280px, 1fr))', gap: '1.25rem', marginBottom: '2rem' }}>
        {workflows.map((wf) => (
          <div key={wf.id} className="glass-card" style={{ padding: '1.5rem', display: 'flex', flexDirection: 'column', justifyContent: 'space-between' }}>
            <div>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: '0.75rem' }}>
                <h3 style={{ fontSize: '1.1rem', fontWeight: 700 }}>{wf.name}</h3>
                <span className="badge badge-emerald">{wf.status}</span>
              </div>
              <p style={{ fontSize: '0.85rem', color: 'var(--text-secondary)', marginBottom: '1rem', lineHeight: '1.4' }}>
                {wf.description}
              </p>

              <div style={{ background: 'var(--bg-primary)', padding: '0.75rem', borderRadius: '8px', border: '1px solid var(--border-color)', marginBottom: '1rem', fontSize: '0.78rem' }}>
                <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '0.25rem' }}>
                  <span style={{ color: 'var(--text-muted)' }}>Trigger Event:</span>
                  <span style={{ fontWeight: 600, color: 'var(--accent-secondary)' }}>{wf.trigger_type}</span>
                </div>
                <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '0.25rem' }}>
                  <span style={{ color: 'var(--text-muted)' }}>Total Run Count:</span>
                  <span style={{ fontWeight: 600 }}>{wf.run_count} runs</span>
                </div>
              </div>
            </div>

            <div style={{ display: 'flex', gap: '0.5rem' }}>
              <button
                onClick={() => handleTriggerManual(wf)}
                disabled={runningId === wf.id}
                className="btn-primary"
                style={{ flex: 1, justifyContent: 'center', fontSize: '0.82rem' }}
              >
                <Play size={14} /> {runningId === wf.id ? "Running..." : "Test Run"}
              </button>
              <button onClick={() => handleViewRuns(wf)} className="btn-secondary" style={{ fontSize: '0.82rem' }}>
                <Clock size={14} /> Logs ({wf.run_count})
              </button>
            </div>
          </div>
        ))}
      </div>

      {/* Execution Audit Log View */}
      {selectedWorkflowRuns && (
        <div className="glass-card" style={{ padding: '1.5rem', border: '1px solid var(--border-glow)' }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1rem' }}>
            <h3 style={{ fontSize: '1.1rem', fontWeight: 700, display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
              <FileCode size={18} color="var(--accent-primary)" /> Execution Run Logs: {selectedWorkflowRuns.workflow.name}
            </h3>
            <button onClick={() => setSelectedWorkflowRuns(null)} className="btn-secondary" style={{ padding: '0.25rem 0.65rem', fontSize: '0.78rem' }}>
              Close Logs
            </button>
          </div>

          <div style={{ display: 'flex', flexDirection: 'column', gap: '0.75rem', maxHeight: '320px', overflowY: 'auto' }}>
            {selectedWorkflowRuns.runs.length === 0 ? (
              <p style={{ color: 'var(--text-muted)', fontSize: '0.85rem' }}>No execution runs recorded yet.</p>
            ) : (
              selectedWorkflowRuns.runs.map((run) => (
                <div key={run.id} style={{ padding: '0.85rem', background: 'var(--bg-primary)', borderRadius: '8px', border: '1px solid var(--border-color)' }}>
                  <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '0.5rem', fontSize: '0.8rem' }}>
                    <span style={{ fontWeight: 600, display: 'flex', alignItems: 'center', gap: '0.35rem' }}>
                      <CheckCircle2 size={14} color="var(--accent-success)" /> Run #{run.id} Status: {run.status.toUpperCase()}
                    </span>
                    <span style={{ color: 'var(--text-muted)' }}>Duration: {run.duration_ms}ms</span>
                  </div>
                  <pre style={{ background: '#080c14', padding: '0.65rem', borderRadius: '6px', fontSize: '0.78rem', color: '#38bdf8', overflowX: 'auto' }}>
                    {run.output_log}
                  </pre>
                </div>
              ))
            )}
          </div>
        </div>
      )}

      {/* Create Workflow Modal */}
      {showCreateModal && (
        <div style={{
          position: 'fixed', top: 0, left: 0, right: 0, bottom: 0,
          background: 'rgba(0,0,0,0.75)', backdropFilter: 'blur(8px)',
          display: 'flex', alignItems: 'center', justifyContent: 'center', zIndex: 100
        }}>
          <div className="glass-card animate-fade-in" style={{ width: '100%', maxWidth: '500px', padding: '1.75rem', background: 'var(--bg-secondary)' }}>
            <h3 style={{ fontSize: '1.25rem', fontWeight: 700, marginBottom: '1rem' }}>Create Workflow Automation</h3>
            <form onSubmit={handleCreateWorkflow} style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
              <div>
                <label style={{ fontSize: '0.8rem', fontWeight: 600, color: 'var(--text-secondary)', display: 'block', marginBottom: '0.35rem' }}>Workflow Title</label>
                <input type="text" required value={name} onChange={(e) => setName(e.target.value)} placeholder="e.g. Daily Executive Sales Digest" style={{ width: '100%', padding: '0.65rem', borderRadius: '8px', background: 'var(--bg-primary)', border: '1px solid var(--border-color)', color: '#fff', fontSize: '0.9rem' }} />
              </div>
              <div>
                <label style={{ fontSize: '0.8rem', fontWeight: 600, color: 'var(--text-secondary)', display: 'block', marginBottom: '0.35rem' }}>Description</label>
                <input type="text" required value={description} onChange={(e) => setDescription(e.target.value)} placeholder="Summary of trigger & delegation flow" style={{ width: '100%', padding: '0.65rem', borderRadius: '8px', background: 'var(--bg-primary)', border: '1px solid var(--border-color)', color: '#fff', fontSize: '0.9rem' }} />
              </div>
              <div>
                <label style={{ fontSize: '0.8rem', fontWeight: 600, color: 'var(--text-secondary)', display: 'block', marginBottom: '0.35rem' }}>Trigger Type</label>
                <select value={triggerType} onChange={(e) => setTriggerType(e.target.value)} style={{ width: '100%', padding: '0.65rem', borderRadius: '8px', background: 'var(--bg-primary)', border: '1px solid var(--border-color)', color: '#fff', fontSize: '0.9rem' }}>
                  <option value="on_ticket_created">On High-Priority Ticket Created</option>
                  <option value="on_lead_received">On Inbound Enterprise Lead Received</option>
                  <option value="scheduled_daily">Scheduled Daily at 09:00 AM</option>
                </select>
              </div>
              <div>
                <label style={{ fontSize: '0.8rem', fontWeight: 600, color: 'var(--text-secondary)', display: 'block', marginBottom: '0.35rem' }}>Assigned Target AI Agent</label>
                <select value={targetAgentId} onChange={(e) => setTargetAgentId(e.target.value)} style={{ width: '100%', padding: '0.65rem', borderRadius: '8px', background: 'var(--bg-primary)', border: '1px solid var(--border-color)', color: '#fff', fontSize: '0.9rem' }}>
                  {agents.map((a) => (
                    <option key={a.id} value={a.id}>{a.name}</option>
                  ))}
                </select>
              </div>
              <div style={{ display: 'flex', gap: '0.75rem', marginTop: '0.5rem' }}>
                <button type="button" onClick={() => setShowCreateModal(false)} className="btn-secondary" style={{ flex: 1, justifyContent: 'center' }}>Cancel</button>
                <button type="submit" className="btn-primary" style={{ flex: 1, justifyContent: 'center' }}>Save Workflow Rule</button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
};
