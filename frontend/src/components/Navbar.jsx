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
  Database,
  Menu,
  X
} from "lucide-react";

export const Navbar = ({ activeTab, onOpenAuthModal, isMobileMenuOpen, onToggleMobileMenu }) => {
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
      padding: '0 1rem',
      position: 'sticky',
      top: 0,
      zIndex: 50
    }}>
      {/* Brand & Mobile Hamburger */}
      <div style={{ display: 'flex', alignItems: 'center', gap: '0.65rem' }}>
        <button
          onClick={onToggleMobileMenu}
          className="btn-secondary show-on-mobile"
          style={{ padding: '0.4rem', borderRadius: '8px', cursor: 'pointer' }}
          title="Toggle Navigation Menu"
        >
          {isMobileMenuOpen ? <X size={20} /> : <Menu size={20} />}
        </button>

        <div style={{
          width: '36px',
          height: '36px',
          borderRadius: '10px',
          background: 'var(--gradient-primary)',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          boxShadow: 'var(--shadow-glow)',
          flexShrink: 0
        }}>
          <Bot size={20} color="#ffffff" />
        </div>
        <div>
          <h1 style={{ fontSize: '1rem', fontWeight: 700, letterSpacing: '-0.02em', display: 'flex', alignItems: 'center', gap: '0.35rem', margin: 0, whiteSpace: 'nowrap' }}>
            Enterprise <span className="gradient-text">AI</span>
          </h1>
          <span className="hide-on-mobile" style={{ fontSize: '0.7rem', color: 'var(--text-muted)', display: 'flex', alignItems: 'center', gap: '0.35rem' }}>
            <Database size={11} color="var(--accent-success)" />
            MongoDB 7.0 & Multi-Agent Swarm (LangGraph)
          </span>
        </div>
      </div>

      {/* Role Switcher - Desktop Pills & Mobile Dropdown */}
      <div style={{ display: 'flex', alignItems: 'center', gap: '0.35rem' }}>
        {/* Desktop Buttons */}
        <div className="hide-on-mobile" style={{ display: 'flex', alignItems: 'center', gap: '0.35rem', background: 'var(--bg-primary)', padding: '0.2rem 0.4rem', borderRadius: '8px', border: '1px solid var(--border-color)' }}>
          <span style={{ fontSize: '0.68rem', color: 'var(--text-muted)', fontWeight: 600 }}>ROLE:</span>
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
                  padding: '0.25rem 0.55rem',
                  fontSize: '0.72rem',
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

        {/* Mobile Dropdown Select */}
        <div className="show-on-mobile" style={{ alignItems: 'center' }}>
          <select
            value={user?.role || "EMPLOYEE"}
            onChange={(e) => switchRole(e.target.value)}
            style={{
              background: 'var(--bg-primary)',
              color: 'var(--accent-primary)',
              border: '1px solid var(--border-color)',
              padding: '0.3rem 0.5rem',
              borderRadius: '8px',
              fontSize: '0.75rem',
              fontWeight: 700,
              outline: 'none'
            }}
          >
            <option value="SUPER_ADMIN">⚡ Super Admin</option>
            <option value="ORG_ADMIN">🛡️ Org Admin</option>
            <option value="MANAGER">👔 Manager</option>
            <option value="EMPLOYEE">👤 Employee</option>
          </select>
        </div>
      </div>

      {/* User Status & Actions */}
      <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
        <button 
          onClick={toggleTheme} 
          className="btn-secondary hide-on-mobile" 
          style={{ padding: '0.45rem', borderRadius: '8px' }}
          title="Toggle Theme"
        >
          {theme === "dark" ? <Sun size={16} /> : <Moon size={16} />}
        </button>

        {user && (
          <>
            <div className="hide-on-mobile" style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', padding: '0.3rem 0.65rem', background: 'var(--bg-glass)', border: '1px solid var(--border-color)', borderRadius: '8px' }}>
              <ShieldCheck size={15} color="var(--accent-secondary)" />
              <div style={{ textAlign: 'left' }}>
                <div style={{ fontSize: '0.8rem', fontWeight: 600, color: 'var(--text-primary)' }}>{user.fullName}</div>
                <div style={{ fontSize: '0.65rem', color: 'var(--text-muted)' }}>
                  <span className={`badge ${getRoleBadgeClass(user.role)}`} style={{ padding: '0.1rem 0.3rem', fontSize: '0.58rem' }}>
                    {user.role}
                  </span>
                </div>
              </div>
            </div>

            <button
              onClick={logout}
              className="btn-secondary"
              style={{ padding: '0.4rem', borderRadius: '8px', color: '#f87171' }}
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
