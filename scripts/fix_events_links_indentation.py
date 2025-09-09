#!/usr/bin/env python3
"""
Fix indentation for sub-items under 'links:' in _events/*.md files.
All sub-items under 'links:' should be indented with 2 spaces.
"""

import re
from pathlib import Path

def fix_links_indentation(file_path):
    """Fix indentation for links sub-items in a single file."""
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
        
        # Split into lines and process
        lines = front_matter.split('\n')
        fixed_lines = []
        in_links_section = False
        
        for line in lines:
            # Check if we're entering the links section
            if line.strip() == 'links:' or line.strip() == 'links: ':
                in_links_section = True
                fixed_lines.append(line)
                continue
            
            # Check if we're leaving the links section (next top-level key or empty line)
            if in_links_section:
                # If line is empty or starts with a non-space character (new top-level key)
                if not line or (line and not line.startswith(' ')):
                    in_links_section = False
                    if line:  # Don't add empty lines to the check
                        fixed_lines.append(line)
                        continue
            
            # If we're in the links section and the line has content but no proper indentation
            if in_links_section and line.strip() and not line.startswith('  '):
                # Add 2-space indentation
                fixed_line = '  ' + line.strip()
                fixed_lines.append(fixed_line)
            else:
                fixed_lines.append(line)
        
        # Reconstruct the file
        new_front_matter = '\n'.join(fixed_lines)
        new_content = f"---\n{new_front_matter}\n---\n{body}"
        
        # Only write if content changed
        if new_content != content:
            file_path.write_text(new_content, encoding='utf-8')
            return True, "Fixed links indentation"
        else:
            return False, "No changes needed"
            
    except Exception as e:
        return False, f"Error: {e}"

def main():
    """Fix links indentation in all _events files."""
    events_dir = Path('_events')
    if not events_dir.exists():
        print("_events directory not found")
        return
    
    print("Processing _events collection...")
    event_files = list(events_dir.glob("*.md"))
    total_files = len(event_files)
    fixed_files = 0
    
    for file_path in event_files:
        fixed, message = fix_links_indentation(file_path)
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

