#!/usr/bin/env python3
"""
Fix YAML metadata formatting issues in Jekyll collections.
- Fix closing --- on same line as data field
- Standardize quote usage (remove unnecessary quotes around simple values)
- Ensure proper YAML structure
"""

import os
import re
from pathlib import Path

def fix_yaml_metadata(file_path):
    """Fix YAML metadata formatting in a single file."""
    try:
        content = file_path.read_text(encoding='utf-8', errors='ignore')
        
        # Check if file has front matter
        if not content.startswith('---\n'):
            return False, "No front matter found"
        
        # Find the end of front matter
        parts = content.split('---\n', 2)
        if len(parts) < 3:
            return False, "Malformed front matter"
        
        front_matter = parts[1]
        body = parts[2]
        
        # Fix closing --- on same line as data field
        # Pattern: "value"--- -> "value"\n---
        front_matter = re.sub(r'(".*?")\s*---$', r'\1\n---', front_matter, flags=re.MULTILINE)
        
        # Fix other patterns where --- might be on same line
        front_matter = re.sub(r'(\S+)\s*---$', r'\1\n---', front_matter, flags=re.MULTILINE)
        
        # Standardize quotes - remove quotes around simple values that don't need them
        lines = front_matter.split('\n')
        fixed_lines = []
        
        for line in lines:
            line = line.strip()
            if not line or line == '---':
                fixed_lines.append(line)
                continue
                
            # Skip if line doesn't contain a colon
            if ':' not in line:
                fixed_lines.append(line)
                continue
            
            key, value = line.split(':', 1)
            key = key.strip()
            value = value.strip()
            
            # Remove quotes around simple values (no spaces, no special chars)
            if value.startswith('"') and value.endswith('"'):
                unquoted = value[1:-1]
                # Only remove quotes if it's a simple value (no spaces, no special punctuation)
                if (not ' ' in unquoted and 
                    not any(char in unquoted for char in ['&', '*', '!', '|', '>', '<', '@', '#', '%', '^', '(', ')', '[', ']', '{', '}', ';', ':', ',', '.', '?', '/', '\\']) and
                    not unquoted.startswith('http') and
                    not unquoted.startswith('archive/')):
                    value = unquoted
            
            # Add quotes back if value contains spaces or special characters and doesn't already have them
            elif (' ' in value or 
                  any(char in value for char in ['&', '*', '!', '|', '>', '<', '@', '#', '%', '^', '(', ')', '[', ']', '{', '}', ';', ':', ',', '.', '?', '/', '\\']) and
                  not value.startswith('"') and
                  not value.startswith("'")):
                value = f'"{value}"'
            
            fixed_lines.append(f"{key}: {value}")
        
        # Reconstruct the file
        new_front_matter = '\n'.join(fixed_lines)
        new_content = f"---\n{new_front_matter}\n---\n{body}"
        
        # Only write if content changed
        if new_content != content:
            file_path.write_text(new_content, encoding='utf-8')
            return True, "Fixed YAML formatting"
        else:
            return False, "No changes needed"
            
    except Exception as e:
        return False, f"Error: {e}"

def main():
    """Fix YAML metadata in all collection files."""
    collections = ['_results', '_events', '_posts']
    total_files = 0
    fixed_files = 0
    
    for collection in collections:
        if not Path(collection).exists():
            print(f"Collection {collection} not found, skipping...")
            continue
            
        print(f"\nProcessing {collection} collection...")
        collection_files = list(Path(collection).glob("*.md"))
        total_files += len(collection_files)
        
        for file_path in collection_files:
            fixed, message = fix_yaml_metadata(file_path)
            if fixed:
                print(f"  ✓ {file_path.name}: {message}")
                fixed_files += 1
            elif "Error" in message:
                print(f"  ✗ {file_path.name}: {message}")
    
    print(f"\nSummary:")
    print(f"  Total files processed: {total_files}")
    print(f"  Files fixed: {fixed_files}")
    print(f"  Files unchanged: {total_files - fixed_files}")

if __name__ == "__main__":
    main()

