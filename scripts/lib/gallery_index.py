#!/usr/bin/env python3
"""
Gallery indexing utilities for fast lookups and deduplication.

Provides hash-based and path-based indexing for media entries.
"""

from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple
import logging

logger = logging.getLogger(__name__)


class GalleryIndex:
    """Fast lookup index for gallery media entries."""
    
    def __init__(self, media_list: List[Dict[str, Any]]):
        """
        Initialize index from media list.
        
        Args:
            media_list: List of media entries from gallery data
        """
        self.media_list = media_list
        self.hash_index: Dict[str, int] = {}  # hash -> index
        self.path_index: Dict[str, int] = {}  # normalized path -> index
        
        self._build_indexes()
    
    def _build_indexes(self) -> None:
        """Build hash and path indexes."""
        for i, entry in enumerate(self.media_list):
            # Index by hash if present
            if 'hash' in entry and entry['hash']:
                self.hash_index[entry['hash']] = i
            
            # Index by normalized path
            if 'path' in entry and entry['path']:
                normalized_path = self._normalize_path(entry['path'])
                self.path_index[normalized_path] = i
    
    def _normalize_path(self, path: str) -> str:
        """
        Normalize path for consistent indexing.
        
        Args:
            path: File path to normalize
            
        Returns:
            Normalized path string
        """
        # Convert to POSIX path and normalize
        normalized = Path(path).as_posix()
        
        # Ensure it starts with / for site-relative paths
        if not normalized.startswith('/'):
            normalized = '/' + normalized
        
        return normalized
    
    def find_by_hash(self, hash_value: str) -> Optional[Dict[str, Any]]:
        """
        Find media entry by hash.
        
        Args:
            hash_value: SHA-1 hash to search for
            
        Returns:
            Media entry dict if found, None otherwise
        """
        if hash_value in self.hash_index:
            return self.media_list[self.hash_index[hash_value]]
        return None
    
    def find_by_path(self, path: str) -> Optional[Dict[str, Any]]:
        """
        Find media entry by path.
        
        Args:
            path: File path to search for
            
        Returns:
            Media entry dict if found, None otherwise
        """
        normalized_path = self._normalize_path(path)
        if normalized_path in self.path_index:
            return self.media_list[self.path_index[normalized_path]]
        return None
    
    def upsert_entry(self, entry: Dict[str, Any], prefer_hash: bool = True) -> Tuple[bool, int]:
        """
        Insert or update media entry.
        
        Args:
            entry: Media entry to upsert
            prefer_hash: Whether to prefer hash-based matching over path-based
            
        Returns:
            Tuple of (was_new_entry, entry_index)
        """
        existing_entry = None
        existing_index = None
        
        # Try hash-based lookup first if prefer_hash and hash is available
        if prefer_hash and 'hash' in entry and entry['hash']:
            existing_entry = self.find_by_hash(entry['hash'])
            if existing_entry:
                existing_index = self.hash_index[entry['hash']]
        
        # Fall back to path-based lookup
        if not existing_entry and 'path' in entry and entry['path']:
            existing_entry = self.find_by_path(entry['path'])
            if existing_entry:
                existing_index = self.path_index[self._normalize_path(entry['path'])]
        
        if existing_entry:
            # Update existing entry
            self._update_existing_entry(existing_index, entry)
            return False, existing_index
        else:
            # Add new entry
            new_index = len(self.media_list)
            self.media_list.append(entry)
            
            # Update indexes
            if 'hash' in entry and entry['hash']:
                self.hash_index[entry['hash']] = new_index
            if 'path' in entry and entry['path']:
                self.path_index[self._normalize_path(entry['path'])] = new_index
            
            return True, new_index
    
    def _update_existing_entry(self, index: int, new_entry: Dict[str, Any]) -> None:
        """
        Update existing entry with new data.
        
        Args:
            index: Index of existing entry
            new_entry: New entry data to merge
        """
        existing = self.media_list[index]
        
        # Preserve all existing fields, only add new ones
        for key, value in new_entry.items():
            if key not in existing:
                existing[key] = value
            elif key == 'hash' and not existing.get('hash'):
                # Backfill missing hash
                existing['hash'] = value
                # Update hash index
                self.hash_index[value] = index
    
    def append_caption(self, entry: Dict[str, Any], caption: str, source: str, method: str) -> bool:
        """
        Append caption to entry if unique.
        
        Args:
            entry: Media entry to update
            caption: Caption text
            source: Source file/context
            method: Extraction method
            
        Returns:
            True if caption was added, False if duplicate
        """
        if not caption or not caption.strip():
            return False
        
        caption = caption.strip()
        
        # Check if this is a single caption string
        if 'caption' in entry and isinstance(entry['caption'], str):
            # Convert to array format if we have a non-empty existing caption
            if entry['caption'].strip():
                entry['captions'] = [{
                    'text': entry['caption'],
                    'source': 'existing',
                    'method': 'legacy'
                }]
            else:
                entry['captions'] = []
            # Remove the old string field
            del entry['caption']
        
        # Ensure captions array exists
        if 'captions' not in entry:
            entry['captions'] = []
        
        # Check for duplicates (case-insensitive text + same source)
        caption_lower = caption.lower()
        for existing in entry['captions']:
            if (existing.get('text', '').lower() == caption_lower and 
                existing.get('source') == source):
                logger.debug(f"Duplicate caption skipped: {caption[:50]}... from {source}")
                return False
        
        # Add new caption
        entry['captions'].append({
            'text': caption,
            'source': source,
            'method': method
        })
        
        logger.debug(f"Added caption: {caption[:50]}... from {source}")
        return True
    
    def ensure_hash(self, entry: Dict[str, Any], file_path: Optional[Path] = None) -> bool:
        """
        Ensure entry has a hash field, computing it if missing.
        
        Args:
            entry: Media entry to update
            file_path: Optional file path to compute hash from
            
        Returns:
            True if hash was added/updated, False otherwise
        """
        if 'hash' in entry and entry['hash']:
            return False  # Already has hash
        
        # Try to get file path
        if not file_path and 'path' in entry:
            file_path = Path(entry['path'])
        
        if not file_path or not file_path.exists():
            logger.warning(f"Cannot compute hash for {entry.get('path', 'unknown')} - file not found")
            return False
        
        # Compute hash
        from .hash_utils import file_sha1
        hash_value = file_sha1(file_path)
        
        if hash_value:
            entry['hash'] = hash_value
            # Update index
            self.hash_index[hash_value] = self.media_list.index(entry)
            return True
        
        return False
