#!/usr/bin/env python3
"""
Update _data/champions.yml using front matter data from _results/*championship.md files.
"""
import os
import re
import yaml
from pathlib import Path

def load_existing_champions():
    """Load existing champions.yml data."""
    champions_path = Path("_data/champions.yml")
    if champions_path.exists():
        with open(champions_path, 'r', encoding='utf-8') as f:
            return yaml.safe_load(f) or []
    return []

def process_championship_files():
    """Process all championship files and extract data."""
    championship_data = []
    results_dir = Path("_results")
    
    if not results_dir.exists():
        print("_results directory not found!")
        return championship_data
    
    # Find all championship files
    for file_path in results_dir.glob("*championship.md"):
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Extract front matter
            if content.startswith('---'):
                parts = content.split('---', 2)
                if len(parts) >= 3:
                    front_matter = yaml.safe_load(parts[1])
                else:
                    continue
            else:
                continue
            
            # Extract information
            year = front_matter.get('year', '')
            title = front_matter.get('title', '')
            series = front_matter.get('series', '')
            club = front_matter.get('club', '')
            location = front_matter.get('location', '')
            results_url = front_matter.get('results_url', '')
            
            if not year:
                print(f"Skipping {file_path.name}: No year found")
                continue
            
            # Determine championship type and result_id
            if 'international' in series.lower() or 'international' in title.lower():
                result_id = f"international-{year}"
                championship_type = "International"
            elif 'north american' in series.lower() or 'north american' in title.lower():
                result_id = f"north-american-{year}"
                championship_type = "North American"
            else:
                result_id = f"championship-{year}"
                championship_type = "Championship"
            
            # Extract skipper and crew from title if possible
            skipper = ""
            crew = ""
            
            # Try to extract from title (e.g., "2023 International Championship - John Smith with Jane Doe")
            title_parts = title.split(' - ')
            if len(title_parts) > 1:
                names_part = title_parts[1]
                if ' with ' in names_part:
                    skipper, crew = names_part.split(' with ', 1)
                else:
                    skipper = names_part
            
            championship_data.append({
                "year": int(year),
                "result_id": result_id,
                "skipper": skipper.strip(),
                "crew": crew.strip(),
                "club": club.strip(),
                "location": location.strip(),
                "boat": "",  # Not typically in front matter
                "results_url": results_url.strip(),
                "championship_type": championship_type
            })
            
            print(f"Processed {file_path.name}: {year} {championship_type}")
            
        except Exception as e:
            print(f"Error processing {file_path.name}: {e}")
            continue
    
    return championship_data

def update_champions_yml():
    """Update champions.yml with data from championship files."""
    print("Updating _data/champions.yml from championship files...")
    
    # Load existing champions data
    existing_champions = load_existing_champions()
    print(f"Loaded {len(existing_champions)} existing champions")
    
    # Process championship files
    championship_data = process_championship_files()
    print(f"Found {len(championship_data)} championship files")
    
    # Create a mapping of existing champions by result_id
    existing_by_result_id = {}
    for champ in existing_champions:
        result_id = champ.get('result_id', '')
        if result_id:
            existing_by_result_id[result_id] = champ
    
    # Update or add champions
    updated_count = 0
    added_count = 0
    
    for champ_data in championship_data:
        result_id = champ_data['result_id']
        
        if result_id in existing_by_result_id:
            # Update existing champion
            existing_champ = existing_by_result_id[result_id]
            
            # Update only club, location, and results_url if they're empty in existing data
            updated = False
            if not existing_champ.get('club') and champ_data['club']:
                existing_champ['club'] = champ_data['club']
                updated = True
            if not existing_champ.get('location') and champ_data['location']:
                existing_champ['location'] = champ_data['location']
                updated = True
            if not existing_champ.get('results_url') and champ_data['results_url']:
                existing_champ['results_url'] = champ_data['results_url']
                updated = True
            
            if updated:
                updated_count += 1
                print(f"Updated {result_id}")
        else:
            # Skip adding new champions - only update existing ones
            print(f"Skipped {result_id} - not in existing champions data")
    
    # Sort by year (most recent first)
    existing_champions.sort(key=lambda x: x.get('year', 0), reverse=True)
    
    # Write back to file
    with open('_data/champions.yml', 'w', encoding='utf-8') as f:
        yaml.safe_dump(existing_champions, f, sort_keys=False, allow_unicode=True, width=1200)
    
    print(f"\n=== SUMMARY ===")
    print(f"Total champions: {len(existing_champions)}")
    print(f"Updated: {updated_count}")
    print(f"Updated _data/champions.yml (only club, location, and results_url fields)")

def main():
    """Main function."""
    update_champions_yml()

if __name__ == "__main__":
    main()
