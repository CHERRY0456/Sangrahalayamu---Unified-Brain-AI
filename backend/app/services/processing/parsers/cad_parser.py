"""
Industrial CAD Parser for AutoCAD .DXF engineering drawings & P&ID vector schematics.
Extracts drawing layers, text blocks, equipment tags, and line connections.
"""
import os
import re
import logging
from typing import List, Set

from .base import BaseParser, ParsedDocument, ParsedChunk

logger = logging.getLogger("industrybrain.parsers.cad")

EQUIPMENT_TAG_REGEX = re.compile(r"\b([A-Z]{1,4}-[0-9]{2,4}[A-Z]?)\b")


class CADParser(BaseParser):
    def parse(self, file_path: str, filename: str) -> ParsedDocument:
        logger.info(f"[CADParser] Parsing CAD drawing file '{filename}'")
        raw_text_lines = []
        chunks = []
        equipment_tags: Set[str] = set()
        chunk_idx = 0

        ext = os.path.splitext(filename)[1].lower()
        if ext == ".dxf":
            try:
                import ezdxf
                doc = ezdxf.readfile(file_path)
                msp = doc.modelspace()

                # Extract text & MText entities
                for entity in msp:
                    text_content = ""
                    if entity.dxftype() == "TEXT":
                        text_content = entity.dxf.text.strip()
                    elif entity.dxftype() == "MTEXT":
                        text_content = entity.text.strip()

                    if text_content:
                        raw_text_lines.append(f"Layer [{entity.dxf.layer}]: {text_content}")
                        for tag in EQUIPMENT_TAG_REGEX.findall(text_content):
                            equipment_tags.add(tag)

            except Exception as e:
                logger.warning(f"[CADParser] ezdxf extraction failed for {filename}: {e}")

        # Batch text into chunks
        full_raw_text = "\n".join(raw_text_lines)
        for i in range(0, len(raw_text_lines), 20):
            batch = "\n".join(raw_text_lines[i:i+20])
            if batch.strip():
                chunks.append(ParsedChunk(
                    content=batch,
                    chunk_index=chunk_idx,
                    metadata={"source": filename, "format": "CAD"}
                ))
                chunk_idx += 1

        return ParsedDocument(
            filename=filename,
            file_type="dxf" if ext == ".dxf" else "cad",
            raw_text=full_raw_text,
            chunks=chunks,
            equipment_tags=list(equipment_tags)
        )
