import React, { useState } from "react";
import { AuthProvider, useAuth } from "./context/AuthContext";
import { Navbar } from "./components/Navbar";
import { Sidebar } from "./components/Sidebar";
import { AuthModal } from "./components/Auth/AuthModal";
import { ChatInterface } from "./components/Chat/ChatInterface";
import { AgentDirectory } from "./components/Agents/AgentDirectory";
import { DocumentManager } from "./components/Knowledge/DocumentManager";
import { ApprovalsCenter } from "./components/Approvals/ApprovalsCenter";
import { WorkflowBuilder } from "./components/Workflows/WorkflowBuilder";
import { IntegrationsManager } from "./components/Integrations/IntegrationsManager";
import { AdminDashboard } from "./components/Admin/AdminDashboard";

const MainAppContent = () => {
  const { user } = useAuth();
  const [activeTab, setActiveTab] = useState("chat");
  const [showAuthModal, setShowAuthModal] = useState(!user);

  // If not logged in, show auth modal fullscreen
  if (!user) {
    return (
      <div style={{ minHeight: "100vh", background: "var(--bg-primary)", display: "flex", alignItems: "center", justifyContent: "center" }}>
        <AuthModal isOpen={true} onClose={() => {}} />
      </div>
    );
  }

  return (
    <div style={{ minHeight: "100vh", display: "flex", flexDirection: "column", background: "var(--bg-primary)", color: "var(--text-primary)" }}>
      <Navbar activeTab={activeTab} onOpenAuthModal={() => setShowAuthModal(true)} />
      
      <div style={{ display: "flex", flex: 1 }}>
        <Sidebar activeTab={activeTab} setActiveTab={setActiveTab} />
        
        <main style={{ flex: 1, display: "flex", flexDirection: "column", overflow: "hidden" }}>
          {activeTab === "chat" && <ChatInterface />}
          {activeTab === "agents" && <AgentDirectory />}
          {activeTab === "knowledge" && <DocumentManager />}
          {activeTab === "approvals" && <ApprovalsCenter />}
          {activeTab === "workflows" && <WorkflowBuilder />}
          {activeTab === "integrations" && <IntegrationsManager />}
          {activeTab === "admin" && <AdminDashboard />}
        </main>
      </div>

      <AuthModal isOpen={showAuthModal} onClose={() => setShowAuthModal(false)} />
    </div>
  );
};

export function App() {
  return (
    <AuthProvider>
      <MainAppContent />
    </AuthProvider>
  );
}

export default App;
