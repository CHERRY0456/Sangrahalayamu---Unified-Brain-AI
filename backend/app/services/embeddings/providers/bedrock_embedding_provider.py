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
    AWS Bedrock implementation for embeddings.
    Tries the default model (Cohere) and falls back to the fallback model (Titan) on failure.
    """
    def __init__(self):
        self.region = settings.aws.region
        
        # If access keys are not provided, boto3 will fall back to IAM roles/env vars automatically
        kwargs = {"region_name": self.region}
        if settings.aws.access_key_id and settings.aws.secret_access_key:
            kwargs["aws_access_key_id"] = settings.aws.access_key_id
            kwargs["aws_secret_access_key"] = settings.aws.secret_access_key
            
        self.client = boto3.client("bedrock-runtime", **kwargs)
        self.default_model = settings.embedding.default_model
        self.fallback_model = settings.embedding.fallback_model
        
    def embed_text(self, text: str) -> EmbeddingVector:
        return self.embed_batch([text])[0]
        
    def embed_batch(self, texts: List[str]) -> List[EmbeddingVector]:
        try:
            return self._invoke_model(self.default_model, texts)
        except Exception as e:
            logger.warning(f"Default embedding model {self.default_model} failed: {e}. Attempting fallback...")
            try:
                return self._invoke_model(self.fallback_model, texts)
            except Exception as fallback_e:
                logger.error(f"Fallback embedding model {self.fallback_model} also failed: {fallback_e}")
                raise RuntimeError(f"Embedding generation failed for both default and fallback models. Error: {fallback_e}")

    def _invoke_model(self, model_id: str, texts: List[str]) -> List[EmbeddingVector]:
        start_time = time.time()
        
        if "cohere" in model_id.lower():
            # Cohere native batch support
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
            
            # Extract usage
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
            
        elif "titan" in model_id.lower():
            # Titan typically embeds single strings. Iterate sequentially for the batch
            results = []
            for t in texts:
                iter_start = time.time()
                body = json.dumps({"inputText": t})
                response = self.client.invoke_model(
                    body=body,
                    modelId=model_id,
                    accept="application/json",
                    contentType="application/json"
                )
                response_body = json.loads(response.get("body").read())
                emb = response_body.get("embedding", [])
                latency = time.time() - iter_start
                
                results.append(
                    EmbeddingVector(
                        vector=emb,
                        model=model_id,
                        provider=EmbeddingProviderEnum.BEDROCK,
                        dimensions=len(emb),
                        latency=latency,
                        usage={"input_tokens": response_body.get("inputTextTokenCount", 0)},
                        metadata={"provider": "titan"}
                    )
                )
            return results
        else:
            raise ValueError(f"Unsupported Bedrock embedding model family: {model_id}")
