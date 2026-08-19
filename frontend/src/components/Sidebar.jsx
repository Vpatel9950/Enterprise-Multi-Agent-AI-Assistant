import React from "react";
import { useAuth } from "../context/AuthContext";
import { 
  MessageSquare, 
  Users, 
  FileText, 
  Workflow, 
  Share2, 
  BarChart3, 
  ChevronRight,
  Sparkles
} from "lucide-react";

export const Sidebar = ({ activeTab, setActiveTab }) => {
  const { isAdmin } = useAuth();

  const navItems = [
    { id: "chat", label: "Agent Chat Console", icon: MessageSquare, badge: "Live" },
    { id: "agents", label: "Specialized AI Agents", icon: Users, badge: "6 Agents" },
    { id: "knowledge", label: "Knowledge Base (RAG)", icon: FileText, badge: "Docs" },
    { id: "workflows", label: "Workflow Builder", icon: Workflow, badge: "Automated" },
    { id: "integrations", label: "Integrations Hub", icon: Share2, badge: "5 Tools" },
    { id: "admin", label: "Admin Analytics", icon: BarChart3, badge: isAdmin ? "Admin" : "Restricted", adminOnly: true }
  ];

  return (
    <aside style={{
      width: '260px',
      borderRight: '1px solid var(--border-color)',
      background: 'var(--bg-secondary)',
      display: 'flex',
      flexDirection: 'column',
      justifyContent: 'space-between',
      padding: '1.25rem 0.85rem',
      height: 'calc(100vh - 64px)',
      position: 'sticky',
      top: '64px'
    }}>
      <div style={{ display: 'flex', flexDirection: 'column', gap: '0.35rem' }}>
        <div style={{ padding: '0 0.5rem 0.5rem 0.5rem', fontSize: '0.72rem', fontWeight: 700, color: 'var(--text-muted)', textTransform: 'uppercase', letterSpacing: '0.08em' }}>
          Navigation
        </div>

        {navItems.map((item) => {
          const Icon = item.icon;
          const isActive = activeTab === item.id;
          const isDisabled = item.adminOnly && !isAdmin;

          return (
            <button
              key={item.id}
              onClick={() => !isDisabled && setActiveTab(item.id)}
              disabled={isDisabled}
              style={{
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'space-between',
                padding: '0.75rem 0.85rem',
                borderRadius: 'var(--radius-sm)',
                border: isActive ? '1px solid var(--border-glow)' : '1px solid transparent',
                background: isActive ? 'rgba(99, 102, 241, 0.12)' : 'transparent',
                color: isActive ? 'var(--accent-primary)' : isDisabled ? 'var(--text-muted)' : 'var(--text-primary)',
                cursor: isDisabled ? 'not-allowed' : 'pointer',
                transition: 'all 0.2s ease',
                fontWeight: isActive ? 600 : 500,
                fontSize: '0.9rem',
                opacity: isDisabled ? 0.6 : 1
              }}
            >
              <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
                <Icon size={18} color={isActive ? "var(--accent-primary)" : "var(--text-secondary)"} />
                <span>{item.label}</span>
              </div>
              <span className={`badge ${isActive ? 'badge-indigo' : 'badge-cyan'}`} style={{ fontSize: '0.65rem' }}>
                {item.badge}
              </span>
            </button>
          );
        })}
      </div>

      {/* Footer Multi-Agent Card */}
      <div className="glass-card" style={{ padding: '1rem', background: 'var(--gradient-card)', border: '1px solid var(--border-glow)' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', color: 'var(--accent-secondary)', fontSize: '0.82rem', fontWeight: 700, marginBottom: '0.35rem' }}>
          <Sparkles size={16} />
          Multi-Agent Supervisor
        </div>
        <p style={{ fontSize: '0.75rem', color: 'var(--text-secondary)', lineHeight: '1.4' }}>
          Intelligent auto-routing delegates queries across HR, Sales, Tech & Data agents seamlessly.
        </p>
      </div>
    </aside>
  );
};
