import React, { useState, useEffect, useRef } from "react";
import ReactMarkdown from "react-markdown";
import { api } from "../../services/api";

// Separate component for collapsible agent traces (Rules of Hooks compliance)
const AgentTraces = ({ traces }) => {
  const [open, setOpen] = useState(false);
  if (!traces || traces.length === 0) return null;
  return (
    <div style={{ marginTop: '0.85rem', borderRadius: '8px', overflow: 'hidden', border: '1px solid rgba(6, 182, 212, 0.25)', fontSize: '0.78rem' }}>
      <div
        onClick={() => setOpen(!open)}
        style={{ padding: '0.5rem 0.75rem', background: 'rgba(6, 182, 212, 0.08)', cursor: 'pointer', fontWeight: 700, color: 'var(--accent-secondary)', display: 'flex', alignItems: 'center', gap: '0.35rem', userSelect: 'none' }}
      >
        <span>⚡ Agent Execution Traces ({traces.length} steps)</span>
        <span style={{ marginLeft: 'auto', fontSize: '0.7rem' }}>{open ? '▲ Hide' : '▼ Show'}</span>
      </div>
      {open && (
        <div style={{ padding: '0.5rem 0.75rem', background: 'rgba(6, 182, 212, 0.04)' }}>
          {traces.map((tr, idx) => (
            <div key={idx} style={{ display: 'flex', alignItems: 'flex-start', gap: '0.5rem', color: 'var(--text-secondary)', marginBottom: '0.25rem' }}>
              <span style={{ color: 'var(--accent-success)', flexShrink: 0 }}>✓</span>
              <span>
                <strong>{tr.agent_name || tr.agentName}</strong>: {tr.action}
                <span style={{ fontSize: '0.7rem', color: 'var(--text-muted)', marginLeft: '0.4rem' }}>
                  ({tr.duration_ms || tr.durationMs}ms)
                </span>
              </span>
            </div>
          ))}
        </div>
      )}
    </div>
  );
};
import { useAuth } from "../../context/AuthContext";
import { 
  Send, 
  Plus, 
  Sparkles, 
  FileText, 
  Download, 
  Bot, 
  User, 
  Cpu, 
  Zap, 
  Layers, 
  ShieldAlert,
  CheckCircle2,
  Clock,
  ExternalLink,
  ChevronRight
} from "lucide-react";

export const ChatInterface = () => {
  const { user, isManager, isOrgAdmin } = useAuth();
  const [conversations, setConversations] = useState([]);
  const [activeConvId, setActiveConvId] = useState(null);
  const [messages, setMessages] = useState([]);
  const [selectedAgentCode, setSelectedAgentCode] = useState("orchestrator");
  const [inputQuery, setInputQuery] = useState("");
  const [loading, setLoading] = useState(false);
  const [showRAGModal, setShowRAGModal] = useState(null);
  const messagesEndRef = useRef(null);

  const agentsList = [
    { code: "orchestrator", name: "⚡ Auto Router (Supervisor)", desc: "Analyzes intent & plans multi-agent swarm DAG" },
    { code: "rag_agent", name: "📚 Knowledge & RAG Agent", desc: "Searches company policies with citations" },
    { code: "hr_agent", name: "🏢 HR & Employee Agent", desc: "Benefits, PTO, leave allowance & handbook" },
    { code: "finance_agent", name: "💳 Finance & Budget Agent", desc: "Department budgets, spend & variance" },
    { code: "dev_agent", name: "🛠️ Developer & Architecture Agent", desc: "API specs, cloud infrastructure & code debug" },
    { code: "research_agent", name: "🔬 Research & Synthesis Agent", desc: "Multi-document executive briefing" },
    { code: "db_agent", name: "🗄️ Database Query Agent", desc: "Controlled read-only MongoDB aggregations" },
    { code: "action_agent", name: "⚡ Action Agent (HITL Gate)", desc: "State-modifying operations with human review" }
  ];

  useEffect(() => {
    loadConversations();
  }, [user]);

  useEffect(() => {
    if (activeConvId) {
      loadMessages(activeConvId);
    }
  }, [activeConvId]);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, loading]);

  const loadConversations = async () => {
    try {
      const data = await api.getConversations();
      setConversations(data);
      if (data.length > 0 && !activeConvId) {
        setActiveConvId(data[0].id || data[0]._id);
      }
    } catch (err) {
      console.error("Failed to load conversations", err);
    }
  };

  const loadMessages = async (convId) => {
    try {
      const msgs = await api.getConversationMessages(convId);
      setMessages(msgs);
    } catch (err) {
      console.error("Failed to load conversation messages", err);
    }
  };

  const handleNewChat = () => {
    setActiveConvId(null);
    setMessages([]);
  };

  const handleSendMessage = async (e) => {
    e?.preventDefault();
    if (!inputQuery.trim() || loading) return;

    const userText = inputQuery;
    setInputQuery("");
    setLoading(true);

    // Optimistic user bubble
    const tempUserMsg = {
      id: "temp-" + Date.now(),
      senderType: "USER",
      senderName: user?.fullName || "Employee",
      content: userText,
      createdAt: new Date().toISOString()
    };
    setMessages((prev) => [...prev, tempUserMsg]);

    try {
      const res = await api.sendMessage(
        activeConvId,
        selectedAgentCode === "orchestrator" ? null : selectedAgentCode,
        userText
      );

      if (res) {
        if (!activeConvId || activeConvId !== res.conversation_id) {
          setActiveConvId(res.conversation_id);
          loadConversations();
        }

        const agentMsg = {
          id: "agent-" + Date.now(),
          senderType: "AGENT",
          senderName: res.assigned_agent || "Orchestrator Agent",
          content: res.response,
          citations: res.citations || [],
          agentTraces: res.agent_traces || [],
          approval_required: res.approval_required,
          approval_id: res.approval_id,
          durationMs: res.duration_ms,
          tokensUsed: res.tokens_used,
          createdAt: new Date().toISOString()
        };
        setMessages((prev) => [...prev, agentMsg]);
      }
    } catch (err) {
      console.error("Failed to send message", err);
      const errorMsg = {
        id: "err-" + Date.now(),
        senderType: "SYSTEM",
        senderName: "System Error",
        content: `Execution failed: ${err.message}. Ensure AI microservice is running.`,
        createdAt: new Date().toISOString()
      };
      setMessages((prev) => [...prev, errorMsg]);
    } finally {
      setLoading(false);
    }
  };

  const handleApproveAction = async (approvalId) => {
    try {
      await api.submitApprovalDecision(approvalId, "APPROVED", `Approved by ${user?.fullName}`);
      alert("Action approved! The Action Agent has executed the operation.");
      if (activeConvId) loadMessages(activeConvId);
    } catch (err) {
      alert("Approval failed: " + err.message);
    }
  };

  return (
    <div style={{ display: 'flex', height: 'calc(100vh - 64px)', overflow: 'hidden', width: '100%', boxSizing: 'border-box' }}>
      {/* Sessions Sidebar */}
      <div style={{
        width: '280px',
        borderRight: '1px solid var(--border-color)',
        background: 'var(--bg-primary)',
        display: 'flex',
        flexDirection: 'column',
        padding: '1rem 0.75rem'
      }}>
        <button onClick={handleNewChat} className="btn-primary" style={{ width: '100%', justifyContent: 'center', marginBottom: '1rem' }}>
          <Plus size={16} /> New AI Session
        </button>

        <div style={{ fontSize: '0.72rem', fontWeight: 700, color: 'var(--text-muted)', textTransform: 'uppercase', marginBottom: '0.5rem', paddingLeft: '0.25rem' }}>
          MongoDB Conversation History
        </div>

        <div style={{ flex: 1, overflowY: 'auto', display: 'flex', flexDirection: 'column', gap: '0.35rem' }}>
          {conversations.map((conv) => {
            const cId = conv.id || conv._id;
            const isActive = cId === activeConvId;
            return (
              <div
                key={cId}
                onClick={() => setActiveConvId(cId)}
                style={{
                  padding: '0.65rem 0.75rem',
                  borderRadius: 'var(--radius-sm)',
                  border: isActive ? '1px solid var(--border-glow)' : '1px solid transparent',
                  background: isActive ? 'var(--bg-card-hover)' : 'transparent',
                  color: isActive ? 'var(--text-primary)' : 'var(--text-secondary)',
                  cursor: 'pointer',
                  fontSize: '0.85rem',
                  display: 'flex',
                  alignItems: 'center',
                  gap: '0.5rem',
                  transition: 'all 0.2s ease'
                }}
              >
                <Bot size={15} color={isActive ? "var(--accent-primary)" : "var(--text-muted)"} />
                <span style={{ whiteSpace: 'nowrap', overflow: 'hidden', textOverflow: 'ellipsis' }}>
                  {conv.title || "Conversation"}
                </span>
              </div>
            );
          })}
        </div>
      </div>

      {/* Main Chat Workspace */}
      <div style={{ flex: 1, minWidth: 0, display: 'flex', flexDirection: 'column', background: 'var(--bg-secondary)', position: 'relative', overflow: 'hidden' }}>
        {/* Chat Control Header */}
        <div style={{
          padding: '0.85rem 1.5rem',
          borderBottom: '1px solid var(--border-color)',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'space-between',
          background: 'var(--bg-glass)'
        }}>
          {/* Agent Picker Dropdown */}
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
            <div style={{ fontSize: '0.85rem', fontWeight: 600, color: 'var(--text-secondary)' }}>
              Assigned Agent:
            </div>
            <select
              value={selectedAgentCode}
              onChange={(e) => setSelectedAgentCode(e.target.value)}
              style={{
                background: 'var(--bg-primary)',
                color: 'var(--text-primary)',
                border: '1px solid var(--border-color)',
                borderRadius: '8px',
                padding: '0.45rem 0.85rem',
                fontSize: '0.85rem',
                fontWeight: 600,
                cursor: 'pointer'
              }}
            >
              {agentsList.map((a) => (
                <option key={a.code} value={a.code}>
                  {a.name}
                </option>
              ))}
            </select>

            <span className="badge badge-indigo" style={{ fontSize: '0.7rem' }}>
              Qdrant RAG & HITL Active
            </span>
          </div>

          <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
            <span className="badge badge-cyan" style={{ fontSize: '0.72rem' }}>
              Clearance: {user?.role || "EMPLOYEE"}
            </span>
          </div>
        </div>

        {/* Message Feed */}
        <div style={{ flex: 1, overflowY: 'auto', padding: '1.5rem 2rem', display: 'flex', flexDirection: 'column', gap: '1.25rem' }}>
          {messages.length === 0 ? (
            <div style={{ textAlign: 'center', margin: 'auto', maxWidth: '600px' }}>
              <div style={{
                width: '64px',
                height: '64px',
                borderRadius: '20px',
                background: 'var(--gradient-primary)',
                display: 'inline-flex',
                alignItems: 'center',
                justifyContent: 'center',
                marginBottom: '1rem',
                boxShadow: 'var(--shadow-glow)'
              }}>
                <Sparkles size={32} color="#fff" />
              </div>
              <h2 style={{ fontSize: '1.4rem', fontWeight: 700, marginBottom: '0.5rem' }}>
                Enterprise Multi-Agent Assistant
              </h2>
              <p style={{ fontSize: '0.88rem', color: 'var(--text-secondary)', lineHeight: '1.5', marginBottom: '1.5rem' }}>
                Ask anything across company policies, budgets, code architecture, or database metrics. The Orchestrator automatically delegates tasks to specialized agents.
              </p>

              {/* Sample Prompts */}
              <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '0.75rem' }}>
                {[
                  "What is our company PTO & parental leave policy?",
                  "Show Q3 consolidated departmental budget variance",
                  "Query database message analytics and user count",
                  "Provision cloud cluster staging-ai-swarm"
                ].map((prompt, idx) => (
                  <button
                    key={idx}
                    onClick={() => { setInputQuery(prompt); }}
                    className="glass-card"
                    style={{
                      padding: '0.75rem',
                      textAlign: 'left',
                      fontSize: '0.8rem',
                      color: 'var(--text-primary)',
                      cursor: 'pointer',
                      border: '1px solid var(--border-color)'
                    }}
                  >
                    💡 "{prompt}"
                  </button>
                ))}
              </div>
            </div>
          ) : (
            messages.map((msg, index) => {
              const isUser = msg.senderType === "USER";
              const isSystem = msg.senderType === "SYSTEM";

              if (isSystem) {
                return (
                  <div key={index} style={{ textAlign: 'center', margin: '0.5rem 0', fontSize: '0.8rem', color: 'var(--text-muted)' }}>
                    <span style={{ padding: '0.35rem 0.85rem', background: 'rgba(239, 68, 68, 0.15)', borderRadius: '9999px', border: '1px solid rgba(239, 68, 68, 0.3)', color: 'var(--accent-danger)' }}>
                      ⚠️ {msg.content}
                    </span>
                  </div>
                );
              }

              return (
                <div
                  key={index}
                  className="animate-fade-in"
                  style={{
                    display: 'flex',
                    flexDirection: isUser ? 'row-reverse' : 'row',
                    gap: '0.85rem',
                    alignItems: 'flex-start'
                  }}
                >
                  <div style={{
                    width: '36px',
                    height: '36px',
                    borderRadius: '10px',
                    background: isUser ? 'var(--accent-primary)' : 'var(--bg-card)',
                    border: '1px solid var(--border-color)',
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'center',
                    flexShrink: 0
                  }}>
                    {isUser ? <User size={18} color="#fff" /> : <Bot size={18} color="var(--accent-secondary)" />}
                  </div>

                  <div style={{ maxWidth: '80%' }}>
                    <div style={{
                      display: 'flex',
                      alignItems: 'center',
                      gap: '0.5rem',
                      marginBottom: '0.25rem',
                      justifyContent: isUser ? 'flex-end' : 'flex-start'
                    }}>
                      <span style={{ fontSize: '0.8rem', fontWeight: 600, color: 'var(--text-primary)' }}>
                        {msg.senderName}
                      </span>
                      {msg.durationMs && (
                        <span style={{ fontSize: '0.7rem', color: 'var(--text-muted)' }}>
                          ⚡ {msg.durationMs}ms
                        </span>
                      )}
                    </div>

                    <div
                      className="glass-card markdown-body"
                      style={{
                        padding: '1rem',
                        borderRadius: 'var(--radius-md)',
                        background: isUser ? 'rgba(99, 102, 241, 0.18)' : 'var(--bg-card)',
                        border: isUser ? '1px solid rgba(99, 102, 241, 0.4)' : '1px solid var(--border-color)',
                        whiteSpace: isUser ? 'pre-wrap' : 'normal',
                        lineHeight: '1.7',
                        fontSize: '0.92rem'
                      }}
                    >
                      {isUser ? (
                        msg.content
                      ) : (
                        <ReactMarkdown
                          components={{
                            h1: ({node, ...props}) => <h1 style={{fontSize:'1.3rem', fontWeight:700, margin:'0.6rem 0', color:'#e2e8f0'}} {...props}/>,
                            h2: ({node, ...props}) => <h2 style={{fontSize:'1.1rem', fontWeight:700, margin:'0.5rem 0', color:'#e2e8f0'}} {...props}/>,
                            h3: ({node, ...props}) => <h3 style={{fontSize:'1rem', fontWeight:600, margin:'0.4rem 0', color:'#cbd5e1'}} {...props}/>,
                            p:  ({node, ...props}) => <p style={{margin:'0.4rem 0'}} {...props}/>,
                            ul: ({node, ...props}) => <ul style={{paddingLeft:'1.4rem', margin:'0.4rem 0'}} {...props}/>,
                            ol: ({node, ...props}) => <ol style={{paddingLeft:'1.4rem', margin:'0.4rem 0'}} {...props}/>,
                            li: ({node, ...props}) => <li style={{marginBottom:'0.2rem'}} {...props}/>,
                            strong: ({node, ...props}) => <strong style={{color:'#a5f3fc', fontWeight:600}} {...props}/>,
                            code: ({node, inline, ...props}) => inline
                              ? <code style={{background:'rgba(99,102,241,0.2)', padding:'0.1rem 0.4rem', borderRadius:'4px', fontSize:'0.85em', color:'#c4b5fd'}} {...props}/>
                              : <code style={{display:'block', background:'rgba(0,0,0,0.3)', padding:'0.75rem', borderRadius:'8px', fontSize:'0.82em', overflowX:'auto', margin:'0.5rem 0', color:'#86efac'}} {...props}/>,
                            blockquote: ({node, ...props}) => <blockquote style={{borderLeft:'3px solid var(--accent-primary)', paddingLeft:'0.8rem', margin:'0.5rem 0', color:'var(--text-secondary)', fontStyle:'italic'}} {...props}/>,
                            hr: ({node, ...props}) => <hr style={{border:'none', borderTop:'1px solid var(--border-color)', margin:'0.8rem 0'}} {...props}/>,
                            table: ({node, ...props}) => <table style={{borderCollapse:'collapse', width:'100%', margin:'0.5rem 0', fontSize:'0.85rem'}} {...props}/>,
                            th: ({node, ...props}) => <th style={{border:'1px solid var(--border-color)', padding:'0.4rem 0.6rem', background:'rgba(99,102,241,0.15)', textAlign:'left'}} {...props}/>,
                            td: ({node, ...props}) => <td style={{border:'1px solid var(--border-color)', padding:'0.4rem 0.6rem'}} {...props}/>,
                          }}
                        >
                          {msg.content}
                        </ReactMarkdown>
                      )}

                      {/* Multi-Agent Execution Traces - Collapsible */}
                      <AgentTraces traces={msg.agentTraces} />

                      {/* Human-in-the-Loop (HITL) Inline Approval Banner */}
                      {msg.approval_required && msg.approval_id && (
                        <div style={{
                          marginTop: '0.85rem',
                          padding: '0.85rem',
                          background: 'rgba(245, 158, 11, 0.12)',
                          border: '1px solid rgba(245, 158, 11, 0.4)',
                          borderRadius: '8px',
                          display: 'flex',
                          alignItems: 'center',
                          justifyContent: 'space-between'
                        }}>
                          <div style={{ display: 'flex', alignItems: 'center', gap: '0.6rem' }}>
                            <ShieldAlert size={20} color="var(--accent-warning)" />
                            <div>
                              <div style={{ fontSize: '0.82rem', fontWeight: 700, color: 'var(--accent-warning)' }}>
                                Human-in-the-Loop Review Required
                              </div>
                              <div style={{ fontSize: '0.72rem', color: 'var(--text-secondary)' }}>
                                Request ID: #{msg.approval_id}
                              </div>
                            </div>
                          </div>
                          {isManager || isOrgAdmin ? (
                            <button
                              onClick={() => handleApproveAction(msg.approval_id)}
                              className="btn-primary"
                              style={{ padding: '0.35rem 0.85rem', fontSize: '0.78rem' }}
                            >
                              Approve & Execute Action
                            </button>
                          ) : (
                            <span className="badge badge-amber" style={{ fontSize: '0.7rem' }}>
                              Pending Manager Review
                            </span>
                          )}
                        </div>
                      )}

                      {/* RAG Knowledge Citations Button */}
                      {msg.citations && msg.citations.length > 0 && (
                        <div style={{ marginTop: '0.85rem' }}>
                          <button
                            onClick={() => setShowRAGModal(msg.citations)}
                            className="badge badge-cyan"
                            style={{ cursor: 'pointer', border: '1px solid rgba(6, 182, 212, 0.4)' }}
                          >
                            <FileText size={12} /> {msg.citations.length} Knowledge Base Citations
                          </button>
                        </div>
                      )}
                    </div>
                  </div>
                </div>
              );
            })
          )}

          {loading && (
            <div style={{ display: 'flex', gap: '0.85rem', alignItems: 'center' }}>
              <div style={{ width: '36px', height: '36px', borderRadius: '10px', background: 'var(--bg-card)', border: '1px solid var(--border-color)', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
                <Bot size={18} className="pulse-glow" color="var(--accent-primary)" />
              </div>
              <div className="glass-card" style={{ padding: '0.75rem 1.25rem', fontSize: '0.85rem', color: 'var(--text-secondary)', display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                <Cpu size={16} className="pulse-glow" /> Orchestrator is executing multi-agent DAG pipeline...
              </div>
            </div>
          )}

          <div ref={messagesEndRef} />
        </div>

        {/* Input Bar */}
        <form
          onSubmit={handleSendMessage}
          style={{
            padding: '0.75rem 1rem',
            borderTop: '1px solid var(--border-color)',
            background: 'var(--bg-secondary)',
            display: 'flex',
            gap: '0.5rem',
            alignItems: 'center',
            flexShrink: 0,
            boxSizing: 'border-box'
          }}
        >
          <input
            type="text"
            value={inputQuery}
            onChange={(e) => setInputQuery(e.target.value)}
            placeholder="Ask anything... (e.g. PTO policy, Q3 budget variance, diagnose connection pool, provision cluster)"
            style={{
              flex: 1,
              minWidth: 0,
              padding: '0.75rem 1rem',
              borderRadius: 'var(--radius-md)',
              background: 'var(--bg-primary)',
              border: '1px solid var(--border-color)',
              color: '#fff',
              fontSize: '0.9rem',
              outline: 'none',
              boxSizing: 'border-box'
            }}
          />
          <button type="submit" disabled={loading || !inputQuery.trim()} className="btn-primary" style={{ padding: '0.75rem 1.25rem', flexShrink: 0, whiteSpace: 'nowrap' }}>
            <Send size={16} /> Send
          </button>
        </form>
      </div>

      {/* RAG Citations Modal */}
      {showRAGModal && (
        <div style={{
          position: 'fixed',
          top: 0, left: 0, right: 0, bottom: 0,
          background: 'rgba(0,0,0,0.75)',
          backdropFilter: 'blur(6px)',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          zIndex: 100
        }}>
          <div className="glass-card animate-fade-in" style={{ width: '100%', maxWidth: '560px', padding: '1.5rem', background: 'var(--bg-secondary)' }}>
            <h3 style={{ fontSize: '1.15rem', fontWeight: 700, marginBottom: '1rem', display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
              <FileText color="var(--accent-secondary)" /> Verified Knowledge Base Citations
            </h3>
            <div style={{ display: 'flex', flexDirection: 'column', gap: '0.75rem', maxHeight: '350px', overflowY: 'auto' }}>
              {showRAGModal.map((c, idx) => (
                <div key={idx} style={{ padding: '0.75rem', background: 'var(--bg-primary)', borderRadius: '8px', border: '1px solid var(--border-color)' }}>
                  <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '0.35rem' }}>
                    <span style={{ fontWeight: 600, fontSize: '0.85rem', color: 'var(--accent-primary)' }}>
                      {c.source_name || c.sourceName}
                    </span>
                    <span className="badge badge-emerald" style={{ fontSize: '0.65rem' }}>
                      Relevance: {Math.round((c.relevance_score || c.relevanceScore) * 100)}%
                    </span>
                  </div>
                  <div style={{ fontSize: '0.72rem', color: 'var(--text-muted)', marginBottom: '0.35rem' }}>
                    Section: {c.section || "General"} • Page: {c.page_number || c.pageNumber || 1}
                  </div>
                  <p style={{ fontSize: '0.8rem', color: 'var(--text-secondary)', lineHeight: '1.4' }}>
                    "{c.snippet}"
                  </p>
                </div>
              ))}
            </div>
            <button onClick={() => setShowRAGModal(null)} className="btn-secondary" style={{ marginTop: '1rem', width: '100%', justifyContent: 'center' }}>
              Close Citations
            </button>
          </div>
        </div>
      )}
    </div>
  );
};
