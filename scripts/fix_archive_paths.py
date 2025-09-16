#!/usr/bin/env python3
"""
Fix incorrect /archive/ paths in legacy website files.

This script finds paths that start with /archive/ but don't contain "legacy-website"
and corrects them to /archive/legacy-website/
"""

import re
import pathlib
from typing import List, Tuple

ROOT = pathlib.Path("archive/legacy-website")
EXTS = {".html", ".htm", ".css", ".js"}

# Pattern to find /archive/legacy-web (truncated) that should be /archive/legacy-website
INCORRECT_ARCHIVE_PATTERN = re.compile(r'("/archive/legacy-web)(">)', re.IGNORECASE)

def fix_archive_paths_in_file(file_path: pathlib.Path, dry_run: bool = True) -> dict:
    """Fix incorrect archive paths in a single file."""
    try:
        content = file_path.read_text(encoding='utf-8', errors='ignore')
        original_content = content
        changes = []
        
        def fix_path(match):
            path_part = match.group(1)
            quote_part = match.group(2)
            
            # Fix /archive/legacy-web to /archive/legacy-website
            if path_part == "/archive/legacy-web":
                new_path = "/archive/legacy-website"
            else:
                return match.group(0)
            
            changes.append(f"{path_part} -> {new_path}")
            return f"{new_path}{quote_part}"
        
        # Apply the fix
        matches = INCORRECT_ARCHIVE_PATTERN.findall(content)
        if matches:
            print(f"  Found {len(matches)} matches in {file_path.name}")
            for match in matches:
                print(f"    Match: {match}")
        content = INCORRECT_ARCHIVE_PATTERN.sub(fix_path, content)
        
        # Write changes if not dry run
        if not dry_run and content != original_content:
            file_path.write_text(content, encoding='utf-8')
        
        return {
            'changed': content != original_content,
            'changes': changes
        }
        
    except Exception as e:
        return {'error': str(e)}

def main():
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == '--fix':
        print("=== FIXING INCORRECT ARCHIVE PATHS ===\n")
        dry_run = False
    else:
        print("=== ANALYZING INCORRECT ARCHIVE PATHS (DRY RUN) ===\n")
        print("Use --fix to actually make changes\n")
        dry_run = True
    
    fixed_files = 0
    total_changes = 0
    
    # Process all files
    for file_path in sorted(ROOT.rglob("*")):
        if not file_path.is_file() or file_path.suffix.lower() not in EXTS:
            continue
        
        # Check if this file contains the pattern we're looking for
        try:
            content = file_path.read_text(encoding='utf-8', errors='ignore')
            if '/archive/legacy-web' in content:
                print(f"Found pattern in: {file_path.relative_to(ROOT)}")
        except:
            pass
            
        result = fix_archive_paths_in_file(file_path, dry_run=dry_run)
        
        if result.get('changed'):
            fixed_files += 1
            rel_path = file_path.relative_to(ROOT)
            print(f"✅ {'Would fix' if dry_run else 'Fixed'} {rel_path}")
            
            for change in result['changes']:
                print(f"  • {change}")
                total_changes += 1
        
        if result.get('error'):
            rel_path = file_path.relative_to(ROOT)
            print(f"❌ Error processing {rel_path}: {result['error']}")
    
    print(f"\n=== {'ANALYSIS' if dry_run else 'FIX'} COMPLETE ===")
    print(f"Files {'with issues' if dry_run else 'fixed'}: {fixed_files}")
    print(f"Total changes: {total_changes}")

if __name__ == "__main__":
    main()
