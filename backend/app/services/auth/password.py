import re
from fastapi import HTTPException, status

class PasswordService:
    @staticmethod
    def validate_password_strength(password: str) -> None:
        """
        Enforces corporate secure password policy parameters.
        - Minimum length of 6 characters
        - Must contain at least one digit
        - Must contain at least one alphabet character
        """
        if len(password) < 6:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Password must be at least 6 characters long."
            )
        
        if not re.search(r"[A-Za-z]", password):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Password must contain at least one alphabetical letter."
            )

        if not re.search(r"\d", password):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Password must contain at least one numeric digit."
            )
