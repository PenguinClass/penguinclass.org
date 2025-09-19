#!/usr/bin/env python3
"""
Fix filenames that start with underscore by renaming them to not start with underscore.

Jekyll doesn't serve files that start with underscore by default, so we need to rename them.
This script renames files and updates the gallery.json accordingly.
"""

import json
import argparse
from pathlib import Path
from datetime import datetime

class UnderscoreFilenameFixer:
    def __init__(self, gallery_path: str = "assets/data/gallery.json"):
        self.gallery_path = Path(gallery_path)
        self.backup_path = None
        self.renames_made = []
        
    def create_backup(self):
        """Create a backup of the gallery file before fixing."""
        if self.gallery_path.exists():
            timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
            self.backup_path = self.gallery_path.with_name(f'{self.gallery_path.stem}.{timestamp}-backup.json')
            self.gallery_path.rename(self.backup_path)
            print(f"Created backup: {self.backup_path}")
            return True
        return False
    
    def fix_underscore_filenames(self, create_backup: bool = True, dry_run: bool = False) -> dict:
        """Fix filenames that start with underscore."""
        if create_backup and not dry_run:
            self.create_backup()
        
        # Load gallery data from backup if it exists, otherwise from original
        source_path = self.backup_path if self.backup_path else self.gallery_path
        if not source_path.exists():
            raise FileNotFoundError(f"Gallery file not found: {source_path}")
        
        with open(source_path, 'r', encoding='utf-8') as f:
            gallery_data = json.load(f)
        
        # Find files that start with underscore
        underscore_files = []
        for item in gallery_data.get('media_index', []):
            filename = item.get('filename', '')
            if filename.startswith('_'):
                underscore_files.append(item)
        
        print(f"Found {len(underscore_files)} files starting with underscore")
        
        if not underscore_files:
            print("No files need to be renamed")
            return {'files_renamed': 0, 'renames': []}
        
        # Rename files and update gallery data
        for item in underscore_files:
            old_filename = item['filename']
            old_path = item['path']
            
            # Create new filename by replacing underscore with a prefix
            new_filename = f"IMG{old_filename[1:]}"  # Replace _ with IMG
            new_path = str(Path(old_path).parent / new_filename)
            
            # Update the item
            item['filename'] = new_filename
            item['path'] = new_path
            item['encoded_path'] = self.url_encode_path(new_path)
            
            self.renames_made.append({
                'old_path': old_path,
                'new_path': new_path,
                'old_filename': old_filename,
                'new_filename': new_filename
            })
            
            print(f"  {old_filename} -> {new_filename}")
            
            # Actually rename the file if not dry run
            if not dry_run:
                old_file_path = Path(old_path)
                new_file_path = Path(new_path)
                
                if old_file_path.exists():
                    old_file_path.rename(new_file_path)
                    print(f"    Renamed file: {old_file_path} -> {new_file_path}")
                else:
                    print(f"    Warning: File not found: {old_file_path}")
        
        # Save updated gallery data if not dry run
        if not dry_run:
            with open(self.gallery_path, 'w', encoding='utf-8') as f:
                json.dump(gallery_data, f, indent=2, ensure_ascii=False)
            print(f"Updated gallery data saved to: {self.gallery_path}")
        
        return {
            'files_renamed': len(underscore_files),
            'renames': self.renames_made,
            'backup_path': str(self.backup_path) if self.backup_path else None
        }
    
    def url_encode_path(self, path: str) -> str:
        """URL encode special characters in file paths."""
        from urllib.parse import quote
        # Split the path into directory and filename parts
        path_obj = Path(path)
        encoded_parts = []
        
        # Encode each part of the path
        for part in path_obj.parts:
            # Only encode special characters that cause issues in URLs
            encoded_part = quote(part, safe='')
            encoded_parts.append(encoded_part)
        
        return '/'.join(encoded_parts)

def main():
    parser = argparse.ArgumentParser(description='Fix filenames starting with underscore')
    parser.add_argument('--gallery-path', default='assets/data/gallery.json',
                       help='Path to gallery.json file')
    parser.add_argument('--no-backup', action='store_true',
                       help='Skip creating backup before fixing')
    parser.add_argument('--dry-run', action='store_true',
                       help='Show what would be renamed without actually doing it')
    
    args = parser.parse_args()
    
    fixer = UnderscoreFilenameFixer(args.gallery_path)
    
    try:
        result = fixer.fix_underscore_filenames(
            create_backup=not args.no_backup,
            dry_run=args.dry_run
        )
        
        if result['files_renamed'] > 0:
            if args.dry_run:
                print(f"\n✅ Would rename {result['files_renamed']} files")
            else:
                print(f"\n✅ Successfully renamed {result['files_renamed']} files")
        else:
            print("\n✅ No files need to be renamed")
            
    except Exception as e:
        print(f"❌ Error during filename fixing: {e}")
        return 1
    
    return 0

if __name__ == '__main__':
    exit(main())
