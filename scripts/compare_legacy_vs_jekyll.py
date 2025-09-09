#!/usr/bin/env python3
"""
Compare legacy website files with what's already in the Jekyll archive
to identify missing content that needs migration.
"""

import os
import glob
from pathlib import Path

def get_file_list(directory, extensions=['.html', '.htm']):
    """Get list of files with specified extensions from directory."""
    files = []
    if os.path.exists(directory):
        for ext in extensions:
            pattern = os.path.join(directory, f"**/*{ext}")
            files.extend(glob.glob(pattern, recursive=True))
    return [os.path.basename(f) for f in files]

def main():
    # Paths
    legacy_path = "/mnt/c/Documents and Settings/samco/OneDrive/Organizations/Penguin Class/2024-08 penguinclass.com cleanup/httpdocs/"
    jekyll_archive_path = "archive/legacy-website/"
    
    print("Comparing legacy website with Jekyll archive...")
    print(f"Legacy path: {legacy_path}")
    print(f"Jekyll archive path: {jekyll_archive_path}")
    
    # Get file lists
    legacy_files = set(get_file_list(legacy_path))
    jekyll_files = set(get_file_list(jekyll_archive_path))
    
    print(f"\nLegacy website HTML files: {len(legacy_files)}")
    print(f"Jekyll archive HTML files: {len(jekyll_files)}")
    
    # Find missing files
    missing_files = legacy_files - jekyll_files
    extra_files = jekyll_files - legacy_files
    
    print(f"\nMissing from Jekyll archive: {len(missing_files)}")
    if missing_files:
        print("Missing files:")
        for f in sorted(missing_files):
            print(f"  - {f}")
    
    print(f"\nExtra in Jekyll archive: {len(extra_files)}")
    if extra_files:
        print("Extra files:")
        for f in sorted(extra_files):
            print(f"  - {f}")
    
    # Also check for other important file types
    print("\n" + "="*50)
    print("Checking other file types...")
    
    for ext in ['.pdf', '.doc', '.docx', '.jpg', '.jpeg', '.png', '.gif']:
        legacy_other = set(get_file_list(legacy_path, [ext]))
        jekyll_other = set(get_file_list(jekyll_archive_path, [ext]))
        
        missing_other = legacy_other - jekyll_other
        if missing_other:
            print(f"\nMissing {ext} files: {len(missing_other)}")
            for f in sorted(list(missing_other)[:10]):  # Show first 10
                print(f"  - {f}")
            if len(missing_other) > 10:
                print(f"  ... and {len(missing_other) - 10} more")

if __name__ == "__main__":
    main()

