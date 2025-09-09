#!/usr/bin/env python3
"""
Fix all file:// URLs in the entire Jekyll site and legacy website archive.
"""

import os
import re
import glob

def fix_file_urls_in_file(file_path):
    """Fix file:// URLs in a single file."""
    
    try:
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()
        
        original_content = content
        fixes_applied = 0
        
        # Fix file:///C:/Users/krafft/Documents/My%20Documents/CSK/Penguin/ URLs
        if 'file:///C:/Users/krafft/Documents/My%20Documents/CSK/Penguin/' in content:
            content = re.sub(
                r'file:///C:/Users/krafft/Documents/My%20Documents/CSK/Penguin/([^"\s<>]+)',
                r'archive/legacy-website/\1',
                content
            )
            fixes_applied += content.count('archive/legacy-website/') - original_content.count('archive/legacy-website/')
        
        # Fix file:///C:/Users/krafft/Documents/My%20Documents/CSK/ URLs (without Penguin)
        if 'file:///C:/Users/krafft/Documents/My%20Documents/CSK/' in content:
            content = re.sub(
                r'file:///C:/Users/krafft/Documents/My%20Documents/CSK/([^"\s<>]+)',
                r'archive/legacy-website/\1',
                content
            )
            fixes_applied += original_content.count('file:///C:/Users/krafft/Documents/My%20Documents/CSK/') - content.count('file:///C:/Users/krafft/Documents/My%20Documents/CSK/')
        
        # Fix file:///C:/JavaScore/reports/ URLs
        if 'file:///C:/JavaScore/reports/' in content:
            content = re.sub(
                r'file:///C:/JavaScore/reports/([^"\s<>]+)',
                r'archive/legacy-website/\1',
                content
            )
            fixes_applied += original_content.count('file:///C:/JavaScore/reports/') - content.count('file:///C:/JavaScore/reports/')
        
        # Fix other file:// URLs (generic)
        if 'file://' in content:
            content = re.sub(
                r'file://[^"\s<>]+',
                lambda m: m.group(0).replace('file://', 'archive/legacy-website/'),
                content
            )
            fixes_applied += original_content.count('file://') - content.count('file://')
        
        if content != original_content:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            return fixes_applied
        
        return 0
        
    except Exception as e:
        print(f"  Error processing {file_path}: {e}")
        return 0

def main():
    print("Fixing all file:// URLs in the site...")
    
    # Files to process
    file_patterns = [
        '**/*.html',
        '**/*.htm', 
        '**/*.md',
        '**/*.yml',
        '**/*.yaml',
        '**/*.json',
        '**/*.txt'
    ]
    
    total_fixes = 0
    files_processed = 0
    files_fixed = 0
    
    for pattern in file_patterns:
        for file_path in glob.glob(pattern, recursive=True):
            # Skip certain directories and files
            if any(skip in file_path for skip in [
                '.git/', 
                'vendor/', 
                '_site/', 
                'node_modules/',
                '.bundle/',
                'scripts/fix_',  # Skip our own fix scripts
                'scripts/parse_champions.py'  # Skip this one as it's just a constant
            ]):
                continue
            
            files_processed += 1
            fixes = fix_file_urls_in_file(file_path)
            
            if fixes > 0:
                files_fixed += 1
                total_fixes += fixes
                print(f"  {file_path}: {fixes} fixes")
    
    print(f"\nFile URL cleanup complete!")
    print(f"  Files processed: {files_processed}")
    print(f"  Files fixed: {files_fixed}")
    print(f"  Total fixes: {total_fixes}")

if __name__ == "__main__":
    main()
