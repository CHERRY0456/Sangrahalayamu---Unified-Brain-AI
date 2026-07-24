from enum import Enum

class EnvironmentEnum(str, Enum):
    DEVELOPMENT = "development"
    STAGING = "staging"
    PRODUCTION = "production"
    TESTING = "testing"

class LogLevelEnum(str, Enum):
    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"

class StorageProviderEnum(str, Enum):
    LOCAL = "local"
    S3 = "s3"
    AZURE = "azure"
    GCS = "gcs"

class NotificationProviderEnum(str, Enum):
    IN_APP = "in_app"
    EMAIL = "email"
    SLACK = "slack"

class OCRProviderEnum(str, Enum):
    TESSERACT = "tesseract"
    TEXTRACT = "textract"
    DOCLING = "docling"

class LLMProviderEnum(str, Enum):
    BEDROCK = "bedrock"
    OPENAI = "openai"
    AZURE = "azure"
    ANTHROPIC = "anthropic"

class EmbeddingProviderEnum(str, Enum):
    BEDROCK = "bedrock"
    OPENAI = "openai"
    SENTENCE_TRANSFORMERS = "sentence_transformers"

class ChunkStrategyEnum(str, Enum):
    SEMANTIC = "semantic"
    FIXED_SIZE = "fixed_size"
    LAYOUT_AWARE = "layout_aware"
