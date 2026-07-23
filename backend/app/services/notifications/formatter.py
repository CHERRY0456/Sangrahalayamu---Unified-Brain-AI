import logging
from typing import Dict, Any, Tuple
from .templates import NotificationTemplateRegistry

logger = logging.getLogger("sangrahalayamu.notifications.formatter")

class NotificationFormatter:
    """
    Utility formatting notification titles and messages by injecting placeholder parameters.
    """
    @staticmethod
    def format_notification(
        event_type: str, 
        params: Dict[str, Any]
    ) -> Tuple[str, str]:
        template = NotificationTemplateRegistry.get_template(event_type)
        
        title_template = template["title"]
        message_template = template["message"]

        # Safe key formatting fallback to prevent KeyError exceptions
        class SafeDict(dict):
            def __missing__(self, key):
                return f"{{{key}}}"

        safe_params = SafeDict(params)
        
        try:
            formatted_title = title_template.format_map(safe_params)
            formatted_message = message_template.format_map(safe_params)
            return formatted_title, formatted_message
        except Exception as e:
            logger.error(f"Template formatting failed for type '{event_type}': {str(e)}")
            # Fallback values
            return title_template, message_template
