from typing import List, Dict, Any, Optional

TEMPLATES = {
    "enterprise_default": (
        "You are 'Sangrahalayamu', an advanced, secure enterprise RAG assistant. "
        "Your goal is to answer the user query based ONLY on the provided document contexts. "
        "If the answer cannot be determined from the context, state that you do not have enough information. "
        "Always cite your sources using bracketed notations like '[Doc: <filename>]' or '[Chunk: <id>]' "
        "when summarizing facts. Do not make unsupported claims."
    ),
    "technical_support": (
        "You are 'Sangrahalayamu' engineering advisor. You help engineers and technicians "
        "calibrate, maintain, and troubleshoot equipment. "
        "Structure your response with clear, bulleted steps. Highlight any safety warnings or "
        "equipment indicators (like VLV-xxx, BLR-xxx, EQ-xxx) mentioned in the source context. "
        "Always add a 'SAFETY WARNING' section if safety guidelines or regulatory rules are referenced. "
        "Cite the document name and section for every fact."
    ),
    "compliance": (
        "You are 'Sangrahalayamu' compliance auditor. Your focus is verifying alignment with "
        "regulatory guidelines and safety standards (e.g. OSHA 1910.263). "
        "Analyze the document text, verify compliance statements, and cite section numbers, "
        "versions, and authors. Note any violations or calibration discrepancies. "
        "For every claim, explicitly output the bracketed document citation."
    ),
    "executive_summary": (
        "You are 'Sangrahalayamu' executive analyst. Provide a high-level briefing "
        "summarizing the key findings, plant parameters, and downtime stats from the context. "
        "Keep the summary under 150 words. Do not list granular details unless critical. "
        "Format with bulleted takeaways and cite primary source manuals at the end."
    )
}

class RAGPromptBuilder:
    @staticmethod
    def build_system_prompt(template_name: str, user_role: str, department: str) -> str:
        """
        Builds system instructions based on template selection and user persona context.
        """
        base = TEMPLATES.get(template_name, TEMPLATES["enterprise_default"])
        persona_str = f" Currently serving a '{user_role}' from the '{department}' department."
        return f"{base}\n{persona_str}"

    @staticmethod
    def build_user_prompt(
        query: str, 
        context_chunks: List[Dict[str, Any]], 
        graph_paths: List[Dict[str, Any]]
    ) -> str:
        """
        Assembles the retrieval context, graph edges, and query into a grounded LLM prompt.
        """
        context_blocks = []
        for idx, ch in enumerate(context_chunks):
            doc_name = ch.get("document_name", "Unknown File")
            sec = ch.get("section", "Introduction")
            cid = ch.get("chunk_id", "N/A")
            text = ch.get("text", "")
            context_blocks.append(
                f"--- [SOURCE {idx+1}] ---\n"
                f"Document: {doc_name} | Section: {sec} | Chunk ID: {cid}\n"
                f"Content: {text}\n"
            )
            
        context_str = "\n".join(context_blocks)
        
        graph_str = ""
        if graph_paths:
            graph_edges = []
            for edge in graph_paths:
                graph_edges.append(f"  ({edge.get('source')}) --[{edge.get('relationship_type')}]--> ({edge.get('target')})")
            graph_str = "--- GRAPH RELATIONSHIP PATHS ---\n" + "\n".join(graph_edges) + "\n"

        prompt = (
            f"Here is the verified context to ground your response:\n\n"
            f"{context_str}\n"
            f"{graph_str}"
            f"Query: {query}\n\n"
            f"Generate a grounded answer citing the source documents using '[Doc: <filename>]' bracket format. "
            f"If the context does not contain the answer, say 'I cannot find the answer in the provided documents.'"
        )
        return prompt
