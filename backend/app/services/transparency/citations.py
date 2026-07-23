import re
from typing import List, Dict, Any
from app.services.retrieval.models import HybridRetrievalPackage
from .models import CitationSummary

class CitationAuditor:
    @staticmethod
    def audit(
        output_text: str, 
        retrieved_chunks: List[Any], 
        citations_list: List[Any]
    ) -> CitationSummary:
        # Match bracketed tags '[Doc: <filename>]'
        doc_citations = re.findall(r"\[Doc: ([^\]]+)\]", output_text)
        citation_count = len(doc_citations)

        # Detect duplicate citations in output
        duplicate_count = 0
        seen_citations = set()
        for doc in doc_citations:
            if doc in seen_citations:
                duplicate_count += 1
            seen_citations.add(doc)

        # Detect unused retrieved chunks
        unused_ids = []
        cited_filenames = {doc.lower().strip() for doc in doc_citations}
        for chunk in retrieved_chunks:
            doc_name = chunk.document_name.lower().strip()
            if doc_name not in cited_filenames:
                unused_ids.append(chunk.chunk_id)

        # Flag missing citations if output text makes claims but has no tags
        has_claims = any(kw in output_text.lower() for kw in ["boiler", "valve", "calibration", "procedure"])
        missing_citations = has_claims and (citation_count == 0) and ("cannot find" not in output_text.lower())

        return CitationSummary(
            citation_count=citation_count,
            duplicate_citations_count=duplicate_count,
            unused_retrieved_chunks=unused_ids,
            missing_citations=missing_citations,
            provenance="citation_auditor"
        )
