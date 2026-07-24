from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import computed_field, Field, field_validator, model_validator
from typing import Optional
from pathlib import Path
from dotenv import load_dotenv

# Resolve path to .env file relative to this file's directory (backend/app/core)
BASE_DIR = Path(__file__).resolve().parent.parent.parent
env_file_path = BASE_DIR / ".env"

load_dotenv(dotenv_path=env_file_path)

from app.core.enums import (
    EnvironmentEnum, LogLevelEnum, StorageProviderEnum, 
    NotificationProviderEnum, OCRProviderEnum, LLMProviderEnum, 
    EmbeddingProviderEnum, ChunkStrategyEnum
)
from app.core.validators import (
    validate_temperature, validate_top_p, validate_top_k,
    validate_embedding_dimensions, validate_aws_region,
    validate_upload_size_limit, validate_postgres_port,
    validate_qdrant_port, validate_chunk_sizes
)

class ApplicationSettings(BaseSettings):
    name: str = Field(validation_alias="APP_NAME", default="Sangrahalayamu")
    version: str = Field(validation_alias="APP_VERSION", default="1.0.0")
    env: EnvironmentEnum = Field(validation_alias="APP_ENV", default=EnvironmentEnum.DEVELOPMENT)
    debug: bool = Field(validation_alias="DEBUG", default=True)
    log_level: LogLevelEnum = Field(validation_alias="LOG_LEVEL", default=LogLevelEnum.INFO)
    api_prefix: str = Field(validation_alias="API_PREFIX", default="/api")
    secret_key: str = Field(validation_alias="SECRET_KEY", default="dev_secret_key_change_in_production")
    jwt_secret_key: str = Field(validation_alias="JWT_SECRET_KEY", default="dev_jwt_secret_key_change_in_production")
    access_token_expire_minutes: int = Field(validation_alias="ACCESS_TOKEN_EXPIRE_MINUTES", default=30)
    refresh_token_expire_days: int = Field(validation_alias="REFRESH_TOKEN_EXPIRE_DAYS", default=7)

class DatabaseSettings(BaseSettings):
    host: str = Field(validation_alias="POSTGRES_HOST", default="localhost")
    port: int = Field(validation_alias="POSTGRES_PORT", default=5432)
    db: str = Field(validation_alias="POSTGRES_DB", default="sangrahalayamu")
    user: str = Field(validation_alias="POSTGRES_USER", default="postgres")
    password: str = Field(validation_alias="POSTGRES_PASSWORD", default="postgres")
    
    pool_size: int = Field(validation_alias="DATABASE_POOL_SIZE", default=20)
    max_overflow: int = Field(validation_alias="DATABASE_MAX_OVERFLOW", default=10)
    pool_timeout: int = Field(validation_alias="DATABASE_POOL_TIMEOUT", default=30)
    pool_recycle: int = Field(validation_alias="DATABASE_POOL_RECYCLE", default=1800)
    echo: bool = Field(validation_alias="DATABASE_ECHO", default=False)

    @field_validator("port")
    @classmethod
    def check_port(cls, v: int) -> int:
        return validate_postgres_port(v)

    @computed_field
    @property
    def url(self) -> str:
        import urllib.parse
        encoded_password = urllib.parse.quote_plus(self.password)
        return f"postgresql://{self.user}:{encoded_password}@{self.host}:{self.port}/{self.db}"

class Neo4jSettings(BaseSettings):
    host: str = Field(validation_alias="NEO4J_HOST", default="localhost")
    port: int = Field(validation_alias="NEO4J_PORT", default=7687)
    username: str = Field(validation_alias="NEO4J_USERNAME", default="neo4j")
    password: str = Field(validation_alias="NEO4J_PASSWORD", default="password")
    database: str = Field(validation_alias="NEO4J_DATABASE", default="neo4j")
    
    max_connection_pool_size: int = Field(validation_alias="NEO4J_MAX_CONNECTION_POOL_SIZE", default=50)
    connection_timeout: float = Field(validation_alias="NEO4J_CONNECTION_TIMEOUT", default=30.0)
    max_transaction_retry_time: float = Field(validation_alias="NEO4J_MAX_TRANSACTION_RETRY_TIME", default=15.0)

    @computed_field
    @property
    def uri(self) -> str:
        return f"bolt://{self.host}:{self.port}"

class QdrantSettings(BaseSettings):
    host: str = Field(validation_alias="QDRANT_HOST", default="localhost")
    port: int = Field(validation_alias="QDRANT_PORT", default=6333)
    grpc_port: int = Field(validation_alias="QDRANT_GRPC_PORT", default=6334)
    api_key: Optional[str] = Field(validation_alias="QDRANT_API_KEY", default=None)
    
    collection_name: str = Field(validation_alias="QDRANT_COLLECTION_NAME", default="industry_brain")
    vector_size: int = Field(validation_alias="QDRANT_VECTOR_SIZE", default=1536)
    distance: str = Field(validation_alias="QDRANT_DISTANCE", default="Cosine")
    timeout: float = Field(validation_alias="QDRANT_TIMEOUT", default=10.0)
    use_https: bool = Field(validation_alias="QDRANT_USE_HTTPS", default=False)

    @field_validator("port", "grpc_port")
    @classmethod
    def check_port(cls, v: int) -> int:
        return validate_qdrant_port(v)

    @field_validator("vector_size")
    @classmethod
    def check_dimension(cls, v: int) -> int:
        return validate_embedding_dimensions(v)

class AWSSettings(BaseSettings):
    region: str = Field(validation_alias="AWS_REGION", default="us-east-1")
    access_key_id: Optional[str] = Field(validation_alias="AWS_ACCESS_KEY_ID", default=None)
    secret_access_key: Optional[str] = Field(validation_alias="AWS_SECRET_ACCESS_KEY", default=None)

    @field_validator("region")
    @classmethod
    def check_region(cls, v: str) -> str:
        return validate_aws_region(v)

class LLMSettings(BaseSettings):
    default_model: str = Field(validation_alias="DEFAULT_LLM_MODEL", default="anthropic.claude-3-haiku-20240307-v1:0")
    fallback_model: str = Field(validation_alias="FALLBACK_LLM_MODEL", default="meta.llama3-8b-instruct-v1:0")
    provider: LLMProviderEnum = Field(validation_alias="LLM_PROVIDER", default=LLMProviderEnum.BEDROCK)
    
    temperature: float = Field(validation_alias="LLM_TEMPERATURE", default=0.1)
    top_p: float = Field(validation_alias="LLM_TOP_P", default=0.9)
    top_k: int = Field(validation_alias="LLM_TOP_K", default=250)
    max_tokens: int = Field(validation_alias="LLM_MAX_TOKENS", default=1024)

    @field_validator("temperature")
    @classmethod
    def check_temperature(cls, v: float) -> float:
        return validate_temperature(v)

    @field_validator("top_p")
    @classmethod
    def check_top_p(cls, v: float) -> float:
        return validate_top_p(v)

    @field_validator("top_k")
    @classmethod
    def check_top_k(cls, v: int) -> int:
        return validate_top_k(v)

class EmbeddingSettings(BaseSettings):
    default_model: str = Field(validation_alias="DEFAULT_EMBEDDING_MODEL", default="amazon.titan-embed-text-v2:0")
    fallback_model: str = Field(validation_alias="FALLBACK_EMBEDDING_MODEL", default="amazon.titan-embed-text-v1")
    provider: EmbeddingProviderEnum = Field(validation_alias="EMBEDDING_PROVIDER", default=EmbeddingProviderEnum.BEDROCK)
    dimension: int = Field(validation_alias="EMBEDDING_DIMENSION", default=1536)

    @field_validator("dimension")
    @classmethod
    def check_dimension(cls, v: int) -> int:
        return validate_embedding_dimensions(v)

class RetrievalSettings(BaseSettings):
    weight_semantic: float = Field(validation_alias="RETRIEVAL_WEIGHT_SEMANTIC", default=0.60)
    weight_graph: float = Field(validation_alias="RETRIEVAL_WEIGHT_GRAPH", default=0.25)
    weight_metadata: float = Field(validation_alias="RETRIEVAL_WEIGHT_METADATA", default=0.15)
    
    top_k_vector: int = Field(validation_alias="TOP_K_VECTOR", default=10)
    top_k_graph: int = Field(validation_alias="TOP_K_GRAPH", default=10)
    top_k_metadata: int = Field(validation_alias="TOP_K_METADATA", default=10)
    
    min_similarity_score: float = Field(validation_alias="MIN_SIMILARITY_SCORE", default=0.50)
    enable_reranking: bool = Field(validation_alias="ENABLE_RERANKING", default=True)
    enable_permission_filtering: bool = Field(validation_alias="ENABLE_PERMISSION_FILTERING", default=True)
    enable_metadata_filtering: bool = Field(validation_alias="ENABLE_METADATA_FILTERING", default=True)

class ChunkingSettings(BaseSettings):
    strategy: ChunkStrategyEnum = Field(validation_alias="CHUNK_STRATEGY", default=ChunkStrategyEnum.LAYOUT_AWARE)
    min_chunk_size: int = Field(validation_alias="MIN_CHUNK_SIZE", default=200)
    max_chunk_size: int = Field(validation_alias="MAX_CHUNK_SIZE", default=1000)
    chunk_overlap: int = Field(validation_alias="CHUNK_OVERLAP", default=100)
    
    preserve_layout: bool = Field(validation_alias="PRESERVE_LAYOUT", default=True)
    preserve_tables: bool = Field(validation_alias="PRESERVE_TABLES", default=True)
    preserve_images: bool = Field(validation_alias="PRESERVE_IMAGES", default=True)

    @model_validator(mode="after")
    def check_chunk_sizes(self) -> 'ChunkingSettings':
        return validate_chunk_sizes(self)

class ProcessingSettings(BaseSettings):
    max_upload_size: int = Field(validation_alias="MAX_UPLOAD_SIZE", default=10485760) # 10 MB
    default_doc_classification: str = Field(validation_alias="DEFAULT_DOC_CLASSIFICATION", default="Internal")
    pluggable_duplicate_detection: str = Field(validation_alias="PLUGGABLE_DUPLICATE_DETECTION", default="disabled")
    
    storage_provider: StorageProviderEnum = Field(validation_alias="STORAGE_PROVIDER", default=StorageProviderEnum.LOCAL)
    storage_root: str = Field(validation_alias="STORAGE_ROOT", default="storage")
    temp_directory: str = Field(validation_alias="TEMP_DIRECTORY", default="storage/tmp")
    allow_overwrite: bool = Field(validation_alias="ALLOW_OVERWRITE", default=False)
    enable_checksum: bool = Field(validation_alias="ENABLE_CHECKSUM", default=True)

    enable_docling: bool = Field(validation_alias="ENABLE_DOCLING", default=True)
    enable_ocr: bool = Field(validation_alias="ENABLE_OCR", default=True)
    ocr_provider: OCRProviderEnum = Field(validation_alias="OCR_PROVIDER", default=OCRProviderEnum.DOCLING)
    ocr_confidence_threshold: float = Field(validation_alias="OCR_CONFIDENCE_THRESHOLD", default=0.7)
    
    enable_layout_tree: bool = Field(validation_alias="ENABLE_LAYOUT_TREE", default=True)
    enable_entity_stage: bool = Field(validation_alias="ENABLE_ENTITY_STAGE", default=True)
    enable_relationship_stage: bool = Field(validation_alias="ENABLE_RELATIONSHIP_STAGE", default=True)

    @field_validator("max_upload_size")
    @classmethod
    def check_upload_size(cls, v: int) -> int:
        return validate_upload_size_limit(v)

class ContextSettings(BaseSettings):
    system_prompt_version: str = Field(validation_alias="SYSTEM_PROMPT_VERSION", default="v1.0")
    max_context_documents: int = Field(validation_alias="MAX_CONTEXT_DOCUMENTS", default=5)
    max_context_tokens: int = Field(validation_alias="MAX_CONTEXT_TOKENS", default=4096)
    enable_citations: bool = Field(validation_alias="ENABLE_CITATIONS", default=True)
    enable_confidence_score: bool = Field(validation_alias="ENABLE_CONFIDENCE_SCORE", default=True)

class AuditSettings(BaseSettings):
    enable_audit_logging: bool = Field(validation_alias="ENABLE_AUDIT_LOGGING", default=True)
    enable_user_history: bool = Field(validation_alias="ENABLE_USER_HISTORY", default=True)
    audit_retention_days: int = Field(validation_alias="AUDIT_RETENTION_DAYS", default=365)
    history_retention_days: int = Field(validation_alias="HISTORY_RETENTION_DAYS", default=90)
    max_history_events: int = Field(validation_alias="MAX_HISTORY_EVENTS", default=100)

class NotificationSettings(BaseSettings):
    enable_notifications: bool = Field(validation_alias="ENABLE_NOTIFICATIONS", default=True)
    provider: NotificationProviderEnum = Field(validation_alias="NOTIFICATION_PROVIDER", default=NotificationProviderEnum.IN_APP)
    default_channel: str = Field(validation_alias="DEFAULT_NOTIFICATION_CHANNEL", default="in_app")
    retention_days: int = Field(validation_alias="NOTIFICATION_RETENTION_DAYS", default=30)

class FeatureFlagSettings(BaseSettings):
    enable_health_checks: bool = Field(validation_alias="ENABLE_HEALTH_CHECKS", default=True)
    enable_startup_validation: bool = Field(validation_alias="ENABLE_STARTUP_VALIDATION", default=True)
    
    enable_rag: bool = Field(validation_alias="ENABLE_RAG", default=True)
    enable_knowledge_graph: bool = Field(validation_alias="ENABLE_KNOWLEDGE_GRAPH", default=True)
    enable_recommendations: bool = Field(validation_alias="ENABLE_RECOMMENDATIONS", default=True)
    enable_transparency: bool = Field(validation_alias="ENABLE_TRANSPARENCY", default=True)
    enable_persona_engine: bool = Field(validation_alias="ENABLE_PERSONA_ENGINE", default=False)
    enable_compliance_agent: bool = Field(validation_alias="ENABLE_COMPLIANCE_AGENT", default=False)
    enable_rca_agent: bool = Field(validation_alias="ENABLE_RCA_AGENT", default=False)
    enable_failure_intelligence: bool = Field(validation_alias="ENABLE_FAILURE_INTELLIGENCE", default=False)

class PerformanceSettings(BaseSettings):
    request_timeout_seconds: int = Field(validation_alias="REQUEST_TIMEOUT_SECONDS", default=30)
    bedrock_runtime_timeout: int = Field(validation_alias="BEDROCK_RUNTIME_TIMEOUT", default=60)
    bedrock_max_retries: int = Field(validation_alias="BEDROCK_MAX_RETRIES", default=3)
    bedrock_streaming: bool = Field(validation_alias="BEDROCK_STREAMING", default=False)


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=str(env_file_path),
        env_file_encoding="utf-8",
        extra="ignore"
    )
    
    app: ApplicationSettings = Field(default_factory=ApplicationSettings)
    database: DatabaseSettings = Field(default_factory=DatabaseSettings)
    neo4j: Neo4jSettings = Field(default_factory=Neo4jSettings)
    qdrant: QdrantSettings = Field(default_factory=QdrantSettings)
    aws: AWSSettings = Field(default_factory=AWSSettings)
    llm: LLMSettings = Field(default_factory=LLMSettings)
    embedding: EmbeddingSettings = Field(default_factory=EmbeddingSettings)
    retrieval: RetrievalSettings = Field(default_factory=RetrievalSettings)
    chunking: ChunkingSettings = Field(default_factory=ChunkingSettings)
    processing: ProcessingSettings = Field(default_factory=ProcessingSettings)
    context: ContextSettings = Field(default_factory=ContextSettings)
    audit: AuditSettings = Field(default_factory=AuditSettings)
    notifications: NotificationSettings = Field(default_factory=NotificationSettings)
    flags: FeatureFlagSettings = Field(default_factory=FeatureFlagSettings)
    performance: PerformanceSettings = Field(default_factory=PerformanceSettings)

settings = Settings()
