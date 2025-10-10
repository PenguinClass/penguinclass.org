#!/usr/bin/env python3
"""
HTML image and caption extraction utilities.

Extracts images and captions from HTML/HTM files in the legacy website archive.
"""

import re
from pathlib import Path
from typing import List, Dict, Any, Optional
from urllib.parse import urljoin, urlparse
from bs4 import BeautifulSoup, Tag
import logging

logger = logging.getLogger(__name__)


def extract_images_from_html(html_path: Path, base_path: Path = None) -> List[Dict[str, Any]]:
    """
    Extract images and captions from HTML file.
    
    Args:
        html_path: Path to HTML file
        base_path: Base path for resolving relative URLs (defaults to html_path.parent)
        
    Returns:
        List of image records with path, caption, source, method, and metadata
    """
    if base_path is None:
        base_path = html_path.parent
    
    try:
        # Try UTF-8 first, fall back to latin-1 for legacy files
        try:
            with open(html_path, 'r', encoding='utf-8') as f:
                content = f.read()
        except UnicodeDecodeError:
            with open(html_path, 'r', encoding='latin-1') as f:
                content = f.read()
        
        soup = BeautifulSoup(content, 'lxml')
        images = []
        
        # Extract document metadata
        doc_metadata = _extract_document_metadata(html_path, soup)
        
        # Find all img tags
        for i, img in enumerate(soup.find_all('img')):
            img_record = _extract_image_record(img, html_path, base_path, i, doc_metadata)
            if img_record:
                images.append(img_record)
        
        return images
        
    except Exception as e:
        logger.error(f"Error processing HTML file {html_path}: {e}")
        return []


def _extract_document_metadata(html_path: Path, soup: BeautifulSoup) -> Dict[str, Any]:
    """
    Extract date and event information from HTML document.
    
    Args:
        html_path: Path to HTML file
        soup: BeautifulSoup object
        
    Returns:
        Dictionary with date and event information
    """
    metadata = {
        'date': None,
        'event': None,
        'year': None
    }
    
    # Extract from filename patterns
    filename = html_path.stem
    date_patterns = [
        r'(\d{4})[-_](\d{1,2})[-_](\d{1,2})',  # YYYY-MM-DD or YYYY_MM_DD
        r'(\d{4})(\d{2})(\d{2})',  # YYYYMMDD
        r'(\d{1,2})[-_](\d{1,2})[-_](\d{4})',  # MM-DD-YYYY or MM_DD_YYYY
    ]
    
    for pattern in date_patterns:
        match = re.search(pattern, filename)
        if match:
            groups = match.groups()
            if len(groups) == 3:
                if len(groups[0]) == 4:  # YYYY-MM-DD format
                    year, month, day = groups
                else:  # MM-DD-YYYY format
                    month, day, year = groups
                
                try:
                    metadata['date'] = f"{year}-{month.zfill(2)}-{day.zfill(2)}"
                    metadata['year'] = year
                    break
                except ValueError:
                    continue
    
    # Extract from title tag
    title_tag = soup.find('title')
    if title_tag:
        title_text = title_tag.get_text().strip()
        # Look for year in title
        year_match = re.search(r'\b(19|20)\d{2}\b', title_text)
        if year_match and not metadata['year']:
            metadata['year'] = year_match.group()
        
        # Look for event names
        event_patterns = [
            r'(Regatta|Championship|International|Fleet|Race|Event)',
            r'(Penguin\s+\w+)',
            r'(BYC|TAYC|CRYC|GIYS|CYC|MRYC)',
        ]
        
        for pattern in event_patterns:
            event_match = re.search(pattern, title_text, re.IGNORECASE)
            if event_match:
                metadata['event'] = event_match.group().strip()
                break
    
    # Extract from content
    content_text = soup.get_text()
    
    # Look for date patterns in content
    if not metadata['date']:
        content_date_patterns = [
            r'(\d{4})[-/](\d{1,2})[-/](\d{1,2})',  # YYYY/MM/DD or YYYY-MM-DD
            r'(\d{1,2})[-/](\d{1,2})[-/](\d{4})',  # MM/DD/YYYY or MM-DD-YYYY
        ]
        
        for pattern in content_date_patterns:
            match = re.search(pattern, content_text)
            if match:
                groups = match.groups()
                if len(groups) == 3:
                    if len(groups[0]) == 4:  # YYYY-MM-DD format
                        year, month, day = groups
                    else:  # MM-DD-YYYY format
                        month, day, year = groups
                    
                    try:
                        metadata['date'] = f"{year}-{month.zfill(2)}-{day.zfill(2)}"
                        metadata['year'] = year
                        break
                    except ValueError:
                        continue
    
    # Look for event names in content
    if not metadata['event']:
        event_patterns = [
            r'(Penguin\s+\w+\s+Regatta)',
            r'(Penguin\s+Championship)',
            r'(International\s+Penguin)',
            r'(BYC\s+Penguin)',
            r'(TAYC\s+Penguin)',
            r'(CRYC\s+Penguin)',
            r'(GIYS\s+Penguin)',
        ]
        
        for pattern in event_patterns:
            event_match = re.search(pattern, content_text, re.IGNORECASE)
            if event_match:
                metadata['event'] = event_match.group().strip()
                break
    
    return metadata


def _extract_image_record(img: Tag, html_path: Path, base_path: Path, index: int, doc_metadata: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """
    Extract image record from img tag.
    
    Args:
        img: BeautifulSoup img tag
        html_path: Path to HTML file
        base_path: Base path for resolving URLs
        index: Image index in file
        
    Returns:
        Image record dict or None if invalid
    """
    src = img.get('src')
    if not src:
        return None
    
    # Resolve relative URLs
    if src.startswith('http://') or src.startswith('https://'):
        # External URL - skip for now
        return None
    
    # Convert to absolute path
    if src.startswith('/'):
        # Site-relative path
        abs_path = base_path / src.lstrip('/')
    else:
        # Relative to HTML file
        abs_path = html_path.parent / src
    
    # Normalize path
    try:
        abs_path = abs_path.resolve()
    except (OSError, ValueError):
        logger.warning(f"Cannot resolve path: {src} from {html_path}")
        return None
    
    # Check if file exists
    if not abs_path.exists():
        logger.warning(f"Image file not found: {abs_path}")
        return None
    
    # Extract caption
    caption = _extract_caption(img, html_path, index)
    
    return {
        'abs_path': abs_path,
        'caption': caption,
        'source': f"{html_path.name}#img-{index}",
        'method': 'html-extraction',
        'doc_metadata': doc_metadata
    }


def _extract_caption(img: Tag, html_path: Path, index: int) -> str:
    """
    Extract caption for image using multiple heuristics.
    
    Args:
        img: BeautifulSoup img tag
        html_path: Path to HTML file
        index: Image index in file
        
    Returns:
        Caption text or empty string
    """
    # 1. Check for figcaption element
    figcaption = img.find_parent('figure')
    if figcaption:
        caption_elem = figcaption.find('figcaption')
        if caption_elem:
            return _clean_caption_text(caption_elem.get_text())
    
    # 2. Check aria-describedby
    aria_desc = img.get('aria-describedby')
    if aria_desc:
        # Find element with matching ID
        parent = img.find_parent()
        if parent:
            desc_elem = parent.find(id=aria_desc)
            if desc_elem:
                return _clean_caption_text(desc_elem.get_text())
    
    # 3. Check for sibling caption elements
    parent = img.find_parent()
    if parent:
        # Look for common caption class names
        caption_classes = ['figcaption', 'caption', 'wp-caption-text', 'image-caption', 'photo-caption']
        for class_name in caption_classes:
            caption_elem = parent.find(class_=re.compile(class_name, re.I))
            if caption_elem:
                return _clean_caption_text(caption_elem.get_text())
    
    # 4. Check alt and title attributes
    alt_text = img.get('alt', '').strip()
    title_text = img.get('title', '').strip()
    
    if alt_text and len(alt_text) > 10:  # Only use alt if it's substantial
        return alt_text
    elif title_text and len(title_text) > 10:
        return title_text
    
    # 5. Look for nearby "Figure/Photo ..." paragraphs
    parent = img.find_parent()
    if parent:
        # Check previous and next siblings
        for sibling in [parent.find_previous_sibling(), parent.find_next_sibling()]:
            if sibling and sibling.name in ['p', 'div']:
                text = _clean_caption_text(sibling.get_text())
                if _looks_like_caption(text):
                    return text
        
        # Check parent's siblings
        grandparent = parent.find_parent()
        if grandparent:
            for sibling in [grandparent.find_previous_sibling(), grandparent.find_next_sibling()]:
                if sibling and sibling.name in ['p', 'div']:
                    text = _clean_caption_text(sibling.get_text())
                    if _looks_like_caption(text):
                        return text
    
    return ""


def _clean_caption_text(text: str) -> str:
    """Clean and normalize caption text."""
    if not text:
        return ""
    
    # Remove extra whitespace
    text = re.sub(r'\s+', ' ', text.strip())
    
    # Remove common prefixes
    prefixes_to_remove = [
        r'^Figure\s+\d+[:\-\s]*',
        r'^Photo\s+\d+[:\-\s]*',
        r'^Image\s+\d+[:\-\s]*',
        r'^Fig\.\s*\d+[:\-\s]*',
    ]
    
    for prefix in prefixes_to_remove:
        text = re.sub(prefix, '', text, flags=re.IGNORECASE)
    
    return text.strip()


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
    ]
    
    for pattern in caption_patterns:
        if re.search(pattern, text, re.IGNORECASE):
            return True
    
    return False
