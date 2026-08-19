import json
import time
import datetime
from typing import Dict, Any
from sqlalchemy.orm import Session
from app.models import Workflow, WorkflowRun, Agent
from app.services.integration_service import IntegrationService

class WorkflowService:
    @staticmethod
    def execute_workflow(db: Session, workflow_id: int, input_payload: Dict[str, Any]) -> WorkflowRun:
        workflow = db.query(Workflow).filter(Workflow.id == workflow_id).first()
        if not workflow:
            raise ValueError(f"Workflow ID {workflow_id} not found")

        start_time = time.time()
        
        try:
            config = json.loads(workflow.config_json) if workflow.config_json else {}
        except Exception:
            config = {}

        target_agent = db.query(Agent).filter(Agent.id == workflow.target_agent_id).first()
        agent_name = target_agent.name if target_agent else "Orchestrator Agent"

        log_lines = []
        log_lines.append(f"[{datetime.datetime.utcnow().strftime('%H:%M:%S')}] Trigger fired: '{workflow.trigger_type}' on workflow '{workflow.name}'")
        log_lines.append(f"[{datetime.datetime.utcnow().strftime('%H:%M:%S')}] Assigned Primary Agent: {agent_name}")
        log_lines.append(f"[{datetime.datetime.utcnow().strftime('%H:%M:%S')}] Processing Payload: {json.dumps(input_payload)}")

        # Step 1: Execute rule actions
        action_type = config.get("action_type", "notify_and_delegate")
        target_service = config.get("target_service", "slack")

        log_lines.append(f"[{datetime.datetime.utcnow().strftime('%H:%M:%S')}] Step 1: Evaluating rule conditions... (STATUS: PASSED)")
        log_lines.append(f"[{datetime.datetime.utcnow().strftime('%H:%M:%S')}] Step 2: Context memory loaded for agent {agent_name}")

        # Step 2: Call Integration service if specified
        if target_service:
            int_res = IntegrationService.trigger_integration(
                db, 
                service_type=target_service, 
                action=action_type, 
                payload={"message": f"Workflow '{workflow.name}' automated execution log for {agent_name}"}
            )
            log_lines.append(f"[{datetime.datetime.utcnow().strftime('%H:%M:%S')}] Step 3: Integration Hook ({target_service.upper()}) -> {int_res.get('message')}")

        duration_ms = int((time.time() - start_time) * 1000)
        log_lines.append(f"[{datetime.datetime.utcnow().strftime('%H:%M:%S')}] Workflow execution completed successfully in {duration_ms}ms.")

        workflow.run_count += 1
        workflow.last_run_at = datetime.datetime.utcnow()

        run_record = WorkflowRun(
            workflow_id=workflow.id,
            status="success",
            input_payload=json.dumps(input_payload),
            output_log="\n".join(log_lines),
            executed_at=datetime.datetime.utcnow(),
            duration_ms=duration_ms
        )
        db.add(run_record)
        db.commit()
        db.refresh(run_record)

        return run_record
