#!/usr/bin/env python3
"""
PDF image and caption extraction utilities.

Extracts images and captions from PDF files using PyMuPDF.
"""

import re
from pathlib import Path
from typing import List, Dict, Any, Optional
import fitz  # PyMuPDF
import logging

logger = logging.getLogger(__name__)


def extract_images_from_pdf(pdf_path: Path) -> List[Dict[str, Any]]:
    """
    Extract images and captions from PDF file.
    
    Args:
        pdf_path: Path to PDF file
        
    Returns:
        List of image records with bytes, extension, caption, source, and method
    """
    try:
        doc = fitz.open(pdf_path)
        images = []
        
        for page_num in range(len(doc)):
            page = doc[page_num]
            
            # Get images on this page
            image_list = page.get_images()
            
            for img_index, img in enumerate(image_list):
                image_record = _extract_image_from_page(doc, page, img, pdf_path, page_num, img_index)
                if image_record:
                    images.append(image_record)
        
        doc.close()
        return images
        
    except Exception as e:
        logger.error(f"Error processing PDF file {pdf_path}: {e}")
        return []


def _extract_image_from_page(doc, page, img, pdf_path: Path, page_num: int, img_index: int) -> Optional[Dict[str, Any]]:
    """
    Extract image from PDF page.
    
    Args:
        doc: PyMuPDF document object
        page: PyMuPDF page object
        img: Image info tuple
        pdf_path: Path to PDF file
        page_num: Page number (0-based)
        img_index: Image index on page
        
    Returns:
        Image record dict or None if invalid
    """
    try:
        # Get image data
        xref = img[0]
        pix = fitz.Pixmap(doc, xref)
        
        # Convert to bytes
        if pix.n - pix.alpha < 4:  # GRAY or RGB
            img_data = pix.tobytes("png")
            ext = '.png'
        else:  # CMYK: convert to RGB first
            pix1 = fitz.Pixmap(fitz.csRGB, pix)
            img_data = pix1.tobytes("png")
            ext = '.png'
            pix1 = None
        
        pix = None
        
        if not img_data:
            return None
        
        # Find caption for this image
        caption = _find_caption_for_image(page, img_index)
        
        return {
            'bytes': img_data,
            'ext': ext,
            'caption': caption,
            'source': f"{pdf_path.name}#p{page_num}-img{img_index}",
            'method': 'pdf-nearest-text'
        }
        
    except Exception as e:
        logger.warning(f"Error extracting image {img_index} from page {page_num}: {e}")
        return None


def _find_caption_for_image(page, img_index: int) -> str:
    """
    Find caption for image using text proximity.
    
    Args:
        page: PyMuPDF page object
        img_index: Image index on page
        
    Returns:
        Caption text or empty string
    """
    try:
        # Get image rectangle
        image_list = page.get_images()
        if img_index >= len(image_list):
            return ""
        
        img = image_list[img_index]
        img_rect = page.get_image_rects(img[0])[0] if page.get_image_rects(img[0]) else None
        
        if not img_rect:
            return ""
        
        # Get text blocks
        text_dict = page.get_text("dict")
        text_blocks = []
        
        for block in text_dict["blocks"]:
            if "lines" in block:
                for line in block["lines"]:
                    for span in line["spans"]:
                        text_blocks.append({
                            'text': span['text'].strip(),
                            'bbox': span['bbox']
                        })
        
        # Find nearest text block
        best_caption = ""
        best_distance = float('inf')
        
        for block in text_blocks:
            if not block['text']:
                continue
            
            text_rect = fitz.Rect(block['bbox'])
            
            # Calculate distance from image
            distance = _calculate_distance(img_rect, text_rect)
            
            # Prefer text below the image
            if text_rect.y0 > img_rect.y1:  # Text is below image
                distance *= 0.5  # Reduce distance for text below
            
            # Check if text looks like a caption
            if _looks_like_caption(block['text']) and distance < best_distance:
                best_caption = block['text']
                best_distance = distance
        
        return best_caption
        
    except Exception as e:
        logger.warning(f"Error finding caption for image {img_index}: {e}")
        return ""


def _calculate_distance(rect1: fitz.Rect, rect2: fitz.Rect) -> float:
    """
    Calculate distance between two rectangles.
    
    Args:
        rect1: First rectangle
        rect2: Second rectangle
        
    Returns:
        Distance value
    """
    # Calculate center points
    center1 = fitz.Point((rect1.x0 + rect1.x1) / 2, (rect1.y0 + rect1.y1) / 2)
    center2 = fitz.Point((rect2.x0 + rect2.x1) / 2, (rect2.y0 + rect2.y1) / 2)
    
    # Calculate Euclidean distance
    return ((center1.x - center2.x) ** 2 + (center1.y - center2.y) ** 2) ** 0.5


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
        r'^Championship\s+',
        r'^International\s+',
    ]
    
    for pattern in caption_patterns:
        if re.search(pattern, text, re.IGNORECASE):
            return True
    
    return False
