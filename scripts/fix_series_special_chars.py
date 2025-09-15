#!/usr/bin/env python3
"""
Fix special characters in series field in _results files that are causing Jekyll permalink issues.
"""

import os
import re
import glob

def fix_series_special_chars():
    """Replace special characters with hyphens in series field in _results files."""
    results_dir = "_results"
    fixed_count = 0
    
    for file_path in glob.glob(os.path.join(results_dir, "*.md")):
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Check if file has series field with special characters
            if re.search(r'series:\s+[^a-zA-Z0-9-]', content):
                # Replace special characters with hyphens in series field
                # First, replace spaces and & with hyphens
                new_content = re.sub(r'series:\s+([^"\n]+)', lambda m: f'series: {re.sub(r"[ &]+", "-", m.group(1))}', content)
                
                if new_content != content:
                    with open(file_path, 'w', encoding='utf-8') as f:
                        f.write(new_content)
                    print(f"Fixed special chars in series field: {file_path}")
                    fixed_count += 1
                    
        except Exception as e:
            print(f"Error processing {file_path}: {e}")
    
    print(f"Fixed special chars in {fixed_count} files")

if __name__ == "__main__":
    fix_series_special_chars()
