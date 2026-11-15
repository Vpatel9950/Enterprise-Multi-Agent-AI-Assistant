import React from "react";
import { useAuth } from "../context/AuthContext";
import { 
  MessageSquare, 
  Users, 
  FileText, 
  Workflow, 
  Share2, 
  BarChart3, 
  CheckSquare,
  Sparkles,
  Layers,
  Database
} from "lucide-react";

export const Sidebar = ({ activeTab, setActiveTab, isMobileMenuOpen }) => {
  const { isManager, isOrgAdmin, isSuperAdmin } = useAuth();

  const navItems = [
    { id: "chat", label: "Multi-Agent Console", icon: MessageSquare, badge: "Live" },
    { id: "agents", label: "Specialized Agents", icon: Users, badge: "7 Swarm" },
    { id: "knowledge", label: "Knowledge Base (RAG)", icon: FileText, badge: "ACL Docs" },
    { id: "approvals", label: "HITL Approvals", icon: CheckSquare, badge: "Human Gate" },
    { id: "workflows", label: "Workflow Engine", icon: Workflow, badge: "Automated" },
    { id: "integrations", label: "Enterprise Connectors", icon: Share2, badge: "5 Tools" },
    { id: "admin", label: "Admin & Audit Center", icon: BarChart3, badge: (isOrgAdmin || isSuperAdmin) ? "Admin" : "Restricted", adminOnly: true }
  ];

  return (
    <aside 
      className={isMobileMenuOpen ? "mobile-drawer" : "hide-on-mobile"}
      style={{
        width: '260px',
        borderRight: '1px solid var(--border-color)',
        background: 'var(--bg-secondary)',
        display: 'flex',
        flexDirection: 'column',
        justifyContent: 'space-between',
        padding: '1.25rem 0.85rem',
        height: 'calc(100vh - 64px)',
        position: 'sticky',
        top: '64px',
        flexShrink: 0,
        zIndex: 40
      }}
    >
      <div style={{ display: 'flex', flexDirection: 'column', gap: '0.35rem' }}>
        <div style={{ padding: '0 0.5rem 0.5rem 0.5rem', fontSize: '0.72rem', fontWeight: 700, color: 'var(--text-muted)', textTransform: 'uppercase', letterSpacing: '0.08em' }}>
          Workspace Navigation
        </div>

        {navItems.map((item) => {
          const Icon = item.icon;
          const isActive = activeTab === item.id;
          const isDisabled = item.adminOnly && !(isOrgAdmin || isSuperAdmin);

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
                fontSize: '0.88rem',
                opacity: isDisabled ? 0.5 : 1
              }}
            >
              <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
                <Icon size={18} color={isActive ? "var(--accent-primary)" : "var(--text-secondary)"} />
                <span>{item.label}</span>
              </div>
              <span className={`badge ${isActive ? 'badge-indigo' : 'badge-cyan'}`} style={{ fontSize: '0.62rem' }}>
                {item.badge}
              </span>
            </button>
          );
        })}
      </div>

      {/* Footer Multi-Agent Architecture Card */}
      <div className="glass-card" style={{ padding: '1rem', background: 'var(--gradient-card)', border: '1px solid var(--border-glow)' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', color: 'var(--accent-secondary)', fontSize: '0.82rem', fontWeight: 700, marginBottom: '0.35rem' }}>
          <Sparkles size={16} />
          LangGraph Agent Swarm
        </div>
        <p style={{ fontSize: '0.74rem', color: 'var(--text-secondary)', lineHeight: '1.4' }}>
          Dynamic DAG task breakdown across RAG, HR, Finance, Dev, Research, DB & Action Agents.
        </p>
      </div>
    </aside>
  );
};
