import re
import logging
from datetime import datetime
from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session

from app.services.processing.models import (
    ExtractedEntity,
    ExtractedRelationship,
    ProvenanceRecord,
    LayoutTreeNode
)
from .entities import normalize_entity_name
from .stage import PipelineStage, PipelineContext

logger = logging.getLogger("sangrahalayamu.processing.relationships")


class ProcessingRelationshipExtractor:
    """
    Identifies semantic relationships between extracted entities within layout nodes.
    """

    @staticmethod
    def extract_from_node(
        node: LayoutTreeNode,
        entities: List[ExtractedEntity],
        doc_id: int,
        parser_name: str,
        relationships: List[ExtractedRelationship]
    ) -> None:
        """
        Recursively extracts relationships from text within layout tree nodes.
        Uses proximity matching within a single layout block scope.
        """
        text = node.text
        text_lower = text.lower()
        page = node.page_numbers[0] if node.page_numbers else 1
        section = node.text if node.type == "heading" else "Content Block"

        # Find entities present in this block
        present_entities = []
        for ent in entities:
            # We search for the normalized form or original tokens in the text
            # E.g. search for normalized tag like "PMP-303" or matching fragments
            raw_pattern = ent.name.replace("-", "[- ]?")
            if re.search(r"\b" + raw_pattern + r"\b", text, re.IGNORECASE):
                present_entities.append(ent)

        # Proximity matches
        equipment_nodes = [e for e in present_entities if e.label in ["Equipment", "Machine"]]
        employee_nodes = [e for e in present_entities if e.label == "Employee"]
        location_nodes = [e for e in present_entities if e.label == "Location"]
        dept_nodes = [e for e in present_entities if e.label == "Department"]
        standard_nodes = [e for e in present_entities if e.label == "SafetyStandard"]
        component_nodes = [e for e in present_entities if e.label == "Component"]

        def add_relationship(source: str, target: str, rel_type: str, meta: Dict[str, Any]) -> None:
            # Enforce canonical name normalization
            canonical_source = normalize_entity_name(source)
            canonical_target = normalize_entity_name(target)

            if canonical_source == canonical_target:
                return

            # Avoid duplicates
            if not any(r.source == canonical_source and r.target == canonical_target and r.type == rel_type for r in relationships):
                prov = ProvenanceRecord(
                    document_id=doc_id,
                    page=page,
                    section=section,
                    parser=parser_name,
                    extraction_method="regex_proximity_rules",
                    confidence=node.confidence,
                    timestamp=datetime.utcnow()
                )
                relationships.append(ExtractedRelationship(
                    source=canonical_source,
                    target=canonical_target,
                    type=rel_type,
                    metadata=meta,
                    provenance=prov
                ))

        # 1. connected_to (e.g. pump connected to valve, pump attached to sensor)
        if len(equipment_nodes) >= 2 and any(kw in text_lower for kw in ["connect", "feed", "flow", "pipe", "link"]):
            for i in range(len(equipment_nodes) - 1):
                add_relationship(equipment_nodes[i].name, equipment_nodes[i+1].name, "connected_to", {"context": "Flow pipe linkage"})

        if equipment_nodes and component_nodes and any(kw in text_lower for kw in ["connect", "attach", "mount", "fit", "use"]):
            for eq in equipment_nodes:
                for comp in component_nodes:
                    add_relationship(eq.name, comp.name, "connected_to", {"context": f"Component attached: {comp.name}"})

        # 2. maintains (Employee -> Equipment)
        if employee_nodes and equipment_nodes:
            if any(kw in text_lower for kw in ["maintain", "check", "inspect", "calibrate", "repair", "service", "alert"]):
                for emp in employee_nodes:
                    for eq in equipment_nodes:
                        add_relationship(emp.name, eq.name, "maintains", {"action": "maintenance_alert_or_service"})

        # 3. follows (Equipment -> SafetyStandard)
        if equipment_nodes and standard_nodes:
            if any(kw in text_lower for kw in ["follow", "comply", "require", "standard", "regulation", "govern"]):
                for eq in equipment_nodes:
                    for std in standard_nodes:
                        add_relationship(eq.name, std.name, "follows", {"type": "Standard Compliance Checklist"})

        # 4. located_in (Equipment -> Location)
        if equipment_nodes and location_nodes:
            if any(kw in text_lower for kw in ["located", "placed", "installed", "room", "deck", "area"]):
                for eq in equipment_nodes:
                    for loc in location_nodes:
                        add_relationship(eq.name, loc.name, "located_in", {"site": loc.name})

        # 5. belongs_to (Employee -> Department)
        if employee_nodes and dept_nodes:
            for emp in employee_nodes:
                for dept in dept_nodes:
                    add_relationship(emp.name, dept.name, "belongs_to", {"org": dept.name})

        # Recurse children
        for child in node.children:
            ProcessingRelationshipExtractor.extract_from_node(child, entities, doc_id, parser_name, relationships)


class RelationshipsStage(PipelineStage):
    """
    Ingestion pipeline stage mapping relationships between extracted entities.
    """
    def execute(self, context: PipelineContext, db: Session) -> None:
        parser_result = context.extra_state.get("parser_result")
        if not parser_result or context.entities is None:
            raise ValueError("Parser and Entities stages must run before Relationships stage.")

        extracted_rels: List[ExtractedRelationship] = []
        ProcessingRelationshipExtractor.extract_from_node(
            parser_result.layout_root,
            context.entities,
            context.document_id,
            parser_result.metadata.get("parser", "DoclingParser"),
            extracted_rels
        )
        context.relationships = extracted_rels
        logger.info(f"[RelationshipsStage] Identified {len(extracted_rels)} relationships with provenance records.")
