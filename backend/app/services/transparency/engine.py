import logging
from sqlalchemy.orm import Session

from app.core.config import settings
from app.models.user import User
from app.services.retrieval.models import HybridRetrievalPackage
from app.services.orchestrator.models import AIResponse

from .models import TransparencyReport
from .confidence import ConfidenceEvaluator
from .retrieval import RetrievalExplanationEngine
from .permissions import PermissionComplianceEngine
from .citations import CitationAuditor
from .warnings import SystemWarningEngine
from .execution import ExecutionTimingTracer

logger = logging.getLogger("sangrahalayamu.transparency.engine")

class TransparencyEngine:
    @staticmethod
    def generate_explanation(
        db: Session,
        ai_response: AIResponse,
        retrieval_package: HybridRetrievalPackage,
        user: User
    ) -> TransparencyReport:
        """
        Gathers summaries from RAG stages to compile a complete Explainability report.
        Handles Production/Debug scrubbing rules.
        """
        # 1. Compile individual sections
        conf_report = ConfidenceEvaluator.analyze(
            confidence_score=ai_response.confidence,
            warnings=ai_response.warnings
        )
        
        ret_report = RetrievalExplanationEngine.generate(retrieval_package)
        
        perm_report = PermissionComplianceEngine.generate(
            db=db,
            user=user,
            retrieval_package=retrieval_package
        )
        
        cit_report = CitationAuditor.audit(
            output_text=ai_response.answer,
            retrieved_chunks=retrieval_package.chunks,
            citations_list=ai_response.citations
        )
        
        system_warnings = SystemWarningEngine.compile_warnings(
            ai_response=ai_response,
            retrieval_package=retrieval_package,
            permissions=perm_report
        )
        
        exec_trace = ExecutionTimingTracer.trace(ai_response)

        # Assemble sources reference list
        sources_list = [
            {
                "document_id": src.get("document_id"),
                "document_name": src.get("document_name"),
                "section": src.get("section")
            } for src in ai_response.sources
        ]

        # Debug-only diagnostics data
        debug_diagnostics = None
        if settings.flags.enable_transparency:
            debug_diagnostics = {
                "validation_attempts": ai_response.generation_metadata.validation_attempts if ai_response.generation_metadata else 1,
                "retrieval_raw_summary": retrieval_package.metadata_summary,
                "raw_token_usage": ai_response.token_usage,
                "validation_warnings": ai_response.warnings
            }

        # 2. Production mode scrubbing logic (Ticket #9 constraint)
        # If debug mode is disabled, hide latencies trace and internal diagnostics payload
        final_trace = exec_trace if settings.flags.enable_transparency or settings.flags.enable_transparency else None

        report = TransparencyReport(
            confidence_analysis=conf_report,
            retrieval=ret_report,
            permissions=perm_report,
            citations=cit_report,
            warnings=system_warnings,
            execution_trace=final_trace,
            sources=sources_list,
            diagnostics=debug_diagnostics,
            provenance="transparency_engine"
        )

        return report

# Global instance for controller/endpoint import
transparency_engine = TransparencyEngine()
