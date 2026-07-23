import os
import mimetypes
import logging
from abc import ABC, abstractmethod
from typing import List, Dict, Type, Optional, Tuple
from app.services.processing.models import ParserResult, LayoutTreeNode

logger = logging.getLogger("sangrahalayamu.processing.parser_registry")


class BaseParser(ABC):
    """
    Abstract Base Parser interface. Every specialized parser implements this.
    """
    @abstractmethod
    def can_parse(self, file_path: str, mime_type: str, file_header: bytes) -> bool:
        """
        Determines if this parser handles the given file path/modality.
        """
        pass

    @abstractmethod
    def parse(self, file_path: str, filename: str) -> ParserResult:
        """
        Parses the document into the unified ParserResult layout structure.
        """
        pass


class _ParserRegistry:
    """
    Registry for pluggable Modality-Aware parsers.
    Selection is content-modality driven rather than purely extension based.
    """
    def __init__(self) -> None:
        self._parsers: List[BaseParser] = []

    def register_parser(self, parser_instance: BaseParser) -> None:
        """
        Register a new parser instance.
        """
        self._parsers.append(parser_instance)
        logger.debug(f"[ParserRegistry] Registered parser: {type(parser_instance).__name__}")

    def select_parser(self, file_path: str) -> BaseParser:
        """
        Analyzes the file contents (magic bytes, headers, structures) to detect
        its modality and select the correct parser.
        """
        # Read the first 4096 bytes for signature inspections
        file_header = b""
        if os.path.exists(file_path):
            try:
                with open(file_path, "rb") as f:
                    file_header = f.read(4096)
            except Exception as e:
                logger.warning(f"[ParserRegistry] Could not read file header for magic check: {e}")

        # Guess mime type based on filename
        mime_type, _ = mimetypes.guess_type(file_path)
        mime_type = mime_type or "application/octet-stream"

        # Special magic checks to refine mime type if generic text or binary
        refined_mime = self._refine_mime_type(file_path, mime_type, file_header)

        # Loop registered parsers and pick the first one that votes yes
        for parser in self._parsers:
            if parser.can_parse(file_path, refined_mime, file_header):
                logger.info(
                    f"[ParserRegistry] Selected parser '{type(parser).__name__}' "
                    f"for file '{os.path.basename(file_path)}' (detected mime: {refined_mime})"
                )
                return parser

        # Fallback to GenericTextParser if nothing else fits
        # Find the text parser in the registry
        for parser in self._parsers:
            if type(parser).__name__ == "GenericTextParser":
                return parser

        # If not registered, return a default text parser instance
        from .parser_registry import GenericTextParser
        return GenericTextParser()

    def _refine_mime_type(self, file_path: str, base_mime: str, file_header: bytes) -> str:
        """
        Inspect magic bytes or file headers to detect precise modalities.
        """
        # Image signatures
        if file_header.startswith(b"\x89PNG\r\n\x1a\n"):
            return "image/png"
        if file_header.startswith(b"\xff\xd8\xff"):
            return "image/jpeg"
        if file_header.startswith(b"RIFF") and b"WEBP" in file_header[8:16]:
            return "image/webp"
        if file_header.startswith(b"II*\x00") or file_header.startswith(b"MM\x00*"):
            return "image/tiff"
            
        # PDF signature
        if file_header.startswith(b"%PDF-"):
            return "application/pdf"
            
        # Office zip files (docx, xlsx, pptx)
        if file_header.startswith(b"PK\x03\x04"):
            ext = os.path.splitext(file_path)[1].lower()
            if ext in (".docx", ".docm"):
                return "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
            if ext in (".xlsx", ".xlsm"):
                return "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            if ext in (".pptx", ".pptm"):
                return "application/vnd.openxmlformats-officedocument.presentationml.presentation"

        # Check if email header
        # E.g., starts with From: , Received: , Date: , Subject:
        lines = file_header.split(b"\n")[:10]
        email_indicators = 0
        for line in lines:
            if any(line.lower().startswith(prefix) for prefix in (b"from:", b"to:", b"subject:", b"date:", b"received:")):
                email_indicators += 1
        if email_indicators >= 2:
            return "message/rfc822"

        # Check if structured CSV/TSV table
        # Look for commas/tabs in first few lines
        text_preview = ""
        try:
            text_preview = file_header.decode("utf-8", errors="ignore")
        except Exception:
            pass

        if text_preview:
            lines_str = text_preview.split("\n")[:5]
            if len(lines_str) >= 2:
                # Count commas, semicolons, tabs
                comma_counts = [line.count(",") for line in lines_str if line.strip()]
                semi_counts = [line.count(";") for line in lines_str if line.strip()]
                tab_counts = [line.count("\t") for line in lines_str if line.strip()]
                
                # If they are consistent and > 0, treat as CSV/TSV
                if len(comma_counts) >= 2 and all(c > 0 for c in comma_counts) and len(set(comma_counts)) <= 2:
                    return "text/csv"
                if len(semi_counts) >= 2 and all(c > 0 for c in semi_counts) and len(set(semi_counts)) <= 2:
                    return "text/csv"
                if len(tab_counts) >= 2 and all(t > 0 for t in tab_counts) and len(set(tab_counts)) <= 2:
                    return "text/tab-separated-values"

            # Check if Log format
            # Typical log file lines start with ISO date or timestamp, or carry priority tags [INFO], [WARNING]
            log_indicators = 0
            for line in lines_str:
                if any(tag in line for tag in ["[INFO]", "[WARN", "[ERR", "[DEBUG", " | INFO ", " | WARN"]):
                    log_indicators += 1
                if len(line) > 10 and (line[:4].isdigit() and line[4] == "-"): # starts with YYYY-MM-DD
                    log_indicators += 1
            if log_indicators >= 2:
                return "text/x-log"

            # Check if source code symbols
            code_keywords = ["import ", "def ", "class ", "function ", "#include", "func ", "select ", "package ", "package main", "using namespace"]
            if any(kw in text_preview for kw in code_keywords):
                return "text/x-source"

        return base_mime


# Singleton ParserRegistry
ParserRegistry = _ParserRegistry()
