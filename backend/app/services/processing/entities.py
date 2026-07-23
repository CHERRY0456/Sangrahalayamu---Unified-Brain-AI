import re
import logging
from datetime import datetime
from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session

from app.services.processing.models import ExtractedEntity, ProvenanceRecord, LayoutTreeNode
from .stage import PipelineStage, PipelineContext

logger = logging.getLogger("sangrahalayamu.processing.entities")


def normalize_entity_name(name: str) -> str:
    """
    Normalizes industrial entity names and asset tags to a canonical form.
    E.g. "Pump-101A" -> "PMP-101A", "P101A" -> "PMP-101A", "Pump 101 A" -> "PMP-101A".
    """
    cleaned = name.strip()
    if not cleaned:
        return name

    # Convert to uppercase and strip common symbols
    val = cleaned.upper()
    val_clean = re.sub(r"[^A-Z0-9]", "", val)  # e.g., PUMP101A, P101A, BOILERROOM

    # Pattern 1: Match standard industrial tag prefixes followed by numbers
    # Group 1: Prefix (PUMP, PMP, P, BOILER, BLR, B, VALVE, VLV, V, MOTOR, MTR, M, SENSOR, SNR, S)
    # Group 2: Number code (e.g. 101, 303, 402)
    # Group 3: Optional suffix letter (e.g. A, B)
    pattern = r"^(PUMP|PMP|P|BOILER|BLR|B|VALVE|VLV|V|MOTOR|MTR|M|SENSOR|SNR|S|EQUIP|EQ|E)(\d+)([A-Z]?)$"
    match = re.match(pattern, val_clean)
    if match:
        prefix_raw = match.group(1)
        num_code = match.group(2)
        suffix = match.group(3) or ""

        # Map to unified canonical prefixes
        prefix_map = {
            "PUMP": "PMP", "PMP": "PMP", "P": "PMP",
            "BOILER": "BLR", "BLR": "BLR", "B": "BLR",
            "VALVE": "VLV", "VLV": "VLV", "V": "VLV",
            "MOTOR": "MTR", "MTR": "MTR", "M": "MTR",
            "SENSOR": "SNR", "SNR": "SNR", "S": "SNR",
            "EQUIP": "EQP", "EQ": "EQP", "E": "EQP"
        }
        canonical_prefix = prefix_map.get(prefix_raw, "EQP")
        return f"{canonical_prefix}-{num_code}{suffix}"

    # Return standard clean format for other values
    return cleaned


class ProcessingEntityExtractor:
    """
    Extracts enterprise assets, components, safety standards, risks,
    and personnel directly from the preserved document layout tree.
    """

    @staticmethod
    def extract_from_node(
        node: LayoutTreeNode,
        doc_id: int,
        parser_name: str,
        entities: List[ExtractedEntity]
    ) -> None:
        """
        Recursively traverses the layout tree node and extracts entities
        from text properties, appending provenance records.
        """
        text = node.text
        page = node.page_numbers[0] if node.page_numbers else 1
        section = node.text if node.type == "heading" else "Content Block"

        def add_entity(name: str, label: str, meta: Dict[str, Any]) -> None:
            canonical_name = normalize_entity_name(name)
            # Avoid duplicate entities in the same scope
            if not any(e.name == canonical_name and e.label == label for e in entities):
                prov = ProvenanceRecord(
                    document_id=doc_id,
                    page=page,
                    section=section,
                    parser=parser_name,
                    extraction_method="regex_rules",
                    confidence=node.confidence,
                    timestamp=datetime.utcnow()
                )
                entities.append(ExtractedEntity(
                    name=canonical_name,
                    label=label,
                    metadata=meta,
                    provenance=prov
                ))

        # 1. Equipment Tag extraction (e.g., PMP-303, EQ-101, BLR-402, P101A, Pump-101A)
        # Match alphanumeric tag structures
        tags = re.findall(r"\b(?:EQ|BLR|VLV|PMP|P|B|V|MTR|SNR|PMP)-\d+[A-Z]?\b|\b[PVB]\d{3}[A-Z]?\b", text, re.IGNORECASE)
        for tag in tags:
            label = "Equipment"
            if tag.upper().startswith("B") or "BLR" in tag.upper():
                label = "Machine"
            add_entity(tag, label, {"tag": tag})

        # 2. Components vocab
        components_vocab = ["valve", "turbine", "actuator", "boiler", "compressor", "generator", "sensor", "pump", "switch", "motor"]
        for comp in components_vocab:
            if re.search(r"\b" + re.escape(comp) + r"s?\b", text, re.IGNORECASE):
                add_entity(comp.capitalize(), "Component", {"category": "Industrial"})

        # 3. Safety/Compliance
        safety_matches = re.findall(r"\b(?:OSHA|ISO|ANSI|ASME)\s*[\d\.]+\b", text, re.IGNORECASE)
        for s_ref in safety_matches:
            add_entity(s_ref, "SafetyStandard", {"type": "Regulation"})

        # 4. Locations
        locations_vocab = ["Boiler Room", "Unit 4", "Control Room", "Turbine Deck", "Plant A", "Plant B", "Warehouse A"]
        for loc in locations_vocab:
            if re.search(r"\b" + re.escape(loc) + r"\b", text, re.IGNORECASE):
                add_entity(loc, "Location", {"site": "Main Campus"})

        # 5. Departments
        depts_vocab = ["Operations", "Maintenance", "Compliance", "Engineering", "Executive"]
        for dept in depts_vocab:
            if re.search(r"\b" + re.escape(dept) + r"\b", text, re.IGNORECASE):
                add_entity(dept, "Department", {"org": "Sangrahalayamu"})

        # 6. Employee Names
        employees = ["Ravi Kumar", "Priya Sharma", "Arjun Mehta", "Neha Iyer", "Vikram Rao"]
        for emp in employees:
            if re.search(r"\b" + re.escape(emp) + r"\b", text, re.IGNORECASE):
                add_entity(emp, "Employee", {"role": "Staff"})

        # Recurse children
        for child in node.children:
            ProcessingEntityExtractor.extract_from_node(child, doc_id, parser_name, entities)


class EntitiesStage(PipelineStage):
    """
    Ingestion pipeline stage that extracts entities from the layout tree.
    """
    def execute(self, context: PipelineContext, db: Session) -> None:
        parser_result = context.extra_state.get("parser_result")
        if not parser_result:
            raise ValueError("Parser stage must run before Entities stage.")
        
        extracted: List[ExtractedEntity] = []
        ProcessingEntityExtractor.extract_from_node(
            parser_result.layout_root,
            context.document_id,
            parser_result.metadata.get("parser", "DoclingParser"),
            extracted
        )
        context.entities = extracted
        logger.info(f"[EntitiesStage] Extracted {len(extracted)} entities with provenance records.")
