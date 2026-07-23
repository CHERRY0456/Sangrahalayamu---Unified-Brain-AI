from app.core.config import settings
from app.core.constants import ROLE_CLEARANCE_MAP, CLEARANCE_LEVELS, CLASSIFICATION_CLEARANCE_MAP

class ClearanceEvaluator:
    @staticmethod
    def get_user_clearance(role_name: str) -> str:
        """
        Resolves a user's role to their configured clearance level (e.g., LEVEL_1).
        """
        return ROLE_CLEARANCE_MAP.get(role_name, "LEVEL_1")

    @staticmethod
    def get_document_required_clearance(classification: str) -> str:
        """
        Resolves a document classification to the required clearance level setting.
        """
        return CLASSIFICATION_CLEARANCE_MAP.get(classification, "LEVEL_1")

    @staticmethod
    def is_clearance_sufficient(user_clearance: str, required_clearance: str) -> bool:
        """
        Validates if user_clearance priority level meets or exceeds the required_clearance.
        """
        levels = CLEARANCE_LEVELS
        user_priority = levels.get(user_clearance, 0)
        required_priority = levels.get(required_clearance, 0)
        return user_priority >= required_priority
