#!/usr/bin/env python3
"""
Fix encoding issues by attempting to recover original characters from U+FFFD.

This script tries to intelligently replace U+FFFD characters with likely original characters
based on context and common patterns.
"""

import re
import pathlib
from typing import Dict, List

ROOT = pathlib.Path("archive/legacy-website")
EXTS = {".html", ".htm", ".txt", ".css", ".js"}

# Common character replacements based on context
CHAR_REPLACEMENTS = {
    # Common patterns in dates and names
    r'(\d{4})\s*\s*(\d{4})': r'\1–\2',  # Year ranges like "1945 2024" -> "1945–2024"
    r'(\d{1,2})\s*\s*(\d{1,2})': r'\1–\2',  # Day ranges
    r'(\w+)\s*\s*(\w+)': r'\1–\2',  # Word ranges
    r'\s*(\d{4})': r'–\1',  # Leading dash
    r'(\d{4})\s*': r'\1–',  # Trailing dash
    r'\s*(\d{1,2})': r'–\1',  # Leading dash for days
    r'(\d{1,2})\s*': r'\1–',  # Trailing dash for days
    
    # Common punctuation
    r'\s*': '–',  # Standalone replacement with en dash
    r'\s*\s*': '–',  # Spaced replacement with en dash
    
    # Copyright symbol
    r'\s*\(c\)': '©',  # Copyright symbol
    r'\(c\)\s*': '©',  # Copyright symbol
    
    # Common in names and titles
    r'(\w)\s*\s*(\w)': r'\1–\2',  # Between words
}

def fix_encoding_with_recovery(file_path: pathlib.Path, dry_run: bool = True) -> Dict:
    """Fix encoding issues by attempting to recover original characters."""
    try:
        content = file_path.read_text(encoding='utf-8', errors='ignore')
        original_content = content
        changes = []
        
        # Count U+FFFD characters
        fffd_count = content.count('\uFFFD')
        if fffd_count == 0:
            return {'changed': False, 'changes': [], 'fffd_count': 0}
        
        changes.append(f"Found {fffd_count} U+FFFD replacement characters")
        
        # Apply intelligent replacements
        for pattern, replacement in CHAR_REPLACEMENTS.items():
            matches = re.findall(pattern, content)
            if matches:
                new_content = re.sub(pattern, replacement, content)
                if new_content != content:
                    count = len(matches)
                    changes.append(f"Replaced {count} instances of pattern '{pattern}' with '{replacement}'")
                    content = new_content
        
        # For any remaining U+FFFD characters, try to replace with en dash
        remaining_fffd = content.count('\uFFFD')
        if remaining_fffd > 0:
            content = content.replace('\uFFFD', '–')
            changes.append(f"Replaced {remaining_fffd} remaining U+FFFD characters with en dash (–)")
        
        # Write back if not dry run
        if not dry_run and content != original_content:
            file_path.write_text(content, encoding='utf-8')
        
        return {
            'changed': content != original_content,
            'changes': changes,
            'fffd_count': fffd_count
        }
        
    except Exception as e:
        return {'error': str(e)}

def main():
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == '--fix':
        print("=== FIXING ENCODING WITH CHARACTER RECOVERY ===\n")
        dry_run = False
    else:
        print("=== ANALYZING ENCODING WITH CHARACTER RECOVERY (DRY RUN) ===\n")
        print("Use --fix to actually make changes\n")
        dry_run = True
    
    fixed_files = 0
    total_fffd_chars = 0
    total_changes = 0
    
    # Process all files
    for file_path in sorted(ROOT.rglob("*")):
        if not file_path.is_file() or file_path.suffix.lower() not in EXTS:
            continue
            
        result = fix_encoding_with_recovery(file_path, dry_run=dry_run)
        
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
