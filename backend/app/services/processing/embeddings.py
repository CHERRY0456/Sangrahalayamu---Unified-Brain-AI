import hashlib
from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
from pydantic import BaseModel
import boto3
import json

from app.core.config import settings

class EmbeddingMetadata(BaseModel):
    chunk_id: str
    provider: str
    model: str
    dimensions: int
    checksum: str
    success: bool

class EmbeddingInterface(ABC):
    @abstractmethod
    def generate_embedding_vectors(self, texts: List[str]) -> List[List[float]]:
        """
        Generates high-dimensional embedding vectors in memory (used only during validation).
        """
        pass

    @abstractmethod
    def generate_embedding_payload(self, chunk_id: str, text: str) -> EmbeddingMetadata:
        """
        Extracts structural embedding metadata to save in database chunks.
        """
        pass

class BedrockEmbeddingProvider(EmbeddingInterface):
    """
    AWS Bedrock implementation of EmbeddingInterface generating vectors.
    """
    def __init__(self, provider: str = "AWSBedrock", model: Optional[str] = None, dimensions: Optional[int] = None):
        self.provider = provider
        self.model = model or settings.embedding.default_model
        self.dimensions = dimensions or settings.embedding.dimension

        # Pull region from environment or default to us-east-1
        import os
        region = os.environ.get("AWS_REGION", os.environ.get("AWS_DEFAULT_REGION", "us-east-1"))
        kwargs = {"region_name": region}
        if settings.aws.access_key_id and settings.aws.secret_access_key:
            kwargs["aws_access_key_id"] = settings.aws.access_key_id
            kwargs["aws_secret_access_key"] = settings.aws.secret_access_key
        self.client = boto3.client('bedrock-runtime', **kwargs)

    def generate_embedding_vectors(self, texts: List[str]) -> List[List[float]]:
        vectors = []
        for text in texts:
            # Construct payload based on model family
            if "cohere.embed" in self.model:
                body_dict = {
                    "texts": [text],
                    "input_type": "search_document"
                }
            else: # Default to amazon.titan-embed
                body_dict = {
                    "inputText": text
                }
                
            body = json.dumps(body_dict)
            response = self.client.invoke_model(
                body=body,
                modelId=self.model,
                accept="application/json",
                contentType="application/json"
            )
            response_body = json.loads(response.get('body').read())
            
            # Extract embedding based on model family response structure
            if "cohere.embed" in self.model:
                embedding = response_body.get("embeddings", [])
                if embedding and len(embedding) > 0:
                    vectors.append(embedding[0])
                else:
                    raise ValueError("No embedding returned from Bedrock API (Cohere).")
            else:
                embedding = response_body.get("embedding")
                if embedding:
                    vectors.append(embedding)
                else:
                    raise ValueError("No embedding returned from Bedrock API (Titan).")
        return vectors

    def generate_embedding_payload(self, chunk_id: str, text: str) -> EmbeddingMetadata:
        checksum = hashlib.sha256(text.encode("utf-8")).hexdigest()
        return EmbeddingMetadata(
            chunk_id=chunk_id,
            provider=self.provider,
            model=self.model,
            dimensions=self.dimensions,
            checksum=checksum,
            success=True
        )

from sqlalchemy.orm import Session
from .stage import PipelineStage, PipelineContext

class EmbeddingsStage(PipelineStage):
    """
    Pipeline stage wrapper for generating embedding payload metadata.
    """
    def __init__(self, provider: Optional[EmbeddingInterface] = None):
        self.provider = provider or BedrockEmbeddingProvider()

    def execute(self, context: PipelineContext, db: Session) -> None:
        if context.chunks is None:
            raise ValueError("Chunking stage must run before Embeddings stage.")

        for chunk in context.chunks:
            # Actually call AWS Bedrock to generate vectors in memory
            _vectors = self.provider.generate_embedding_vectors([chunk.text])

            # Persist only structural embedding metadata inside chunk payload
            payload_metadata = self.provider.generate_embedding_payload(
                chunk_id=chunk.chunk_id,
                text=chunk.text
            )
            chunk.embedding_metadata = payload_metadata.model_dump()
