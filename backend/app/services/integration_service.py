import datetime
from typing import Dict, Any
from sqlalchemy.orm import Session
from app.models import Integration

class IntegrationService:
    @staticmethod
    def trigger_integration(db: Session, service_type: str, action: str, payload: Dict[str, Any]) -> Dict[str, Any]:
        integration = db.query(Integration).filter(Integration.service_type == service_type).first()
        now_str = datetime.datetime.utcnow().isoformat()

        if integration:
            integration.last_sync_at = datetime.datetime.utcnow()
            db.commit()

        if service_type == "slack":
            channel = payload.get("channel", "#general")
            message = payload.get("message", "Notification from Enterprise AI Assistant")
            return {
                "status": "success",
                "service": "Slack Workspace",
                "channel": channel,
                "delivered_at": now_str,
                "message": f"Broadcasted message to {channel}: '{message}'"
            }

        elif service_type == "crm":
            lead_name = payload.get("lead_name", "Enterprise Prospect")
            deal_value = payload.get("deal_value", "$50,000")
            return {
                "status": "success",
                "service": "Salesforce CRM",
                "record_id": f"CRM-DEAL-{int(datetime.datetime.utcnow().timestamp())}",
                "lead_name": lead_name,
                "deal_value": deal_value,
                "synced_at": now_str,
                "message": f"Created new high-priority lead record for {lead_name} worth {deal_value}."
            }

        elif service_type == "erp":
            order_id = payload.get("order_id", "ERP-98721")
            return {
                "status": "success",
                "service": "SAP ERP Enterprise System",
                "transaction_id": f"TXN-{order_id}",
                "synced_at": now_str,
                "message": f"Successfully audited stock inventory and order state for item {order_id}."
            }

        elif service_type == "email":
            recipient = payload.get("recipient", "executive@enterprise.com")
            subject = payload.get("subject", "AI Workflow Escalation Notice")
            return {
                "status": "success",
                "service": "SendGrid Email Dispatch",
                "recipient": recipient,
                "subject": subject,
                "dispatched_at": now_str,
                "message": f"Dispatched automated email to {recipient} with subject '{subject}'."
            }

        elif service_type == "jira":
            summary = payload.get("summary", "System Issue automatically flagged by Tech Support Agent")
            priority = payload.get("priority", "High")
            return {
                "status": "success",
                "service": "Jira Software Cloud",
                "issue_key": f"SUP-{int(datetime.datetime.utcnow().timestamp()) % 10000}",
                "priority": priority,
                "summary": summary,
                "created_at": now_str,
                "message": f"Logged Jira ticket [{priority}]: {summary}"
            }

        return {
            "status": "simulated",
            "service": service_type,
            "action": action,
            "timestamp": now_str,
            "message": f"Executed action {action} on service {service_type}"
        }
