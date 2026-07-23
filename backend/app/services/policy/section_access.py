from typing import Dict, Any, List

class SectionAccessEvaluator:
    @staticmethod
    def is_section_accessible(role_name: str, doc_metadata: Dict[str, Any], section_name: str) -> bool:
        """
        Evaluates if the user's role has permission to access a specific document section.
        Looks up the 'section_exclusions' block inside the document metadata.
        E.g. doc_metadata = {
            "section_exclusions": {
                "Field Technician": ["Section 5.1", "Section 5.2"],
                "Maintenance Engineer": ["Section 5.1"]
            }
        }
        """
        if not section_name:
            return True
            
        exclusions: Dict[str, List[str]] = doc_metadata.get("section_exclusions", {})
        role_exclusions = exclusions.get(role_name, [])
        
        # Check if the requested section matches any of the excluded strings
        for excluded_section in role_exclusions:
            if excluded_section.lower().strip() == section_name.lower().strip():
                return False
                
        return True
