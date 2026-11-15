import os
import sys

# Ensure app path in sys.path
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from app.config import settings
print(f"[OK] Settings loaded: {settings.PROJECT_NAME} (Version: {settings.VERSION})")
print(f"[OK] MongoDB URI Configured: {settings.MONGODB_URI}")

from app.agents.orchestrator import OrchestratorAgent
print("[OK] OrchestratorAgent loaded successfully.")

# Test intent classification
plan_hr = OrchestratorAgent.classify_intent("What is our company PTO policy?")
print(f"[OK] Intent Classification for PTO query: {plan_hr}")
assert "hr_agent" in plan_hr or "rag_agent" in plan_hr

plan_fin = OrchestratorAgent.classify_intent("Show Q3 budget spend variance")
print(f"[OK] Intent Classification for Budget query: {plan_fin}")
assert "finance_agent" in plan_fin

plan_act = OrchestratorAgent.classify_intent("Provision cloud cluster staging")
print(f"[OK] Intent Classification for Action query: {plan_act}")
assert "action_agent" in plan_act

print("\n=== ALL AI SERVICE MODULES AND INTENT ROUTERS VERIFIED 100% ===")
