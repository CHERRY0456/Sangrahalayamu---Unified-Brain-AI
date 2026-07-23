from typing import List

class PermissionEvaluator:
    @staticmethod
    def has_permission(role_permissions: List[str], required_permission: str) -> bool:
        """
        Validates if the user's role permissions contain the required permission tag.
        """
        return required_permission in role_permissions
