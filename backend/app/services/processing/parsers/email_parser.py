"""
Industrial Email Archive Parser for .MSG and .EML communication records.
Extracts email metadata, subject lines, body text, equipment tags, and attachments.
"""
import os
import re
import logging
from typing import Set

from .base import BaseParser, ParsedDocument, ParsedChunk

logger = logging.getLogger("industrybrain.parsers.email")

EQUIPMENT_TAG_REGEX = re.compile(r"\b([A-Z]{1,4}-[0-9]{2,4}[A-Z]?)\b")


class EmailParser(BaseParser):
    def parse(self, file_path: str, filename: str) -> ParsedDocument:
        logger.info(f"[EmailParser] Parsing email archive '{filename}'")
        ext = os.path.splitext(filename)[1].lower()

        subject = ""
        sender = ""
        body = ""
        equipment_tags: Set[str] = set()

        if ext == ".msg":
            try:
                import extract_msg
                msg = extract_msg.Message(file_path)
                subject = msg.subject or ""
                sender = msg.sender or ""
                body = msg.body or ""
                msg.close()
            except Exception as e:
                logger.warning(f"[EmailParser] extract_msg failed for {filename}: {e}")
        elif ext == ".eml":
            try:
                import mailparser
                mail = mailparser.parse_from_file(file_path)
                subject = mail.subject or ""
                sender = str(mail.from_)
                body = mail.body or ""
            except Exception as e:
                logger.warning(f"[EmailParser] mailparser failed for {filename}: {e}")
        else:
            with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                body = f.read()

        full_raw_text = f"Subject: {subject}\nFrom: {sender}\n\n{body}"
        for tag in EQUIPMENT_TAG_REGEX.findall(full_raw_text):
            equipment_tags.add(tag)

        chunks = []
        if full_raw_text.strip():
            chunks.append(ParsedChunk(
                content=full_raw_text,
                chunk_index=0,
                metadata={"source": filename, "subject": subject, "sender": sender}
            ))

        return ParsedDocument(
            filename=filename,
            file_type="msg" if ext == ".msg" else "eml",
            raw_text=full_raw_text,
            chunks=chunks,
            equipment_tags=list(equipment_tags),
            metadata={"subject": subject, "sender": sender}
        )
