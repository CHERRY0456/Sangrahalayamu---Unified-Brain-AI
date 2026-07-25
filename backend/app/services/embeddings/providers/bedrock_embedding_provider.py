"""
AWS Bedrock implementation for Cohere Embeddings (Exclusive Cohere Embed v3 - Zero Fallback Mandate).
Supports Cohere v3 (cohere.embed-multilingual-v3 / cohere.embed-english-v3).
"""
import json
import time
import boto3
import logging
from typing import List, Dict, Any

from app.core.config import settings
from app.core.enums import EmbeddingProviderEnum
from ..interfaces.embedding_provider import BaseEmbeddingProvider
from ..schemas.embedding_models import EmbeddingVector

logger = logging.getLogger(__name__)


class BedrockEmbeddingProvider(BaseEmbeddingProvider):
    """
    AWS Bedrock provider using Cohere Embed v3 models exclusively. No fallbacks allowed.
    """
    def __init__(self):
        self.region = settings.aws.region
        
        kwargs = {"region_name": self.region}
        if settings.aws.access_key_id and settings.aws.secret_access_key:
            kwargs["aws_access_key_id"] = settings.aws.access_key_id
            kwargs["aws_secret_access_key"] = settings.aws.secret_access_key
            
        self.client = boto3.client("bedrock-runtime", **kwargs)
        self.model = settings.embedding.default_model or "cohere.embed-multilingual-v3"
        
    def embed_text(self, text: str) -> EmbeddingVector:
        return self.embed_batch([text])[0]
        
    def embed_batch(self, texts: List[str]) -> List[EmbeddingVector]:
        """
        Executes Cohere Embed v3 call on AWS Bedrock in chunks of max 96 items (AWS limit is 128).
        """
        if not texts:
            return []

        batch_size = 96
        all_results: List[EmbeddingVector] = []

        try:
            for i in range(0, len(texts), batch_size):
                sub_batch = texts[i:i + batch_size]
                sub_results = self._invoke_cohere_model(self.model, sub_batch)
                all_results.extend(sub_results)
            return all_results
        except Exception as e:
            logger.error(f"[BedrockEmbeddingProvider|FATAL] Cohere embedding generation failed for model {self.model}: {e}")
            raise RuntimeError(f"AWS Bedrock Cohere Embedding API call failed: {e}") from e

    def _invoke_cohere_model(self, model_id: str, texts: List[str]) -> List[EmbeddingVector]:
        start_time = time.time()
        
        body = json.dumps({
            "texts": texts,
            "input_type": "search_document"
        })
        response = self.client.invoke_model(
            body=body,
            modelId=model_id,
            accept="application/json",
            contentType="application/json"
        )
        response_body = json.loads(response.get("body").read())
        embeddings = response_body.get("embeddings", [])
        
        if not embeddings:
            raise RuntimeError(f"AWS Bedrock Cohere model '{model_id}' returned empty embeddings.")

        meta = response_body.get("meta", {})
        billed_units = meta.get("billed_units", {})
        
        latency = time.time() - start_time
        results = []
        for emb in embeddings:
            results.append(
                EmbeddingVector(
                    vector=emb,
                    model=model_id,
                    provider=EmbeddingProviderEnum.BEDROCK,
                    dimensions=len(emb),
                    latency=latency,
                    usage={"input_tokens": billed_units.get("input_tokens", 0)},
                    metadata={"provider": "cohere", "response_meta": meta}
                )
            )
        return results
