import React from "react";
import { useAuth } from "../context/AuthContext";
import { 
  Bot, 
  Sun, 
  Moon, 
  LogOut, 
  ShieldCheck, 
  User as UserIcon, 
  Activity,
  ChevronRight
} from "lucide-react";

export const Navbar = ({ activeTab, onOpenAuthModal }) => {
  const { user, logout, theme, toggleTheme, isAdmin, loginAsAdmin, loginAsUser } = useAuth();

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
      {/* Brand & Logo */}
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
          <h1 style={{ fontSize: '1.15rem', fontWeight: 700, letterSpacing: '-0.02em', display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
            Enterprise <span className="gradient-text">AI Assistant</span>
          </h1>
          <span style={{ fontSize: '0.72rem', color: 'var(--text-muted)', display: 'flex', alignItems: 'center', gap: '0.35rem' }}>
            <span style={{ width: '6px', height: '6px', borderRadius: '50%', background: 'var(--accent-success)' }}></span>
            Multi-Agent System Online (v1.0)
          </span>
        </div>
      </div>

      {/* Center Active View Title */}
      <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', fontSize: '0.88rem', color: 'var(--text-secondary)' }}>
        <span>Platform</span>
        <ChevronRight size={14} />
        <span style={{ color: 'var(--text-primary)', fontWeight: 600, textTransform: 'capitalize' }}>
          {activeTab.replace('_', ' ')}
        </span>
      </div>

      {/* Right User Actions & Controls */}
      <div style={{ display: 'flex', alignItems: 'center', gap: '1rem' }}>
        {/* Theme Switcher */}
        <button 
          onClick={toggleTheme} 
          className="btn-secondary" 
          style={{ padding: '0.45rem', borderRadius: '8px' }}
          title="Toggle Theme"
        >
          {theme === "dark" ? <Sun size={18} /> : <Moon size={18} />}
        </button>

        {user ? (
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
            {/* Quick Demo Role Switcher Pill */}
            <div style={{ display: 'flex', gap: '0.35rem', background: 'var(--bg-primary)', padding: '0.2rem', borderRadius: '8px', border: '1px solid var(--border-color)' }}>
              <button 
                onClick={loginAsUser}
                style={{
                  padding: '0.25rem 0.6rem',
                  fontSize: '0.75rem',
                  borderRadius: '6px',
                  border: 'none',
                  background: !isAdmin ? 'var(--accent-primary)' : 'transparent',
                  color: !isAdmin ? '#fff' : 'var(--text-secondary)',
                  cursor: 'pointer',
                  fontWeight: 600
                }}
              >
                User View
              </button>
              <button 
                onClick={loginAsAdmin}
                style={{
                  padding: '0.25rem 0.6rem',
                  fontSize: '0.75rem',
                  borderRadius: '6px',
                  border: 'none',
                  background: isAdmin ? 'var(--accent-primary)' : 'transparent',
                  color: isAdmin ? '#fff' : 'var(--text-secondary)',
                  cursor: 'pointer',
                  fontWeight: 600
                }}
              >
                Admin View
              </button>
            </div>

            {/* Profile Info */}
            <div style={{ display: 'flex', alignItems: 'center', gap: '0.6rem', padding: '0.35rem 0.75rem', background: 'var(--bg-glass)', border: '1px solid var(--border-color)', borderRadius: '8px' }}>
              {isAdmin ? <ShieldCheck size={16} color="#818cf8" /> : <UserIcon size={16} color="#38bdf8" />}
              <div style={{ textAlign: 'left' }}>
                <div style={{ fontSize: '0.82rem', fontWeight: 600, color: 'var(--text-primary)' }}>{user.full_name}</div>
                <div style={{ fontSize: '0.7rem', color: 'var(--text-muted)' }}>
                  {isAdmin ? "System Administrator" : user.department || "Enterprise User"}
                </div>
              </div>
            </div>

            <button 
              onClick={logout} 
              className="btn-danger" 
              style={{ padding: '0.45rem 0.75rem', fontSize: '0.8rem', display: 'flex', alignItems: 'center', gap: '0.35rem' }}
            >
              <LogOut size={15} />
              Logout
            </button>
          </div>
        ) : (
          <button onClick={onOpenAuthModal} className="btn-primary">
            Sign In / Register
          </button>
        )}
      </div>
    </header>
  );
};
