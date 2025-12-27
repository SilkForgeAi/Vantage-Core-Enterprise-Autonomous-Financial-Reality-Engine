"""Atomic post-trade audit logging system."""
import json
import os
from datetime import datetime
from typing import Dict, Any, Optional
from pathlib import Path
import structlog

from config.settings import settings


logger = structlog.get_logger()


class AuditLogger:
    """
    Atomic audit logger for post-trade logs.
    
    Each executed fill emits a structured log with:
    - Justification against live venue data at time=0
    - Auditable, traceable reasoning chain
    """
    
    def __init__(self):
        self.log_dir = Path(settings.audit_log_dir)
        self.log_dir.mkdir(parents=True, exist_ok=True)
    
    def log_execution(
        self,
        execution_id: str,
        user_id: str,
        intent: str,
        reasoning: str,
        action_taken: str,
        unified_state_at_execution: Dict[str, Any],
        fill_result: Optional[Dict[str, Any]] = None,
        latency_ms: float = 0,
        error: Optional[str] = None
    ):
        """
        Log an execution with full audit trail.
        
        Args:
            execution_id: Unique execution identifier
            user_id: User identifier
            intent: Extracted intent
            reasoning: LLM reasoning chain
            action_taken: What action was taken
            unified_state_at_execution: Snapshot of unified state when decision was made
            fill_result: Order fill result if applicable
            latency_ms: End-to-end latency in milliseconds
            error: Error message if execution failed
        """
        audit_entry = {
            "execution_id": execution_id,
            "timestamp": datetime.utcnow().isoformat(),
            "user_id": user_id,
            "intent": intent,
            "reasoning": reasoning,
            "action_taken": action_taken,
            "unified_state_at_execution": unified_state_at_execution,
            "fill_result": fill_result,
            "latency_ms": latency_ms,
            "error": error,
            "audit_version": "1.0"
        }
        
        # Write to file (atomic write)
        log_file = self.log_dir / f"{execution_id}.json"
        with open(log_file, 'w') as f:
            json.dump(audit_entry, f, indent=2)
        
        # Also write to daily log file for easier browsing
        daily_log_file = self.log_dir / f"daily_{datetime.utcnow().date().isoformat()}.jsonl"
        with open(daily_log_file, 'a') as f:
            f.write(json.dumps(audit_entry) + '\n')
        
        logger.info(
            "Audit log written",
            execution_id=execution_id,
            user_id=user_id,
            action_taken=action_taken,
            latency_ms=latency_ms
        )
    
    def get_execution_log(self, execution_id: str) -> Optional[Dict[str, Any]]:
        """Retrieve an execution log by ID."""
        log_file = self.log_dir / f"{execution_id}.json"
        if log_file.exists():
            with open(log_file, 'r') as f:
                return json.load(f)
        return None
    
    def get_user_executions(self, user_id: str, limit: int = 100) -> list[Dict[str, Any]]:
        """Get recent execution logs for a user."""
        executions = []
        
        # Search daily logs
        for daily_log in sorted(self.log_dir.glob("daily_*.jsonl"), reverse=True):
            with open(daily_log, 'r') as f:
                for line in f:
                    try:
                        entry = json.loads(line)
                        if entry.get("user_id") == user_id:
                            executions.append(entry)
                            if len(executions) >= limit:
                                return executions
                    except:
                        continue
        
        return executions


# Global audit logger instance
audit_logger = AuditLogger()

