#!/usr/bin/env python3
"""
Fix ampersand and spaces in series field in _results files.
"""

import os
import re
import glob

def fix_series_ampersand():
    """Replace ampersand and spaces with hyphens in series field in _results files."""
    results_dir = "_results"
    fixed_count = 0
    
    for file_path in glob.glob(os.path.join(results_dir, "*.md")):
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Check if file has series field with ampersand or spaces
            if 'series: Comet & Penguin Invitational' in content:
                # Replace the specific problematic series
                new_content = content.replace('series: Comet & Penguin Invitational', 'series: Comet-Penguin-Invitational')
                
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(new_content)
                print(f"Fixed ampersand in series field: {file_path}")
                fixed_count += 1
                    
        except Exception as e:
            print(f"Error processing {file_path}: {e}")
    
    print(f"Fixed ampersand in {fixed_count} files")

if __name__ == "__main__":
    fix_series_ampersand()
