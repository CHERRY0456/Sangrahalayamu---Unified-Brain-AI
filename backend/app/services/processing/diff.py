import difflib
import logging
from typing import List, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import select
from fastapi import HTTPException, status

from app.models.document import Document

logger = logging.getLogger("sangrahalayamu.processing.diff")

class DocumentDiffEngine:
    """
    Document Clause/Version Diffing Engine.
    
    Compares two document revisions (e.g. Revision A vs. Revision B) line-by-line,
    clause-by-clause, or section-by-section to generate structured additions (+),
    deletions (-), and modifications (~).
    """
    
    @staticmethod
    def compare_documents(db: Session, doc_id_a: int, doc_id_b: int) -> Dict[str, Any]:
        doc_a = db.scalar(select(Document).where(Document.id == doc_id_a, Document.is_active == True))
        doc_b = db.scalar(select(Document).where(Document.id == doc_id_b, Document.is_active == True))
        
        if not doc_a or not doc_b:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="One or both requested document IDs for comparison were not found."
            )

        text_a = DocumentDiffEngine._extract_raw_markdown(doc_a)
        text_b = DocumentDiffEngine._extract_raw_markdown(doc_b)

        lines_a = [line.strip() for line in text_a.split("\n") if line.strip()]
        lines_b = [line.strip() for line in text_b.split("\n") if line.strip()]

        differ = difflib.SequenceMatcher(None, lines_a, lines_b)
        diff_chunks = []
        
        added_count = 0
        deleted_count = 0
        modified_count = 0
        unchanged_count = 0

        for tag, i1, i2, j1, j2 in differ.get_opcodes():
            if tag == "equal":
                for line in lines_a[i1:i2]:
                    unchanged_count += 1
                    diff_chunks.append({
                        "change_type": "unchanged",
                        "content": line
                    })
            elif tag == "replace":
                modified_count += max(i2 - i1, j2 - j1)
                for line_a in lines_a[i1:i2]:
                    diff_chunks.append({
                        "change_type": "removed",
                        "content": line_a
                    })
                for line_b in lines_b[j1:j2]:
                    diff_chunks.append({
                        "change_type": "added",
                        "content": line_b
                    })
            elif tag == "delete":
                deleted_count += (i2 - i1)
                for line in lines_a[i1:i2]:
                    diff_chunks.append({
                        "change_type": "removed",
                        "content": line
                    })
            elif tag == "insert":
                added_count += (j2 - j1)
                for line in lines_b[j1:j2]:
                    diff_chunks.append({
                        "change_type": "added",
                        "content": line
                    })

        similarity_ratio = round(differ.ratio() * 100, 2)

        return {
            "document_a": {
                "id": doc_a.id,
                "name": doc_a.name,
                "uuid": doc_a.uuid
            },
            "document_b": {
                "id": doc_b.id,
                "name": doc_b.name,
                "uuid": doc_b.uuid
            },
            "similarity_ratio_pct": similarity_ratio,
            "stats": {
                "additions": added_count,
                "deletions": deleted_count,
                "modifications": modified_count,
                "unchanged": unchanged_count
            },
            "clause_diffs": diff_chunks
        }

    @staticmethod
    def _extract_raw_markdown(doc: Document) -> str:
        if not doc.doc_metadata:
            return doc.name
        payload = doc.doc_metadata.get("processed_payload", {})
        summary = payload.get("summary", "")
        chunks = payload.get("chunks", [])
        
        chunk_texts = [c.get("text", "") for c in chunks if isinstance(c, dict)]
        if chunk_texts:
            return "\n\n".join(chunk_texts)
        return summary or doc.name

doc_diff_engine = DocumentDiffEngine()
