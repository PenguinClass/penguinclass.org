#!/usr/bin/env python3
"""
Common gallery importer logic for both generate and import scripts.

This module contains the shared GalleryImporter class that handles media processing,
categorization, and gallery data generation for both the generate and import workflows.
"""

import json
import re
import subprocess
import yaml
from pathlib import Path
from typing import Dict, List, Set, Optional
from collections import defaultdict
from urllib.parse import urlparse, quote
from datetime import datetime
import sys
sys.path.append(str(Path(__file__).parent))
from lib.gallery_utils import GalleryUtils
from lib.hash_utils import file_sha1

# Photo extensions to look for
PHOTO_EXTENSIONS = {'.jpg', '.jpeg', '.png', '.gif', '.bmp', '.tiff', '.tif', '.webp'}

# Video extensions to look for
VIDEO_EXTENSIONS = {'.mp4', '.avi', '.mov', '.wmv', '.flv', '.webm', '.mkv', '.m4v'}

# External video platforms
EXTERNAL_VIDEO_PLATFORMS = {
    'youtube.com', 'youtu.be', 'vimeo.com', 'dailymotion.com', 'twitch.tv'
}

# Directories to exclude
EXCLUDED_DIRECTORIES = {
    'Penguin_web_dec2010',
    '_vti_cnf'
}

class GalleryImporter:
    """Common gallery importer logic for processing media files and generating gallery data."""
    
    def __init__(self, import_path: str = None, date: str = None, source: str = None, 
                 credit: str = None, event: str = None, location: str = None, 
                 pattern: str = None):
        self.import_path = Path(import_path) if import_path else None
        self.date = date
        self.source = source or "import"
        self.credit = credit or "Unknown photographer"
        self.event = event
        self.location = location
        self.pattern = pattern
        self.media_items = []
        self.categories = defaultdict(list)
        self.events = defaultdict(list)
        self.years = defaultdict(list)
        self.exclusion_rules = self.load_exclusion_rules()
        self.credit_overrides = self.load_credit_overrides()
        self.utils = GalleryUtils()
    
    def load_exclusion_rules(self) -> Dict:
        """Load exclusion rules from the JSON file."""
        exclusion_file = Path("assets/data/gallery-exclude.json")
        if not exclusion_file.exists():
            print("Warning: No exclusion rules file found at assets/data/gallery-exclude.json")
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
            print(f"Error loading exclusion rules: {e}")
            return {
                'exclude_paths': [],
                'exclude_regex_patterns': [],
                'exclude_urls': [],
                'size_limits': {'min_size_kb': 0, 'max_size_kb': None}
            }
    
    def load_credit_overrides(self) -> Dict:
        """Load manual credit overrides from JSON file."""
        credit_file = Path("assets/data/gallery-credits.json")
        if not credit_file.exists():
            print("Info: No credit overrides file found at assets/data/gallery-credits.json")
            return {}
        
        try:
            with open(credit_file, 'r') as f:
                data = json.load(f)
                return data.get('overrides', {})
        except Exception as e:
            print(f"Error loading credit overrides: {e}")
            return {}
    
    def save_media_captions_credits(self, media_items: List[Dict]) -> None:
        """Save media captions and credits to tmp file for reapplication."""
        tmp_file = Path("tmp/media_captions_credits.json")
        tmp_file.parent.mkdir(exist_ok=True)
        
        captions_credits = {}
        for media in media_items:
            path = media.get('path', '')
            if path:
                captions_credits[path] = {
                    'credit': media.get('credit', ''),
                    'caption': media.get('caption', ''),
                    'description': media.get('description', '')
                }
        
        with open(tmp_file, 'w') as f:
            json.dump(captions_credits, f, indent=2)
        
        print(f"Saved media captions and credits to {tmp_file}")
    
    def load_media_captions_credits(self) -> Dict:
        """Load media captions and credits from tmp file."""
        tmp_file = Path("tmp/media_captions_credits.json")
        if not tmp_file.exists():
            return {}
        
        try:
            with open(tmp_file, 'r') as f:
                return json.load(f)
        except Exception as e:
            print(f"Error loading media captions and credits: {e}")
            return {}
    
    def is_excluded_path(self, path: Path) -> bool:
        """Check if path should be excluded based on exclusion rules."""
        path_str = str(path)
        
        # Check for excluded directories (legacy hardcoded exclusions)
        for excluded_dir in EXCLUDED_DIRECTORIES:
            if f'/{excluded_dir}/' in path_str or path_str.endswith(f'/{excluded_dir}'):
                return True
        
        # Check explicit path exclusions
        for exclude_path in self.exclusion_rules.get('exclude_paths', []):
            if path_str == exclude_path or path_str.endswith(exclude_path):
                return True
        
        # Check regex pattern exclusions
        for pattern_info in self.exclusion_rules.get('exclude_regex_patterns', []):
            pattern = pattern_info.get('pattern', '')
            try:
                if re.search(pattern, path_str):
                    return True
            except re.error as e:
                print(f"Warning: Invalid regex pattern '{pattern}': {e}")
        
        return False
    
    def is_excluded_by_size(self, file_size: int) -> bool:
        """Check if file should be excluded based on size limits."""
        size_limits = self.exclusion_rules.get('size_limits', {})
        min_size_kb = size_limits.get('min_size_kb', 0)
        max_size_kb = size_limits.get('max_size_kb')
        
        # Convert bytes to KB
        size_kb = file_size / 1024
        
        if min_size_kb and size_kb < min_size_kb:
            return True
        
        if max_size_kb and size_kb > max_size_kb:
            return True
        
        return False
    
    def is_external_url(self, url: str) -> bool:
        """Check if URL is external."""
        try:
            parsed = urlparse(url)
            return bool(parsed.netloc)
        except:
            return False
    
    def get_media_type(self, file_path: str) -> str:
        """Determine if this is a photo, video, or external media."""
        if self.is_external_url(file_path):
            # Check if it's an external video platform
            parsed = urlparse(file_path)
            if any(platform in parsed.netloc for platform in EXTERNAL_VIDEO_PLATFORMS):
                return 'external_video'
            else:
                return 'external_media'
        
        path = Path(file_path)
        extension = path.suffix.lower()
        
        if extension in PHOTO_EXTENSIONS:
            return 'photo'
        elif extension in VIDEO_EXTENSIONS:
            return 'video'
        else:
            return 'unknown'
    
    def get_external_platform(self, url: str) -> Optional[str]:
        """Get the external platform name from URL."""
        try:
            parsed = urlparse(url)
            domain = parsed.netloc.lower()
            
            if 'youtube.com' in domain or 'youtu.be' in domain:
                return 'youtube'
            elif 'vimeo.com' in domain:
                return 'vimeo'
            elif 'dailymotion.com' in domain:
                return 'dailymotion'
            elif 'twitch.tv' in domain:
                return 'twitch'
            else:
                return 'external'
        except:
            return 'external'
    
    def extract_credit_from_metadata(self, filename: str, path: str, exif_data: Dict = None) -> str:
        """Extract photographer/videographer credit using multiple methods."""
        filename_lower = filename.lower()
        path_lower = path.lower()
        
        # 1. Check for manual overrides first
        if path in self.credit_overrides:
            return self.utils.normalize_photographer_name(self.credit_overrides[path])
        
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
                normalized_name = self.utils.normalize_photographer_name(name)
                return normalized_name
        
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
                return self.utils.normalize_photographer_name(exif_data['Artist'].strip())
            if 'Copyright' in exif_data and exif_data['Copyright'].strip():
                return self.utils.normalize_photographer_name(exif_data['Copyright'].strip())
            if 'Creator' in exif_data and exif_data['Creator'].strip():
                return self.utils.normalize_photographer_name(exif_data['Creator'].strip())
        
        # 6. Check for known photographer directories (conservative)
        known_photographer_dirs = {
            'will', 'keyworth', 'frank', 'parisi'
        }
        
        for photographer in known_photographer_dirs:
            if f'/{photographer}/' in path_lower or path_lower.endswith(f'/{photographer}'):
                return self.utils.normalize_photographer_name(photographer)
        
        # Default for unknown
        return "Unknown photographer"
    
    def categorize_media(self, metadata: Dict) -> List[str]:
        """Categorize media based on filename, path, and other metadata."""
        categories = []
        filename = metadata['filename'].lower()
        path = metadata['path'].lower()
        event_keyword = metadata.get('event_keyword', '').lower()
        media_type = metadata.get('media_type', '')
        
        # Media type categories
        if media_type == 'video':
            categories.append('Videos')
        elif media_type == 'external_video':
            categories.append('External Videos')
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
            categories.append(self.utils.normalize_category_name('TAYC'))
        elif any(word in filename or word in path or word in event_keyword for word in ['cryc', 'corsica']):
            categories.append(self.utils.normalize_category_name('CRYC'))
        elif any(word in filename or word in path or word in event_keyword for word in ['giys', 'greenwich']):
            categories.append(self.utils.normalize_category_name('GIYS'))
        elif any(word in filename or word in path or word in event_keyword for word in ['beachwood', 'byc', 'baltimore']):
            categories.append(self.utils.normalize_category_name('BYC'))
        
        # Type-based categories
        if any(word in filename or word in path or word in event_keyword for word in ['boat', 'sail', 'rigging']):
            categories.append('Boats')
        elif any(word in filename or word in path or word in event_keyword for word in ['people', 'crew', 'sailor']):
            categories.append('People')
        elif any(word in filename or word in path or word in event_keyword for word in ['award', 'trophy', 'prize']):
            categories.append('Awards')
        
        # Default category
        if not categories:
            categories.append('General')
        
        return categories
    
    def extract_metadata(self, file_path: str, file_size: int = 0, modified_time: str = '') -> Dict:
        """Extract metadata from media file."""
        media_type = self.get_media_type(file_path)
        filename = Path(file_path).name
        
        # Extract EXIF data for images
        exif_data = {}
        if media_type == 'photo' and Path(file_path).suffix.lower() in {'.jpg', '.jpeg', '.tiff', '.tif'}:
            exif_data = self.utils.extract_exif_metadata(file_path)
        
        # Generate hash for the file
        file_hash = None
        if not self.is_external_url(file_path):
            file_path_obj = Path(file_path)
            if file_path_obj.exists():
                file_hash = file_sha1(file_path_obj)
        
        # Extract year from date parameter or filename
        year = None
        if self.date:
            try:
                year = int(self.date.split('-')[0])
            except (ValueError, IndexError):
                pass
        
        if not year:
            year_match = re.search(r'\b(19|20)\d{2}\b', file_path)
            if year_match:
                year = int(year_match.group())
        
        # Use provided credit parameter if available, otherwise extract from metadata
        if self.credit and self.credit != "Unknown photographer":
            credit = self.credit
        else:
            credit = self.extract_credit_from_metadata(filename, file_path, exif_data)
        
        metadata = {
            'filename': filename,
            'path': file_path,
            'encoded_path': self.utils.url_encode_path(file_path),
            'size': file_size,
            'modified': modified_time,
            'extension': Path(file_path).suffix.lower(),
            'media_type': media_type,
            'source': self.source,
            'credit': credit,
            'exif': exif_data,
            'hash': file_hash
        }
        
        # Handle external URLs
        if self.is_external_url(file_path):
            metadata['is_external'] = True
            metadata['external_url'] = file_path
            metadata['external_platform'] = self.get_external_platform(file_path)
        else:
            metadata['is_external'] = False
        
        # Add year if found
        if year:
            metadata['year'] = year
        
        # Try to extract event information
        filename_lower = file_path.lower()
        
        # Common event keywords
        event_keywords = [
            'international', 'championship', 'champ', 'north american', 'na',
            'annual', 'regatta', 'frostbite', 'heritage', 'turkey trot',
            'spring', 'summer', 'fall', 'winter', 'tayc', 'cryc', 'giys',
            'beachwood', 'corsica', 'admiral byrd', 'meyers'
        ]
        
        for keyword in event_keywords:
            if keyword in filename_lower:
                metadata['event_keyword'] = keyword
                break
        
        # Add categories to the metadata
        metadata['categories'] = self.categorize_media(metadata)
        
        # Add custom fields if provided
        if self.date:
            metadata['date'] = self.date
        if self.event:
            metadata['event'] = self.event
        if self.location:
            metadata['location'] = self.location
        
        return metadata
    
    def filter_excluded_media(self, media_list: List[Dict]) -> List[Dict]:
        """Filter out media based on exclusion rules."""
        filtered = []
        excluded_count = 0
        excluded_by_path = 0
        excluded_by_size = 0
        
        for media in media_list:
            excluded = False
            reason = ""
            
            # Check path exclusions
            if self.is_excluded_path(Path(media['path'])):
                excluded = True
                excluded_by_path += 1
                reason = "path exclusion"
            
            # Check size exclusions
            elif self.is_excluded_by_size(media.get('size', 0)):
                excluded = True
                excluded_by_size += 1
                reason = "size exclusion"
            
            if excluded:
                excluded_count += 1
                print(f"Excluding ({reason}): {media['path']}")
            else:
                filtered.append(media)
        
        if excluded_count > 0:
            print(f"Excluded {excluded_count} media items:")
            if excluded_by_path > 0:
                print(f"  - {excluded_by_path} by path exclusion")
            if excluded_by_size > 0:
                print(f"  - {excluded_by_size} by size exclusion")
        
        return filtered
    
    def deduplicate_media(self, media_items: List[Dict]) -> List[Dict]:
        """Remove duplicate media entries based on hash comparison."""
        seen_hashes = set()
        unique_media = []
        duplicates_removed = 0
        
        for media in media_items:
            # Skip if no hash (external URLs or files that couldn't be hashed)
            if not media.get('hash'):
                unique_media.append(media)
                continue
            
            # Check if we've seen this hash before
            if media['hash'] in seen_hashes:
                duplicates_removed += 1
                print(f"Removing duplicate: {media['path']} (hash: {media['hash'][:8]}...)")
                continue
            
            # Add to seen hashes and unique media
            seen_hashes.add(media['hash'])
            unique_media.append(media)
        
        if duplicates_removed > 0:
            print(f"Removed {duplicates_removed} duplicate media entries")
        
        return unique_media, duplicates_removed
    
    def generate_categories_summary(self, media_items: List[Dict]) -> Dict:
        """Generate categories summary from media items' categories arrays."""
        categories_summary = defaultdict(list)
        
        for media in media_items:
            categories = media.get('categories', [])
            for category in categories:
                categories_summary[category].append(media)
        
        return dict(categories_summary)
    
    def generate_credit_stats(self, media_items: List[Dict]) -> Dict:
        """Generate statistics about photo/video credits."""
        credit_counts = defaultdict(int)
        total_credited = 0
        total_unknown = 0
        
        for media in media_items:
            credit = media.get('credit', 'Unknown photographer')
            credit_counts[credit] += 1
            
            if credit == 'Unknown photographer':
                total_unknown += 1
            else:
                total_credited += 1
        
        # Get top 10 most common credits
        top_credits = sorted(credit_counts.items(), key=lambda x: x[1], reverse=True)[:10]
        
        return {
            'total_credited': total_credited,
            'total_unknown': total_unknown,
            'unique_credits': len(credit_counts),
            'top_credits': top_credits,
            'credit_breakdown': dict(credit_counts)
        }
    
    def organize_media(self, media_list: List[Dict]):
        """Organize media by events and years (skip categories grouping)."""
        for media in media_list:
            # Add to year-based organization
            if 'year' in media:
                self.years[media['year']].append(media)
            
            # Add to event-based organization
            if 'event_keyword' in media:
                self.events[media['event_keyword']].append(media)
            elif self.event:
                self.events[self.event].append(media)
            
            # Note: Categories are now stored on each media item, not grouped separately
    
    def scan_directory(self) -> List[Dict]:
        """Scan the import directory for media files with optional pattern filtering."""
        media_files = []
        
        if not self.import_path or not self.import_path.exists():
            print(f"Error: Import path does not exist: {self.import_path}")
            return media_files
        
        print(f"Scanning directory: {self.import_path}")
        if self.pattern:
            print(f"Filtering files matching pattern: {self.pattern}")
        
        # Find all media files
        for file_path in self.import_path.rglob('*'):
            if file_path.is_file():
                extension = file_path.suffix.lower()
                if extension in PHOTO_EXTENSIONS or extension in VIDEO_EXTENSIONS:
                    # Apply pattern filter if specified
                    if self.pattern:
                        if not self._matches_pattern(file_path, self.pattern):
                            continue
                    
                    # Get file stats
                    stat = file_path.stat()
                    file_size = stat.st_size
                    modified_time = datetime.fromtimestamp(stat.st_mtime).isoformat()
                    
                    # Create relative path from project root
                    try:
                        relative_path = file_path.relative_to(Path.cwd())
                    except ValueError:
                        relative_path = file_path
                    
                    media_files.append({
                        'path': str(relative_path),
                        'size': file_size,
                        'modified': modified_time
                    })
        
        print(f"Found {len(media_files)} media files")
        if self.pattern:
            print(f"Pattern '{self.pattern}' matched {len(media_files)} files")
        return media_files
    
    def _matches_pattern(self, file_path: Path, pattern: str) -> bool:
        """Check if file matches the given pattern."""
        import fnmatch
        
        # Check filename
        if fnmatch.fnmatch(file_path.name.lower(), pattern.lower()):
            return True
        
        # Check relative path from import directory
        try:
            relative_path = file_path.relative_to(self.import_path)
            if fnmatch.fnmatch(str(relative_path).lower(), pattern.lower()):
                return True
        except ValueError:
            pass
        
        # Check full path
        if fnmatch.fnmatch(str(file_path).lower(), pattern.lower()):
            return True
        
        return False
    
    def load_analysis_data(self) -> Dict:
        """Load the photo analysis data."""
        analysis_file = Path("tmp/gallery_analysis.json")
        if not analysis_file.exists():
            print("Error: tmp/gallery_analysis.json not found. Run analyze_photos.py first.")
            return {}
        
        with open(analysis_file, 'r') as f:
            return json.load(f)
    
    def generate_search_terms(self, media_items: List[Dict]) -> Dict[str, List[str]]:
        """Generate search terms for the media gallery."""
        terms = {
            'locations': set(),
            'event_types': set(),
            'years': set(),
            'media_types': set(),
            'platforms': set(),
            'keywords': set()
        }
        
        for media in media_items:
            if media.get('location') and media['location'] != 'unknown':
                terms['locations'].add(media['location'])
            if media.get('event_type') and media['event_type'] != 'general':
                terms['event_types'].add(media['event_type'])
            if media.get('year'):
                terms['years'].add(str(media['year']))
            if media.get('media_type'):
                terms['media_types'].add(media['media_type'])
            if media.get('external_platform'):
                terms['platforms'].add(media['external_platform'])
            
            # Extract keywords from filename
            filename_words = re.findall(r'\b[a-zA-Z]+\b', media['filename'].lower())
            terms['keywords'].update(filename_words)
        
        # Convert sets to sorted lists
        return {k: sorted(list(v)) for k, v in terms.items()}
    
    def generate_gallery_data(self, analysis_data: Dict = None) -> Dict:
        """Generate structured data for the gallery."""
        if analysis_data:
            # Generate mode - use analysis data
            photos = analysis_data.get('photos', [])
            
            # Load existing captions and credits
            existing_captions_credits = self.load_media_captions_credits()
            
            # Filter out excluded media
            filtered_photos = self.filter_excluded_media(photos)
            
            # Convert to media items with enhanced metadata
            media_items = []
            for photo in filtered_photos:
                media_metadata = self.extract_metadata(
                    photo['path'], 
                    photo.get('size', 0), 
                    photo.get('modified', '')
                )
                
                # Apply existing captions and credits if available
                path = media_metadata.get('path', '')
                if path in existing_captions_credits:
                    existing_data = existing_captions_credits[path]
                    media_metadata['credit'] = existing_data.get('credit', media_metadata.get('credit', ''))
                    media_metadata['caption'] = existing_data.get('caption', '')
                    media_metadata['description'] = existing_data.get('description', '')
                
                media_items.append(media_metadata)
            
            # Deduplicate media based on hash
            unique_media, duplicates_removed = self.deduplicate_media(media_items)
            
            # Save current captions and credits for future reapplication
            self.save_media_captions_credits(unique_media)
            
        else:
            # Import mode - scan directory
            media_files = self.scan_directory()
            
            if not media_files:
                print("No media files found in the import directory.")
                return {}
            
            # Convert to media items with enhanced metadata
            media_items = []
            for media_file in media_files:
                media_metadata = self.extract_metadata(
                    media_file['path'], 
                    media_file.get('size', 0), 
                    media_file.get('modified', '')
                )
                media_items.append(media_metadata)
            
            unique_media = media_items
            duplicates_removed = 0
        
        # Organize media
        self.organize_media(unique_media)
        
        # Generate categories summary from media items
        categories_summary = self.generate_categories_summary(unique_media)
        
        # Create summary statistics
        stats = {
            'total_media': len(unique_media),
            'total_duplicates_removed': duplicates_removed,
            'photos': len([m for m in unique_media if m['media_type'] == 'photo']),
            'videos': len([m for m in unique_media if m['media_type'] == 'video']),
            'external_videos': len([m for m in unique_media if m['media_type'] == 'external_video']),
            'years_count': len(self.years),
            'events_count': len(self.events),
            'date_range': {
                'earliest': min(self.years.keys()) if self.years else 'unknown',
                'latest': max(self.years.keys()) if self.years else 'unknown'
            },
            'credits': self.generate_credit_stats(unique_media)
        }
        
        # Add import info if in import mode
        if not analysis_data:
            stats['import_info'] = {
                'date': self.date,
                'source': self.source,
                'credit': self.credit,
                'event': self.event,
                'location': self.location,
                'import_path': str(self.import_path) if self.import_path else None
            }
        
        # Create gallery collections
        collections = {}
        
        if analysis_data:
            # Generate mode collections
            collections = {
                'featured': {
                    'title': 'Featured Media',
                    'description': 'Highlights from recent events',
                    'media': [m for m in unique_media if m.get('year') and int(m['year']) >= 2020][:20]
                },
                'championships': {
                    'title': 'Championships',
                    'description': 'International and North American Championships',
                    'media': [m for m in unique_media if 'Championships' in m.get('categories', [])]
                },
                'videos': {
                    'title': 'Videos',
                    'description': 'All video content',
                    'media': [m for m in unique_media if m['media_type'] in ['video', 'external_video']]
                },
                'historical': {
                    'title': 'Historical Media',
                    'description': 'Media from the early years of the Penguin Class',
                    'media': [m for m in unique_media if m.get('year') and int(m['year']) < 2010]
                }
            }
        else:
            # Import mode collections
            collections = {
                'imported': {
                    'title': f'Imported from {self.import_path.name if self.import_path else "unknown"}',
                    'description': f'Media imported on {datetime.now().strftime("%Y-%m-%d")}',
                    'media': unique_media
                }
            }
            
            if self.event:
                collections['event'] = {
                    'title': self.event,
                    'description': f'Media from {self.event}',
                    'media': unique_media
                }
        
        return {
            'stats': stats,
            'categories': categories_summary,
            'years': dict(self.years),
            'events': dict(self.events),
            'collections': collections,
            'media_index': unique_media,
            'search_terms': self.generate_search_terms(unique_media)
        }
    
    def merge_to_main_gallery(self, gallery_data: Dict):
        """Merge this gallery data directly into the main gallery.json file."""
        main_gallery_path = Path("assets/data/gallery.json")
        
        # Load existing main gallery or create new structure
        if main_gallery_path.exists():
            try:
                with open(main_gallery_path, 'r') as f:
                    main_gallery = json.load(f)
                print(f"Loaded existing main gallery with {main_gallery.get('stats', {}).get('total_media', 0)} items")
            except Exception as e:
                print(f"Error loading main gallery: {e}")
                return
        else:
            print("Creating new main gallery structure")
            main_gallery = {
                'stats': {
                    'total_media': 0,
                    'total_duplicates_removed': 0,
                    'photos': 0,
                    'videos': 0,
                    'external_videos': 0,
                    'categories_count': 0,
                    'years_count': 0,
                    'events_count': 0,
                    'date_range': {'earliest': None, 'latest': None},
                    'credits': {
                        'total_credited': 0,
                        'total_unknown': 0,
                        'unique_credits': 0,
                        'top_credits': [],
                        'credit_breakdown': {}
                    }
                },
                'categories': {},
                'years': {},
                'events': {},
                'collections': {},
                'media_index': [],
                'search_terms': {
                    'locations': [],
                    'event_types': [],
                    'years': [],
                    'media_types': [],
                    'platforms': [],
                    'keywords': []
                }
            }
        
        # Get existing paths to avoid duplicates
        existing_paths = {item['path'] for item in main_gallery.get('media_index', [])}
        
        # Add new items
        new_items = []
        for item in gallery_data.get('media_index', []):
            if item['path'] not in existing_paths:
                new_items.append(item)
            else:
                print(f"Skipping duplicate: {item['path']}")
        
        if not new_items:
            print("No new items to add to main gallery")
            return
        
        # Add to main gallery
        main_gallery['media_index'].extend(new_items)
        
        # Merge categories
        for category_name, category_items in gallery_data.get('categories', {}).items():
            if category_name not in main_gallery['categories']:
                main_gallery['categories'][category_name] = []
            main_gallery['categories'][category_name].extend([item for item in category_items if item in new_items])
        
        # Merge years
        for year, year_items in gallery_data.get('years', {}).items():
            if year not in main_gallery['years']:
                main_gallery['years'][year] = []
            main_gallery['years'][year].extend([item for item in year_items if item in new_items])
        
        # Merge events
        for event_name, event_items in gallery_data.get('events', {}).items():
            if event_name not in main_gallery['events']:
                main_gallery['events'][event_name] = []
            main_gallery['events'][event_name].extend([item for item in event_items if item in new_items])
        
        # Merge collections
        for collection_name, collection_data in gallery_data.get('collections', {}).items():
            if collection_name not in main_gallery['collections']:
                main_gallery['collections'][collection_name] = collection_data
            else:
                existing_media = main_gallery['collections'][collection_name].get('media', [])
                new_media = [item for item in collection_data.get('media', []) if item in new_items]
                main_gallery['collections'][collection_name]['media'] = existing_media + new_media
        
        # Update statistics
        media_index = main_gallery['media_index']
        photos = len([m for m in media_index if m.get('media_type') == 'photo'])
        videos = len([m for m in media_index if m.get('media_type') == 'video'])
        external_videos = len([m for m in media_index if m.get('media_type') == 'external_video'])
        
        years = set()
        for item in media_index:
            if 'year' in item:
                years.add(item['year'])
        
        events = set()
        for item in media_index:
            if 'event' in item and item['event']:
                events.add(item['event'])
        
        # Count credits
        credit_counts = defaultdict(int)
        for item in media_index:
            credit = item.get('credit', 'Unknown photographer')
            credit_counts[credit] += 1
        
        total_credited = sum(1 for credit in credit_counts.keys() if credit != 'Unknown photographer')
        total_unknown = credit_counts.get('Unknown photographer', 0)
        
        # Update stats
        main_gallery['stats'] = {
            'total_media': len(media_index),
            'total_duplicates_removed': main_gallery['stats'].get('total_duplicates_removed', 0),
            'photos': photos,
            'videos': videos,
            'external_videos': external_videos,
            'categories_count': len(main_gallery.get('categories', {})),
            'years_count': len(years),
            'events_count': len(events),
            'date_range': {
                'earliest': min(years) if years else 'unknown',
                'latest': max(years) if years else 'unknown'
            },
            'credits': {
                'total_credited': total_credited,
                'total_unknown': total_unknown,
                'unique_credits': len(credit_counts),
                'top_credits': sorted(credit_counts.items(), key=lambda x: x[1], reverse=True)[:10],
                'credit_breakdown': dict(credit_counts)
            }
        }
        
        # Create backup
        if main_gallery_path.exists():
            backup_path = main_gallery_path.with_name(f'{main_gallery_path.stem}.{datetime.now().strftime("%Y%m%d-%H%M%S")}-backup.json')
            main_gallery_path.rename(backup_path)
            print(f"Created backup: {backup_path}")
        
        # Save merged gallery
        main_gallery_path.parent.mkdir(exist_ok=True)
        with open(main_gallery_path, 'w') as f:
            json.dump(main_gallery, f, indent=2)
        
        print(f"✅ Merged {len(new_items)} new items into main gallery: {main_gallery_path}")
        print(f"📊 Main gallery now has {len(media_index)} total items")
