import re
from typing import Dict, Any, List
from app.models.user import User
from app.models.document import Document
from app.services.processing.models import ParsedDocument

class ProcessingMetadataGenerator:
    """
    Analyzes parsed document content to extract document understanding properties and structured domain metadata.
    """
    @staticmethod
    def generate(parsed_doc: ParsedDocument, uploader: User) -> Dict[str, Any]:
        text_content = parsed_doc.raw_markdown
        
        # 1. Resolve Document Type
        doc_type = "Standard Reference Manual"
        lower_name = parsed_doc.title.lower()
        if "sop" in lower_name or "procedure" in lower_name:
            doc_type = "Standard Operating Procedure (SOP)"
        elif "safety" in lower_name or "osha" in lower_name:
            doc_type = "Safety & Compliance Regulation"
        elif "matrix" in lower_name or "risk" in lower_name:
            doc_type = "Risk Assessment Matrix"
        elif "schedule" in lower_name or "timeline" in lower_name:
            doc_type = "Project Schedule / Timeline"

        # 2. Extract Reading Statistics
        words = re.findall(r"\w+", text_content)
        word_count = len(words)
        reading_time_mins = max(1, int(word_count / 200))  # Standard 200 WPM

        # 3. Detect Language
        # Simple stop word analysis
        lang = "en"
        if "der" in text_content.lower() or "und" in text_content.lower():
            lang = "de"
        elif "le" in text_content.lower() or "et" in text_content.lower():
            lang = "fr"

        # 4. Generate summary (extract first 3 paragraph elements or first 300 characters)
        summary = ""
        paragraphs = [el.text for el in parsed_doc.elements if el.type == "paragraph" and len(el.text) > 30]
        if paragraphs:
            summary = " ".join(paragraphs[:2])
            if len(summary) > 250:
                summary = summary[:247] + "..."
        else:
            summary = text_content[:250].strip().replace("\n", " ") + "..."

        # 5. Extract high-frequency keywords
        clean_words = [w.lower() for w in words if len(w) > 4 and w.lower() not in [
            "about", "their", "there", "would", "could", "should", "which", "these", "under"
        ]]
        freq_map = {}
        for cw in clean_words:
            freq_map[cw] = freq_map.get(cw, 0) + 1
        sorted_kws = sorted(freq_map.items(), key=lambda x: x[1], reverse=True)
        keywords = [kw[0] for kw in sorted_kws[:6]]

        # 6. Extract domain-specific metadata
        # Extract Equipment keys (e.g., EQ-101, BLR-402, VLV-501)
        equipment_matches = list(set(re.findall(r"\b(?:EQ|BLR|VLV|PMP)-\d+\b", text_content, re.IGNORECASE)))
        equipment_ids = [eq.upper() for eq in equipment_matches]
        
        # Scan for version tags (e.g. v1.2, Version 2.0)
        version_match = re.search(r"\b(?:v|version)\s*(\d+\.\d+)\b", text_content, re.IGNORECASE)
        version = version_match.group(1) if version_match else "1.0"
        
        # Scan for Author
        author_match = re.search(r"\bauthor\s*:\s*([\w\s]+)\b", text_content, re.IGNORECASE)
        author = author_match.group(1).strip() if author_match else uploader.name
        
        # Scan for Plant location
        plant_match = re.search(r"\b(?:plant|unit|facility)\s*([A-Za-z0-9\-]+)\b", text_content, re.IGNORECASE)
        plant = plant_match.group(1).strip() if plant_match else "Central Facility"

        # SOP classification type
        sop_type = "Operations"
        if "calibration" in lower_name:
            sop_type = "Calibration"
        elif "maintenance" in lower_name:
            sop_type = "Maintenance"
        elif "safety" in lower_name:
            sop_type = "Safety Compliance"

        return {
            "title": parsed_doc.title,
            "summary": summary,
            "keywords": keywords,
            "language": lang,
            "doc_type": doc_type,
            "stats": {
                "word_count": word_count,
                "reading_time_minutes": reading_time_mins
            },
            "domain_metadata": {
                "department": uploader.department,
                "equipment": equipment_ids,
                "sop_type": sop_type,
                "plant": plant,
                "version": version,
                "author": author
            }
        }

from sqlalchemy.orm import Session
from .stage import PipelineStage, PipelineContext

class MetadataStage(PipelineStage):
    """
    Pipeline stage wrapper for document metadata and understanding extraction.
    """
    def execute(self, context: PipelineContext, db: Session) -> None:
        if not context.parsed_doc:
            raise ValueError("Parser stage must run before Metadata stage.")
        context.metadata = ProcessingMetadataGenerator.generate(context.parsed_doc, context.uploader)

