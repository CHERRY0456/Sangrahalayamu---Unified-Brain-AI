from sqlalchemy import select
from sqlalchemy.orm import Session
from app.models.notification import UserNotificationPreference

class PreferenceEvaluator:
    # Priority numeric hierarchy mapping
    PRIORITY_LEVELS = {
        "INFO": 1,
        "WARNING": 2,
        "CRITICAL": 3
    }

    @staticmethod
    def is_delivery_permitted(
        db: Session, 
        user_id: int, 
        priority: str
    ) -> bool:
        """
        Validates whether user preferences permit dispatch matching priority tier (Ticket #12 constraint).
        """
        stmt = select(UserNotificationPreference).where(UserNotificationPreference.user_id == user_id)
        pref = db.scalar(stmt)
        if not pref:
            # Defaults to true if no preference registry exists
            return True

        if not pref.enabled:
            return False

        # Compare priority thresholds
        event_rank = PreferenceEvaluator.PRIORITY_LEVELS.get(priority.upper(), 1)
        user_rank = PreferenceEvaluator.PRIORITY_LEVELS.get(pref.minimum_priority.upper(), 1)

        return event_rank >= user_rank
