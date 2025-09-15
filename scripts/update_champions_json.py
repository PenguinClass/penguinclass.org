#!/usr/bin/env python3
"""
Update assets/data/champions.json from _data/champions.yml.
"""
import json
import yaml
from pathlib import Path

def main():
    """Update champions.json from champions.yml."""
    print("Updating assets/data/champions.json from _data/champions.yml...")
    
    # Load champions.yml
    champions_yml_path = Path("_data/champions.yml")
    if not champions_yml_path.exists():
        print("_data/champions.yml not found!")
        return
    
    with open(champions_yml_path, 'r', encoding='utf-8') as f:
        champions = yaml.safe_load(f) or []
    
    print(f"Loaded {len(champions)} champions from _data/champions.yml")
    
    # Create output directory if it doesn't exist
    output_dir = Path("assets/data")
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Write to JSON file
    output_file = output_dir / "champions.json"
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(champions, f, ensure_ascii=False, indent=2)
    
    print(f"Created {output_file}")
    
    # Show some examples
    print("\nSample champions:")
    for champ in champions[:5]:
        year = champ.get('year', 'N/A')
        skipper = champ.get('skipper', 'N/A')
        club = champ.get('club', 'N/A')
        print(f"  {year} - {skipper} - {club}")
    
    # Show year range
    years = [c['year'] for c in champions if c.get('year')]
    if years:
        print(f"\nYear range: {min(years)} - {max(years)}")
    
    print("Done!")

if __name__ == "__main__":
    main()
