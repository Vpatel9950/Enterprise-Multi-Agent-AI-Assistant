import React, { useState, useEffect } from "react";
import { api } from "../../services/api";
import { useAuth } from "../../context/AuthContext";
import { FileText, Plus, Trash2, Search, Database, Layers, CheckCircle } from "lucide-react";

export const DocumentManager = () => {
  const { isAdmin } = useAuth();
  const [documents, setDocuments] = useState([]);
  const [showAddModal, setShowAddModal] = useState(false);
  const [filename, setFilename] = useState("");
  const [category, setCategory] = useState("General Policy");
  const [content, setContent] = useState("");

  // Semantic query test sandbox state
  const [testQuery, setTestQuery] = useState("");
  const [searchResults, setSearchResults] = useState(null);
  const [searching, setSearching] = useState(false);

  useEffect(() => {
    loadDocuments();
  }, []);

  const loadDocuments = async () => {
    try {
      const data = await api.getDocuments();
      setDocuments(data);
    } catch (err) {
      console.error("Failed to load documents", err);
    }
  };

  const handleCreateDoc = async (e) => {
    e.preventDefault();
    if (!filename || !content) return;
    try {
      await api.createDocument({ filename, category, content });
      setShowAddModal(false);
      setFilename("");
      setContent("");
      loadDocuments();
    } catch (err) {
      console.error("Failed to add document", err);
    }
  };

  const handleDeleteDoc = async (id) => {
    if (!window.confirm("Are you sure you want to remove this document from RAG index?")) return;
    try {
      await api.deleteDocument(id);
      loadDocuments();
    } catch (err) {
      console.error("Failed to delete document", err);
    }
  };

  const handleTestSearch = async (e) => {
    e.preventDefault();
    if (!testQuery.trim()) return;
    setSearching(true);
    try {
      const res = await api.searchKnowledge(testQuery);
      setSearchResults(res.results);
    } catch (err) {
      console.error("Failed to test RAG search", err);
    } finally {
      setSearching(false);
    }
  };

  return (
    <div className="page-container">
      <div className="page-header">
        <div>
          <h2 style={{ fontSize: 'clamp(1.2rem, 3.5vw, 1.5rem)', fontWeight: 700, display: 'flex', alignItems: 'center', gap: '0.6rem' }}>
            <Database className="gradient-text" size={26} /> RAG Knowledge Base Hub
          </h2>
          <p style={{ fontSize: '0.85rem', color: 'var(--text-secondary)', marginTop: '0.25rem' }}>
            Upload company policies, technical SLAs, and sales documentation to empower AI agent retrieval.
          </p>
        </div>
        {isAdmin && (
          <button onClick={() => setShowAddModal(true)} className="btn-primary">
            <Plus size={16} /> Index New Document
          </button>
        )}
      </div>

      {/* Semantic Search Sandbox Tool */}
      <div className="glass-card" style={{ padding: '1.25rem', marginBottom: '1.5rem', border: '1px solid var(--border-glow)' }}>
        <h3 style={{ fontSize: '1rem', fontWeight: 700, marginBottom: '0.5rem', display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
          <Search size={18} color="var(--accent-secondary)" /> Live RAG Retrieval Vector Sandbox
        </h3>
        <p style={{ fontSize: '0.8rem', color: 'var(--text-secondary)', marginBottom: '1rem' }}>
          Test how the RAG engine chunks text and scores semantic relevance against user queries.
        </p>

        <form onSubmit={handleTestSearch} style={{ display: 'flex', gap: '0.75rem', flexWrap: 'wrap' }}>
          <input
            type="text"
            value={testQuery}
            onChange={(e) => setTestQuery(e.target.value)}
            placeholder="Type query to test vector similarity matching (e.g. 'What is our PTO policy?')..."
            style={{ flex: '1 1 240px', minWidth: 0, padding: '0.65rem 1rem', borderRadius: '8px', background: 'var(--bg-primary)', border: '1px solid var(--border-color)', color: '#fff', fontSize: '0.9rem' }}
          />
          <button type="submit" disabled={searching} className="btn-primary" style={{ whiteSpace: 'nowrap' }}>
            {searching ? "Searching..." : "Test RAG Query"}
          </button>
        </form>

        {searchResults && (
          <div style={{ marginTop: '1rem', display: 'flex', flexDirection: 'column', gap: '0.6rem' }}>
            <div style={{ fontSize: '0.8rem', fontWeight: 600, color: 'var(--accent-primary)' }}>
              Matches Found: {searchResults.length}
            </div>
            {searchResults.map((match, idx) => (
              <div key={idx} style={{ padding: '0.75rem', background: 'var(--bg-primary)', borderRadius: '8px', border: '1px solid var(--border-color)' }}>
                <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '0.25rem', flexWrap: 'wrap', gap: '0.35rem' }}>
                  <span style={{ fontWeight: 600, fontSize: '0.85rem' }}>
                    {match.source_name || match.filename} — <em style={{ fontWeight: 400, color: 'var(--text-secondary)' }}>{match.section}</em>
                  </span>
                  <span className="badge badge-emerald">
                    Score: {Math.round((match.relevance_score || match.similarity_score || 0) * 100)}%
                  </span>
                </div>
                <p style={{ fontSize: '0.8rem', color: 'var(--text-secondary)' }}>"{match.snippet}"</p>
              </div>
            ))}
          </div>
        )}
      </div>

      {/* Indexed Documents Table */}
      <div className="glass-card" style={{ padding: '1.5rem' }}>
        <h3 style={{ fontSize: '1.1rem', fontWeight: 700, marginBottom: '1rem' }}>Indexed Enterprise Knowledge Files</h3>
        <div style={{ overflowX: 'auto' }}>
          <table style={{ width: '100%', borderCollapse: 'collapse' }}>
            <thead>
              <tr style={{ borderBottom: '1px solid var(--border-color)', textTransform: 'uppercase', fontSize: '0.75rem', color: 'var(--text-muted)' }}>
                <th style={{ padding: '0.75rem', textAlign: 'left' }}>Document Name</th>
                <th style={{ padding: '0.75rem', textAlign: 'left' }}>Category</th>
                <th style={{ padding: '0.75rem', textAlign: 'left' }}>Word Count</th>
                <th style={{ padding: '0.75rem', textAlign: 'left' }}>Chunks</th>
                <th style={{ padding: '0.75rem', textAlign: 'left' }}>Uploaded By</th>
                {isAdmin && <th style={{ padding: '0.75rem', textAlign: 'right' }}>Actions</th>}
              </tr>
            </thead>
            <tbody>
              {documents.map((doc) => (
                <tr key={doc.id} style={{ borderBottom: '1px solid var(--border-color)', fontSize: '0.88rem' }}>
                  <td style={{ padding: '0.75rem', fontWeight: 600, display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                    <FileText size={16} color="var(--accent-primary)" />
                    {doc.fileName || doc.filename || doc.file_name}
                  </td>
                  <td style={{ padding: '0.75rem' }}>
                    <span className="badge badge-cyan" style={{ fontSize: '0.7rem' }}>
                      {doc.classification || doc.category || 'INTERNAL'}
                    </span>
                  </td>
                  <td style={{ padding: '0.75rem' }}>
                    {Math.round((doc.fileSize || 0) / 100)} words
                  </td>
                  <td style={{ padding: '0.75rem' }}>{doc.chunkCount || doc.chunk_count || '—'} chunks</td>
                  <td style={{ padding: '0.75rem', color: 'var(--text-secondary)' }}>
                    {doc.uploadedByName || doc.uploaded_by || 'System'}
                  </td>
                  {isAdmin && (
                    <td style={{ padding: '0.75rem', textAlign: 'right' }}>
                      <button onClick={() => handleDeleteDoc(doc.id)} className="btn-danger" style={{ padding: '0.3rem 0.6rem', fontSize: '0.75rem' }}>
                        <Trash2 size={13} /> Delete
                      </button>
                    </td>
                  )}
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      {/* Add Document Modal */}
      {showAddModal && (
        <div style={{
          position: 'fixed', top: 0, left: 0, right: 0, bottom: 0,
          background: 'rgba(0,0,0,0.75)', backdropFilter: 'blur(8px)',
          display: 'flex', alignItems: 'center', justifyContent: 'center', zIndex: 100
        }}>
          <div className="glass-card animate-fade-in" style={{ width: '100%', maxWidth: '520px', padding: '1.75rem', background: 'var(--bg-secondary)' }}>
            <h3 style={{ fontSize: '1.2rem', fontWeight: 700, marginBottom: '1rem' }}>Index New Knowledge Document</h3>
            <form onSubmit={handleCreateDoc} style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
              <div>
                <label style={{ fontSize: '0.8rem', fontWeight: 600, color: 'var(--text-secondary)', display: 'block', marginBottom: '0.35rem' }}>
                  Document Title / Filename
                </label>
                <input
                  type="text" required value={filename} onChange={(e) => setFilename(e.target.value)}
                  placeholder="e.g. Sales_Discount_Policy_2026.txt"
                  style={{ width: '100%', padding: '0.65rem', borderRadius: '8px', background: 'var(--bg-primary)', border: '1px solid var(--border-color)', color: '#fff', fontSize: '0.9rem' }}
                />
              </div>
              <div>
                <label style={{ fontSize: '0.8rem', fontWeight: 600, color: 'var(--text-secondary)', display: 'block', marginBottom: '0.35rem' }}>
                  Category
                </label>
                <select
                  value={category} onChange={(e) => setCategory(e.target.value)}
                  style={{ width: '100%', padding: '0.65rem', borderRadius: '8px', background: 'var(--bg-primary)', border: '1px solid var(--border-color)', color: '#fff', fontSize: '0.9rem' }}
                >
                  <option value="HR & Compliance">HR & Compliance</option>
                  <option value="Sales">Sales & RFP</option>
                  <option value="Technical">Technical Architecture & SLA</option>
                  <option value="General Policy">General Policy</option>
                </select>
              </div>
              <div>
                <label style={{ fontSize: '0.8rem', fontWeight: 600, color: 'var(--text-secondary)', display: 'block', marginBottom: '0.35rem' }}>
                  Document Content Text
                </label>
                <textarea
                  rows={6} required value={content} onChange={(e) => setContent(e.target.value)}
                  placeholder="Paste raw documentation text here..."
                  style={{ width: '100%', padding: '0.65rem', borderRadius: '8px', background: 'var(--bg-primary)', border: '1px solid var(--border-color)', color: '#fff', fontSize: '0.85rem' }}
                />
              </div>
              <div style={{ display: 'flex', gap: '0.75rem', marginTop: '0.5rem' }}>
                <button type="button" onClick={() => setShowAddModal(false)} className="btn-secondary" style={{ flex: 1, justifyContent: 'center' }}>Cancel</button>
                <button type="submit" className="btn-primary" style={{ flex: 1, justifyContent: 'center' }}>Parse & Index</button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
};

const intVal = (v) => Math.round(v);
