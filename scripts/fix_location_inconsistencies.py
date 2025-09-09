#!/usr/bin/env python3
"""
Fix minor location inconsistencies in champions.yml to match yacht clubs database.
"""

import yaml
import json

def fix_location_inconsistencies():
    """Fix location inconsistencies to match yacht clubs database."""
    
    with open('_data/champions.yml', 'r') as f:
        champions = yaml.safe_load(f)
    
    with open('_data/yachtclubs.yml', 'r') as f:
        yacht_clubs = yaml.safe_load(f)
    
    # Create lookup for expected locations
    club_lookup = {club['name']: club['location'] for club in yacht_clubs}
    
    fixes_applied = 0
    
    for champion in champions:
        club = champion.get('club', '').strip()
        location = champion.get('location', '').strip()
        
        if club and location and club in club_lookup:
            expected_location = club_lookup[club]
            if location != expected_location:
                champion['location'] = expected_location
                fixes_applied += 1
                print(f"  {champion.get('year', 'Unknown')}: Fixed {club} location to '{expected_location}'")
    
    print(f"\nApplied {fixes_applied} location consistency fixes")
    
    # Write updated champions data
    with open('_data/champions.yml', 'w') as f:
        yaml.dump(champions, f, default_flow_style=False, sort_keys=False)
    
    print("Updated _data/champions.yml")
    
    # Regenerate JSON
    with open('assets/data/champions.json', 'w') as f:
        json.dump(champions, f, ensure_ascii=False, indent=2)
    
    print("Regenerated assets/data/champions.json")
    print("Done!")

if __name__ == "__main__":
    fix_location_inconsistencies()
