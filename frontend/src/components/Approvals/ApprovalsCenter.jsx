import React, { useState, useEffect } from "react";
import { api } from "../../services/api";
import { useAuth } from "../../context/AuthContext";
import { 
  CheckSquare, 
  ShieldAlert, 
  CheckCircle2, 
  XCircle, 
  Clock, 
  Terminal, 
  AlertTriangle,
  User,
  ExternalLink
} from "lucide-react";

export const ApprovalsCenter = () => {
  const { user, isManager, isOrgAdmin, isSuperAdmin } = useAuth();
  const [approvals, setApprovals] = useState([]);
  const [loading, setLoading] = useState(true);
  const [resolvingId, setResolvingId] = useState(null);
  const [reviewNotes, setReviewNotes] = useState({});

  useEffect(() => {
    loadApprovals();
  }, [user]);

  const loadApprovals = async () => {
    setLoading(true);
    try {
      const data = await api.getApprovals();
      setApprovals(data);
    } catch (err) {
      console.error("Failed to load approvals", err);
    } finally {
      setLoading(false);
    }
  };

  const handleDecision = async (approvalId, decision) => {
    setResolvingId(approvalId);
    try {
      const notes = reviewNotes[approvalId] || `Marked as ${decision} by ${user.fullName}`;
      await api.submitApprovalDecision(approvalId, decision, notes);
      await loadApprovals();
    } catch (err) {
      alert("Approval resolution failed: " + err.message);
    } finally {
      setResolvingId(null);
    }
  };

  const getRiskBadge = (risk) => {
    switch (risk) {
      case "CRITICAL": return <span className="badge" style={{ background: 'rgba(239,68,68,0.2)', color: '#ef4444', border: '1px solid #ef4444' }}>CRITICAL RISK</span>;
      case "HIGH": return <span className="badge badge-amber">HIGH RISK</span>;
      case "MEDIUM": return <span className="badge badge-cyan">MEDIUM RISK</span>;
      default: return <span className="badge badge-emerald">LOW RISK</span>;
    }
  };

  const getStatusBadge = (status) => {
    switch (status) {
      case "APPROVED": return <span className="badge badge-emerald"><CheckCircle2 size={12} /> APPROVED</span>;
      case "REJECTED": return <span className="badge badge-amber"><XCircle size={12} /> REJECTED</span>;
      default: return <span className="badge badge-indigo"><Clock size={12} /> PENDING REVIEW</span>;
    }
  };

  return (
    <div style={{ padding: '2rem', flex: 1, overflowY: 'auto' }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1.5rem' }}>
        <div>
          <h2 style={{ fontSize: '1.5rem', fontWeight: 700, display: 'flex', alignItems: 'center', gap: '0.6rem' }}>
            <CheckSquare className="gradient-text" size={26} /> Human-in-the-Loop (HITL) Action Approvals
          </h2>
          <p style={{ fontSize: '0.88rem', color: 'var(--text-secondary)', marginTop: '0.25rem' }}>
            Enterprise safety gate ensuring state mutation, external notifications, and cloud provisioning require explicit manager review.
          </p>
        </div>
        <button onClick={loadApprovals} className="btn-secondary" style={{ fontSize: '0.8rem' }}>
          Refresh Queue
        </button>
      </div>

      {loading ? (
        <div style={{ padding: '3rem', textAlign: 'center', color: 'var(--text-secondary)' }}>
          Loading pending approval requests...
        </div>
      ) : approvals.length === 0 ? (
        <div className="glass-card" style={{ padding: '3rem', textAlign: 'center' }}>
          <CheckCircle2 size={42} color="var(--accent-success)" style={{ margin: '0 auto 1rem' }} />
          <h3 style={{ fontSize: '1.2rem', fontWeight: 700 }}>Zero Pending Approvals</h3>
          <p style={{ color: 'var(--text-secondary)', fontSize: '0.88rem', marginTop: '0.25rem' }}>
            All agent execution actions have been verified and processed.
          </p>
        </div>
      ) : (
        <div style={{ display: 'flex', flexDirection: 'column', gap: '1.25rem' }}>
          {approvals.map((req) => (
            <div key={req.id || req._id} className="glass-card" style={{ padding: '1.5rem', border: req.status === 'PENDING' ? '1px solid var(--border-glow)' : '1px solid var(--border-color)' }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: '1rem' }}>
                <div>
                  <div style={{ display: 'flex', alignItems: 'center', gap: '0.6rem', marginBottom: '0.35rem' }}>
                    <h3 style={{ fontSize: '1.15rem', fontWeight: 700 }}>{req.actionType}</h3>
                    {getRiskBadge(req.riskLevel)}
                    {getStatusBadge(req.status)}
                  </div>
                  <div style={{ fontSize: '0.82rem', color: 'var(--text-secondary)', display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                    <User size={14} /> Requested by: <strong>{req.requestedByName || "Employee"}</strong> • Target System: <span style={{ color: 'var(--accent-secondary)' }}>{req.targetSystem}</span>
                  </div>
                </div>
                <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>
                  Created: {new Date(req.createdAt).toLocaleString()}
                </div>
              </div>

              {/* Action Payload Box */}
              <div style={{ marginBottom: '1rem' }}>
                <span style={{ fontSize: '0.75rem', fontWeight: 600, color: 'var(--text-muted)', textTransform: 'uppercase' }}>
                  Proposed Operation Payload:
                </span>
                <pre style={{ background: '#080c14', padding: '0.85rem', borderRadius: '8px', fontSize: '0.8rem', color: '#38bdf8', overflowX: 'auto', marginTop: '0.35rem' }}>
                  {JSON.stringify(req.actionPayload, null, 2)}
                </pre>
              </div>

              {/* Action Controls for Managers/Admins */}
              {req.status === 'PENDING' ? (
                isManager || isOrgAdmin || isSuperAdmin ? (
                  <div style={{ display: 'flex', gap: '0.75rem', alignItems: 'center', paddingTop: '0.5rem', borderTop: '1px solid var(--border-color)' }}>
                    <input
                      type="text"
                      placeholder="Add optional review notes / justification..."
                      value={reviewNotes[req.id || req._id] || ""}
                      onChange={(e) => setReviewNotes({ ...reviewNotes, [req.id || req._id]: e.target.value })}
                      style={{ flex: 1, padding: '0.6rem 0.85rem', borderRadius: '8px', background: 'var(--bg-primary)', border: '1px solid var(--border-color)', color: '#fff', fontSize: '0.85rem' }}
                    />
                    <button
                      onClick={() => handleDecision(req.id || req._id, "APPROVED")}
                      disabled={resolvingId === (req.id || req._id)}
                      className="btn-primary"
                      style={{ background: 'var(--accent-success)', border: 'none', padding: '0.6rem 1.25rem' }}
                    >
                      <CheckCircle2 size={16} /> Approve & Execute
                    </button>
                    <button
                      onClick={() => handleDecision(req.id || req._id, "REJECTED")}
                      disabled={resolvingId === (req.id || req._id)}
                      className="btn-danger"
                      style={{ padding: '0.6rem 1.25rem' }}
                    >
                      <XCircle size={16} /> Reject
                    </button>
                  </div>
                ) : (
                  <div style={{ fontSize: '0.8rem', color: 'var(--text-muted)', fontStyle: 'italic' }}>
                    ⏳ Awaiting review from a Department Manager or Organization Administrator.
                  </div>
                )
              ) : (
                <div style={{ fontSize: '0.8rem', color: 'var(--text-secondary)', display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                  <span>Reviewed by <strong>{req.reviewedByName}</strong> at {new Date(req.reviewedAt).toLocaleString()}</span>
                  {req.reviewNotes && <span>— "{req.reviewNotes}"</span>}
                </div>
              )}
            </div>
          ))}
        </div>
      )}
    </div>
  );
};
