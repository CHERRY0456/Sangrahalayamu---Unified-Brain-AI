"""
Document Ingestion CLI Script for IndustryBrain-AI.
Processes local documents through the Docling layout-aware pipeline and indexes them into Qdrant & Neo4j.
"""
import sys
import os
import asyncio
import logging

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.services.processing.pipeline import ingestion_pipeline

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("ingest_documents")


async def main(file_path: str):
    if not os.path.exists(file_path):
        logger.error(f"File not found: {file_path}")
        sys.exit(1)

    logger.info(f"Starting ingestion pipeline for file: {file_path}")
    with open(file_path, "rb") as f:
        file_bytes = f.read()

    filename = os.path.basename(file_path)
    result = await ingestion_pipeline.run(file_bytes=file_bytes, filename=filename)
    logger.info(f"Ingestion completed successfully for {filename}. Status: {result}")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        logger.error("Usage: python ingest_documents.py <path_to_document>")
        sys.exit(1)

    file_path = sys.argv[1]
    asyncio.run(main(file_path))
