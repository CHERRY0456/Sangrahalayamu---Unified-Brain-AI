from typing import Dict, Any

# Reusable templates mapping placeholder variables (Ticket #12 constraint)
TEMPLATES = {
    "ACCESS_APPROVED": {
        "title": "Access Override Request Approved",
        "message": "Your temporary access request for document '{document_name}' has been approved by reviewer. Sections allowed: {sections}."
    },
    "ACCESS_REJECTED": {
        "title": "Access Override Request Rejected",
        "message": "Your temporary access request for document ID '{document_id}' was rejected. Reviewer remarks: '{remarks}'."
    },
    "DOCUMENT_PROCESSED": {
        "title": "Document Ingestion Completed",
        "message": "Document '{filename}' was processed successfully. Ingested {chunks} text chunks and parsed {entities} graph elements."
    },
    "UPLOAD_SUCCESS": {
        "title": "Document Uploaded Successfully",
        "message": "File '{filename}' ({size} bytes) was uploaded successfully by user '{uploader}'."
    },
    "SYSTEM_WARNING": {
        "title": "⚠️ System Alert Warning",
        "message": "Platform warning: {alert_description} (Source service: '{service_source}')."
    }
}

class NotificationTemplateRegistry:
    @staticmethod
    def get_template(template_key: str) -> Dict[str, str]:
        return TEMPLATES.get(template_key.upper(), {
            "title": "Platform Alert Notification",
            "message": "A platform event was recorded: {message}."
        })
