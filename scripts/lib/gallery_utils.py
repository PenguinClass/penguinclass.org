#!/usr/bin/env python3
"""
Shared gallery utilities for generate and import scripts.

This module contains common functionality for gallery data processing,
including normalization, EXIF handling, and photographer credit processing.
"""

import json
import re
import yaml
import subprocess
from pathlib import Path
from typing import Dict, List, Optional
from urllib.parse import quote

class GalleryUtils:
    """Shared utilities for gallery data processing."""
    
    def __init__(self):
        self.normalization_data = {}
        self.yacht_clubs_data = []
        self.load_normalization_data()
    
    def load_normalization_data(self):
        """Load normalization and yacht clubs data."""
        # Load normalization data
        norm_path = Path("_data/normalization.yml")
        if norm_path.exists():
            try:
                with open(norm_path, 'r', encoding='utf-8') as f:
                    self.normalization_data = yaml.safe_load(f) or {}
            except Exception as e:
                print(f"Error loading normalization data: {e}")
                self.normalization_data = {}
        
        # Load yacht clubs data
        yachtclubs_path = Path("_data/yachtclubs.yml")
        if yachtclubs_path.exists():
            try:
                with open(yachtclubs_path, 'r', encoding='utf-8') as f:
                    self.yacht_clubs_data = yaml.safe_load(f) or []
            except Exception as e:
                print(f"Error loading yacht clubs data: {e}")
                self.yacht_clubs_data = []
    
    def normalize_category_name(self, category: str) -> str:
        """Normalize category name using club aliases and yacht club full names."""
        if not category:
            return category
        
        # Check club aliases first
        club_aliases = self.normalization_data.get('club_aliases', {})
        if category in club_aliases:
            return club_aliases[category]
        
        # Check yacht clubs data for abbreviations
        for club in self.yacht_clubs_data:
            if isinstance(club, dict):
                name = club.get('name', '')
                # Check if the category matches an abbreviation in the club name
                if category.upper() in name.upper() or name.upper() in category.upper():
                    return name
        
        return category
    
    def normalize_photographer_name(self, name: str) -> str:
        """Normalize photographer name by handling underscores and capitalization."""
        if not name or name.lower() in ['unknown photographer', 'unknown', '']:
            return 'Unknown photographer'
        
        # Replace underscores with spaces
        normalized = name.replace('_', ' ')
        
        # Handle common variations
        normalized = re.sub(r'\s+', ' ', normalized)  # Multiple spaces to single space
        normalized = normalized.strip()
        
        # Title case but preserve some exceptions
        words = normalized.split()
        result = []
        for word in words:
            if word.upper() in ['MD', 'NJ', 'NY', 'CA', 'USA', 'U.S.A.']:
                result.append(word.upper())
            elif word.lower() in ['of', 'the', 'and', 'or', 'in', 'on', 'at', 'to', 'for', 'with', 'by']:
                result.append(word.lower())
            else:
                result.append(word.title())
        
        return ' '.join(result)
    
    def extract_exif_metadata(self, file_path: str) -> Dict:
        """Extract only useful EXIF metadata from image file using exiftool."""
        exif_data = {}
        
        # Define the useful EXIF fields we want to keep
        useful_fields = [
            'DateTime', 'DateTimeOriginal', 'CreateDate', 'ModifyDate',
            'GPSLatitude', 'GPSLongitude', 'GPSAltitude', 'GPSLocation',
            'Artist', 'Copyright', 'ImageDescription', 'UserComment',
            'ImageWidth', 'ImageHeight', 'ExifImageWidth', 'ExifImageHeight',
            'Make', 'Model', 'Software', 'LensModel'
        ]
        
        try:
            # Try exiftool with specific field selection
            field_args = []
            for field in useful_fields:
                field_args.extend(['-{}'.format(field)])
            
            result = subprocess.run(['exiftool', '-json', '-q'] + field_args + [file_path], 
                                  capture_output=True, text=True, timeout=10)
            if result.returncode == 0:
                exif_json = json.loads(result.stdout)
                if exif_json and len(exif_json) > 0:
                    raw_exif = exif_json[0]
                    # Filter to only include useful fields
                    exif_data = {k: v for k, v in raw_exif.items() if k in useful_fields}
        except (subprocess.TimeoutExpired, subprocess.CalledProcessError, FileNotFoundError, json.JSONDecodeError):
            # Fallback to file command for basic info
            try:
                result = subprocess.run(['file', file_path], capture_output=True, text=True, timeout=5)
                if result.returncode == 0:
                    file_output = result.stdout
                    # Extract basic info from file output
                    if 'Exif Standard' in file_output:
                        # Parse manufacturer, model, datetime from file output
                        if 'manufacturer=' in file_output:
                            manufacturer = re.search(r'manufacturer=([^,]+)', file_output)
                            if manufacturer:
                                exif_data['Make'] = manufacturer.group(1).strip()
                        if 'model=' in file_output:
                            model = re.search(r'model=([^,]+)', file_output)
                            if model:
                                exif_data['Model'] = model.group(1).strip()
                        if 'datetime=' in file_output:
                            datetime_match = re.search(r'datetime=([^,]+)', file_output)
                            if datetime_match:
                                exif_data['DateTime'] = datetime_match.group(1).strip()
            except (subprocess.TimeoutExpired, subprocess.CalledProcessError):
                pass
        
        return exif_data
    
    def url_encode_path(self, path: str) -> str:
        """URL encode special characters in file paths."""
        # Split the path into directory and filename parts
        path_obj = Path(path)
        encoded_parts = []
        
        # Encode each part of the path
        for part in path_obj.parts:
            # Only encode special characters that cause issues in URLs
            encoded_part = quote(part, safe='')
            encoded_parts.append(encoded_part)
        
        return '/'.join(encoded_parts)
    
    def extract_credit_from_metadata(self, filename: str, path: str, exif_data: Dict = None, credit_overrides: Dict = None) -> str:
        """Extract photographer/videographer credit using multiple methods."""
        filename_lower = filename.lower()
        path_lower = path.lower()
        
        # 1. Check for manual overrides first
        if credit_overrides and path in credit_overrides:
            return self.normalize_photographer_name(credit_overrides[path])
        
        # 2. Check for explicit photographer patterns in filename (conservative approach)
        photographer_patterns = [
            r'_by_([a-zA-Z_]+)',  # _by_John or _by_John_Smith
            r'photoby([a-zA-Z_]+)',  # photobyJohn or photobyJohn_Smith
            r'photo_by_([a-zA-Z_]+)',  # photo_by_John or photo_by_John_Smith
            r'credit_([a-zA-Z_]+)',  # credit_John or credit_John_Smith
        ]
        
        for pattern in photographer_patterns:
            match = re.search(pattern, filename_lower)
            if match:
                name = match.group(1)
                normalized_name = self.normalize_photographer_name(name)
                return f"Photo by {normalized_name}"
        
        # 3. Check for copyright notices in filename
        if 'copyright' in filename_lower or '©' in filename:
            return "Copyright protected"
        
        # 4. Check for watermarks or credits in filename
        if 'watermark' in filename_lower or 'credit' in filename_lower:
            return "Credited photographer"
        
        # 5. Use EXIF data if available
        if exif_data:
            # Check for photographer in EXIF
            if 'Artist' in exif_data and exif_data['Artist'].strip():
                return f"Photo by {self.normalize_photographer_name(exif_data['Artist'].strip())}"
            if 'Copyright' in exif_data and exif_data['Copyright'].strip():
                return self.normalize_photographer_name(exif_data['Copyright'].strip())
            if 'Creator' in exif_data and exif_data['Creator'].strip():
                return f"Photo by {self.normalize_photographer_name(exif_data['Creator'].strip())}"
        
        # 6. Check for known photographer directories (conservative)
        known_photographer_dirs = {
            'will', 'keyworth', 'frank', 'parisi'
        }
        
        for photographer in known_photographer_dirs:
            if f'/{photographer}/' in path_lower or path_lower.endswith(f'/{photographer}'):
                return f"Photo by {self.normalize_photographer_name(photographer)}"
        
        # Default for unknown
        return "Unknown photographer"
    
    def extract_categories_from_metadata(self, item: dict) -> List[str]:
        """Extract categories from filename, path, and other metadata."""
        categories = []
        filename = item.get('filename', '').lower()
        path = item.get('path', '').lower()
        event_keyword = item.get('event_keyword', '').lower()
        media_type = item.get('media_type', '')
        
        # Media type categories
        if media_type == 'video':
            categories.append('Videos')
        elif media_type == 'photo':
            categories.append('Photos')
        
        # Event-based categories
        if any(word in filename or word in path or word in event_keyword for word in ['international', 'champ']):
            categories.append('Championships')
        elif any(word in filename or word in path or word in event_keyword for word in ['annual', 'regatta']):
            categories.append('Regattas')
        elif any(word in filename or word in path or word in event_keyword for word in ['frostbite']):
            categories.append('Frostbite')
        elif any(word in filename or word in path or word in event_keyword for word in ['heritage']):
            categories.append('Heritage')
        
        # Location-based categories (normalized)
        if any(word in filename or word in path or word in event_keyword for word in ['tayc', 'tred avon']):
            categories.append(self.normalize_category_name('TAYC'))
        elif any(word in filename or word in path or word in event_keyword for word in ['cryc', 'corsica']):
            categories.append(self.normalize_category_name('CRYC'))
        elif any(word in filename or word in path or word in event_keyword for word in ['giys', 'greenwich']):
            categories.append(self.normalize_category_name('GIYS'))
        elif any(word in filename or word in path or word in event_keyword for word in ['beachwood', 'byc', 'baltimore']):
            categories.append(self.normalize_category_name('BYC'))
        
        # Type-based categories
        if any(word in filename or word in path or word in event_keyword for word in ['boat', 'sail', 'rigging']):
            categories.append('Boats')
        elif any(word in filename or word in path or word in event_keyword for word in ['people', 'crew', 'sailor']):
            categories.append('People')
        elif any(word in filename or word in path or word in event_keyword for word in ['award', 'trophy', 'prize']):
            categories.append('Awards')
        
        # Remove duplicates and return
        return list(set(categories))
