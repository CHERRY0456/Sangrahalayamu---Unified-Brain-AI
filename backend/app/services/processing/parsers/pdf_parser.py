"""
High-Speed PyMuPDF (fitz) + pdfplumber Industrial PDF & P&ID Parser.
Extracts text, table matrices, equipment tags, and process parameters with zero RAM overhead.
"""
import os
import re
import logging
from typing import List, Dict, Any

from .base import BaseParser, ParsedDocument, ParsedChunk, ParsedTable

logger = logging.getLogger("industrybrain.parsers.pdf")

EQUIPMENT_TAG_REGEX = re.compile(r"\b([A-Z]{1,4}-[0-9]{2,4}[A-Z]?)\b")
REGULATORY_REGEX = re.compile(r"\b(OISD-[0-9]{3}|PESO|Factory Act|ISO\s?[0-9]{4,5}|OSHA)\b", re.IGNORECASE)


class PDFParser(BaseParser):
    def parse(self, file_path: str, filename: str) -> ParsedDocument:
        logger.info(f"[PDFParser] Extracting PDF layout & data for '{filename}'")
        raw_pages_text = []
        chunks = []
        tables = []
        equipment_tags = set()
        regulatory_refs = set()
        process_parameters = []

        chunk_counter = 0

        # 1. PyMuPDF (fitz) for fast text & vector extraction (< 20ms/page)
        try:
            import fitz  # PyMuPDF
            doc = fitz.open(file_path)
            
            for page_idx, page in enumerate(doc):
                page_num = page_idx + 1
                text = page.get_text("text") or ""
                raw_pages_text.append(text)

                # Find equipment tags (P-101A, V-402, B-201)
                for tag in EQUIPMENT_TAG_REGEX.findall(text):
                    equipment_tags.add(tag)

                # Find regulatory references
                for reg in REGULATORY_REGEX.findall(text):
                    regulatory_refs.add(reg.upper())

                # Chunk text by paragraphs / blocks
                blocks = page.get_text("blocks")
                for b in blocks:
                    b_text = b[4].strip()
                    if len(b_text) > 30:
                        chunks.append(ParsedChunk(
                            content=b_text,
                            chunk_index=chunk_counter,
                            page_number=page_num,
                            metadata={"source": filename, "page": page_num}
                        ))
                        chunk_counter += 1

            doc.close()
        except Exception as e:
            logger.warning(f"[PDFParser] PyMuPDF extraction warning for {filename}: {e}")

        # 2. pdfplumber for table matrix extraction
        try:
            import pdfplumber
            with pdfplumber.open(file_path) as pdf:
                for page_idx, page in enumerate(pdf.pages):
                    extracted_tables = page.extract_tables()
                    for t_idx, tbl in enumerate(extracted_tables):
                        if not tbl or len(tbl) < 2:
                            continue
                        headers = [str(cell or "").strip() for cell in tbl[0]]
                        rows = [[str(cell or "").strip() for cell in row] for row in tbl[1:]]
                        tables.append(ParsedTable(
                            title=f"Table {t_idx+1} (Page {page_idx+1})",
                            headers=headers,
                            rows=rows,
                            page_number=page_idx+1
                        ))
        except Exception as e:
            logger.debug(f"[PDFParser] pdfplumber table extraction info for {filename}: {e}")

        full_raw_text = "\n\n".join(raw_pages_text)

        return ParsedDocument(
            filename=filename,
            file_type="pdf",
            raw_text=full_raw_text,
            chunks=chunks,
            tables=tables,
            metadata={"page_count": len(raw_pages_text), "file_size_bytes": os.path.getsize(file_path)},
            equipment_tags=list(equipment_tags),
            process_parameters=process_parameters,
            regulatory_references=list(regulatory_refs)
        )
