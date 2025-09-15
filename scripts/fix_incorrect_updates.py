#!/usr/bin/env python3
"""
Fix incorrectly updated _results files that have bad club/location data.
"""
import os
import yaml
from pathlib import Path

def fix_incorrect_updates():
    """Fix files with incorrect club/location data."""
    
    results_dir = Path("_results")
    if not results_dir.exists():
        print("_results directory not found!")
        return False
    
    # List of files that were incorrectly updated
    problematic_files = [
        "2013-heritage-regatta.md",
        "2013-icpfr-regatta.md", 
        "2015-president-s-cup.md",
        "2016-regatta.md",
        "2017-regatta.md",
        "2018-heritage-regatta.md",
        "2021-comet-penguin-invitational.md",
        "2021-heritage-regatta.md",
        "2022-comet-penguin-invitational.md",
        "2023-turkey-trot-regatta.md"
    ]
    
    fixed_count = 0
    
    for filename in problematic_files:
        file_path = results_dir / filename
        if not file_path.exists():
            print(f"File not found: {filename}")
            continue
            
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Extract front matter
            if not content.startswith('---'):
                print(f"Skipping {filename}: No front matter")
                continue
            
            parts = content.split('---', 2)
            if len(parts) < 3:
                print(f"Skipping {filename}: Malformed front matter")
                continue
            
            front_matter_text = parts[1]
            content_body = parts[2]
            
            # Parse front matter
            front_matter = yaml.safe_load(front_matter_text) or {}
            
            # Check if this file has the problematic data
            club = front_matter.get('club', '')
            location = front_matter.get('location', '')
            
            # Fix problematic data
            needs_update = False
            
            if club == 'Location:' or club == '':
                front_matter['club'] = ''
                needs_update = True
                print(f"  Fixed club in {filename}")
            
            if location.startswith('[View Results]') or location.startswith('View Results'):
                front_matter['location'] = ''
                needs_update = True
                print(f"  Fixed location in {filename}")
            
            # Update file if needed
            if needs_update:
                new_front_matter = yaml.safe_dump(front_matter, sort_keys=False, allow_unicode=True, width=1200)
                new_content = f"---\n{new_front_matter.strip()}\n---{content_body}"
                
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(new_content)
                
                print(f"Fixed {filename}")
                fixed_count += 1
            else:
                print(f"No fixes needed for {filename}")
                
        except Exception as e:
            print(f"Error processing {filename}: {e}")
            continue
    
    print(f"\nFixed {fixed_count} files")
    return True

def main():
    """Main function."""
    print("Fixing incorrectly updated _results files...")
    if fix_incorrect_updates():
        print("Successfully fixed problematic files!")
    else:
        print("Failed to fix files")

if __name__ == "__main__":
    main()
