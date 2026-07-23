import logging
from app.core.config import settings
from .providers import NotificationProvider, InAppProvider, EmailProvider, SlackProvider, TeamsProvider

logger = logging.getLogger("sangrahalayamu.notifications.factory")

_PROVIDER_MAP = {
    "in_app": InAppProvider,
    "email":  EmailProvider,
    "slack":  SlackProvider,
    "teams":  TeamsProvider,
}


class NotificationProviderFactory:
    """
    Resolves the active NotificationProvider from configuration.
    Setting NOTIFICATION_PROVIDER in .env switches channels without
    touching any business service code.
    """
    @staticmethod
    def get_provider() -> NotificationProvider:
        provider_key = settings.notifications.provider.lower().strip()
        provider_class = _PROVIDER_MAP.get(provider_key)

        if provider_class is None:
            logger.warning(
                f"[ProviderFactory] Unknown provider '{provider_key}'. "
                "Falling back to InAppProvider."
            )
            return InAppProvider()

        logger.debug(f"[ProviderFactory] Active provider resolved: '{provider_key}'")
        return provider_class()
