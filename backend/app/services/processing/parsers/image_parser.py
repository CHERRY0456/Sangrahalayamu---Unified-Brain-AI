"""
Industrial Image & Scanned Form Parser using Tesseract OCR & OpenCV.
Extracts text, inspection details, and equipment tags from visual records.
"""
import os
import re
import logging
from typing import Set

from .base import BaseParser, ParsedDocument, ParsedChunk

logger = logging.getLogger("industrybrain.parsers.image")

EQUIPMENT_TAG_REGEX = re.compile(r"\b([A-Z]{1,4}-[0-9]{2,4}[A-Z]?)\b")


class ImageParser(BaseParser):
    def parse(self, file_path: str, filename: str) -> ParsedDocument:
        logger.info(f"[ImageParser] Running OCR on image file '{filename}'")
        extracted_text = ""
        equipment_tags: Set[str] = set()

        try:
            import pytesseract
            from PIL import Image
            img = Image.open(file_path)
            extracted_text = pytesseract.image_to_string(img) or ""
        except Exception as e:
            logger.warning(f"[ImageParser] PyTesseract failed for {filename}: {e}")

        extracted_text = extracted_text.strip()
        for tag in EQUIPMENT_TAG_REGEX.findall(extracted_text):
            equipment_tags.add(tag)

        chunks = []
        if extracted_text:
            chunks.append(ParsedChunk(
                content=extracted_text,
                chunk_index=0,
                metadata={"source": filename, "format": "OCR Image"}
            ))

        return ParsedDocument(
            filename=filename,
            file_type="image",
            raw_text=extracted_text,
            chunks=chunks,
            equipment_tags=list(equipment_tags)
        )
