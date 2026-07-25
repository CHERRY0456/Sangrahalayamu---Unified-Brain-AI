import logging
from typing import List, Dict, Any, Optional
from qdrant_client import QdrantClient
from qdrant_client.http import models as qmodels
from app.core.config import settings

logger = logging.getLogger(__name__)

class VectorRepository:
    """
    Low-level wrapper around the Qdrant client.
    """
    def __init__(self):
        kwargs = {}
        if settings.qdrant.api_key:
            kwargs["api_key"] = settings.qdrant.api_key
            
        if settings.qdrant.host.startswith("http"):
            kwargs["url"] = settings.qdrant.host
        else:
            kwargs["host"] = settings.qdrant.host
            kwargs["port"] = settings.qdrant.port

        self.client = QdrantClient(
            https=settings.qdrant.use_https,
            timeout=settings.qdrant.timeout,
            **kwargs
        )
        self.collection_name = settings.qdrant.collection_name
        self.vector_size = settings.qdrant.vector_size
        
        distance_map = {
            "Cosine": qmodels.Distance.COSINE,
            "Dot": qmodels.Distance.DOT,
            "Euclid": qmodels.Distance.EUCLID
        }
        self.distance = distance_map.get(settings.qdrant.distance, qmodels.Distance.COSINE)

    def health_check(self) -> bool:
        try:
            return len(self.client.get_collections().collections) >= 0
        except Exception as e:
            logger.error(f"Qdrant health check failed: {e}")
            return False

    def validate_collection(self) -> bool:
        """Ensure collection exists with matching vector dimension and indices."""
        try:
            info = self.client.get_collection(self.collection_name)
            current_dim = getattr(info.config.params.vectors, 'size', None)
            if current_dim is not None and current_dim != self.vector_size:
                logger.warning(f"Qdrant collection dimension mismatch ({current_dim} vs {self.vector_size}). Recreating collection...")
                self.client.delete_collection(self.collection_name)
                self._create_collection()
                return True
        except Exception:
            self._create_collection()
            return True

        # Ensure required payload indices exist
        for field in ["document_id", "workspace_id", "role_permissions"]:
            try:
                self.client.create_payload_index(
                    collection_name=self.collection_name,
                    field_name=field,
                    field_schema=qmodels.PayloadSchemaType.KEYWORD
                )
            except Exception:
                pass
        return True

    def _create_collection(self):
        logger.info(f"Creating Qdrant collection '{self.collection_name}' with size {self.vector_size}")
        self.client.create_collection(
            collection_name=self.collection_name,
            vectors_config=qmodels.VectorParams(
                size=self.vector_size,
                distance=self.distance
            )
        )
        
        for field in ["document_id", "workspace_id", "role_permissions"]:
            try:
                self.client.create_payload_index(
                    collection_name=self.collection_name,
                    field_name=field,
                    field_schema=qmodels.PayloadSchemaType.KEYWORD
                )
            except Exception:
                pass

    def upsert_batch(self, points: List[qmodels.PointStruct]):
        """Upsert a batch of vectors with payloads."""
        self.validate_collection()
        self.client.upsert(
            collection_name=self.collection_name,
            points=points
        )

    def delete_by_document(self, document_id: str):
        """Delete all vectors belonging to a document."""
        self.client.delete(
            collection_name=self.collection_name,
            points_selector=qmodels.FilterSelector(
                filter=qmodels.Filter(
                    must=[
                        qmodels.FieldCondition(
                            key="document_id",
                            match=qmodels.MatchValue(value=document_id)
                        )
                    ]
                )
            )
        )

    def search(
        self,
        query_vector: List[float],
        filter_conditions: Optional[List[qmodels.Condition]] = None,
        limit: int = 10,
        score_threshold: Optional[float] = None
    ) -> List[qmodels.ScoredPoint]:
        """
        Search with metadata and permission filters.
        """
        self.validate_collection()
        search_filter = None
        if filter_conditions:
            search_filter = qmodels.Filter(must=filter_conditions)

        try:
            if hasattr(self.client, "search"):
                return self.client.search(
                    collection_name=self.collection_name,
                    query_vector=query_vector,
                    query_filter=search_filter,
                    limit=limit,
                    score_threshold=score_threshold
                )
            elif hasattr(self.client, "query_points"):
                res = self.client.query_points(
                    collection_name=self.collection_name,
                    query=query_vector,
                    query_filter=search_filter,
                    limit=limit,
                    score_threshold=score_threshold
                )
                return getattr(res, "points", res)
            elif hasattr(self.client, "search_points"):
                return self.client.search_points(
                    collection_name=self.collection_name,
                    vector=query_vector,
                    filter=search_filter,
                    limit=limit,
                    score_threshold=score_threshold
                )
            else:
                logger.error("QdrantClient has no search, query_points, or search_points method.")
                return []
        except Exception as e:
            logger.error(f"Qdrant search execution error: {e}")
            return []

    def get_collection_statistics(self) -> Dict[str, Any]:
        """Return collection vector count and stats."""
        try:
            info = self.client.get_collection(self.collection_name)
            return {
                "points_count": info.points_count,
                "status": info.status,
                "vectors_count": info.vectors_count
            }
        except Exception:
            return {"points_count": 0, "status": "missing"}
