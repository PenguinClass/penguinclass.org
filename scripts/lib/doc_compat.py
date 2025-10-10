#!/usr/bin/env python3
"""
DOC file compatibility utilities.

Handles conversion of legacy .doc files to .docx for processing.
"""

import subprocess
import tempfile
from pathlib import Path
from typing import Optional
import logging

logger = logging.getLogger(__name__)


def convert_doc_to_docx(doc_path: Path) -> Optional[Path]:
    """
    Convert .doc file to .docx using LibreOffice or unoconv.
    
    Args:
        doc_path: Path to .doc file
        
    Returns:
        Path to converted .docx file, or None if conversion failed
    """
    if not doc_path.exists():
        logger.error(f"DOC file not found: {doc_path}")
        return None
    
    # Try LibreOffice first
    docx_path = _convert_with_libreoffice(doc_path)
    if docx_path:
        return docx_path
    
    # Try unoconv as fallback
    docx_path = _convert_with_unoconv(doc_path)
    if docx_path:
        return docx_path
    
    logger.warning(f"Could not convert DOC file {doc_path} - LibreOffice and unoconv not available")
    return None


def _convert_with_libreoffice(doc_path: Path) -> Optional[Path]:
    """
    Convert DOC to DOCX using LibreOffice.
    
    Args:
        doc_path: Path to .doc file
        
    Returns:
        Path to converted .docx file, or None if conversion failed
    """
    try:
        # Create temporary directory for conversion
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            
            # Run LibreOffice conversion
            cmd = [
                'libreoffice',
                '--headless',
                '--convert-to', 'docx',
                '--outdir', str(temp_path),
                str(doc_path)
            ]
            
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=60
            )
            
            if result.returncode == 0:
                # Find the converted file
                docx_name = doc_path.stem + '.docx'
                converted_path = temp_path / docx_name
                
                if converted_path.exists():
                    # Copy to a permanent location
                    permanent_path = doc_path.parent / docx_name
                    permanent_path.write_bytes(converted_path.read_bytes())
                    logger.info(f"Converted {doc_path} to {permanent_path}")
                    return permanent_path
            
            logger.warning(f"LibreOffice conversion failed: {result.stderr}")
            return None
            
    except subprocess.TimeoutExpired:
        logger.warning(f"LibreOffice conversion timed out for {doc_path}")
        return None
    except Exception as e:
        logger.warning(f"LibreOffice conversion error for {doc_path}: {e}")
        return None


def _convert_with_unoconv(doc_path: Path) -> Optional[Path]:
    """
    Convert DOC to DOCX using unoconv.
    
    Args:
        doc_path: Path to .doc file
        
    Returns:
        Path to converted .docx file, or None if conversion failed
    """
    try:
        # Create output path
        docx_path = doc_path.with_suffix('.docx')
        
        # Run unoconv conversion
        cmd = [
            'unoconv',
            '-f', 'docx',
            '-o', str(docx_path),
            str(doc_path)
        ]
        
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=60
        )
        
        if result.returncode == 0 and docx_path.exists():
            logger.info(f"Converted {doc_path} to {docx_path}")
            return docx_path
        
        logger.warning(f"unoconv conversion failed: {result.stderr}")
        return None
        
    except subprocess.TimeoutExpired:
        logger.warning(f"unoconv conversion timed out for {doc_path}")
        return None
    except Exception as e:
        logger.warning(f"unoconv conversion error for {doc_path}: {e}")
        return None


def is_libreoffice_available() -> bool:
    """Check if LibreOffice is available."""
    try:
        result = subprocess.run(
            ['libreoffice', '--version'],
            capture_output=True,
            text=True,
            timeout=10
        )
        return result.returncode == 0
    except (subprocess.TimeoutExpired, FileNotFoundError):
        return False


def is_unoconv_available() -> bool:
    """Check if unoconv is available."""
    try:
        result = subprocess.run(
            ['unoconv', '--version'],
            capture_output=True,
            text=True,
            timeout=10
        )
        return result.returncode == 0
    except (subprocess.TimeoutExpired, FileNotFoundError):
        return False
