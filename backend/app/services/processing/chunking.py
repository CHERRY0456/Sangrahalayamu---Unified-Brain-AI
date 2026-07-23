import uuid
import logging
from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session

from app.services.processing.models import SemanticChunkPayload, LayoutTreeNode
from .stage import PipelineStage, PipelineContext

logger = logging.getLogger("sangrahalayamu.processing.chunking")


class ProcessingSemanticChunker:
    """
    Layout-aware semantic chunker traversing the document layout tree hierarchy
    to form logical text chunks based on section, table, and code boundaries.
    """

    @staticmethod
    def chunk_layout_tree(
        root: LayoutTreeNode,
        doc_id: int,
        doc_uuid: str
    ) -> List[SemanticChunkPayload]:
        chunks: List[SemanticChunkPayload] = []
        chunk_idx = 0

        def build_chunk(
            text: str,
            section: str,
            hierarchy: List[str],
            pages: List[int]
        ) -> SemanticChunkPayload:
            nonlocal chunk_idx
            word_count = len(text.split())
            token_count = int(word_count * 1.35)  # Estimate tokens

            chunk_id = f"{doc_uuid}-chunk-{chunk_idx}"
            chunk_idx += 1

            return SemanticChunkPayload(
                chunk_id=chunk_id,
                parent_doc_id=doc_id,
                section=section,
                heading_hierarchy=list(hierarchy),
                page_numbers=sorted(list(set(pages))) if pages else [1],
                token_count=token_count,
                text=text,
                embedding_metadata={}
            )

        # Active state during traversal
        current_hierarchy: List[str] = []

        def traverse(node: LayoutTreeNode) -> None:
            nonlocal current_hierarchy

            # If heading node, update hierarchy
            is_heading = (node.type == "heading")
            if is_heading:
                level = node.metadata.get("level", 1) or 1
                # Truncate hierarchy to this depth
                current_hierarchy = current_hierarchy[:level - 1]
                current_hierarchy.append(node.text)

            section_name = current_hierarchy[-1] if current_hierarchy else "Introduction"

            # Tables and code blocks are self-contained logical chunks
            if node.type in ("table", "code", "diagram"):
                chunks.append(build_chunk(
                    text=node.text,
                    section=section_name,
                    hierarchy=current_hierarchy,
                    pages=node.page_numbers
                ))
            elif node.text and not is_heading:
                # Standard paragraph / list entry — check if we can group it or make a single chunk
                # To keep it simple and clean, package paragraphs as semantic blocks.
                # If they exceed a threshold, we split them.
                words = node.text.split()
                if len(words) > 350:
                    # Break long paragraphs into ~300 word sub-chunks
                    sub_paras = []
                    current_sub = []
                    for w in words:
                        current_sub.append(w)
                        if len(current_sub) >= 300:
                            sub_paras.append(" ".join(current_sub))
                            current_sub = []
                    if current_sub:
                        sub_paras.append(" ".join(current_sub))
                    
                    for sp in sub_paras:
                        chunks.append(build_chunk(
                            text=sp,
                            section=section_name,
                            hierarchy=current_hierarchy,
                            pages=node.page_numbers
                        ))
                else:
                    chunks.append(build_chunk(
                        text=node.text,
                        section=section_name,
                        hierarchy=current_hierarchy,
                        pages=node.page_numbers
                    ))

            # Recurse children to parse in reading order
            for child in node.children:
                traverse(child)

        traverse(root)

        # In case the document has no content blocks, create a default single chunk from the root text
        if not chunks:
            chunks.append(build_chunk(
                text=root.text or f"Preserved layout container for doc: {root.text}",
                section="Introduction",
                hierarchy=[root.text],
                pages=root.page_numbers or [1]
            ))

        return chunks


class ChunkingStage(PipelineStage):
    """
    Pipeline stage mapping layout-aware chunks.
    """
    def execute(self, context: PipelineContext, db: Session) -> None:
        parser_result = context.extra_state.get("parser_result")
        if not parser_result:
            raise ValueError("Parser stage must run before Chunking stage.")

        context.chunks = ProcessingSemanticChunker.chunk_layout_tree(
            parser_result.layout_root,
            context.document_id,
            context.doc_uuid
        )
        logger.info(f"[ChunkingStage] Created {len(context.chunks)} layout-aware semantic chunks.")
