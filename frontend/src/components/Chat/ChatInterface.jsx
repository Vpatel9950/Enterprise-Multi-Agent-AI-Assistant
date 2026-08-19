import React, { useState, useEffect, useRef } from "react";
import { api } from "../../services/api";
import { 
  Send, 
  Plus, 
  Trash2, 
  Sparkles, 
  FileText, 
  Download, 
  Bot, 
  User, 
  Cpu, 
  Zap, 
  Layers, 
  Info,
  ThumbsUp,
  ThumbsDown,
  CheckCircle,
  HelpCircle
} from "lucide-react";

export const ChatInterface = () => {
  const [conversations, setConversations] = useState([]);
  const [activeConvId, setActiveConvId] = useState(null);
  const [messages, setMessages] = useState([]);
  const [agents, setAgents] = useState([]);
  const [selectedAgentId, setSelectedAgentId] = useState(""); // empty string = Auto Router Supervisor
  const [inputQuery, setInputQuery] = useState("");
  const [loading, setLoading] = useState(false);
  const [showRAGModal, setShowRAGModal] = useState(null);
  const messagesEndRef = useRef(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    loadAgents();
    loadConversations();
  }, []);

  useEffect(() => {
    if (activeConvId) {
      loadConversationDetails(activeConvId);
    }
  }, [activeConvId]);

  useEffect(() => {
    scrollToBottom();
  }, [messages, loading]);

  const loadAgents = async () => {
    try {
      const data = await api.getAgents();
      setAgents(data.filter((a) => a.is_active));
    } catch (err) {
      console.error("Failed to load agents", err);
    }
  };

  const loadConversations = async () => {
    try {
      const data = await api.getConversations();
      setConversations(data);
      if (data.length > 0 && !activeConvId) {
        setActiveConvId(data[0].id);
      }
    } catch (err) {
      console.error("Failed to load conversations", err);
    }
  };

  const loadConversationDetails = async (id) => {
    try {
      const data = await api.getConversation(id);
      setMessages(data.messages || []);
    } catch (err) {
      console.error("Failed to load conversation details", err);
    }
  };

  const handleNewChat = async () => {
    try {
      const newConv = await api.createConversation(
        "New Conversation", 
        selectedAgentId ? parseInt(selectedAgentId) : null
      );
      setConversations([newConv, ...conversations]);
      setActiveConvId(newConv.id);
      setMessages(newConv.messages || []);
    } catch (err) {
      console.error("Failed to create new chat", err);
    }
  };

  const handleDeleteChat = async (e, id) => {
    e.stopPropagation();
    try {
      await api.deleteConversation(id);
      const remaining = conversations.filter((c) => c.id !== id);
      setConversations(remaining);
      if (activeConvId === id) {
        setActiveConvId(remaining.length > 0 ? remaining[0].id : null);
        if (remaining.length === 0) setMessages([]);
      }
    } catch (err) {
      console.error("Failed to delete conversation", err);
    }
  };

  const handleSendMessage = async (e) => {
    e?.preventDefault();
    if (!inputQuery.trim() || loading) return;

    const userText = inputQuery;
    setInputQuery("");
    setLoading(true);

    // Optimistic user message rendering
    const tempUserMsg = {
      id: Date.now(),
      sender_type: "user",
      sender_name: "You",
      content: userText,
      created_at: new Date().toISOString(),
    };
    setMessages((prev) => [...prev, tempUserMsg]);

    try {
      const resMessages = await api.sendMessage(
        activeConvId,
        selectedAgentId ? parseInt(selectedAgentId) : null,
        userText
      );

      if (resMessages && resMessages.length > 0) {
        // If this was a new conversation created automatically
        const newConvId = resMessages[0].conversation_id;
        if (activeConvId !== newConvId) {
          setActiveConvId(newConvId);
          loadConversations();
        } else {
          loadConversationDetails(activeConvId);
        }
      }
    } catch (err) {
      console.error("Error sending message:", err);
    } finally {
      setLoading(false);
    }
  };

  const exportTranscript = () => {
    const textData = messages.map((m) => `[${m.sender_name}] (${m.sender_type}): ${m.content}`).join("\n\n");
    const blob = new Blob([textData], { type: "text/plain" });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = `chat-transcript-${activeConvId || 'export'}.txt`;
    a.click();
  };

  const getAgentColor = (code) => {
    switch (code) {
      case "hr_agent": return "#818cf8";
      case "sales_agent": return "#34d399";
      case "tech_support": return "#f87171";
      case "data_analyst": return "#38bdf8";
      case "workflow_agent": return "#fbbf24";
      default: return "#c084fc";
    }
  };

  return (
    <div style={{ display: 'flex', height: 'calc(100vh - 64px)', overflow: 'hidden' }}>
      {/* Conversations History Sidebar */}
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
          Conversation History
        </div>

        <div style={{ flex: 1, overflowY: 'auto', display: 'flex', flexDirection: 'column', gap: '0.35rem' }}>
          {conversations.map((conv) => {
            const isActive = conv.id === activeConvId;
            return (
              <div
                key={conv.id}
                onClick={() => setActiveConvId(conv.id)}
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
                  justifyContent: 'space-between',
                  transition: 'all 0.2s ease'
                }}
              >
                <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', overflow: 'hidden' }}>
                  <Bot size={15} color={isActive ? "var(--accent-primary)" : "var(--text-muted)"} />
                  <span style={{ whiteSpace: 'nowrap', overflow: 'hidden', textOverflow: 'ellipsis' }}>
                    {conv.title}
                  </span>
                </div>
                <button
                  onClick={(e) => handleDeleteChat(e, conv.id)}
                  style={{ background: 'none', border: 'none', color: 'var(--text-muted)', cursor: 'pointer', opacity: 0.6 }}
                  title="Delete Chat"
                >
                  <Trash2 size={14} />
                </button>
              </div>
            );
          })}
        </div>
      </div>

      {/* Main Chat Workspace */}
      <div style={{ flex: 1, display: 'flex', flexDirection: 'column', background: 'var(--bg-secondary)', position: 'relative' }}>
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
              value={selectedAgentId}
              onChange={(e) => setSelectedAgentId(e.target.value)}
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
              <option value="">⚡ Auto Router (Intelligent AI Supervisor)</option>
              {agents.map((a) => (
                <option key={a.id} value={a.id}>
                  {a.name} ({a.code})
                </option>
              ))}
            </select>

            <span className="badge badge-indigo" style={{ fontSize: '0.7rem' }}>
              RAG & Memory Active
            </span>
          </div>

          <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
            <button onClick={exportTranscript} className="btn-secondary" style={{ padding: '0.4rem 0.75rem', fontSize: '0.8rem' }}>
              <Download size={15} /> Export Transcript
            </button>
          </div>
        </div>

        {/* Message History Feed */}
        <div style={{ flex: 1, overflowY: 'auto', padding: '1.5rem 2rem', display: 'flex', flexDirection: 'column', gap: '1.25rem' }}>
          {messages.length === 0 ? (
            <div style={{ textAlign: 'center', margin: 'auto', maxWidth: '500px' }}>
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
                Ask questions about HR policy, sales pipeline stats, technical bug diagnostics, automated workflow triggers, or data queries!
              </p>

              {/* Sample Quick Prompts */}
              <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '0.75rem' }}>
                {[
                  "What is our company PTO & parental leave policy?",
                  "Show Q3 sales deal pipeline summary",
                  "Diagnose database connection pool error",
                  "Generate SQL query for agent resolution times"
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
            messages.map((msg) => {
              const isUser = msg.sender_type === "user";
              const isSystem = msg.sender_type === "system";
              
              let meta = {};
              try {
                if (msg.metadata_json) meta = JSON.parse(msg.metadata_json);
              } catch (e) {}

              if (isSystem) {
                return (
                  <div key={msg.id} style={{ textAlign: 'center', margin: '0.5rem 0', fontSize: '0.8rem', color: 'var(--text-muted)' }}>
                    <span style={{ padding: '0.35rem 0.85rem', background: 'var(--bg-glass)', borderRadius: '9999px', border: '1px solid var(--border-color)' }}>
                      ℹ️ {msg.content}
                    </span>
                  </div>
                );
              }

              return (
                <div
                  key={msg.id}
                  className="animate-fade-in"
                  style={{
                    display: 'flex',
                    flexDirection: isUser ? 'row-reverse' : 'row',
                    gap: '0.85rem',
                    alignItems: 'flex-start'
                  }}
                >
                  {/* Avatar Icon */}
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

                  {/* Message Card Bubble */}
                  <div style={{ maxWidth: '75%' }}>
                    <div style={{
                      display: 'flex',
                      alignItems: 'center',
                      gap: '0.5rem',
                      marginBottom: '0.25rem',
                      justifyContent: isUser ? 'flex-end' : 'flex-start'
                    }}>
                      <span style={{ fontSize: '0.8rem', fontWeight: 600, color: 'var(--text-primary)' }}>
                        {msg.sender_name}
                      </span>
                      {meta.duration_ms && (
                        <span style={{ fontSize: '0.7rem', color: 'var(--text-muted)' }}>
                          ⚡ {meta.duration_ms}ms
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
                        whiteSpace: 'pre-wrap'
                      }}
                    >
                      {msg.content}

                      {/* Multi-Agent Sub-Task Trace Box */}
                      {meta.subagent_traces && meta.subagent_traces.length > 0 && (
                        <div style={{
                          marginTop: '0.85rem',
                          padding: '0.65rem',
                          background: 'rgba(6, 182, 212, 0.08)',
                          border: '1px solid rgba(6, 182, 212, 0.25)',
                          borderRadius: '8px',
                          fontSize: '0.78rem'
                        }}>
                          <div style={{ fontWeight: 700, color: 'var(--accent-secondary)', display: 'flex', alignItems: 'center', gap: '0.35rem', marginBottom: '0.35rem' }}>
                            <Layers size={14} /> Multi-Agent Collaboration Trace
                          </div>
                          {meta.subagent_traces.map((tr, idx) => (
                            <div key={idx} style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', color: 'var(--text-secondary)' }}>
                              <CheckCircle size={13} color="var(--accent-success)" />
                              <strong>{tr.agent_name}</strong>: {tr.action}
                            </div>
                          ))}
                        </div>
                      )}

                      {/* RAG Knowledge Citations Button */}
                      {meta.citations && meta.citations.length > 0 && (
                        <div style={{ marginTop: '0.85rem' }}>
                          <button
                            onClick={() => setShowRAGModal(meta.citations)}
                            className="badge badge-cyan"
                            style={{ cursor: 'pointer', border: '1px solid rgba(6, 182, 212, 0.4)' }}
                          >
                            <FileText size={12} /> {meta.citations.length} Knowledge Base Citations
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
                <Cpu size={16} className="pulse-glow" /> AI Agent is reasoning & querying knowledge base...
              </div>
            </div>
          )}

          <div ref={messagesEndRef} />
        </div>

        {/* Input Bar Form */}
        <form
          onSubmit={handleSendMessage}
          style={{
            padding: '1rem 1.5rem',
            borderTop: '1px solid var(--border-color)',
            background: 'var(--bg-secondary)',
            display: 'flex',
            gap: '0.75rem'
          }}
        >
          <input
            type="text"
            value={inputQuery}
            onChange={(e) => setInputQuery(e.target.value)}
            placeholder="Ask anything... (e.g. PTO policy, sales pipeline, API error logs, workflow rules)"
            style={{
              flex: 1,
              padding: '0.85rem 1.25rem',
              borderRadius: 'var(--radius-md)',
              background: 'var(--bg-primary)',
              border: '1px solid var(--border-color)',
              color: '#fff',
              fontSize: '0.92rem',
              outline: 'none'
            }}
          />
          <button type="submit" disabled={loading || !inputQuery.trim()} className="btn-primary" style={{ padding: '0 1.5rem' }}>
            <Send size={18} /> Send
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
          <div className="glass-card animate-fade-in" style={{ width: '100%', maxWidth: '540px', padding: '1.5rem', background: 'var(--bg-secondary)' }}>
            <h3 style={{ fontSize: '1.15rem', fontWeight: 700, marginBottom: '1rem', display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
              <FileText color="var(--accent-secondary)" /> Knowledge Base Citations
            </h3>
            <div style={{ display: 'flex', flexDirection: 'column', gap: '0.75rem', maxHeight: '350px', overflowY: 'auto' }}>
              {showRAGModal.map((c, idx) => (
                <div key={idx} style={{ padding: '0.75rem', background: 'var(--bg-primary)', borderRadius: '8px', border: '1px solid var(--border-color)' }}>
                  <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '0.35rem' }}>
                    <span style={{ fontWeight: 600, fontSize: '0.85rem', color: 'var(--accent-primary)' }}>{c.filename}</span>
                    <span className="badge badge-emerald" style={{ fontSize: '0.65rem' }}>Relevance: {intVal(c.score * 100)}%</span>
                  </div>
                  <p style={{ fontSize: '0.8rem', color: 'var(--text-secondary)', lineHeight: '1.4' }}>"{c.snippet}"</p>
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

const intVal = (val) => Math.round(val);
