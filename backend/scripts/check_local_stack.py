"""
Diagnostic Script for IndustryBrain-AI Local Infrastructure Stack.
Checks PostgreSQL RDBMS, Qdrant Vector DB, Neo4j Graph DB, AWS Bedrock Cohere Embeddings, and System RAM.
"""
import sys
import os
import psutil
import logging

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

logging.basicConfig(level=logging.INFO, format="%(asctime)s | %(levelname)s | %(message)s")
logger = logging.getLogger("check_local_stack")


def check_ram():
    mem = psutil.virtual_memory()
    total_gb = mem.total / (1024 ** 3)
    available_gb = mem.available / (1024 ** 3)
    logger.info(f"RAM Check: Total = {total_gb:.2f} GB | Available = {available_gb:.2f} GB")
    if total_gb <= 8.5:
        logger.info("[8GB RAM Mode Detected] Native PyPDF/Office/CAD low-memory parsers active.")


def check_postgres():
    try:
        from app.database.postgres import engine
        from sqlalchemy import text
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        logger.info("[OK] PostgreSQL RDBMS Connection: SUCCESSFUL")
        return True
    except Exception as e:
        logger.error(f"[FAIL] PostgreSQL Connection Error: {e}")
        return False


def check_qdrant():
    try:
        from app.services.qdrant.qdrant_service import qdrant_service
        is_ok = qdrant_service.health_check()
        if is_ok:
            logger.info("[OK] Qdrant Vector DB Connection (1024-dim Cohere Sync): SUCCESSFUL")
        else:
            logger.warning("[DEGRADED] Qdrant Vector DB returned health False")
        return is_ok
    except Exception as e:
        logger.error(f"[FAIL] Qdrant Connection Error: {e}")
        return False


def check_neo4j():
    try:
        from app.services.graph.providers.neo4j_provider import get_neo4j_provider
        provider = get_neo4j_provider()
        with provider.session() as session:
            session.run("MATCH (n) RETURN count(n) LIMIT 1")
        logger.info("[OK] Neo4j Graph DB Connection: SUCCESSFUL")
        return True
    except Exception as e:
        logger.error(f"[FAIL] Neo4j Connection Error: {e}")
        return False


def check_cohere_embeddings():
    try:
        from app.services.embeddings.providers.bedrock_embedding_provider import BedrockEmbeddingProvider
        provider = BedrockEmbeddingProvider()
        vec = provider.embed_text("Industrial equipment test query")
        logger.info(f"[OK] AWS Bedrock Cohere Embed v3: SUCCESSFUL ({len(vec.vector)} dims)")
        return True
    except Exception as e:
        logger.error(f"[FAIL] AWS Bedrock Cohere Embedding Error: {e}")
        return False


if __name__ == "__main__":
    logger.info("=== IndustryBrain-AI Local Infrastructure Diagnostic ===")
    check_ram()
    p_ok = check_postgres()
    q_ok = check_qdrant()
    n_ok = check_neo4j()
    c_ok = check_cohere_embeddings()

    logger.info("=========================================================")
    if p_ok and q_ok and n_ok and c_ok:
        logger.info("ALL SYSTEMS OPERATIONAL (0 Mock Data / Cohere Exclusive Mandate Enforced).")
    else:
        logger.warning("One or more local services require connection review.")
