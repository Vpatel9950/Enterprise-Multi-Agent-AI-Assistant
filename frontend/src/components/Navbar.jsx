import React from "react";
import { useAuth } from "../context/AuthContext";
import { 
  Bot, 
  Sun, 
  Moon, 
  LogOut, 
  ShieldCheck, 
  User as UserIcon, 
  ChevronRight,
  Building2,
  Database
} from "lucide-react";

export const Navbar = ({ activeTab, onOpenAuthModal }) => {
  const { user, logout, theme, toggleTheme, switchRole } = useAuth();

  const getRoleBadgeClass = (role) => {
    switch (role) {
      case "SUPER_ADMIN": return "badge-indigo";
      case "ORG_ADMIN": return "badge-cyan";
      case "MANAGER": return "badge-emerald";
      default: return "badge-amber";
    }
  };

  return (
    <header style={{
      height: '64px',
      borderBottom: '1px solid var(--border-color)',
      background: 'var(--bg-secondary)',
      backdropFilter: 'blur(12px)',
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'space-between',
      padding: '0 1.5rem',
      position: 'sticky',
      top: 0,
      zIndex: 40
    }}>
      {/* Brand & Platform Architecture */}
      <div style={{ display: 'flex', alignItems: 'center', gap: '0.85rem' }}>
        <div style={{
          width: '38px',
          height: '38px',
          borderRadius: '10px',
          background: 'var(--gradient-primary)',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          boxShadow: 'var(--shadow-glow)'
        }}>
          <Bot size={22} color="#ffffff" />
        </div>
        <div>
          <h1 style={{ fontSize: '1.1rem', fontWeight: 700, letterSpacing: '-0.02em', display: 'flex', alignItems: 'center', gap: '0.4rem' }}>
            Enterprise <span className="gradient-text">AI Assistant</span>
          </h1>
          <span style={{ fontSize: '0.72rem', color: 'var(--text-muted)', display: 'flex', alignItems: 'center', gap: '0.35rem' }}>
            <Database size={11} color="var(--accent-success)" />
            MongoDB 7.0 & Multi-Agent Swarm (LangGraph)
          </span>
        </div>
      </div>

      {/* Role Switcher Matrix */}
      <div style={{ display: 'flex', alignItems: 'center', gap: '0.4rem', background: 'var(--bg-primary)', padding: '0.25rem', borderRadius: '8px', border: '1px solid var(--border-color)' }}>
        <span style={{ fontSize: '0.7rem', color: 'var(--text-muted)', padding: '0 0.4rem', fontWeight: 600 }}>ROLE:</span>
        {[
          { label: "Super Admin", role: "SUPER_ADMIN" },
          { label: "Org Admin", role: "ORG_ADMIN" },
          { label: "Manager", role: "MANAGER" },
          { label: "Employee", role: "EMPLOYEE" }
        ].map((item) => {
          const isSelected = user?.role === item.role;
          return (
            <button
              key={item.role}
              onClick={() => switchRole(item.role)}
              style={{
                padding: '0.25rem 0.6rem',
                fontSize: '0.74rem',
                borderRadius: '6px',
                border: 'none',
                background: isSelected ? 'var(--accent-primary)' : 'transparent',
                color: isSelected ? '#fff' : 'var(--text-secondary)',
                cursor: 'pointer',
                fontWeight: isSelected ? 700 : 500,
                transition: 'all 0.15s ease'
              }}
            >
              {item.label}
            </button>
          );
        })}
      </div>

      {/* User Status & Actions */}
      <div style={{ display: 'flex', alignItems: 'center', gap: '0.85rem' }}>
        <button 
          onClick={toggleTheme} 
          className="btn-secondary" 
          style={{ padding: '0.45rem', borderRadius: '8px' }}
          title="Toggle Theme"
        >
          {theme === "dark" ? <Sun size={17} /> : <Moon size={17} />}
        </button>

        {user && (
          <>
            <div style={{ display: 'flex', alignItems: 'center', gap: '0.6rem', padding: '0.35rem 0.75rem', background: 'var(--bg-glass)', border: '1px solid var(--border-color)', borderRadius: '8px' }}>
              <ShieldCheck size={16} color="var(--accent-secondary)" />
              <div style={{ textAlign: 'left' }}>
                <div style={{ fontSize: '0.82rem', fontWeight: 600, color: 'var(--text-primary)' }}>{user.fullName}</div>
                <div style={{ fontSize: '0.68rem', color: 'var(--text-muted)', display: 'flex', alignItems: 'center', gap: '0.3rem' }}>
                  <span className={`badge ${getRoleBadgeClass(user.role)}`} style={{ padding: '0.1rem 0.35rem', fontSize: '0.6rem' }}>
                    {user.role}
                  </span>
                  <span>• {user.department || "Enterprise"}</span>
                </div>
              </div>
            </div>

            <button
              onClick={logout}
              className="btn-secondary"
              style={{ padding: '0.45rem', borderRadius: '8px', color: '#f87171' }}
              title="Sign Out / Log Out"
            >
              <LogOut size={16} />
            </button>
          </>
        )}
      </div>
    </header>
  );
};
