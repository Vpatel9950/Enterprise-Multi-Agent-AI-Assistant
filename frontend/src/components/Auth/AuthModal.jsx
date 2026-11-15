import React, { useState } from "react";
import { useAuth } from "../../context/AuthContext";
import { X, Lock, Mail, User as UserIcon, Shield, Sparkles } from "lucide-react";

export const AuthModal = ({ isOpen, onClose }) => {
  const { login, register, switchRole, user } = useAuth();
  const [isRegister, setIsRegister] = useState(false);
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [fullName, setFullName] = useState("");
  const [department, setDepartment] = useState("Engineering");
  const [error, setError] = useState("");

  if (!isOpen) return null;

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError("");
    try {
      if (isRegister) {
        await register({ email, password, full_name: fullName, department, role: "user" });
      } else {
        await login(email, password);
      }
      onClose();
    } catch (err) {
      setError(err.message);
    }
  };

  const handleQuickDemo = (role) => {
    try {
      switchRole(role);
      onClose();
    } catch (err) {
      setError("Demo login failed");
    }
  };

  return (
    <div style={{
      position: 'fixed',
      top: 0,
      left: 0,
      right: 0,
      bottom: 0,
      background: 'rgba(0, 0, 0, 0.75)',
      backdropFilter: 'blur(8px)',
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'center',
      zIndex: 100,
      padding: '1rem'
    }}>
      <div className="glass-card animate-fade-in" style={{
        width: '100%',
        maxWidth: '460px',
        background: 'var(--bg-secondary)',
        padding: '2rem',
        borderRadius: 'var(--radius-lg)',
        position: 'relative',
        boxShadow: 'var(--shadow-md)'
      }}>
        {user && (
          <button 
            onClick={onClose} 
            style={{ position: 'absolute', top: '1.25rem', right: '1.25rem', background: 'none', border: 'none', color: 'var(--text-muted)', cursor: 'pointer' }}
          >
            <X size={20} />
          </button>
        )}

        <div style={{ textAlign: 'center', marginBottom: '1.25rem' }}>
          <div style={{
            width: '48px',
            height: '48px',
            borderRadius: '14px',
            background: 'var(--gradient-primary)',
            display: 'inline-flex',
            alignItems: 'center',
            justifyContent: 'center',
            marginBottom: '0.75rem'
          }}>
            <Shield size={24} color="#fff" />
          </div>
          <h2 style={{ fontSize: '1.4rem', fontWeight: 700 }}>
            {isRegister ? "Create Account" : "Enterprise Sign In"}
          </h2>
          <p style={{ fontSize: '0.85rem', color: 'var(--text-secondary)', marginTop: '0.25rem' }}>
            Access Multi-Agent Platform & AI Assistant Workflows
          </p>
        </div>

        {/* Quick Demo Switcher Banner */}
        <div style={{
          background: 'rgba(99, 102, 241, 0.1)',
          border: '1px dashed var(--border-glow)',
          borderRadius: 'var(--radius-sm)',
          padding: '0.85rem',
          marginBottom: '1.25rem',
          textAlign: 'center'
        }}>
          <div style={{ fontSize: '0.78rem', fontWeight: 700, color: 'var(--accent-primary)', marginBottom: '0.5rem', display: 'flex', alignItems: 'center', justifyContent: 'center', gap: '0.35rem' }}>
            <Sparkles size={15} /> Instant Demo One-Click Sign In
          </div>
          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '0.4rem' }}>
            <button type="button" onClick={() => handleQuickDemo('SUPER_ADMIN')} className="btn-secondary" style={{ fontSize: '0.75rem', justifyContent: 'center', padding: '0.35rem' }}>
              ⚡ Super Admin
            </button>
            <button type="button" onClick={() => handleQuickDemo('ORG_ADMIN')} className="btn-secondary" style={{ fontSize: '0.75rem', justifyContent: 'center', padding: '0.35rem' }}>
              🛡️ Org Admin
            </button>
            <button type="button" onClick={() => handleQuickDemo('MANAGER')} className="btn-secondary" style={{ fontSize: '0.75rem', justifyContent: 'center', padding: '0.35rem' }}>
              👔 Manager
            </button>
            <button type="button" onClick={() => handleQuickDemo('EMPLOYEE')} className="btn-secondary" style={{ fontSize: '0.75rem', justifyContent: 'center', padding: '0.35rem' }}>
              👤 Employee
            </button>
          </div>
        </div>

        {error && (
          <div style={{ background: 'rgba(239, 68, 68, 0.15)', border: '1px solid rgba(239, 68, 68, 0.3)', color: 'var(--accent-danger)', padding: '0.6rem', borderRadius: '6px', fontSize: '0.82rem', marginBottom: '1rem' }}>
            {error}
          </div>
        )}

        <form onSubmit={handleSubmit} style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
          {isRegister && (
            <>
              <div>
                <label style={{ fontSize: '0.8rem', fontWeight: 600, color: 'var(--text-secondary)', display: 'block', marginBottom: '0.35rem' }}>
                  Full Name
                </label>
                <div style={{ position: 'relative' }}>
                  <UserIcon size={16} style={{ position: 'absolute', left: '10px', top: '12px', color: 'var(--text-muted)' }} />
                  <input
                    type="text"
                    required
                    value={fullName}
                    onChange={(e) => setFullName(e.target.value)}
                    placeholder="Sarah Jenkins"
                    style={{ width: '100%', padding: '0.65rem 0.65rem 0.65rem 2.2rem', borderRadius: '8px', background: 'var(--bg-primary)', border: '1px solid var(--border-color)', color: '#fff', fontSize: '0.9rem' }}
                  />
                </div>
              </div>

              <div>
                <label style={{ fontSize: '0.8rem', fontWeight: 600, color: 'var(--text-secondary)', display: 'block', marginBottom: '0.35rem' }}>
                  Department
                </label>
                <input
                  type="text"
                  value={department}
                  onChange={(e) => setDepartment(e.target.value)}
                  placeholder="Engineering / HR / Sales"
                  style={{ width: '100%', padding: '0.65rem', borderRadius: '8px', background: 'var(--bg-primary)', border: '1px solid var(--border-color)', color: '#fff', fontSize: '0.9rem' }}
                />
              </div>
            </>
          )}

          <div>
            <label style={{ fontSize: '0.8rem', fontWeight: 600, color: 'var(--text-secondary)', display: 'block', marginBottom: '0.35rem' }}>
              Work Email
            </label>
            <div style={{ position: 'relative' }}>
              <Mail size={16} style={{ position: 'absolute', left: '10px', top: '12px', color: 'var(--text-muted)' }} />
              <input
                type="email"
                required
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                placeholder="admin@enterprise.ai"
                style={{ width: '100%', padding: '0.65rem 0.65rem 0.65rem 2.2rem', borderRadius: '8px', background: 'var(--bg-primary)', border: '1px solid var(--border-color)', color: '#fff', fontSize: '0.9rem' }}
              />
            </div>
          </div>

          <div>
            <label style={{ fontSize: '0.8rem', fontWeight: 600, color: 'var(--text-secondary)', display: 'block', marginBottom: '0.35rem' }}>
              Password
            </label>
            <div style={{ position: 'relative' }}>
              <Lock size={16} style={{ position: 'absolute', left: '10px', top: '12px', color: 'var(--text-muted)' }} />
              <input
                type="password"
                required
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                placeholder="••••••••••••"
                style={{ width: '100%', padding: '0.65rem 0.65rem 0.65rem 2.2rem', borderRadius: '8px', background: 'var(--bg-primary)', border: '1px solid var(--border-color)', color: '#fff', fontSize: '0.9rem' }}
              />
            </div>
          </div>

          <button type="submit" className="btn-primary" style={{ width: '100%', justifyContent: 'center', marginTop: '0.5rem', padding: '0.75rem' }}>
            {isRegister ? "Register Account" : "Sign In to Platform"}
          </button>
        </form>

        <div style={{ marginTop: '1.25rem', textAlign: 'center', fontSize: '0.82rem', color: 'var(--text-muted)' }}>
          {isRegister ? "Already registered?" : "Need an enterprise account?"}{" "}
          <button
            onClick={() => setIsRegister(!isRegister)}
            style={{ background: 'none', border: 'none', color: 'var(--accent-primary)', cursor: 'pointer', fontWeight: 600, textDecoration: 'underline' }}
          >
            {isRegister ? "Sign In" : "Register now"}
          </button>
        </div>
      </div>
    </div>
  );
};
