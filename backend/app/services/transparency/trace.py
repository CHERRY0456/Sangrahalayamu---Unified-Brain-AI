"""
Reasoning trace collector for step-by-step explainability.
"""
from typing import List, Dict, Any
from datetime import datetime, timezone


class ReasoningTrace:
    def __init__(self):
        self.steps: List[Dict[str, Any]] = []

    def add_step(self, stage: str, description: str, details: Dict[str, Any] = None):
        """Append a reasoning step to the trace."""
        self.steps.append({
            "stage": stage,
            "description": description,
            "details": details or {},
            "timestamp": datetime.now(timezone.utc).isoformat()
        })

    def get_trace(self) -> List[Dict[str, Any]]:
        """Return full recorded trace steps."""
        return self.steps
