import logging

logger = logging.getLogger("sangrahalayamu.access_control.events")

class AccessControlEvents:
    @staticmethod
    def on_request_created(request_id: int, requester_name: str, document_name: str) -> None:
        """
        Event hook triggered when a new access override request is logged.
        """
        logger.info(
            f"Event Hook [on_request_created]: Override request {request_id} created by "
            f"'{requester_name}' for document '{document_name}'."
        )

    @staticmethod
    def on_request_approved(request_id: int, approver_name: str, duration_hours: int) -> None:
        """
        Event hook triggered when a compliance reviewer approves a pending override ticket.
        """
        logger.info(
            f"Event Hook [on_request_approved]: Override request {request_id} approved by "
            f"'{approver_name}' with validity period of {duration_hours} hours."
        )

    @staticmethod
    def on_request_rejected(request_id: int, rejector_name: str, reason: str) -> None:
        """
        Event hook triggered when a compliance reviewer rejects a pending override ticket.
        """
        logger.info(
            f"Event Hook [on_request_rejected]: Override request {request_id} rejected by "
            f"'{rejector_name}'. Reason: '{reason}'."
        )
