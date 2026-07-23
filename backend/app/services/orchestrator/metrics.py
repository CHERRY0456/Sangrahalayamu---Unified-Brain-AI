import time
from typing import Dict, Any, Optional

class OrchestrationMetricsTracker:
    """
    Measures and compiles step-by-step latency profiles and retry metrics.
    """
    def __init__(self):
        self.start_time = time.time()
        self.retrieval_latency: float = 0.0
        self.prompt_latency: float = 0.0
        self.llm_latency: float = 0.0
        self.validation_latency: float = 0.0
        self.total_latency: float = 0.0
        self.retry_count: int = 0

    def record_retrieval(self, duration: float):
        self.retrieval_latency = round(duration, 4)

    def record_prompt(self, duration: float):
        self.prompt_latency = round(duration, 4)

    def record_llm(self, duration: float):
        self.llm_latency = round(duration, 4)

    def record_validation(self, duration: float):
        self.validation_latency = round(duration, 4)

    def record_retry(self):
        self.retry_count += 1

    def finalize(self) -> Dict[str, float]:
        self.total_latency = round(time.time() - self.start_time, 4)
        return {
            "retrieval_seconds": self.retrieval_latency,
            "prompt_assembly_seconds": self.prompt_latency,
            "llm_generation_seconds": self.llm_latency,
            "validation_seconds": self.validation_latency,
            "total_request_seconds": self.total_latency,
            "retry_count": float(self.retry_count)
        }
