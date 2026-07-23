import os
import uuid
import logging
import time
from typing import List
from datetime import datetime
from sqlalchemy import select
from sqlalchemy.orm import Session
from fastapi import HTTPException, status

from app.models.document import Document
from app.models.user import User
from app.services.storage import storage_service

from .models import (
    ProcessedDocumentPayload,
    EmbeddingDocument,
    IngestionReport,
    LayoutTreeNode
)
from .stage import PipelineContext, PipelineStage
from .parser import ParserStage
from .metadata import MetadataStage
from .entities import EntitiesStage
from .relationships import RelationshipsStage
from .chunking import ChunkingStage
from .embeddings import EmbeddingsStage, MockEmbeddingProvider, EmbeddingInterface
from .status import ProcessingStatusManager
from .payload_prep import IngestionPayloadPreparer

logger = logging.getLogger("sangrahalayamu.processing.pipeline")


class DocumentProcessingPipeline:
    """
    Ingestion pipeline converting raw storage assets into structured, AI-ready layout trees,
    entities, relationships, semantic chunks, and EmbeddingDocuments.
    """
    # Pluggable Embedding adapter
    embedding_provider: EmbeddingInterface = MockEmbeddingProvider()

    @staticmethod
    def process_document(db: Session, document_id: int) -> ProcessedDocumentPayload:
        """
        Coordinates parsing registry selection, metadata generation, entity/relationship extraction,
        layout-aware semantic chunking, and final IngestionReport generation.
        """
        start_time = time.perf_counter()

        # 1. Fetch document and owner information
        stmt = select(Document).where(Document.id == document_id, Document.is_active == True)
        doc = db.scalar(stmt)
        if not doc:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Document ID {document_id} not found."
            )

        uploader = doc.uploaded_by
        if not uploader:
            # Fallback mock user if missing (for seeded files)
            uploader_stmt = select(User).limit(1)
            uploader = db.scalar(uploader_stmt)

        # 2. Update status to PROCESSING
        ProcessingStatusManager.set_processing(db, doc)
        
        temp_file_path = ""
        try:
            # 3. Retrieve binary content from decoupled Storage service
            file_bytes = storage_service.get_document(doc.stored_name)
            
            # 4. Save to temporary file within workspace directory for Parser access
            backend_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
            temp_dir = os.path.join(backend_root, "storage", "tmp")
            os.makedirs(temp_dir, exist_ok=True)
            
            temp_filename = f"proc_{doc.uuid}_{doc.name}"
            temp_file_path = os.path.join(temp_dir, temp_filename)
            with open(temp_file_path, "wb") as temp_file:
                temp_file.write(file_bytes)

            # 5. Build common PipelineContext execution state
            context = PipelineContext(
                document_id=doc.id,
                doc_uuid=doc.uuid,
                filename=doc.name,
                file_path=temp_file_path,
                uploader=uploader
            )

            # 6. Compose pipeline stages sequentially
            stages: List[PipelineStage] = [
                ParserStage(),
                MetadataStage(),
                EntitiesStage(),
                RelationshipsStage(),
                ChunkingStage(),
                # Keep embedding metadata generation for DB structure support
                EmbeddingsStage(provider=DocumentProcessingPipeline.embedding_provider)
            ]

            # 7. Execute stages
            for stage in stages:
                stage.execute(context, db)

            latency_ms = (time.perf_counter() - start_time) * 1000

            # 8. Retrieve Parser details
            parser_result = context.extra_state.get("parser_result")
            parser_name = parser_result.metadata.get("parser", "DoclingParser") if parser_result else "DoclingParser"
            modality = parser_result.file_type if parser_result else "plain_text"
            char_count = len(parser_result.raw_markdown) if parser_result else 0

            # 9. Prepare EmbeddingDocuments
            embedding_docs = IngestionPayloadPreparer.prepare_embedding_documents(
                chunks=context.chunks or [],
                entities=context.entities or [],
                relationships=context.relationships or [],
                doc_id=doc.id,
                parser_name=parser_name
            )

            # Gather confidence scores for the report
            conf_scores = [e.provenance.confidence for e in (context.entities or []) if e.provenance]
            conf_scores += [r.provenance.confidence for r in (context.relationships or []) if r.provenance]
            if parser_result:
                conf_scores.append(parser_result.layout_root.confidence)

            # 10. Compile IngestionReport
            report = IngestionPayloadPreparer.generate_report(
                parser_name=parser_name,
                modality=modality,
                latency_ms=latency_ms,
                character_count=char_count,
                chunk_count=len(context.chunks or []),
                entity_count=len(context.entities or []),
                relationship_count=len(context.relationships or []),
                confidence_scores=conf_scores,
                warnings=context.extra_state.get("warnings", [])
            )

            # 11. Construct aggregate processed document payload
            from .models import DocumentProfile
            profile = DocumentProfile(
                title=context.metadata["title"],
                doc_type=context.metadata["doc_type"],
                summary=context.metadata["summary"],
                language=context.metadata["language"],
                keywords=context.metadata["keywords"],
                stats=context.metadata["stats"],
                metadata=context.metadata["domain_metadata"],
                extras=parser_result.extras if parser_result else {}
            )

            processed_payload = ProcessedDocumentPayload(
                title=context.metadata["title"],
                summary=context.metadata["summary"],
                keywords=context.metadata["keywords"],
                language=context.metadata["language"],
                doc_type=context.metadata["doc_type"],
                stats=context.metadata["stats"],
                metadata=context.metadata["domain_metadata"],
                layout_root=parser_result.layout_root if parser_result else LayoutTreeNode(node_id="root", type="heading", text=doc.name),
                chunks=context.chunks or [],
                embedding_documents=embedding_docs,
                entities=context.entities or [],
                relationships=context.relationships or [],
                report=report,
                profile=profile
            )

            # 12. Save payload properties to database JSON column
            meta = dict(doc.doc_metadata or {})
            meta["processed_payload"] = processed_payload.model_dump(mode="json")
            meta["title"] = processed_payload.title
            meta["summary"] = processed_payload.summary
            meta["keywords"] = processed_payload.keywords
            
            doc.doc_metadata = meta
            doc.name = processed_payload.title  # Sync normalized title if parsed
            
            # Transition state to PROCESSED
            ProcessingStatusManager.set_processed(db, doc)

            # Emit processing success event (Ticket #11 constraint)
            try:
                from app.services.audit import audit_service, AuditEvent, EVENT_TYPE_PROCESSING
                audit_service.record_event(db, AuditEvent(
                    event_type=EVENT_TYPE_PROCESSING,
                    actor_id=uploader.id if uploader else None,
                    actor_role=uploader.role.name if uploader and uploader.role else "System",
                    resource_type="document",
                    resource_id=str(doc.id),
                    action="process_document",
                    status="SUCCESS",
                    source_service="processing_pipeline",
                    metadata={"chunks": len(processed_payload.chunks), "entities": len(processed_payload.entities)}
                ))
            except Exception:
                pass

            # Notify uploader — document processed (Ticket #12)
            try:
                from app.services.notifications.service import notification_service
                from app.services.notifications.models import NotificationRequest
                if uploader:
                    notification_service.send_notification(db, NotificationRequest(
                        event_type="DOCUMENT_PROCESSED",
                        recipient_id=uploader.id,
                        priority="INFO",
                        title="Document Ingestion Completed",
                        message=(
                            f"Document '{doc.name}' was processed successfully. "
                            f"Ingested {len(processed_payload.chunks)} chunks, "
                            f"{len(processed_payload.entities)} entities, and compiled IngestionReport."
                        ),
                        metadata={
                            "document_id": doc.id,
                            "chunks": len(processed_payload.chunks),
                            "entities": len(processed_payload.entities),
                        },
                    ))
            except Exception:
                pass

            logger.info(
                f"[IngestionEngine] Success: Document ID {doc.id} processed via '{parser_name}' in {latency_ms:.1f}ms. "
                f"Generated {len(processed_payload.chunks)} chunks, {len(processed_payload.entities)} entities."
            )
            return processed_payload

        except Exception as e:
            # 13. Catch exception, log failure trace, and update FAILED status
            error_reason = str(e)
            
            # Emit processing failure event
            try:
                from app.services.audit import audit_service, AuditEvent, EVENT_TYPE_PROCESSING
                audit_service.record_event(db, AuditEvent(
                    event_type=EVENT_TYPE_PROCESSING,
                    actor_id=uploader.id if uploader else None,
                    actor_role=uploader.role.name if uploader and uploader.role else "System",
                    resource_type="document",
                    resource_id=str(document_id),
                    action="process_document",
                    status="FAILED",
                    source_service="processing_pipeline",
                    metadata={"error": error_reason}
                ))
            except Exception:
                pass

            logger.error(f"[IngestionEngine] Processing failed for document ID {document_id}: {error_reason}")
            ProcessingStatusManager.set_failed(db, doc, error_reason)
            raise e
            
        finally:
            # Clean up temp file safely
            if temp_file_path and os.path.exists(temp_file_path):
                try:
                    os.remove(temp_file_path)
                except Exception as clean_err:
                    logger.warning(f"Could not remove temp processing file {temp_file_path}: {str(clean_err)}")
