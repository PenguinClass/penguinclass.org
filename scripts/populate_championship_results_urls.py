#!/usr/bin/env python3
"""
Populate results_url in front matter for all _results/*championship.md files
by extracting "View Results" URLs from their content.
"""
import os
import re
import yaml
from pathlib import Path

def extract_results_url_from_content(content):
    """Extract results URL from content."""
    # Look for "View Results" links
    view_results_patterns = [
        r'\[View Results\]\(([^)]+)\)',
        r'\[Results\]\(([^)]+)\)',
        r'\[Full Results\]\(([^)]+)\)',
    ]
    
    for pattern in view_results_patterns:
        try:
            match = re.search(pattern, content, re.IGNORECASE)
            if match:
                url = match.group(1).strip()
                # Ensure URL has leading slash if it's a relative path
                if url and not url.startswith(('http://', 'https://', '/')):
                    url = '/' + url
                return url
        except re.error:
            continue
    
    return None

def update_championship_file(file_path):
    """Update a single championship file with results_url if needed."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Extract front matter
        if not content.startswith('---'):
            print(f"Skipping {file_path.name}: No front matter")
            return False
        
        parts = content.split('---', 2)
        if len(parts) < 3:
            print(f"Skipping {file_path.name}: Malformed front matter")
            return False
        
        front_matter_text = parts[1]
        content_body = parts[2]
        
        # Parse front matter
        front_matter = yaml.safe_load(front_matter_text) or {}
        
        # Check if results_url is already populated
        current_results_url = front_matter.get('results_url', '')
        if current_results_url:
            print(f"No update needed for {file_path.name}: results_url already set")
            return False
        
        # Extract results URL from content
        results_url = extract_results_url_from_content(content_body)
        if not results_url:
            print(f"No results URL found in content for {file_path.name}")
            return False
        
        # Update front matter
        front_matter['results_url'] = results_url
        
        # Rebuild the file
        new_front_matter = yaml.safe_dump(front_matter, sort_keys=False, allow_unicode=True, width=1200)
        new_content = f"---\n{new_front_matter.strip()}\n---{content_body}"
        
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(new_content)
        
        print(f"Updated {file_path.name}: added results_url = '{results_url}'")
        return True
        
    except Exception as e:
        print(f"Error processing {file_path.name}: {e}")
        return False

def main():
    """Main function."""
    print("Populating results_url in championship files...")
    
    # Process all championship files in _results directory
    results_dir = Path("_results")
    if not results_dir.exists():
        print("_results directory not found!")
        return
    
    # Find all championship files
    championship_files = []
    for file_path in results_dir.glob("*championship.md"):
        championship_files.append(file_path)
    
    print(f"Found {len(championship_files)} championship files")
    
    updated_count = 0
    
    for file_path in sorted(championship_files):
        print(f"\nProcessing {file_path.name}...")
        if update_championship_file(file_path):
            updated_count += 1
    
    print(f"\n=== SUMMARY ===")
    print(f"Total championship files: {len(championship_files)}")
    print(f"Files updated: {updated_count}")
    print(f"Files already had results_url: {len(championship_files) - updated_count}")

if __name__ == "__main__":
    main()
