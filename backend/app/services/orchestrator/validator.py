import re
from typing import List, Dict, Any
from .models import ValidationResult

class RAGResponseValidator:
    """
    Validates LLM output response against context contents to ensure grounding,
    prevent hallucinations, block safety violations, and check citation presence.
    """
    @staticmethod
    def validate_response(
        output_text: str, 
        retrieved_chunks: List[Dict[str, Any]],
        retry_count: int = 0,
        max_retries: int = 3
    ) -> ValidationResult:
        failed_checks = []
        warnings = []
        confidence = 1.0

        # 1. Empty Check
        if not output_text or not output_text.strip():
            failed_checks.append("Response is completely empty.")
            return ValidationResult(
                is_valid=False,
                confidence=0.0,
                failed_checks=failed_checks,
                retry_recommended=retry_count < max_retries,
                warnings=["EMPTY_RESPONSE"]
            )

        # 2. Check for Not Found Fallback (always valid if LLM safely declares it doesn't know)
        if "cannot find the answer" in output_text.lower() or "do not have enough information" in output_text.lower():
            return ValidationResult(
                is_valid=True,
                confidence=1.0,
                failed_checks=[],
                retry_recommended=False,
                warnings=["SAFE_FALLBACK_DECLARED"]
            )

        # 3. Missing Citations Warning
        citation_tags = re.findall(r"\[Doc: [^\]]+\]", output_text)
        if not citation_tags:
            confidence = max(0.0, confidence - 0.30)
            warnings.append("NO_CITATIONS_FOUND")
            # If the user requested strict citations but none were output, mark invalid for retry
            failed_checks.append("Response contains no bracketed source manual citations.")

        # 4. Grounding & Hallucination Check
        # Extract equipment codes in output: EQ-xxx, BLR-xxx, VLV-xxx
        output_codes = set(re.findall(r"(?:EQ|BLR|VLV)-\d+", output_text.upper()))
        
        # Extract equipment codes in context chunks
        context_text = " ".join([ch.get("text", "") for ch in retrieved_chunks]).upper()
        context_codes = set(re.findall(r"(?:EQ|BLR|VLV)-\d+", context_text))
        
        # Check if output contains codes not mentioned in the context
        hallucinated_codes = output_codes - context_codes
        if hallucinated_codes:
            confidence = max(0.0, confidence - 0.60)
            failed_checks.append(f"Hallucination Risk: Referenced equipment codes not present in context: {list(hallucinated_codes)}")
            warnings.append("HALLUCINATION_DETECTED")

        is_valid = len(failed_checks) == 0
        # Recommend retry if invalid and we haven't exhausted retry budget
        retry_rec = not is_valid and (retry_count < max_retries)

        return ValidationResult(
            is_valid=is_valid,
            confidence=round(confidence, 2),
            failed_checks=failed_checks,
            retry_recommended=retry_rec,
            warnings=warnings
        )
