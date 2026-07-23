import os
import re
import uuid
import logging
from typing import List, Dict, Any, Optional
from app.services.processing.models import ParserResult, LayoutTreeNode
from app.services.processing.parser_registry import BaseParser, ParserRegistry
from app.services.processing.ocr import OCRRouter

logger = logging.getLogger("sangrahalayamu.processing.parser")


# ---------------------------------------------------------------------------
# Utility: Helper to convert flat parsed elements to a hierarchical layout tree
# ---------------------------------------------------------------------------

def build_hierarchical_layout_tree(
    doc_title: str,
    flat_elements: List[Dict[str, Any]],
) -> LayoutTreeNode:
    """
    Takes flat parsed elements (with type, text, heading_level, page_number, bounding_box, etc.)
    and nests them into a hierarchical tree where heading nodes act as parents to
    subsequent paragraphs/tables/lists under their scope.
    """
    root = LayoutTreeNode(
        node_id="root",
        type="heading",  # Act as root heading
        text=doc_title,
        page_numbers=[1],
        confidence=1.0,
        metadata={"level": 0}
    )

    # Active path stack of nodes. Starts with root at level 0.
    # Elements in stack are tuples: (heading_level: int, node: LayoutTreeNode)
    stack: List[tuple[int, LayoutTreeNode]] = [(0, root)]

    node_idx = 0
    for el in flat_elements:
        node_id = f"node-{node_idx}"
        node_idx += 1

        el_type = el.get("type", "paragraph")
        text = el.get("text", "")
        pages = el.get("page_numbers", [el.get("page_number", 1)])
        bbox = el.get("bounding_box", None)
        conf = el.get("confidence", 1.0)
        meta = el.get("metadata", {})

        new_node = LayoutTreeNode(
            node_id=node_id,
            type=el_type,
            text=text,
            page_numbers=pages,
            bounding_box=bbox,
            confidence=conf,
            metadata=meta
        )

        if el_type == "heading":
            heading_level = el.get("heading_level", 1) or 1
            # Pop stack until we find a heading with a lower level (i.e. parent level)
            while stack and stack[-1][0] >= heading_level:
                stack.pop()
            
            # The top of stack is now the parent
            parent_node = stack[-1][1]
            parent_node.children.append(new_node)
            # Push self to stack
            stack.append((heading_level, new_node))
        else:
            # Paragraph, Table, List etc. belong to the current active heading on top of stack
            parent_node = stack[-1][1]
            parent_node.children.append(new_node)

    return root


# ---------------------------------------------------------------------------
# 1. GenericTextParser
# ---------------------------------------------------------------------------

class GenericTextParser(BaseParser):
    """
    Fallback parser for standard text, markdown, rtf, configuration files.
    """
    def can_parse(self, file_path: str, mime_type: str, file_header: bytes) -> bool:
        # Falls back to true for general text, or if file ext is txt, md, rtf
        ext = os.path.splitext(file_path)[1].lower()
        if ext in (".txt", ".md", ".rtf", ".cfg", ".conf", ".ini"):
            return True
        if mime_type.startswith("text/"):
            return True
        return False

    def parse(self, file_path: str, filename: str) -> ParserResult:
        logger.info(f"[GenericTextParser] Parsing '{filename}'")
        raw_text = ""
        try:
            with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                raw_text = f.read()
        except Exception as e:
            raw_text = f"Generic fallback parsed content placeholder. File read error: {e}"

        # Parse text into paragraphs and headings
        lines = raw_text.split("\n")
        flat_elements = []
        
        current_paragraph_lines = []
        for line in lines:
            line_str = line.strip()
            if not line_str:
                if current_paragraph_lines:
                    text_block = " ".join(current_paragraph_lines)
                    flat_elements.append({"type": "paragraph", "text": text_block, "page_number": 1})
                    current_paragraph_lines = []
                continue

            # Heading checks: Starts with # (markdown) or is a short capital line
            if line_str.startswith("#"):
                if current_paragraph_lines:
                    text_block = " ".join(current_paragraph_lines)
                    flat_elements.append({"type": "paragraph", "text": text_block, "page_number": 1})
                    current_paragraph_lines = []

                level = len(line_str) - len(line_str.lstrip("#"))
                heading_text = line_str.lstrip("#").strip()
                flat_elements.append({"type": "heading", "text": heading_text, "heading_level": level, "page_number": 1})
            elif line_str.isupper() and len(line_str) < 80:
                if current_paragraph_lines:
                    text_block = " ".join(current_paragraph_lines)
                    flat_elements.append({"type": "paragraph", "text": text_block, "page_number": 1})
                    current_paragraph_lines = []

                flat_elements.append({"type": "heading", "text": line_str, "heading_level": 2, "page_number": 1})
            else:
                current_paragraph_lines.append(line_str)

        if current_paragraph_lines:
            text_block = " ".join(current_paragraph_lines)
            flat_elements.append({"type": "paragraph", "text": text_block, "page_number": 1})

        # Compile Title
        title = filename
        for el in flat_elements:
            if el["type"] == "heading":
                title = el["text"]
                break

        # Tree layout
        root = build_hierarchical_layout_tree(title, flat_elements)

        return ParserResult(
            title=title,
            layout_root=root,
            raw_markdown=raw_text,
            file_type="plain_text",
            word_count=len(raw_text.split()),
            metadata={"parser": "GenericTextParser"}
        )


# ---------------------------------------------------------------------------
# 2. DoclingParser
# ---------------------------------------------------------------------------

class DoclingParser(BaseParser):
    """
    Structured document intelligence parser powered by IBM Docling.
    Falls back gracefully to PyPDF / python-docx / rule-based parsers if dependencies fail.
    """
    def can_parse(self, file_path: str, mime_type: str, file_header: bytes) -> bool:
        ext = os.path.splitext(file_path)[1].lower()
        if ext in (".pdf", ".docx", ".doc", ".pptx", ".ppt", ".html", ".htm"):
            return True
        if mime_type in ("application/pdf", "application/vnd.openxmlformats-officedocument.wordprocessingml.document", "application/msword"):
            return True
        return False

    def parse(self, file_path: str, filename: str) -> ParserResult:
        logger.info(f"[DoclingParser] Attempting IBM Docling parse for '{filename}'")
        try:
            from docling.document_converter import DocumentConverter
            converter = DocumentConverter()
            result = converter.convert(file_path)
            doc = result.document

            markdown_text = doc.export_to_markdown()
            flat_elements = []

            # Traverse docling items to build layout
            for element, level in doc.iterate_items():
                label = getattr(element, "label", "text").lower()
                el_type = "paragraph"
                heading_level = None

                if "heading" in label or "title" in label:
                    el_type = "heading"
                    heading_level = getattr(element, "level", 1) or 1
                elif "table" in label:
                    el_type = "table"
                elif "list" in label:
                    el_type = "list"

                text_content = getattr(element, "text", "")
                page_no = 1
                prov = getattr(element, "prov", None)
                if prov and len(prov) > 0:
                    page_no = getattr(prov[0], "page_no", 1)

                flat_elements.append({
                    "type": el_type,
                    "text": text_content,
                    "heading_level": heading_level,
                    "page_number": page_no,
                    "confidence": 1.0,
                    "metadata": {"docling_label": label}
                })

            title = filename
            for el in flat_elements:
                if el["type"] == "heading" and el["heading_level"] == 1:
                    title = el["text"]
                    break

            root = build_hierarchical_layout_tree(title, flat_elements)

            return ParserResult(
                title=title,
                layout_root=root,
                raw_markdown=markdown_text,
                file_type="structured_document",
                word_count=len(markdown_text.split()),
                metadata={"parser": "DoclingParser", "engine": "IBM Docling"}
            )

        except Exception as docling_err:
            logger.warning(
                f"[DoclingParser] Docling initialization failed. "
                f"Activating PDF/Docx secondary fallbacks. Error: {docling_err}"
            )
            return self._fallback_parse(file_path, filename)

    def _fallback_parse(self, file_path: str, filename: str) -> ParserResult:
        """
        Robust secondary parsing utilizing lighter standard libraries.
        """
        ext = os.path.splitext(filename)[1].lower()
        flat_elements = []
        raw_text_parts = []

        if ext == ".pdf":
            try:
                import pypdf
                reader = pypdf.PdfReader(file_path)
                for page_idx, page in enumerate(reader.pages):
                    page_text = page.extract_text() or ""
                    raw_text_parts.append(page_text)
                    for line in page_text.split("\n"):
                        line_str = line.strip()
                        if not line_str:
                            continue
                        if line_str.isupper() and len(line_str) < 80:
                            flat_elements.append({
                                "type": "heading",
                                "text": line_str,
                                "heading_level": 2,
                                "page_number": page_idx + 1
                            })
                        else:
                            flat_elements.append({
                                "type": "paragraph",
                                "text": line_str,
                                "page_number": page_idx + 1
                            })
            except Exception as e:
                logger.error(f"[DoclingParserFallback] pypdf fallback failed: {e}")
        elif ext in (".docx", ".doc"):
            try:
                import docx
                doc = docx.Document(file_path)
                for p in doc.paragraphs:
                    line_str = p.text.strip()
                    if not line_str:
                        continue
                    if p.style.name.startswith("Heading"):
                        level = int(p.style.name.replace("Heading", "").strip() or "1")
                        flat_elements.append({
                            "type": "heading",
                            "text": line_str,
                            "heading_level": level,
                            "page_number": 1
                        })
                    else:
                        flat_elements.append({
                            "type": "paragraph",
                            "text": line_str,
                            "page_number": 1
                        })
                    raw_text_parts.append(line_str)
            except Exception as e:
                logger.error(f"[DoclingParserFallback] docx fallback failed: {e}")

        # If flat elements remain empty, read as plain text
        if not flat_elements:
            try:
                with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                    raw_text = f.read()
                raw_text_parts.append(raw_text)
                for line in raw_text.split("\n"):
                    line_str = line.strip()
                    if not line_str:
                        continue
                    flat_elements.append({
                        "type": "paragraph",
                        "text": line_str,
                        "page_number": 1
                    })
            except Exception:
                pass

        full_text = "\n\n".join(raw_text_parts)
        title = filename
        for el in flat_elements:
            if el["type"] == "heading":
                title = el["text"]
                break

        # Generate markdown format
        md_lines = []
        for el in flat_elements:
            if el["type"] == "heading":
                hashes = "#" * el["heading_level"]
                md_lines.append(f"{hashes} {el['text']}")
            else:
                md_lines.append(el["text"])
        raw_markdown = "\n\n".join(md_lines)

        root = build_hierarchical_layout_tree(title, flat_elements)

        return ParserResult(
            title=title,
            layout_root=root,
            raw_markdown=raw_markdown,
            file_type="structured_document",
            word_count=len(full_text.split()),
            metadata={"parser": "DoclingParser", "engine": "fallback_extractor"}
        )


# ---------------------------------------------------------------------------
# 3. SpreadsheetParser
# ---------------------------------------------------------------------------

class SpreadsheetParser(BaseParser):
    """
    Parses spreadsheets (CSV, Excel). Represents rows as tabular layout tree nodes.
    """
    def can_parse(self, file_path: str, mime_type: str, file_header: bytes) -> bool:
        ext = os.path.splitext(file_path)[1].lower()
        if ext in (".csv", ".tsv", ".xlsx", ".xls"):
            return True
        if mime_type in ("text/csv", "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"):
            return True
        return False

    def parse(self, file_path: str, filename: str) -> ParserResult:
        logger.info(f"[SpreadsheetParser] Parsing '{filename}'")
        ext = os.path.splitext(filename)[1].lower()
        flat_elements = []
        raw_text_parts = []

        if ext == ".csv":
            try:
                import csv
                with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                    reader = csv.reader(f)
                    rows = list(reader)
                
                # Combine rows to represent a markdown table
                md_rows = []
                for row in rows:
                    md_rows.append("| " + " | ".join(row) + " |")
                
                table_text = "\n".join(md_rows)
                raw_text_parts.append(table_text)
                
                flat_elements.append({
                    "type": "table",
                    "text": table_text,
                    "page_number": 1,
                    "metadata": {"columns": len(rows[0]) if rows else 0, "rows": len(rows)}
                })
            except Exception as e:
                logger.error(f"[SpreadsheetParser] CSV parse error: {e}")
        else:
            # Excel files: attempt openpyxl/pandas, fallback to simple string preview
            try:
                import openpyxl
                wb = openpyxl.load_workbook(file_path, read_only=True, data_only=True)
                for sheet in wb.sheetnames:
                    sheet_data = wb[sheet]
                    rows_list = []
                    for row in sheet_data.iter_rows(values_only=True):
                        row_vals = [str(val) if val is not None else "" for val in row]
                        if any(row_vals):
                            rows_list.append("| " + " | ".join(row_vals) + " |")
                    
                    sheet_text = f"### Sheet: {sheet}\n" + "\n".join(rows_list)
                    raw_text_parts.append(sheet_text)
                    
                    flat_elements.append({
                        "type": "table",
                        "text": sheet_text,
                        "page_number": 1,
                        "metadata": {"sheet_name": sheet}
                    })
            except Exception as e:
                logger.debug(f"[SpreadsheetParser] Excel binary open failed, using text fallback: {e}")
                # String representation fallback
                flat_elements.append({
                    "type": "paragraph",
                    "text": f"Tabular spreadsheet resource: {filename}. Excel load bypassed.",
                    "page_number": 1
                })

        raw_markdown = "\n\n".join(raw_text_parts) if raw_text_parts else f"Spreadsheet empty: {filename}"
        title = f"Spreadsheet: {filename}"
        root = build_hierarchical_layout_tree(title, flat_elements)

        return ParserResult(
            title=title,
            layout_root=root,
            raw_markdown=raw_markdown,
            file_type="spreadsheet",
            word_count=len(raw_markdown.split()),
            metadata={"parser": "SpreadsheetParser"}
        )


# ---------------------------------------------------------------------------
# 4. ImageParser
# ---------------------------------------------------------------------------

class ImageParser(BaseParser):
    """
    Parses images by delegating text extraction and coordinates to the shared OCRRouter.
    """
    def can_parse(self, file_path: str, mime_type: str, file_header: bytes) -> bool:
        ext = os.path.splitext(file_path)[1].lower()
        if ext in (".png", ".jpg", ".jpeg", ".webp", ".tiff", ".tif"):
            return True
        if mime_type.startswith("image/"):
            return True
        return False

    def parse(self, file_path: str, filename: str) -> ParserResult:
        logger.info(f"[ImageParser] Parsing '{filename}' via OCRRouter")
        
        ocr_blocks = OCRRouter.extract_layout(file_path, page_number=1)
        
        flat_elements = []
        md_lines = []
        for block in ocr_blocks:
            flat_elements.append({
                "type": block.type,
                "text": block.text,
                "page_number": block.page_number,
                "confidence": block.confidence,
                "bounding_box": block.bounding_box,
                "metadata": {"extraction_method": "OCRRouter"}
            })
            if block.type == "heading":
                md_lines.append(f"## {block.text}")
            elif block.type == "table":
                md_lines.append(block.text)
            else:
                md_lines.append(block.text)

        raw_markdown = "\n\n".join(md_lines)
        title = f"Scanned Resource: {filename}"
        
        root = build_hierarchical_layout_tree(title, flat_elements)

        return ParserResult(
            title=title,
            layout_root=root,
            raw_markdown=raw_markdown,
            file_type="image",
            word_count=len(raw_markdown.split()),
            metadata={"parser": "ImageParser", "ocr_blocks_count": len(ocr_blocks)}
        )


# ---------------------------------------------------------------------------
# 5. EmailParser
# ---------------------------------------------------------------------------

class EmailParser(BaseParser):
    """
    Parses email message exports (EML, MSG).
    """
    def can_parse(self, file_path: str, mime_type: str, file_header: bytes) -> bool:
        ext = os.path.splitext(file_path)[1].lower()
        if ext in (".eml", ".msg"):
            return True
        if mime_type in ("message/rfc822", "application/vnd.ms-outlook"):
            return True
        return False

    def parse(self, file_path: str, filename: str) -> ParserResult:
        logger.info(f"[EmailParser] Parsing '{filename}'")
        flat_elements = []
        headers = {}
        body = ""

        try:
            from email import message_from_file
            with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                msg = message_from_file(f)
            
            headers["Subject"] = msg.get("Subject", "No Subject")
            headers["From"] = msg.get("From", "Unknown Sender")
            headers["To"] = msg.get("To", "Unknown Recipient")
            headers["Date"] = msg.get("Date", "")
            
            if msg.is_multipart():
                payloads = []
                for part in msg.walk():
                    if part.get_content_type() == "text/plain":
                        payloads.append(part.get_payload(decode=True).decode("utf-8", errors="ignore"))
                body = "\n".join(payloads)
            else:
                body = msg.get_payload(decode=True).decode("utf-8", errors="ignore")
        except Exception as e:
            logger.error(f"[EmailParser] email parser failed, falling back: {e}")
            # Quick string regex fallback
            with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                content = f.read()
            subj_match = re.search(r"Subject:\s*(.*)", content, re.IGNORECASE)
            from_match = re.search(r"From:\s*(.*)", content, re.IGNORECASE)
            headers["Subject"] = subj_match.group(1).strip() if subj_match else "Email Export"
            headers["From"] = from_match.group(1).strip() if from_match else "Unknown"
            body = content

        # Build elements list
        hdr_text = "\n".join([f"{k}: {v}" for k, v in headers.items()])
        flat_elements.append({
            "type": "email_header",
            "text": hdr_text,
            "page_number": 1,
            "metadata": headers
        })

        for para in body.split("\n\n"):
            para_str = para.strip()
            if para_str:
                flat_elements.append({
                    "type": "paragraph",
                    "text": para_str,
                    "page_number": 1
                })

        title = f"Email: {headers.get('Subject', filename)}"
        root = build_hierarchical_layout_tree(title, flat_elements)
        raw_markdown = f"# {title}\n\n```\n{hdr_text}\n```\n\n{body}"

        return ParserResult(
            title=title,
            layout_root=root,
            raw_markdown=raw_markdown,
            file_type="email",
            word_count=len(raw_markdown.split()),
            metadata={"parser": "EmailParser", "headers": headers}
        )


# ---------------------------------------------------------------------------
# 6. LogParser
# ---------------------------------------------------------------------------

class LogParser(BaseParser):
    """
    Parses application logs, tracebacks, and runbook events.
    """
    def can_parse(self, file_path: str, mime_type: str, file_header: bytes) -> bool:
        ext = os.path.splitext(file_path)[1].lower()
        if ext in (".log", ".err", ".out"):
            return True
        if mime_type == "text/x-log":
            return True
        return False

    def parse(self, file_path: str, filename: str) -> ParserResult:
        logger.info(f"[LogParser] Parsing '{filename}'")
        flat_elements = []
        raw_lines = []

        try:
            with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                raw_lines = f.readlines()
        except Exception as e:
            raw_lines = [f"Failed to read logs: {e}"]

        # Process logs by grouping them into elements
        # E.g. group traceback or multiline entry to a single element
        current_entry = []
        entry_meta = {"severity": "INFO"}
        
        for line in raw_lines:
            line_str = line.strip()
            if not line_str:
                continue

            # Detect new entry: line begins with date or starts with [INFO]/[WARN]
            is_new = False
            if line_str.startswith("[") or (len(line_str) > 10 and line_str[:4].isdigit() and line_str[4] == "-"):
                is_new = True

            if is_new and current_entry:
                text_block = "\n".join(current_entry)
                flat_elements.append({
                    "type": "log_entry",
                    "text": text_block,
                    "page_number": 1,
                    "metadata": entry_meta.copy()
                })
                current_entry = []
                entry_meta = {"severity": "INFO"}

            current_entry.append(line_str)
            # Inspect line for severity keywords
            line_upper = line_str.upper()
            if "WARN" in line_upper:
                entry_meta["severity"] = "WARNING"
            elif "ERR" in line_upper or "FAIL" in line_upper or "EXCEPTION" in line_upper:
                entry_meta["severity"] = "ERROR"

        if current_entry:
            text_block = "\n".join(current_entry)
            flat_elements.append({
                "type": "log_entry",
                "text": text_block,
                "page_number": 1,
                "metadata": entry_meta
            })

        title = f"System Logs: {filename}"
        root = build_hierarchical_layout_tree(title, flat_elements)
        full_text = "".join(raw_lines)

        return ParserResult(
            title=title,
            layout_root=root,
            raw_markdown=f"# {title}\n\n```log\n{full_text}\n```",
            file_type="log",
            word_count=len(full_text.split()),
            metadata={"parser": "LogParser", "entries_count": len(flat_elements)}
        )


# ---------------------------------------------------------------------------
# 7. CodeParser
# ---------------------------------------------------------------------------

class CodeParser(BaseParser):
    """
    Parses code repositories/files extracting symbols, classes, functions, and comments.
    """
    def can_parse(self, file_path: str, mime_type: str, file_header: bytes) -> bool:
        ext = os.path.splitext(file_path)[1].lower()
        if ext in (".py", ".js", ".ts", ".go", ".c", ".cpp", ".h", ".rs", ".java", ".sql", ".sh"):
            return True
        if mime_type in ("text/x-source", "application/x-javascript", "text/x-python"):
            return True
        return False

    def parse(self, file_path: str, filename: str) -> ParserResult:
        logger.info(f"[CodeParser] Parsing '{filename}'")
        flat_elements = []
        raw_code = ""

        try:
            with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                raw_code = f.read()
        except Exception as e:
            raw_code = f"// Code read error: {e}"

        lines = raw_code.split("\n")
        
        # Simple symbol extraction using regex
        symbols = []
        current_docstring = []
        for line in lines:
            line_str = line.strip()
            
            # Simple docstring/comment extraction
            if line_str.startswith("#") or line_str.startswith("//") or line_str.startswith("/*") or line_str.startswith("*"):
                current_docstring.append(line_str)
                continue
                
            # Class definitions
            class_match = re.search(r"^\s*class\s+([a-zA-Z0-9_]+)", line)
            if class_match:
                cls_name = class_match.group(1)
                desc = " ".join(current_docstring) if current_docstring else ""
                symbols.append({
                    "type": "heading",
                    "text": f"Class: {cls_name}",
                    "heading_level": 2,
                    "metadata": {"symbol_type": "class", "name": cls_name, "docstring": desc}
                })
                current_docstring = []
                continue

            # Function definitions (Python def, JS/Go function/func, C++ etc.)
            func_match = re.search(r"^\s*(?:def|function|func)\s+([a-zA-Z0-9_]+)", line)
            if func_match:
                fn_name = func_match.group(1)
                desc = " ".join(current_docstring) if current_docstring else ""
                symbols.append({
                    "type": "code",
                    "text": f"Function: {fn_name}\nCode context: {line_str}",
                    "metadata": {"symbol_type": "function", "name": fn_name, "docstring": desc}
                })
                current_docstring = []
                continue

        # If no symbols found, append the raw code blocks
        if not symbols:
            flat_elements.append({
                "type": "code",
                "text": raw_code,
                "page_number": 1,
                "metadata": {"language": os.path.splitext(filename)[1].lstrip(".")}
            })
        else:
            # Reconstruct layout tree using extracted symbols
            flat_elements.extend(symbols)

        title = f"Source Code: {filename}"
        root = build_hierarchical_layout_tree(title, flat_elements)

        return ParserResult(
            title=title,
            layout_root=root,
            raw_markdown=f"# {title}\n\n```code\n{raw_code}\n```",
            file_type="source_code",
            word_count=len(raw_code.split()),
            metadata={"parser": "CodeParser"}
        )


# ---------------------------------------------------------------------------
# Registry Initialization
# ---------------------------------------------------------------------------

# Register the standard parsers in prioritized order (Docling first, then spreadsheet/email/images, fallback to generic text)
ParserRegistry.register_parser(DoclingParser())
ParserRegistry.register_parser(SpreadsheetParser())
ParserRegistry.register_parser(ImageParser())
ParserRegistry.register_parser(EmailParser())
ParserRegistry.register_parser(LogParser())
ParserRegistry.register_parser(CodeParser())
ParserRegistry.register_parser(GenericTextParser())


# ---------------------------------------------------------------------------
# Pipeline Stage Wrapper
# ---------------------------------------------------------------------------

from sqlalchemy.orm import Session
from .stage import PipelineStage, PipelineContext

class ParserStage(PipelineStage):
    """
    Ingestion pipeline stage executing the modality-aware registry parser selection.
    Populates context.parsed_doc.
    """
    def execute(self, context: PipelineContext, db: Session) -> None:
        parser = ParserRegistry.select_parser(context.file_path)
        # Parse the document and assign the unified ParserResult to context
        context.extra_state["parser_result"] = parser.parse(context.file_path, context.filename)
        # Assign mock compatibility parsed_doc to not break older elements if any downstream relies on it
        result = context.extra_state["parser_result"]
        
        # Backwards-compatibility bridge: map layout tree children to flat elements for older stages
        from app.services.processing.models import ParsedDocument, ParsedElement
        flat_elements = []
        
        def _flatten_tree(node: LayoutTreeNode):
            flat_elements.append(ParsedElement(
                type=node.type,
                text=node.text,
                heading_level=node.metadata.get("level", 2) if node.type == "heading" else None,
                page_number=node.page_numbers[0] if node.page_numbers else 1
            ))
            for child in node.children:
                _flatten_tree(child)
                
        _flatten_tree(result.layout_root)
        
        context.parsed_doc = ParsedDocument(
            title=result.title,
            elements=flat_elements,
            raw_markdown=result.raw_markdown,
            metadata=result.metadata
        )
