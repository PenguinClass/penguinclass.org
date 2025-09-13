#!/usr/bin/env python3
"""
Identify mismatches between _data/champions.yml and _results/*championship.md files.
"""
import os
import yaml
from pathlib import Path

def get_championship_files():
    """Get list of championship files and their years."""
    results_dir = Path("_results")
    championship_files = []
    
    if results_dir.exists():
        for file_path in results_dir.glob("*championship.md"):
            # Extract year from filename
            filename = file_path.name
            year_match = None
            for part in filename.split('-'):
                if part.isdigit() and len(part) == 4:
                    year_match = int(part)
                    break
            
            if year_match:
                championship_files.append({
                    'year': year_match,
                    'filename': filename,
                    'file_path': file_path
                })
    
    return sorted(championship_files, key=lambda x: x['year'])

def get_champions_data():
    """Get champions data from YAML."""
    champions_path = Path("_data/champions.yml")
    if champions_path.exists():
        with open(champions_path, 'r', encoding='utf-8') as f:
            return yaml.safe_load(f) or []
    return []

def main():
    """Identify mismatches."""
    print("Identifying mismatches between _data/champions.yml and _results/*championship.md files...")
    
    # Get data
    championship_files = get_championship_files()
    champions_data = get_champions_data()
    
    print(f"Found {len(championship_files)} championship files")
    print(f"Found {len(champions_data)} champions in YAML")
    
    # Get years from each source
    file_years = set(f['year'] for f in championship_files)
    yaml_years = set(c['year'] for c in champions_data if c.get('year'))
    
    print(f"\nChampionship file years: {sorted(file_years)}")
    print(f"YAML champion years: {sorted(yaml_years)}")
    
    # Find mismatches
    missing_files = yaml_years - file_years
    missing_yaml = file_years - yaml_years
    
    print(f"\n=== MISMATCHES ===")
    
    if missing_files:
        print(f"\nYears in YAML but NO championship file:")
        for year in sorted(missing_files):
            # Find the champion data
            champ = next((c for c in champions_data if c.get('year') == year), None)
            if champ:
                skipper = champ.get('skipper', 'N/A')
                series = champ.get('series', 'N/A')
                print(f"  {year}: {skipper} - {series}")
    
    if missing_yaml:
        print(f"\nYears with championship file but NO YAML entry:")
        for year in sorted(missing_yaml):
            file_info = next((f for f in championship_files if f['year'] == year), None)
            if file_info:
                print(f"  {year}: {file_info['filename']}")
    
    if not missing_files and not missing_yaml:
        print("No mismatches found - all years match!")
    
    # Check for data inconsistencies in matching years
    print(f"\n=== DATA CONSISTENCY CHECK ===")
    matching_years = file_years & yaml_years
    
    for year in sorted(matching_years):
        # Get file data
        file_info = next((f for f in championship_files if f['year'] == year), None)
        champ_data = next((c for c in champions_data if c.get('year') == year), None)
        
        if file_info and champ_data:
            # Read the file to check front matter
            try:
                with open(file_info['file_path'], 'r', encoding='utf-8') as f:
                    content = f.read()
                
                if content.startswith('---'):
                    parts = content.split('---', 2)
                    if len(parts) >= 3:
                        front_matter = yaml.safe_load(parts[1]) or {}
                        
                        # Check for inconsistencies
                        issues = []
                        
                        if front_matter.get('club') != champ_data.get('club'):
                            issues.append(f"club: file='{front_matter.get('club')}' vs yaml='{champ_data.get('club')}'")
                        
                        if front_matter.get('location') != champ_data.get('location'):
                            issues.append(f"location: file='{front_matter.get('location')}' vs yaml='{champ_data.get('location')}'")
                        
                        if front_matter.get('results_url') != champ_data.get('results_url'):
                            issues.append(f"results_url: file='{front_matter.get('results_url')}' vs yaml='{champ_data.get('results_url')}'")
                        
                        if issues:
                            print(f"  {year}: {', '.join(issues)}")
                        
            except Exception as e:
                print(f"  {year}: Error reading file - {e}")

if __name__ == "__main__":
    main()
