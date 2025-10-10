#!/usr/bin/env python3
"""
DOCX image and caption extraction utilities.

Extracts embedded images and captions from DOCX files.
"""

import re
from pathlib import Path
from typing import List, Dict, Any, Optional
from docx import Document
from docx.document import Document as DocumentType
from docx.table import Table
from docx.text.paragraph import Paragraph
import logging

logger = logging.getLogger(__name__)


def extract_images_from_docx(docx_path: Path) -> List[Dict[str, Any]]:
    """
    Extract images and captions from DOCX file.
    
    Args:
        docx_path: Path to DOCX file
        
    Returns:
        List of image records with bytes, extension, caption, source, and method
    """
    try:
        doc = Document(docx_path)
        images = []
        
        # Extract images from document relationships
        try:
            for i, rel in enumerate(doc.part.rels.values()):
                if "image" in rel.target_ref:
                    image_record = _extract_image_from_relationship(rel, docx_path, i)
                    if image_record:
                        images.append(image_record)
        except Exception as e:
            logger.warning(f"Could not extract images from relationships in {docx_path}: {e}")
            # Fallback: just extract captions without images
            return _extract_captions_only(docx_path)
        
        return images
        
    except Exception as e:
        logger.error(f"Error processing DOCX file {docx_path}: {e}")
        return []


def _extract_image_from_relationship(rel, docx_path: Path, index: int) -> Optional[Dict[str, Any]]:
    """
    Extract image from relationship.
    
    Args:
        rel: Document relationship object
        docx_path: Path to DOCX file
        index: Image index in file
        
    Returns:
        Image record dict or None if invalid
    """
    try:
        # Get image data
        image_data = rel.target_part.blob
        
        # Determine file extension
        ext = _get_image_extension(image_data)
        if not ext:
            return None
        
        # Find caption for this image
        caption = _find_caption_for_image(rel, docx_path, index)
        
        return {
            'bytes': image_data,
            'ext': ext,
            'caption': caption,
            'source': f"{docx_path.name}#rId{rel.rId}",
            'method': 'docx-extraction'
        }
        
    except Exception as e:
        logger.warning(f"Error extracting image from relationship {rel.rId}: {e}")
        return None


def _get_image_extension(image_data: bytes) -> Optional[str]:
    """
    Determine image file extension from bytes.
    
    Args:
        image_data: Image file bytes
        
    Returns:
        File extension or None if not a recognized image
    """
    # Check magic bytes
    if image_data.startswith(b'\xff\xd8\xff'):
        return '.jpg'
    elif image_data.startswith(b'\x89PNG\r\n\x1a\n'):
        return '.png'
    elif image_data.startswith(b'GIF87a') or image_data.startswith(b'GIF89a'):
        return '.gif'
    elif image_data.startswith(b'BM'):
        return '.bmp'
    elif image_data.startswith(b'RIFF') and b'WEBP' in image_data[:12]:
        return '.webp'
    
    return None


def _find_caption_for_image(rel, docx_path: Path, index: int) -> str:
    """
    Find caption for image using various heuristics.
    
    Args:
        rel: Document relationship object
        docx_path: Path to DOCX file
        index: Image index in file
        
    Returns:
        Caption text or empty string
    """
    try:
        doc = Document(docx_path)
        
        # Look for paragraphs with "Caption" style
        for paragraph in doc.paragraphs:
            if paragraph.style.name == 'Caption':
                text = paragraph.text.strip()
                if text and _looks_like_caption(text):
                    return text
        
        # Look for paragraphs that start with "Figure" or "Photo"
        for paragraph in doc.paragraphs:
            text = paragraph.text.strip()
            if _looks_like_caption(text):
                return text
        
        # Look in tables for captions
        for table in doc.tables:
            for row in table.rows:
                for cell in row.cells:
                    for paragraph in cell.paragraphs:
                        text = paragraph.text.strip()
                        if _looks_like_caption(text):
                            return text
        
        return ""
        
    except Exception as e:
        logger.warning(f"Error finding caption for image {rel.rId}: {e}")
        return ""


def _looks_like_caption(text: str) -> bool:
    """Check if text looks like a caption."""
    if not text or len(text) < 10:
        return False
    
    # Look for caption-like patterns
    caption_patterns = [
        r'^Figure\s+\d+',
        r'^Photo\s+\d+',
        r'^Image\s+\d+',
        r'^Fig\.\s*\d+',
        r'^Penguin\s+',
        r'^Sailing\s+',
        r'^Regatta\s+',
        r'^Race\s+',
        r'^Boat\s+',
        r'^Fleet\s+',
    ]
    
    for pattern in caption_patterns:
        if re.search(pattern, text, re.IGNORECASE):
            return True
    
    return False


def _extract_captions_only(docx_path: Path) -> List[Dict[str, Any]]:
    """
    Fallback function to extract captions from DOCX without images.
    
    Args:
        docx_path: Path to DOCX file
        
    Returns:
        List of caption records
    """
    try:
        doc = Document(docx_path)
        captions = []
        
        # Look for caption-like text in paragraphs
        for i, paragraph in enumerate(doc.paragraphs):
            text = paragraph.text.strip()
            if _looks_like_caption(text):
                captions.append({
                    'caption': text,
                    'source': f"{docx_path.name}#para-{i}",
                    'method': 'docx-caption-only'
                })
        
        # Look in tables for captions
        for table in doc.tables:
            for row in table.rows:
                for cell in row.cells:
                    for paragraph in cell.paragraphs:
                        text = paragraph.text.strip()
                        if _looks_like_caption(text):
                            captions.append({
                                'caption': text,
                                'source': f"{docx_path.name}#table-caption",
                                'method': 'docx-caption-only'
                            })
        
        return captions
        
    except Exception as e:
        logger.error(f"Error extracting captions from {docx_path}: {e}")
        return []
