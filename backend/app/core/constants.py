# Security & Access Control
CLEARANCE_LEVELS: dict[str, int] = {
    "LEVEL_1": 1,
    "LEVEL_2": 2,
    "LEVEL_3": 3,
    "LEVEL_4": 4,
    "LEVEL_5": 5,
}

ROLE_CLEARANCE_MAP: dict[str, str] = {
    "Field Technician": "LEVEL_1",
    "Maintenance Engineer": "LEVEL_2",
    "Project Manager": "LEVEL_3",
    "Regulatory & Compliance Manager": "LEVEL_4",
    "Director / Executive": "LEVEL_5"
}

CLASSIFICATION_CLEARANCE_MAP: dict[str, str] = {
    "Public": "LEVEL_1",
    "Internal": "LEVEL_1",
    "Confidential": "LEVEL_2",
    "Restricted": "LEVEL_4",
    "Executive": "LEVEL_5"
}
