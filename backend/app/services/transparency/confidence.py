from .models import ConfidenceAnalysis

class ConfidenceEvaluator:
    @staticmethod
    def analyze(confidence_score: float, warnings: list) -> ConfidenceAnalysis:
        """
        Determines the explainable confidence analysis report.
        """
        if confidence_score >= 0.90 and "HALLUCINATION_DETECTED" not in warnings:
            reason = (
                "High confidence: All response statements have been verified as grounded "
                "against the retrieved document chunks, with full citation matches and no safety warnings."
            )
        elif "HALLUCINATION_DETECTED" in warnings or confidence_score <= 0.20:
            reason = (
                "Low confidence: Grounding checks failed or detected ungrounded claims during LLM output. "
                "The system generated a safe fallback response."
            )
        else:
            reason = (
                "Medium confidence: Grounded checks passed, but warnings were generated during processing, "
                "such as low semantic match scores or lack of graph expansions."
            )

        return ConfidenceAnalysis(
            confidence=confidence_score,
            reason=reason,
            provenance="validator"
        )
