import re
from typing import Any

def validate_temperature(v: float) -> float:
    if not 0.0 <= v <= 1.0:
        raise ValueError("Temperature must be between 0.0 and 1.0")
    return v

def validate_top_p(v: float) -> float:
    if not 0.0 <= v <= 1.0:
        raise ValueError("Top P must be between 0.0 and 1.0")
    return v

def validate_top_k(v: int) -> int:
    if v < 1:
        raise ValueError("Top K must be at least 1")
    return v

def validate_embedding_dimensions(v: int) -> int:
    if v <= 0:
        raise ValueError("Embedding dimensions must be greater than 0")
    return v

def validate_aws_region(v: str) -> str:
    # simple regex for AWS regions (e.g. us-east-1, eu-central-1)
    if not re.match(r"^[a-z]{2}-[a-z]+-\d+$", v):
        raise ValueError(f"Invalid AWS Region format: {v}")
    return v

def validate_upload_size_limit(v: int) -> int:
    if v <= 0:
        raise ValueError("Upload size limit must be greater than 0 bytes")
    return v

def validate_postgres_port(v: int) -> int:
    if not 1 <= v <= 65535:
        raise ValueError("PostgreSQL port must be between 1 and 65535")
    return v

def validate_qdrant_port(v: int) -> int:
    if not 1 <= v <= 65535:
        raise ValueError("Qdrant port must be between 1 and 65535")
    return v

def validate_chunk_sizes(settings: Any) -> Any:
    # Intended to be used as a model_validator for ChunkingSettings
    if settings.min_chunk_size >= settings.max_chunk_size:
        raise ValueError("min_chunk_size must be less than max_chunk_size")
    if settings.chunk_overlap >= settings.min_chunk_size:
        raise ValueError("chunk_overlap must be less than min_chunk_size")
    return settings
