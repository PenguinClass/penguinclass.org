#!/usr/bin/env python3
"""
Fix the bad data that was incorrectly extracted.
"""
import yaml
from pathlib import Path

def fix_bad_data():
    """Fix files with bad club/location data."""
    
    results_dir = Path("_results")
    if not results_dir.exists():
        print("_results directory not found!")
        return False
    
    # Files that likely have bad data
    files_to_check = [
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
    
    for filename in files_to_check:
        file_path = results_dir / filename
        if not file_path.exists():
            continue
            
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Extract front matter
            if not content.startswith('---'):
                continue
            
            parts = content.split('---', 2)
            if len(parts) < 3:
                continue
            
            front_matter_text = parts[1]
            content_body = parts[2]
            
            # Parse front matter
            front_matter = yaml.safe_load(front_matter_text) or {}
            
            # Check if this file has bad data
            club = front_matter.get('club', '')
            location = front_matter.get('location', '')
            
            # Fix bad data
            needs_update = False
            
            if club == '**Location:**' or club == 'Location:':
                front_matter['club'] = ''
                needs_update = True
                print(f"Fixed bad club data in {filename}")
            
            if location == '**Location:**' or location == 'Location:':
                front_matter['location'] = ''
                needs_update = True
                print(f"Fixed bad location data in {filename}")
            
            # Update file if needed
            if needs_update:
                new_front_matter = yaml.safe_dump(front_matter, sort_keys=False, allow_unicode=True, width=1200)
                new_content = f"---\n{new_front_matter.strip()}\n---{content_body}"
                
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(new_content)
                
                print(f"Fixed {filename}")
                fixed_count += 1
                
        except Exception as e:
            print(f"Error processing {filename}: {e}")
            continue
    
    print(f"\nFixed {fixed_count} files")
    return True

if __name__ == "__main__":
    print("Fixing bad data in _results files...")
    fix_bad_data()
    print("Done!")
