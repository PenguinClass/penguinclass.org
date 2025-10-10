#!/usr/bin/env python3
"""
Image organization utilities for structured directory layout.

Organizes extracted images into assets/images/YYYY/YYYY-MM-DD Event Name structure
based on EXIF data, document metadata, and filename analysis.
"""

import re
import json
from pathlib import Path
from typing import Dict, Any, Optional, Tuple, List
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


def load_exclusion_rules() -> Dict[str, Any]:
    """Load exclusion rules from the JSON file."""
    exclusion_file = Path("assets/data/gallery-exclude.json")
    if not exclusion_file.exists():
        logger.warning("No exclusion rules file found at assets/data/gallery-exclude.json")
        return {
            'exclude_paths': [],
            'exclude_regex_patterns': [],
            'exclude_urls': [],
            'size_limits': {'min_size_kb': 0, 'max_size_kb': None}
        }
    
    try:
        with open(exclusion_file, 'r') as f:
            return json.load(f)
    except Exception as e:
        logger.error(f"Error loading exclusion rules: {e}")
        return {
            'exclude_paths': [],
            'exclude_regex_patterns': [],
            'exclude_urls': [],
            'size_limits': {'min_size_kb': 0, 'max_size_kb': None}
        }


def is_excluded_path(path: Path, exclusion_rules: Dict[str, Any]) -> bool:
    """Check if path should be excluded based on exclusion rules."""
    path_str = str(path)
    
    # Check explicit path exclusions
    for exclude_path in exclusion_rules.get('exclude_paths', []):
        if path_str == exclude_path or path_str.endswith(exclude_path):
            return True
    
    # Check regex pattern exclusions
    for pattern_info in exclusion_rules.get('exclude_regex_patterns', []):
        pattern = pattern_info.get('pattern', '')
        try:
            if re.search(pattern, path_str):
                return True
        except re.error:
            logger.warning(f"Invalid regex pattern in exclusion rules: {pattern}")
    
    return False


def determine_image_organization(img_record: Dict[str, Any], source_file: Path) -> Tuple[str, str, str]:
    """
    Determine the year, date, and event name for organizing an image.
    
    Args:
        img_record: Image record with metadata
        source_file: Source file path
        
    Returns:
        Tuple of (year, date, event_name) for directory structure
    """
    # Extract information from multiple sources (NO EXIF for event names)
    exif_date = _extract_date_from_exif(img_record.get('exif', {}))
    doc_date = img_record.get('doc_metadata', {}).get('date')
    doc_event = img_record.get('doc_metadata', {}).get('event')
    doc_year = img_record.get('doc_metadata', {}).get('year')
    
    # Extract from path and filename
    path_date = _extract_date_from_path(str(source_file))
    filename_date = _extract_date_from_filename(img_record.get('filename', ''))
    source_date = _extract_date_from_filename(source_file.name)
    
    # Determine year (priority: EXIF > Document > Path > Filename)
    year = _determine_year(exif_date, doc_year, path_date, filename_date, source_date)
    
    # Determine date (priority: EXIF > Document > Path > Filename)
    date = _determine_date(exif_date, doc_date, path_date, filename_date, source_date)
    
    # Determine event name (NO EXIF, priority: Document > Path > Filename > Caption)
    event_name = _determine_event_name(
        doc_event,
        str(source_file),
        img_record.get('filename', ''),
        source_file.name,
        img_record.get('caption', '')
    )
    
    return year, date, event_name


def _extract_date_from_exif(exif_data: Dict[str, Any]) -> Optional[str]:
    """Extract date from EXIF data."""
    date_fields = ['DateTimeOriginal', 'CreateDate', 'ModifyDate', 'DateTime']
    
    for field in date_fields:
        if field in exif_data and exif_data[field]:
            try:
                # Parse various EXIF date formats
                date_str = str(exif_data[field])
                
                # Try different formats
                formats = [
                    '%Y:%m:%d %H:%M:%S',
                    '%Y-%m-%d %H:%M:%S',
                    '%Y:%m:%d',
                    '%Y-%m-%d',
                    '%m/%d/%Y',
                    '%d/%m/%Y'
                ]
                
                for fmt in formats:
                    try:
                        dt = datetime.strptime(date_str, fmt)
                        return dt.strftime('%Y-%m-%d')
                    except ValueError:
                        continue
                        
            except (ValueError, TypeError):
                continue
    
    return None


def _extract_date_from_path(path: str) -> Optional[str]:
    """Extract date from path patterns (folder names, etc.)."""
    if not path:
        return None
    
    # Look for YYYY in path
    year_match = re.search(r'\b(19|20)\d{2}\b', path)
    if not year_match:
        return None
    
    year = year_match.group()
    
    # Look for MM_DD_YYYY or MM_YY or MM_YYYY patterns
    date_patterns = [
        r'(\d{1,2})_(\d{1,2})_(\d{4})',  # MM_DD_YYYY
        r'(\d{1,2})_(\d{2})',  # MM_YY (assume 20YY)
        r'(\d{1,2})_(\d{4})',  # MM_YYYY
        r'(\d{1,2})/(\d{1,2})/(\d{4})',  # MM/DD/YYYY
        r'(\d{1,2})-(\d{1,2})-(\d{4})',  # MM-DD-YYYY
    ]
    
    for pattern in date_patterns:
        match = re.search(pattern, path)
        if match:
            groups = match.groups()
            if len(groups) == 3:  # MM_DD_YYYY or MM/DD/YYYY
                month, day, year = groups
                try:
                    datetime(int(year), int(month), int(day))
                    return f"{year}-{month.zfill(2)}-{day.zfill(2)}"
                except ValueError:
                    continue
            elif len(groups) == 2:  # MM_YY or MM_YYYY
                month, year_part = groups
                if len(year_part) == 2:  # MM_YY
                    full_year = f"20{year_part}"
                else:  # MM_YYYY
                    full_year = year_part
                try:
                    # Use first day of month for MM_YY or MM_YYYY
                    datetime(int(full_year), int(month), 1)
                    return f"{full_year}-{month.zfill(2)}-01"
                except ValueError:
                    continue
    
    # If only year found, return year-01-01
    return f"{year}-01-01"


def _extract_date_from_filename(filename: str) -> Optional[str]:
    """Extract date from filename patterns."""
    if not filename:
        return None
    
    # American date formats: MM_DD_YYYY, MM_YY, MM_YYYY, YY (20YY)
    date_patterns = [
        r'(\d{1,2})_(\d{1,2})_(\d{4})',  # MM_DD_YYYY
        r'(\d{1,2})_(\d{2})',  # MM_YY (assume 20YY)
        r'(\d{1,2})_(\d{4})',  # MM_YYYY
        r'(\d{2})',  # YY (assume 20YY)
        r'(\d{4})[-_](\d{1,2})[-_](\d{1,2})',  # YYYY-MM-DD or YYYY_MM_DD
        r'(\d{4})(\d{2})(\d{2})',  # YYYYMMDD
        r'(\d{1,2})[-/](\d{1,2})[-/](\d{4})',  # MM/DD/YYYY or MM-DD-YYYY
    ]
    
    for pattern in date_patterns:
        match = re.search(pattern, filename)
        if match:
            groups = match.groups()
            if len(groups) == 3:  # MM_DD_YYYY or YYYY-MM-DD
                if len(groups[0]) == 4:  # YYYY-MM-DD format
                    year, month, day = groups
                else:  # MM-DD-YYYY format
                    month, day, year = groups
                try:
                    datetime(int(year), int(month), int(day))
                    return f"{year}-{month.zfill(2)}-{day.zfill(2)}"
                except ValueError:
                    continue
            elif len(groups) == 2:  # MM_YY or MM_YYYY
                month, year_part = groups
                if len(year_part) == 2:  # MM_YY
                    full_year = f"20{year_part}"
                else:  # MM_YYYY
                    full_year = year_part
                try:
                    datetime(int(full_year), int(month), 1)
                    return f"{full_year}-{month.zfill(2)}-01"
                except ValueError:
                    continue
            elif len(groups) == 1:  # YY
                year_part = groups[0]
                if len(year_part) == 2:  # YY
                    full_year = f"20{year_part}"
                    return f"{full_year}-01-01"
    
    return None


def _determine_year(exif_date: Optional[str], doc_year: Optional[str], 
                   path_date: Optional[str], filename_date: Optional[str], source_date: Optional[str]) -> str:
    """Determine the year from multiple sources."""
    # Priority: EXIF > Document > Path > Filename > Source filename
    for date_source in [exif_date, doc_year, path_date, filename_date, source_date]:
        if date_source:
            if isinstance(date_source, str) and len(date_source) >= 4:
                # Extract year from date string
                year_match = re.search(r'\b(19|20)\d{2}\b', date_source)
                if year_match:
                    return year_match.group()
            elif isinstance(date_source, str) and date_source.isdigit() and len(date_source) == 4:
                return date_source
    
    # Default to current year if no year found
    return str(datetime.now().year)


def _determine_date(exif_date: Optional[str], doc_date: Optional[str], 
                   path_date: Optional[str], filename_date: Optional[str], source_date: Optional[str]) -> str:
    """Determine the full date from multiple sources."""
    # Priority: EXIF > Document > Path > Filename > Source filename
    for date_source in [exif_date, doc_date, path_date, filename_date, source_date]:
        if date_source and _is_valid_date(date_source):
            return date_source
    
    # Default to current date if no date found
    return datetime.now().strftime('%Y-%m-%d')


def _determine_event_name(doc_event: Optional[str], source_path: str, filename: str, 
                         source_filename: str, caption: str) -> str:
    """Determine the event name from multiple sources (NO EXIF)."""
    # Priority: Document event > Path analysis > Filename analysis > Caption analysis
    
    if doc_event and doc_event.strip():
        return _clean_event_name(doc_event)
    
    # Analyze source path for event patterns
    path_event = _extract_event_from_text(source_path)
    if path_event:
        return path_event
    
    # Analyze filename for event patterns
    filename_event = _extract_event_from_text(filename)
    if filename_event:
        return filename_event
    
    # Analyze source filename
    source_event = _extract_event_from_text(source_filename)
    if source_event:
        return source_event
    
    # Analyze caption
    caption_event = _extract_event_from_text(caption)
    if caption_event:
        return caption_event
    
    # Default event name
    return "Penguin Event"


def _extract_event_from_text(text: str) -> Optional[str]:
    """Extract event name from text using patterns."""
    if not text:
        return None
    
    event_patterns = [
        r'(Penguin\s+\w+\s+Regatta)',
        r'(Penguin\s+Championship)',
        r'(International\s+Penguin)',
        r'(BYC\s+Penguin)',
        r'(TAYC\s+Penguin)',
        r'(CRYC\s+Penguin)',
        r'(GIYS\s+Penguin)',
        r'(CYC\s+Penguin)',
        r'(MRYC\s+Penguin)',
        r'(Penguin\s+Fleet)',
        r'(Penguin\s+Race)',
        r'(Penguin\s+Event)',
        r'(Beachwood\s+Penguin)',
        r'(Tred\s+Avon\s+Penguin)',
        r'(Corsica\s+River\s+Penguin)',
        r'(Gibson\s+Island\s+Penguin)',
    ]
    
    for pattern in event_patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            return _clean_event_name(match.group())
    
    return None


def _clean_event_name(event_name: str) -> str:
    """Clean and normalize event name."""
    if not event_name:
        return "Penguin Event"
    
    # Remove extra whitespace
    event_name = re.sub(r'\s+', ' ', event_name.strip())
    
    # Remove common prefixes/suffixes
    event_name = re.sub(r'^(The\s+)', '', event_name, flags=re.IGNORECASE)
    event_name = re.sub(r'(\s+Event\s*)$', '', event_name, flags=re.IGNORECASE)
    
    # Capitalize properly
    words = event_name.split()
    result = []
    for word in words:
        if word.upper() in ['BYC', 'TAYC', 'CRYC', 'GIYS', 'CYC', 'MRYC', 'IPCDA']:
            result.append(word.upper())
        else:
            result.append(word.title())
    
    return ' '.join(result)


def _is_valid_date(date_str: str) -> bool:
    """Check if a date string is valid."""
    if not date_str:
        return False
    
    try:
        datetime.strptime(date_str, '%Y-%m-%d')
        return True
    except ValueError:
        return False


def create_organized_path(year: str, date: str, event_name: str, filename: str, base_dir: Path) -> Path:
    """
    Create the organized directory path for an image.
    
    Args:
        year: Year (YYYY)
        date: Full date (YYYY-MM-DD)
        event_name: Event name
        filename: Original filename
        base_dir: Base directory (e.g., assets/images)
        
    Returns:
        Full path for the organized image
    """
    # Create directory structure: assets/images/YYYY/YYYY-MM-DD Event Name
    # If no reliable event name, use just assets/images/YYYY
    if event_name and event_name.strip() and event_name != "Penguin Event":
        event_dir_name = f"{date} {event_name}"
        # Sanitize directory name
        event_dir_name = re.sub(r'[<>:"/\\|?*]', '_', event_dir_name)
        event_dir_name = re.sub(r'\s+', ' ', event_dir_name.strip())
        organized_dir = base_dir / year / event_dir_name
    else:
        # If only year available, use assets/images/YYYY
        organized_dir = base_dir / year
    
    return organized_dir / filename


def should_keep_original_path(img_record: Dict[str, Any], source_file: Path) -> bool:
    """
    Determine if image should keep its original path (already in archive structure).
    
    Args:
        img_record: Image record
        source_file: Source file path
        
    Returns:
        True if image should keep original path, False if it should be organized
    """
    abs_path = img_record.get('abs_path')
    if not abs_path:
        return False
    
    abs_path = Path(abs_path)
    
    # Check if image is already in archive/legacy-website structure
    try:
        abs_path.relative_to(Path('archive/legacy-website'))
        return True
    except ValueError:
        pass
    
    # Check if image is already in assets/images structure
    try:
        abs_path.relative_to(Path('assets/images'))
        return True
    except ValueError:
        pass
    
    return False
