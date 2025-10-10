#!/usr/bin/env python3
"""
Hash utilities for gallery data.

Provides SHA-1 hashing functions for file deduplication.
"""

import hashlib
from pathlib import Path
from typing import Optional


def sha1_bytes(data: bytes) -> str:
    """
    Compute SHA-1 hash of bytes data.
    
    Args:
        data: Bytes to hash
        
    Returns:
        SHA-1 hash as hexadecimal string
    """
    return hashlib.sha1(data).hexdigest()


def file_sha1(path: Path) -> Optional[str]:
    """
    Compute SHA-1 hash of a file.
    
    Args:
        path: Path to file
        
    Returns:
        SHA-1 hash as hexadecimal string, or None if file doesn't exist
    """
    if not path.exists():
        return None
    
    try:
        with open(path, 'rb') as f:
            return sha1_bytes(f.read())
    except (IOError, OSError):
        return None
