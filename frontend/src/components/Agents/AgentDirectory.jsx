import React, { useState, useEffect } from "react";
import { api } from "../../services/api";
import { useAuth } from "../../context/AuthContext";
import { Users, Edit3, CheckCircle, Sliders, Shield, Terminal, Zap } from "lucide-react";

export const AgentDirectory = () => {
  const { isAdmin } = useAuth();
  const [agents, setAgents] = useState([]);
  const [editingAgent, setEditingAgent] = useState(null);
  const [editPrompt, setEditPrompt] = useState("");
  const [editTemp, setEditTemp] = useState(0.7);

  useEffect(() => {
    loadAgents();
  }, []);

  const loadAgents = async () => {
    try {
      const data = await api.getAgents();
      setAgents(data);
    } catch (err) {
      console.error("Failed to load agents", err);
    }
  };

  const handleOpenEdit = (agent) => {
    setEditingAgent(agent);
    setEditPrompt(agent.system_prompt);
    setEditTemp(agent.temperature);
  };

  const handleSaveAgent = async (e) => {
    e.preventDefault();
    try {
      await api.updateAgent(editingAgent.id, {
        system_prompt: editPrompt,
        temperature: parseFloat(editTemp),
      });
      setEditingAgent(null);
      loadAgents();
    } catch (err) {
      console.error("Failed to save agent", err);
    }
  };

  return (
    <div style={{ padding: '2rem', flex: 1, overflowY: 'auto' }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1.5rem' }}>
        <div>
          <h2 style={{ fontSize: '1.5rem', fontWeight: 700, display: 'flex', alignItems: 'center', gap: '0.6rem' }}>
            <Users className="gradient-text" size={26} /> Specialized AI Agents Directory
          </h2>
          <p style={{ fontSize: '0.88rem', color: 'var(--text-secondary)', marginTop: '0.25rem' }}>
            Configure agent personas, system prompts, operational tools, and temperature settings.
          </p>
        </div>
        <span className="badge badge-indigo" style={{ padding: '0.5rem 1rem', fontSize: '0.8rem' }}>
          {agents.length} Enterprise Agents Configured
        </span>
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(340px, 1fr))', gap: '1.25rem' }}>
        {agents.map((agent) => (
          <div
            key={agent.id}
            className="glass-card"
            style={{
              padding: '1.5rem',
              display: 'flex',
              flexDirection: 'column',
              justifyContent: 'space-between',
              position: 'relative'
            }}
          >
            <div>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: '0.85rem' }}>
                <div>
                  <h3 style={{ fontSize: '1.1rem', fontWeight: 700, color: 'var(--text-primary)' }}>{agent.name}</h3>
                  <span className="badge badge-cyan" style={{ fontSize: '0.65rem', marginTop: '0.2rem' }}>
                    Code: {agent.code}
                  </span>
                </div>
                <span className={`badge ${agent.is_active ? 'badge-emerald' : 'badge-amber'}`}>
                  {agent.is_active ? "Active" : "Inactive"}
                </span>
              </div>

              <p style={{ fontSize: '0.85rem', color: 'var(--text-secondary)', lineHeight: '1.5', marginBottom: '1rem' }}>
                {agent.role_description}
              </p>

              {/* Specs & Capabilities Box */}
              <div style={{ background: 'var(--bg-primary)', padding: '0.75rem', borderRadius: '8px', border: '1px solid var(--border-color)', marginBottom: '1rem', fontSize: '0.78rem' }}>
                <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '0.35rem' }}>
                  <span style={{ color: 'var(--text-muted)' }}>Model Architecture:</span>
                  <span style={{ fontWeight: 600, color: 'var(--accent-primary)' }}>{agent.model_name}</span>
                </div>
                <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '0.35rem' }}>
                  <span style={{ color: 'var(--text-muted)' }}>Temperature:</span>
                  <span style={{ fontWeight: 600 }}>{agent.temperature}</span>
                </div>
                <div style={{ marginTop: '0.5rem' }}>
                  <span style={{ color: 'var(--text-muted)', display: 'block', marginBottom: '0.25rem' }}>Enabled Tools:</span>
                  <div style={{ display: 'flex', flexWrap: 'wrap', gap: '0.35rem' }}>
                    {Array.isArray(agent.tools_enabled) && agent.tools_enabled.length > 0 ? (
                      agent.tools_enabled.map((t, i) => (
                        <span key={i} style={{ padding: '0.15rem 0.45rem', background: 'var(--bg-glass)', borderRadius: '4px', border: '1px solid var(--border-color)', fontSize: '0.7rem' }}>
                          ⚡ {t}
                        </span>
                      ))
                    ) : (
                      <span style={{ color: 'var(--text-muted)' }}>Standard reasoning</span>
                    )}
                  </div>
                </div>
              </div>
            </div>

            {isAdmin && (
              <button onClick={() => handleOpenEdit(agent)} className="btn-secondary" style={{ width: '100%', justifyContent: 'center', fontSize: '0.85rem' }}>
                <Edit3 size={15} /> Configure Agent Prompt & Rules
              </button>
            )}
          </div>
        ))}
      </div>

      {/* Edit Agent Modal */}
      {editingAgent && (
        <div style={{
          position: 'fixed',
          top: 0, left: 0, right: 0, bottom: 0,
          background: 'rgba(0, 0, 0, 0.75)',
          backdropFilter: 'blur(8px)',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          zIndex: 100,
          padding: '1rem'
        }}>
          <div className="glass-card animate-fade-in" style={{ width: '100%', maxWidth: '520px', padding: '1.75rem', background: 'var(--bg-secondary)' }}>
            <h3 style={{ fontSize: '1.25rem', fontWeight: 700, marginBottom: '1rem' }}>
              Edit Agent: {editingAgent.name}
            </h3>
            <form onSubmit={handleSaveAgent} style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
              <div>
                <label style={{ fontSize: '0.8rem', fontWeight: 600, color: 'var(--text-secondary)', display: 'block', marginBottom: '0.35rem' }}>
                  System Persona Prompt
                </label>
                <textarea
                  rows={5}
                  value={editPrompt}
                  onChange={(e) => setEditPrompt(e.target.value)}
                  style={{ width: '100%', padding: '0.75rem', borderRadius: '8px', background: 'var(--bg-primary)', border: '1px solid var(--border-color)', color: '#fff', fontSize: '0.85rem' }}
                />
              </div>

              <div>
                <label style={{ fontSize: '0.8rem', fontWeight: 600, color: 'var(--text-secondary)', display: 'block', marginBottom: '0.35rem' }}>
                  Temperature ({editTemp})
                </label>
                <input
                  type="range"
                  min="0.0"
                  max="1.0"
                  step="0.1"
                  value={editTemp}
                  onChange={(e) => setEditTemp(e.target.value)}
                  style={{ width: '100%' }}
                />
              </div>

              <div style={{ display: 'flex', gap: '0.75rem', marginTop: '0.5rem' }}>
                <button type="button" onClick={() => setEditingAgent(null)} className="btn-secondary" style={{ flex: 1, justifyContent: 'center' }}>
                  Cancel
                </button>
                <button type="submit" className="btn-primary" style={{ flex: 1, justifyContent: 'center' }}>
                  Save Configuration
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
};
