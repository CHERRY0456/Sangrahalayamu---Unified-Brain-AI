"""
Heterogeneous Document Format & Mime-Type Detector for Industrial Ingestion.
"""
import os
import logging
from typing import Type
from .parsers.base import BaseParser
from .parsers.pdf_parser import PDFParser
from .parsers.office_parser import OfficeParser
from .parsers.cad_parser import CADParser
from .parsers.email_parser import EmailParser
from .parsers.image_parser import ImageParser

logger = logging.getLogger("industrybrain.processing.detector")


class FormatDetector:
    @staticmethod
    def get_parser(filename: str) -> BaseParser:
        """
        Resolves the appropriate format parser based on file extension and mime type.
        """
        ext = os.path.splitext(filename)[1].lower()

        if ext == ".pdf":
            return PDFParser()
        elif ext in [".docx", ".xlsx", ".xls", ".csv", ".pptx"]:
            return OfficeParser()
        elif ext in [".dxf", ".dwg"]:
            return CADParser()
        elif ext in [".msg", ".eml"]:
            return EmailParser()
        elif ext in [".png", ".jpg", ".jpeg", ".tiff", ".bmp"]:
            return ImageParser()
        else:
            # Fallback to PDF/Text parser
            logger.info(f"[FormatDetector] Defaulting parser for unknown extension '{ext}' to PDFParser")
            return PDFParser()


format_detector = FormatDetector()
