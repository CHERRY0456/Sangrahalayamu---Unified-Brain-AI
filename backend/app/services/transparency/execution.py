from app.services.orchestrator.models import AIResponse
from .models import ExecutionTrace

class ExecutionTimingTracer:
    @staticmethod
    def trace(ai_response: AIResponse) -> ExecutionTrace:
        meta = ai_response.generation_metadata
        
        provider = meta.provider if meta else "AWSBedrock"
        model = meta.model if meta else "unknown"
        template = meta.prompt_template if meta else "enterprise_default"

        return ExecutionTrace(
            latencies=ai_response.latency,
            provider=provider,
            model=model,
            prompt_template=template,
            provenance="orchestrator_tracker"
        )
