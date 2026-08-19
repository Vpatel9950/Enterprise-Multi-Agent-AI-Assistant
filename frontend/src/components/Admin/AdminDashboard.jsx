import React, { useState, useEffect } from "react";
import { api } from "../../services/api";
import { useAuth } from "../../context/AuthContext";
import { 
  BarChart3, 
  Users, 
  MessageSquare, 
  Zap, 
  ShieldCheck, 
  Activity, 
  Cpu, 
  Smile, 
  UserCheck, 
  UserX,
  Lock
} from "lucide-react";

export const AdminDashboard = () => {
  const { isAdmin } = useAuth();
  const [analytics, setAnalytics] = useState(null);
  const [users, setUsers] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (isAdmin) {
      loadData();
    }
  }, [isAdmin]);

  const loadData = async () => {
    setLoading(true);
    try {
      const [anData, uData] = await Promise.all([
        api.getAnalytics(),
        api.getUsers(),
      ]);
      setAnalytics(anData);
      setUsers(uData);
    } catch (err) {
      console.error("Failed to load admin dashboard data", err);
    } finally {
      setLoading(false);
    }
  };

  const handleRoleChange = async (userId, newRole) => {
    try {
      await api.updateUserRole(userId, newRole);
      loadData();
    } catch (err) {
      console.error("Failed to update role", err);
    }
  };

  const handleStatusToggle = async (userId, currentStatus) => {
    try {
      await api.toggleUserStatus(userId, !currentStatus);
      loadData();
    } catch (err) {
      console.error("Failed to toggle user status", err);
    }
  };

  if (!isAdmin) {
    return (
      <div style={{ padding: '3rem', textAlign: 'center', margin: 'auto' }}>
        <div style={{ width: '60px', height: '60px', borderRadius: '18px', background: 'rgba(239, 68, 68, 0.15)', display: 'inline-flex', alignItems: 'center', justifyContent: 'center', marginBottom: '1rem' }}>
          <Lock size={30} color="var(--accent-danger)" />
        </div>
        <h2 style={{ fontSize: '1.4rem', fontWeight: 700, marginBottom: '0.5rem' }}>Administrator Access Required</h2>
        <p style={{ color: 'var(--text-secondary)', fontSize: '0.9rem', marginBottom: '1.5rem' }}>
          You must be logged in as an Administrator to view executive system analytics and modify user roles.
        </p>
        <div style={{ display: 'inline-block' }}>
          <span className="badge badge-indigo">Use the top Navbar 'Admin View' button to switch instantly</span>
        </div>
      </div>
    );
  }

  if (loading) {
    return (
      <div style={{ padding: '3rem', textAlign: 'center' }}>
        <Activity size={32} className="pulse-glow" color="var(--accent-primary)" />
        <p style={{ marginTop: '1rem', color: 'var(--text-secondary)' }}>Loading Enterprise Analytics Telemetry...</p>
      </div>
    );
  }

  return (
    <div style={{ padding: '2rem', flex: 1, overflowY: 'auto' }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1.5rem' }}>
        <div>
          <h2 style={{ fontSize: '1.5rem', fontWeight: 700, display: 'flex', alignItems: 'center', gap: '0.6rem' }}>
            <BarChart3 className="gradient-text" size={26} /> Admin Operations & Telemetry Dashboard
          </h2>
          <p style={{ fontSize: '0.88rem', color: 'var(--text-secondary)', marginTop: '0.25rem' }}>
            Monitor real-time system performance, multi-agent usage metrics, and user access control (RBAC).
          </p>
        </div>
        <button onClick={loadData} className="btn-secondary" style={{ fontSize: '0.8rem' }}>
          Refresh Metrics
        </button>
      </div>

      {/* KPI Stats Grid */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(220px, 1fr))', gap: '1rem', marginBottom: '2rem' }}>
        <div className="glass-card" style={{ padding: '1.25rem' }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', color: 'var(--text-muted)', fontSize: '0.8rem', fontWeight: 600, marginBottom: '0.5rem' }}>
            TOTAL CONVERSATIONS
            <MessageSquare size={16} color="var(--accent-primary)" />
          </div>
          <div style={{ fontSize: '1.8rem', fontWeight: 800 }}>{analytics?.total_conversations || 0}</div>
          <div style={{ fontSize: '0.75rem', color: 'var(--accent-success)', marginTop: '0.2rem' }}>
            +18% from last week
          </div>
        </div>

        <div className="glass-card" style={{ padding: '1.25rem' }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', color: 'var(--text-muted)', fontSize: '0.8rem', fontWeight: 600, marginBottom: '0.5rem' }}>
            ACTIVE AGENTS
            <Cpu size={16} color="var(--accent-secondary)" />
          </div>
          <div style={{ fontSize: '1.8rem', fontWeight: 800 }}>{analytics?.active_agents_count || 6}</div>
          <div style={{ fontSize: '0.75rem', color: 'var(--text-secondary)', marginTop: '0.2rem' }}>
            All specialized agents operational
          </div>
        </div>

        <div className="glass-card" style={{ padding: '1.25rem' }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', color: 'var(--text-muted)', fontSize: '0.8rem', fontWeight: 600, marginBottom: '0.5rem' }}>
            AVG RESPONSE LATENCY
            <Zap size={16} color="var(--accent-warning)" />
          </div>
          <div style={{ fontSize: '1.8rem', fontWeight: 800 }}>{analytics?.avg_response_time_ms || 240}ms</div>
          <div style={{ fontSize: '0.75rem', color: 'var(--accent-success)', marginTop: '0.2rem' }}>
            Optimized memory caching
          </div>
        </div>

        <div className="glass-card" style={{ padding: '1.25rem' }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', color: 'var(--text-muted)', fontSize: '0.8rem', fontWeight: 600, marginBottom: '0.5rem' }}>
            SATISFACTION RATING
            <Smile size={16} color="var(--accent-success)" />
          </div>
          <div style={{ fontSize: '1.8rem', fontWeight: 800 }}>{analytics?.avg_satisfaction || 4.9} / 5.0</div>
          <div style={{ fontSize: '0.75rem', color: 'var(--text-secondary)', marginTop: '0.2rem' }}>
            Based on enterprise user feedback
          </div>
        </div>
      </div>

      {/* Agent Performance Ranking & Telemetry Feed Grid */}
      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1.25rem', marginBottom: '2rem' }}>
        <div className="glass-card" style={{ padding: '1.5rem' }}>
          <h3 style={{ fontSize: '1.1rem', fontWeight: 700, marginBottom: '1rem' }}>Top Active AI Agents</h3>
          <div style={{ display: 'flex', flexDirection: 'column', gap: '0.75rem' }}>
            {analytics?.top_agents?.map((agent, idx) => (
              <div key={agent.id} style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', padding: '0.65rem', background: 'var(--bg-primary)', borderRadius: '8px', border: '1px solid var(--border-color)' }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: '0.6rem' }}>
                  <span style={{ fontSize: '0.8rem', fontWeight: 700, color: 'var(--text-muted)', width: '20px' }}>#{idx+1}</span>
                  <div>
                    <div style={{ fontSize: '0.88rem', fontWeight: 600 }}>{agent.name}</div>
                    <div style={{ fontSize: '0.72rem', color: 'var(--text-muted)' }}>Code: {agent.code}</div>
                  </div>
                </div>
                <span className="badge badge-indigo">{agent.query_count} queries processed</span>
              </div>
            ))}
          </div>
        </div>

        <div className="glass-card" style={{ padding: '1.5rem' }}>
          <h3 style={{ fontSize: '1.1rem', fontWeight: 700, marginBottom: '1rem' }}>Recent System Analytics Events</h3>
          <div style={{ display: 'flex', flexDirection: 'column', gap: '0.65rem', maxHeight: '260px', overflowY: 'auto' }}>
            {analytics?.recent_events?.map((ev) => (
              <div key={ev.id} style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', fontSize: '0.8rem', padding: '0.5rem 0.75rem', background: 'var(--bg-primary)', borderRadius: '6px', border: '1px solid var(--border-color)' }}>
                <div>
                  <span style={{ fontWeight: 600, color: 'var(--accent-secondary)' }}>{ev.action_type}</span>
                  <span style={{ color: 'var(--text-muted)', marginLeft: '0.5rem' }}>({ev.timestamp})</span>
                </div>
                <div>
                  <span style={{ color: 'var(--text-muted)', marginRight: '0.5rem' }}>{ev.response_time_ms}ms</span>
                  <span className="badge badge-emerald" style={{ fontSize: '0.65rem' }}>{ev.tokens_used} tokens</span>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* User Management & Role-Based Access Control (RBAC) Table */}
      <div className="glass-card" style={{ padding: '1.5rem' }}>
        <h3 style={{ fontSize: '1.1rem', fontWeight: 700, marginBottom: '1rem', display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
          <Users size={18} color="var(--accent-primary)" /> User Management & RBAC Controls
        </h3>

        <div style={{ overflowX: 'auto' }}>
          <table style={{ width: '100%', borderCollapse: 'collapse' }}>
            <thead>
              <tr style={{ borderBottom: '1px solid var(--border-color)', textTransform: 'uppercase', fontSize: '0.75rem', color: 'var(--text-muted)' }}>
                <th style={{ padding: '0.75rem', textAlign: 'left' }}>User</th>
                <th style={{ padding: '0.75rem', textAlign: 'left' }}>Department</th>
                <th style={{ padding: '0.75rem', textAlign: 'left' }}>Current Role</th>
                <th style={{ padding: '0.75rem', textAlign: 'left' }}>Account Status</th>
                <th style={{ padding: '0.75rem', textAlign: 'right' }}>Role Action</th>
              </tr>
            </thead>
            <tbody>
              {users.map((u) => (
                <tr key={u.id} style={{ borderBottom: '1px solid var(--border-color)', fontSize: '0.88rem' }}>
                  <td style={{ padding: '0.75rem' }}>
                    <div style={{ fontWeight: 600 }}>{u.full_name}</div>
                    <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>{u.email}</div>
                  </td>
                  <td style={{ padding: '0.75rem', color: 'var(--text-secondary)' }}>{u.department}</td>
                  <td style={{ padding: '0.75rem' }}>
                    <span className={`badge ${u.role === 'admin' ? 'badge-indigo' : 'badge-cyan'}`}>
                      {u.role.toUpperCase()}
                    </span>
                  </td>
                  <td style={{ padding: '0.75rem' }}>
                    <span className={`badge ${u.is_active ? 'badge-emerald' : 'badge-amber'}`}>
                      {u.is_active ? "Active" : "Deactivated"}
                    </span>
                  </td>
                  <td style={{ padding: '0.75rem', textAlign: 'right' }}>
                    <div style={{ display: 'flex', gap: '0.35rem', justifyContent: 'flex-end' }}>
                      <button
                        onClick={() => handleRoleChange(u.id, u.role === 'admin' ? 'user' : 'admin')}
                        className="btn-secondary"
                        style={{ padding: '0.25rem 0.55rem', fontSize: '0.75rem' }}
                      >
                        Set as {u.role === 'admin' ? 'User' : 'Admin'}
                      </button>
                      <button
                        onClick={() => handleStatusToggle(u.id, u.is_active)}
                        className="btn-danger"
                        style={{ padding: '0.25rem 0.55rem', fontSize: '0.75rem' }}
                      >
                        {u.is_active ? "Deactivate" : "Activate"}
                      </button>
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
};
