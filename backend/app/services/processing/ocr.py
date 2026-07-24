import logging
from typing import Dict, Any, List, Optional
from pydantic import BaseModel

logger = logging.getLogger("sangrahalayamu.processing.ocr")


class OCRLayoutBlock(BaseModel):
    """
    Standard layout structure extracted by the OCR layer.
    """
    type: str  # heading, paragraph, table, list, line
    text: str
    page_number: int
    confidence: float
    bounding_box: List[float]  # [x, y, width, height]


class OCRRouter:
    """
    Centralized OCR routing engine. Decides if OCR is needed, tries to invoke
    local tools (Tesseract / EasyOCR), and raises explicit failures when OCR
    is unavailable so ingestion never fabricates extracted text.
    """

    @staticmethod
    def needs_ocr(file_path: str, mime_type: str, extracted_text_len: int = 0) -> bool:
        """
        Evaluate if OCR is required based on file type and text density.
        Images always need OCR. Scanned PDFs with no extracted text also do.
        """
        # Image mime types
        if mime_type.startswith("image/"):
            return True
        # PDF with no text extracted
        if mime_type == "application/pdf" and extracted_text_len < 10:
            return True
        return False

    @staticmethod
    def extract_layout(file_path: str, page_number: int = 1) -> List[OCRLayoutBlock]:
        """
        Routes the file to the active OCR engine.
        If local binaries are missing, raises an explicit OCR capability error.
        """
        logger.info(f"[OCRRouter] Invoking OCR for page {page_number} of '{file_path}'")

        # 1. Attempt Tesseract
        try:
            import pytesseract
            from PIL import Image
            # Make sure pytesseract doesn't crash if binary path is unset in windows registry
            # pytesseract.get_tesseract_version()
            img = Image.open(file_path)
            # Fetch detailed data with coordinates
            data = pytesseract.image_to_data(img, output_type=pytesseract.Output.DICT)
            
            blocks = []
            # Parse layout blocks from pytesseract output
            # Pytesseract groups words by block_num, line_num, etc.
            # We can simplify by grouping words with same block_num
            n_boxes = len(data['level'])
            current_block = -1
            current_words = []
            
            # Simplified grouping into paragraphs/lines
            for i in range(n_boxes):
                if data['text'][i].strip():
                    current_words.append(data['text'][i])
                    # If this is the end of block or line, pack it
                    if i == n_boxes - 1 or data['block_num'][i] != data['block_num'][i+1]:
                        text = " ".join(current_words).strip()
                        if text:
                            # Bounding box of the block
                            x = float(data['left'][i])
                            y = float(data['top'][i])
                            w = float(data['width'][i])
                            h = float(data['height'][i])
                            conf = float(data['conf'][i]) / 100.0 if data['conf'][i] != -1 else 0.8
                            
                            # Guess block type by text structure
                            b_type = "paragraph"
                            if len(text) < 60 and text.isupper():
                                b_type = "heading"
                            
                            blocks.append(OCRLayoutBlock(
                                type=b_type,
                                text=text,
                                page_number=page_number,
                                confidence=conf,
                                bounding_box=[x, y, w, h]
                            ))
                        current_words = []
            
            if blocks:
                logger.info(f"[OCRRouter] Successfully extracted {len(blocks)} OCR blocks using PyTesseract")
                return blocks
        except Exception as py_err:
            logger.debug(f"[OCRRouter] PyTesseract extraction failed, trying EasyOCR. Error: {py_err}")

        # 2. Attempt EasyOCR
        try:
            import easyocr
            reader = easyocr.Reader(['en'])
            results = reader.readtext(file_path)
            
            blocks = []
            for res in results:
                # easyocr format: [([[x, y], ...]), text, confidence]
                bbox, text, conf = res
                if not text.strip():
                    continue
                
                # Compute simple bounding box [left, top, width, height]
                xs = [pt[0] for pt in bbox]
                ys = [pt[1] for pt in bbox]
                left = float(min(xs))
                top = float(min(ys))
                width = float(max(xs) - left)
                height = float(max(ys) - top)
                
                b_type = "paragraph"
                if len(text) < 60 and text.isupper():
                    b_type = "heading"
                    
                blocks.append(OCRLayoutBlock(
                    type=b_type,
                    text=text,
                    page_number=page_number,
                    confidence=float(conf),
                    bounding_box=[left, top, width, height]
                ))
            if blocks:
                logger.info(f"[OCRRouter] Successfully extracted {len(blocks)} OCR blocks using EasyOCR")
                return blocks
        except Exception as easy_err:
            logger.debug(f"[OCRRouter] EasyOCR extraction failed. Error: {easy_err}")

        # 3. Graceful Rule-Based Fallback
        # If OCR fails, we cannot use mockup data under zero-mock policy.
        logger.error("[OCRRouter] Local OCR engines missing/failed. Cannot proceed without OCR capabilities.")
        raise RuntimeError("Local OCR engines missing/failed. Cannot proceed without OCR capabilities.")
