#!/usr/bin/env python3
"""
JSON storage utilities for gallery data.

Handles loading and saving gallery.json while preserving unknown fields
and maintaining atomic writes.
"""

import json
import tempfile
from pathlib import Path
from typing import Dict, Any, Tuple, List


def load_gallery(path: Path) -> Dict[str, Any]:
    """
    Load gallery data from JSON file, preserving all unknown fields.
    
    Args:
        path: Path to gallery.json file
        
    Returns:
        Dictionary containing gallery data
        
    Raises:
        FileNotFoundError: If gallery file doesn't exist
        json.JSONDecodeError: If file contains invalid JSON
    """
    if not path.exists():
        raise FileNotFoundError(f"Gallery file not found: {path}")
    
    with open(path, 'r', encoding='utf-8') as f:
        return json.load(f)


def save_gallery(path: Path, data: Dict[str, Any]) -> None:
    """
    Save gallery data to JSON file with atomic write (tmp + rename).
    
    Args:
        path: Path to save gallery.json file
        data: Dictionary containing gallery data
    """
    # Ensure parent directory exists
    path.parent.mkdir(parents=True, exist_ok=True)
    
    # Write to temporary file first
    with tempfile.NamedTemporaryFile(
        mode='w', 
        encoding='utf-8', 
        dir=path.parent,
        prefix=f'.{path.name}.tmp.',
        delete=False
    ) as tmp_file:
        json.dump(data, tmp_file, indent=2, ensure_ascii=False)
        tmp_path = Path(tmp_file.name)
    
    # Atomic rename
    tmp_path.replace(path)


def find_media_array(data: Dict[str, Any]) -> Tuple[List[Dict[str, Any]], str]:
    """
    Find the array that holds media entries in the gallery data.
    
    Args:
        data: Gallery data dictionary
        
    Returns:
        Tuple of (media_list_reference, key_name)
        
    Raises:
        KeyError: If no media array is found
    """
    # Check common keys for media arrays
    possible_keys = ['media_index', 'images', 'media', 'items']
    
    for key in possible_keys:
        if key in data and isinstance(data[key], list):
            return data[key], key
    
    # If not found, raise error with helpful message
    available_keys = [k for k, v in data.items() if isinstance(v, list)]
    raise KeyError(
        f"No media array found. Expected one of {possible_keys}, "
        f"but found lists under: {available_keys}"
    )
