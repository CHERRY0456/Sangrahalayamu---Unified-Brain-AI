import os
import sys
import time
import logging
import threading
import warnings
from typing import Dict, Any, Optional
import concurrent.futures

# Suppress PyTorch DataLoader pin_memory UserWarnings in CPU-only environments
warnings.filterwarnings("ignore", category=UserWarning, message=".*pin_memory.*")
warnings.filterwarnings("ignore", category=UserWarning, module=".*dataloader.*")

from app.core.config import settings

logger = logging.getLogger("sangrahalayamu.processing.docling")

class DoclingService:
    """
    Enterprise Thread-Safe Lazy Singleton Docling Service.
    
    Docling is NEVER initialized at application boot or FastAPI startup.
    Initialization occurs lazily on the first supported document upload request.
    The underlying DocumentConverter instance is cached and reused across requests.
    """
    _instance: Optional['DoclingService'] = None
    _lock = threading.Lock()

    def __new__(cls) -> 'DoclingService':
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super(DoclingService, cls).__new__(cls)
                    cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        if getattr(self, "_initialized", False):
            return

        with self._lock:
            if getattr(self, "_initialized", False):
                return

            self._converter = None
            self._is_ready = False
            self._init_attempted = False
            
            # Observability Metrics
            self._total_conversions = 0
            self._successful_conversions = 0
            self._failed_conversions = 0
            self._timeout_fallbacks = 0
            self._last_latency_ms = 0.0
            self._total_latency_ms = 0.0
            
            # 1. Configure Hugging Face disk cache paths
            backend_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
            hf_cache_dir = os.path.join(backend_root, ".cache", "huggingface")
            os.makedirs(os.path.join(hf_cache_dir, "hub"), exist_ok=True)
            
            # Force absolute environment overrides for all Hugging Face hub & transformers utilities
            os.environ["HF_HOME"] = hf_cache_dir
            os.environ["TRANSFORMERS_CACHE"] = os.path.join(hf_cache_dir, "hub")
            os.environ["HF_HUB_CACHE"] = os.path.join(hf_cache_dir, "hub")
            os.environ["HF_HUB_DISABLE_SYMLINKS_WARNING"] = "1"
            os.environ["HF_HUB_ENABLE_HF_TRANSFER"] = "0"
            
            # Check if models are already present on disk to lock offline mode
            hub_dir = os.path.join(hf_cache_dir, "hub")
            if os.path.exists(hub_dir) and any(f.startswith("models--") for f in os.listdir(hub_dir)):
                logger.info("[DoclingService] Hugging Face layout models detected in cache. Enabling offline mode.")
                os.environ["HF_HUB_OFFLINE"] = "1"
                os.environ["TRANSFORMERS_OFFLINE"] = "1"
            
            # 2. CPU-Only Optimization Thread Environment Settings
            os.environ["CUDA_VISIBLE_DEVICES"] = ""
            os.environ.setdefault("OMP_NUM_THREADS", "1")
            os.environ.setdefault("MKL_NUM_THREADS", "1")
            os.environ.setdefault("TOKENIZERS_PARALLELISM", "false")

            self._hf_cache_dir = hf_cache_dir
            self._initialized = True
            logger.info("[DoclingService] Singleton registered. Docling remains UNINITIALIZED until first upload.")

    def _lazy_init_converter(self) -> bool:
        """
        Lazily instantiates the IBM Docling DocumentConverter.
        Guarded by a thread lock so initialization occurs exactly once.
        """
        if not settings.processing.enable_docling:
            logger.info("[DoclingService] ENABLE_DOCLING=False in settings. Docling initialization bypassed.")
            return False

        if self._is_ready:
            return True

        with self._lock:
            if self._is_ready:
                return True

            logger.info("[DoclingService] First upload received. Initializing IBM Docling DocumentConverter lazily...")
            start_t = time.perf_counter()
            self._init_attempted = True
            try:
                self._converter = self._create_converter()
                self._is_ready = True
                init_ms = (time.perf_counter() - start_t) * 1000
                logger.info(f"[DoclingService|SUCCESS] Docling DocumentConverter initialized in {init_ms:.1f}ms. Models cached at '{self._hf_cache_dir}'.")
                
                # Lock offline mode once initialized so future runs never re-download
                os.environ["HF_HUB_OFFLINE"] = "1"
                os.environ["TRANSFORMERS_OFFLINE"] = "1"
                return True
            except Exception as e:
                # If offline initialization failed because a model variant was missing, try online once
                if os.environ.get("HF_HUB_OFFLINE") == "1":
                    logger.warning(f"[DoclingService|WARN] Offline initialization encountered issue ({e}). Retrying online sync once...")
                    os.environ.pop("HF_HUB_OFFLINE", None)
                    os.environ.pop("TRANSFORMERS_OFFLINE", None)
                    try:
                        self._converter = self._create_converter()
                        self._is_ready = True
                        os.environ["HF_HUB_OFFLINE"] = "1"
                        os.environ["TRANSFORMERS_OFFLINE"] = "1"
                        return True
                    except Exception as online_err:
                        logger.warning(f"[DoclingService|WARN] Docling online sync failed: {online_err}. Native fallbacks active.")
                        self._converter = None
                        self._is_ready = False
                        return False
                
                logger.warning(f"[DoclingService|WARN] Docling initialization failed: {e}. Native fallback parsers will handle documents.")
                self._converter = None
                self._is_ready = False
                return False

    def _create_converter(self) -> Any:
        """
        Creates DocumentConverter configured with lightweight PDF pipeline options 
        (do_ocr=False, do_table_structure=False, images_scale=1.0) to prevent C++ std::bad_alloc OOM crashes.
        """
        from docling.document_converter import DocumentConverter
        try:
            from docling.document_converter import PdfFormatOption
            from docling.datamodel.pipeline_options import PdfPipelineOptions
            
            pipeline_options = PdfPipelineOptions()
            pipeline_options.do_ocr = False
            pipeline_options.do_table_structure = False
            pipeline_options.images_scale = 1.0
            
            # Disable page image generation if supported by the Docling version
            if hasattr(pipeline_options, "generate_page_images"):
                setattr(pipeline_options, "generate_page_images", False)
            
            return DocumentConverter(
                format_options={
                    "pdf": PdfFormatOption(pipeline_options=pipeline_options)
                }
            )
        except Exception:
            return DocumentConverter()

    def convert_document(self, file_path: str, timeout_seconds: Optional[int] = None) -> Any:
        """
        Converts a document layout using the Docling singleton.
        Enforces configurable timeout guard (settings.processing.parser_timeout_seconds).
        """
        if not self._lazy_init_converter() or self._converter is None:
            raise RuntimeError("Docling converter is not initialized.")

        effective_timeout = timeout_seconds or settings.processing.parser_timeout_seconds
        start_t = time.perf_counter()
        self._total_conversions += 1

        def _do_convert():
            return self._converter.convert(file_path)

        try:
            with concurrent.futures.ThreadPoolExecutor(max_workers=1) as executor:
                future = executor.submit(_do_convert)
                result = future.result(timeout=effective_timeout)
                
            latency_ms = (time.perf_counter() - start_t) * 1000
            self._last_latency_ms = latency_ms
            self._total_latency_ms += latency_ms
            self._successful_conversions += 1
            logger.info(f"[DoclingService] Document '{os.path.basename(file_path)}' converted successfully in {latency_ms:.1f}ms.")
            return result

        except concurrent.futures.TimeoutError as te:
            self._failed_conversions += 1
            self._timeout_fallbacks += 1
            logger.warning(f"[DoclingService|TIMEOUT] Docling exceeded timeout threshold ({effective_timeout}s) for '{os.path.basename(file_path)}'.")
            raise TimeoutError(f"Docling conversion timed out after {effective_timeout} seconds.") from te
        except Exception as err:
            self._failed_conversions += 1
            logger.warning(f"[DoclingService|ERROR] Docling conversion failed for '{os.path.basename(file_path)}': {err}")
            raise err

    def is_initialized(self) -> bool:
        return self._is_ready

    def are_models_cached(self) -> bool:
        if os.path.exists(self._hf_cache_dir):
            return len(os.listdir(self._hf_cache_dir)) > 0
        return False

    def get_metrics(self) -> Dict[str, Any]:
        """
        Returns full observability metrics for health and debugging.
        """
        import psutil
        process = psutil.Process(os.getpid())
        memory_mb = process.memory_info().rss / (1024 * 1024)

        avg_latency = (self._total_latency_ms / self._successful_conversions) if self._successful_conversions > 0 else 0.0

        return {
            "docling_status": "initialized" if self._is_ready else ("failed" if self._init_attempted else "not_initialized"),
            "models_cached": self.are_models_cached(),
            "cache_directory": self._hf_cache_dir,
            "max_workers": settings.processing.parser_max_workers,
            "timeout_seconds": settings.processing.parser_timeout_seconds,
            "memory_usage_mb": round(memory_mb, 2),
            "total_conversions": self._total_conversions,
            "successful_conversions": self._successful_conversions,
            "failed_conversions": self._failed_conversions,
            "timeout_fallbacks": self._timeout_fallbacks,
            "last_latency_ms": round(self._last_latency_ms, 2),
            "avg_latency_ms": round(avg_latency, 2)
        }

# Global Singleton Exposing Instance
docling_service = DoclingService()
