#!/usr/bin/env python3
"""
Fix remaining encoding issues in legacy website files.

This script specifically targets:
1. U+FFFD replacement characters
2. Common Windows-1252 characters that weren't properly converted
3. Other encoding artifacts
"""

import re
import pathlib
from typing import Dict, List

ROOT = pathlib.Path("archive/legacy-website")
EXTS = {".html", ".htm", ".txt", ".css", ".js"}

# Common Windows-1252 to UTF-8 mappings for characters that cause issues
CHAR_MAPPINGS = {
    # Smart quotes and dashes
    b'\x91': "'",  # Left single quotation mark
    b'\x92': "'",  # Right single quotation mark  
    b'\x93': '"',  # Left double quotation mark
    b'\x94': '"',  # Right double quotation mark
    b'\x96': '–',  # En dash
    b'\x97': '—',  # Em dash
    b'\x85': '…',  # Horizontal ellipsis
    b'\x80': '€',  # Euro sign
    b'\x82': '‚',  # Single low-9 quotation mark
    b'\x84': '„',  # Double low-9 quotation mark
    b'\x86': '†',  # Dagger
    b'\x87': '‡',  # Double dagger
    b'\x88': 'ˆ',  # Modifier letter circumflex accent
    b'\x89': '‰',  # Per mille sign
    b'\x8a': 'Š',  # Latin capital letter S with caron
    b'\x8b': '‹',  # Single left-pointing angle quotation mark
    b'\x8c': 'Œ',  # Latin capital ligature OE
    b'\x8e': 'Ž',  # Latin capital letter Z with caron
    b'\x91': 'š',  # Latin small letter s with caron
    b'\x9a': 'š',  # Latin small letter s with caron
    b'\x9b': '›',  # Single right-pointing angle quotation mark
    b'\x9c': 'œ',  # Latin small ligature oe
    b'\x9e': 'ž',  # Latin small letter z with caron
    b'\x9f': 'Ÿ',  # Latin capital letter Y with diaeresis
}

def fix_encoding_issues_in_file(file_path: pathlib.Path, dry_run: bool = True) -> Dict:
    """Fix encoding issues in a single file."""
    try:
        # Read as bytes first to handle the raw encoding issues
        with open(file_path, 'rb') as f:
            content_bytes = f.read()
        
        original_content = content_bytes
        changes = []
        
        # Count U+FFFD characters
        fffd_count = content_bytes.count(b'\xef\xbf\xbd')
        if fffd_count > 0:
            changes.append(f"Found {fffd_count} U+FFFD replacement characters")
        
        # Replace problematic bytes with proper UTF-8 characters
        for byte_seq, replacement in CHAR_MAPPINGS.items():
            count = content_bytes.count(byte_seq)
            if count > 0:
                content_bytes = content_bytes.replace(byte_seq, replacement.encode('utf-8'))
                changes.append(f"Replaced {count} instances of byte {byte_seq.hex()} with '{replacement}'")
        
        # Try to decode as UTF-8 and handle any remaining issues
        try:
            content_text = content_bytes.decode('utf-8')
        except UnicodeDecodeError as e:
            # If there are still decode errors, replace them with a safe character
            content_text = content_bytes.decode('utf-8', errors='replace')
            changes.append(f"Fixed remaining decode errors: {e}")
        
        # Remove any remaining U+FFFD characters
        original_fffd_count = content_text.count('\uFFFD')
        if original_fffd_count > 0:
            content_text = content_text.replace('\uFFFD', '')
            changes.append(f"Removed {original_fffd_count} remaining U+FFFD characters")
        
        # Write back as UTF-8
        if not dry_run and content_bytes != original_content:
            file_path.write_text(content_text, encoding='utf-8')
        
        return {
            'changed': content_bytes != original_content or original_fffd_count > 0,
            'changes': changes,
            'fffd_count': fffd_count
        }
        
    except Exception as e:
        return {'error': str(e)}

def main():
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == '--fix':
        print("=== FIXING REMAINING ENCODING ISSUES ===\n")
        dry_run = False
    else:
        print("=== ANALYZING REMAINING ENCODING ISSUES (DRY RUN) ===\n")
        print("Use --fix to actually make changes\n")
        dry_run = True
    
    fixed_files = 0
    total_fffd_chars = 0
    total_changes = 0
    
    # Process all files
    for file_path in sorted(ROOT.rglob("*")):
        if not file_path.is_file() or file_path.suffix.lower() not in EXTS:
            continue
            
        result = fix_encoding_issues_in_file(file_path, dry_run=dry_run)
        
        if result.get('changed') or result.get('fffd_count', 0) > 0:
            fixed_files += 1
            rel_path = file_path.relative_to(ROOT)
            print(f"✅ {'Would fix' if dry_run else 'Fixed'} {rel_path}")
            
            if result.get('fffd_count', 0) > 0:
                print(f"  • U+FFFD characters: {result['fffd_count']}")
                total_fffd_chars += result['fffd_count']
            
            for change in result.get('changes', []):
                print(f"  • {change}")
                total_changes += 1
        
        if result.get('error'):
            rel_path = file_path.relative_to(ROOT)
            print(f"❌ Error processing {rel_path}: {result['error']}")
    
    print(f"\n=== {'ANALYSIS' if dry_run else 'FIX'} COMPLETE ===")
    print(f"Files {'with issues' if dry_run else 'fixed'}: {fixed_files}")
    print(f"Total U+FFFD characters: {total_fffd_chars}")
    print(f"Total changes: {total_changes}")

if __name__ == "__main__":
    main()
