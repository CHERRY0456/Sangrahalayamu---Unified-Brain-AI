from .models import TransparencyReport

class TransparencyReportFormatter:
    @staticmethod
    def to_markdown(report: TransparencyReport) -> str:
        """
        Formats transparency reports into clear, styled markdown explanations.
        """
        md = []
        md.append(f"# Transparency & Trust Report")
        
        # Confidence
        conf = report.confidence_analysis
        md.append(f"### 🛡️ Confidence Score: **{conf.confidence:.2f}**")
        md.append(f"> {conf.reason}")
        
        # Permissions
        perm = report.permissions
        md.append(f"\n### 🔑 Clearance & Access")
        md.append(f"- **Role**: {perm.user_role} | **Clearance level**: {perm.clearance_level}")
        md.append(f"- **Dynamic Overrides applied**: {'Yes' if perm.temporary_override_status else 'No'}")
        md.append(f"- *Summary*: {perm.reason}")
        
        # Retrieval
        ret = report.retrieval
        md.append(f"\n### 🔍 Document Context Retrieval")
        md.append(f"- *Overview*: {ret.description}")
        md.append(f"- **Documents Considered**: {ret.num_documents_considered}")
        md.append(f"- **Semantic hits**: {ret.num_semantic_matches} | **Graph edges traversed**: {ret.num_graph_relations_expanded}")
        
        # Citations
        cit = report.citations
        md.append(f"\n### 📖 Citations Audit")
        md.append(f"- **Valid Citations**: {cit.citation_count}")
        md.append(f"- **Duplicate Citations**: {cit.duplicate_citations_count}")
        md.append(f"- **Unused chunks**: {len(cit.unused_retrieved_chunks)} chunk(s) discarded by LLM")
        
        # Warnings
        if report.warnings:
            md.append(f"\n### ⚠️ System Alerts")
            for wrn in report.warnings:
                md.append(f"- {wrn}")
                
        # Execution timing
        if report.execution_trace:
            tr = report.execution_trace
            md.append(f"\n### ⏱️ Latency & Infrastructure")
            md.append(f"- **LLM Provider**: `{tr.provider}` | **Model**: `{tr.model}`")
            md.append(f"- **Template**: `{tr.prompt_template}`")
            for phase, sec in tr.latencies.items():
                md.append(f"  - *{phase.replace('_', ' ').capitalize()}*: {sec:.4f}s")
                
        return "\n".join(md)
