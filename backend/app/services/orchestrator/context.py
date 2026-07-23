import re
from typing import List, Dict, Any

class ConversationalContextResolver:
    """
    Manages short-term history, pronoun resolution cues, and context budget truncation.
    """
    @staticmethod
    def resolve_pronouns(query: str, history: List[Dict[str, str]]) -> str:
        """
        Analyses history to enrich queries holding ambiguous pronouns (it, they, this).
        """
        lower_query = query.lower()
        pronouns = [" it ", " they ", " this ", " that "]
        
        # Check if the query is a short follow-up containing a pronoun
        has_pronoun = any(p in f" {lower_query} " for p in pronouns) or len(query.split()) < 4
        if not has_pronoun or not history:
            return query
            
        # Inspect the last assistant message in history to extract potential context noun
        for msg in reversed(history):
            if msg.get("role") == "assistant":
                text = msg.get("content", "")
                # Extract potential capitalized entities (equipment or nouns)
                entities = list(set(re.findall(r"\b(?:BLR|VLV|EQ)-\d+\b", text.upper())))
                if entities:
                    return f"{query} (referencing {', '.join(entities)})"
                
                # Alternate fallback: extract first noun sequence
                words = text.split()
                if words:
                    return f"{query} (referencing context: {' '.join(words[:4])})"
                    
        return query

    @staticmethod
    def format_history_payload(history: List[Dict[str, str]], limit: int = 5) -> List[Dict[str, str]]:
        """
        Formats and limits dialogue history payloads to avoid context bloat.
        """
        return history[-limit:]
