from pydantic import BaseModel, Field
from typing import Dict, Any, List, Optional
from datetime import datetime
from enum import Enum

# --- Node Types ---
class NodeType(str, Enum):
    Document = "Document"
    Chunk = "Chunk"
    Asset = "Asset"
    Equipment = "Equipment"
    Pump = "Pump"
    Valve = "Valve"
    Motor = "Motor"
    Sensor = "Sensor"
    Pipe = "Pipe"
    Procedure = "Procedure"
    MaintenanceTask = "MaintenanceTask"
    Inspection = "Inspection"
    SafetyStandard = "SafetyStandard"
    Risk = "Risk"
    Department = "Department"
    Person = "Person"
    Location = "Location"
    Project = "Project"
    FailureMode = "FailureMode"
    Recommendation = "Recommendation"
    Regulation = "Regulation"
    Incident = "Incident"

# --- Relationship Types ---
class RelationshipType(str, Enum):
    CONNECTED_TO = "CONNECTED_TO"
    LOCATED_IN = "LOCATED_IN"
    PART_OF = "PART_OF"
    INSPECTED_BY = "INSPECTED_BY"
    MAINTAINED_BY = "MAINTAINED_BY"
    DESCRIBES = "DESCRIBES"
    AFFECTS = "AFFECTS"
    CAUSES = "CAUSES"
    MITIGATES = "MITIGATES"
    USES = "USES"
    REFERENCES = "REFERENCES"
    DEPENDS_ON = "DEPENDS_ON"
    RELATED_TO = "RELATED_TO"
    VIOLATES = "VIOLATES"
    COMPLIES_WITH = "COMPLIES_WITH"

class GraphNode(BaseModel):
    id: str = Field(..., description="Unique node identifier")
    labels: List[NodeType] = Field(..., description="Node labels (can have multiple)")
    properties: Dict[str, Any] = Field(default_factory=dict, description="Node properties")

class GraphRelationship(BaseModel):
    id: Optional[str] = None
    source_id: str
    target_id: str
    type: RelationshipType
    properties: Dict[str, Any] = Field(default_factory=dict)
    confidence: float = 1.0
    provenance: Optional[Dict[str, Any]] = None

class GraphPath(BaseModel):
    nodes: List[GraphNode]
    relationships: List[GraphRelationship]
