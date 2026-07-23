import re
from typing import List, Dict, Any
from .models import Citation

class CitationGenerator:
    """
    Parses citation tokens in LLM text responses and maps them back to the source chunks.
    """
    @staticmethod
    def generate_citations(output_text: str, context_chunks: List[Dict[str, Any]]) -> List[Citation]:
        citations = []
        if not output_text or not context_chunks:
            return citations

        # Match '[Doc: <filename>]' format
        doc_citations = set(re.findall(r"\[Doc: ([^\]]+)\]", output_text))
        
        for doc_name in doc_citations:
            # Find the first chunk in context matching this document name
            matched_chunk = None
            for ch in context_chunks:
                if ch.get("document_name", "").lower() == doc_name.lower():
                    matched_chunk = ch
                    break
            
            if matched_chunk:
                citations.append(Citation(
                    document_name=matched_chunk.get("document_name"),
                    section=matched_chunk.get("section", "Introduction"),
                    page=matched_chunk.get("page_numbers", [1])[0],
                    chunk_id=matched_chunk.get("chunk_id", ""),
                    matched_text=matched_chunk.get("text", "")[:200] + "..."
                ))
                
        return citations
