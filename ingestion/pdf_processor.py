"""Async PDF processing for merchant summaries."""

import asyncio
import logging
from pathlib import Path
from typing import Optional

logger = logging.getLogger(__name__)


async def process_pdf_async(pdf_path: Path) -> Optional[str]:
    """
    Asynchronously process and extract text from PDF.
    
    This simulates an async operation. In production, this would be
    delegated to a task queue (e.g., Celery + Redis).
    
    Args:
        pdf_path: Path to the PDF file
        
    Returns:
        Extracted text from PDF; None if processing fails
    """
    try:
        # Import here to avoid hard dependency
        try:
            from PyPDF2 import PdfReader
        except ImportError:
            logger.error("PyPDF2 not installed; skipping PDF processing")
            return None
        
        if not pdf_path.exists():
            logger.warning(f"PDF file not found: {pdf_path}")
            return None
        
        logger.info(f"Processing PDF: {pdf_path}")
        
        # Run blocking I/O in a thread pool to make it async
        loop = asyncio.get_event_loop()
        text = await loop.run_in_executor(None, _extract_pdf_text, pdf_path)
        
        logger.info(f"Successfully extracted text from PDF ({len(text)} characters)")
        return text
        
    except Exception as e:
        logger.error(f"PDF processing failed: {e}")
        return None


def _extract_pdf_text(pdf_path: Path) -> str:
    """
    Synchronous PDF text extraction.
    
    Args:
        pdf_path: Path to the PDF file
        
    Returns:
        Extracted text
    """
    try:
        from PyPDF2 import PdfReader
    except ImportError:
        return ""
    
    text_parts = []
    
    try:
        reader = PdfReader(pdf_path)
        for page in reader.pages:
            text_parts.append(page.extract_text())
    except Exception as e:
        logger.error(f"Failed to extract text from PDF: {e}")
        return ""
    
    return "\n".join(text_parts)
