#!/usr/bin/env python3
"""
Align champions data with yacht clubs data by fixing mismatches and standardizing names.
"""

import yaml
import json

def align_champions_with_yachtclubs():
    """Align champions data with yacht clubs data."""
    
    with open('_data/champions.yml', 'r') as f:
        champions = yaml.safe_load(f)
    
    with open('_data/yachtclubs.yml', 'r') as f:
        yacht_clubs = yaml.safe_load(f)
    
    # Create yacht clubs lookup
    yacht_clubs_lookup = {club['name']: club['location'] for club in yacht_clubs}
    
    fixes_applied = 0
    
    print("Applying fixes to align champions with yacht clubs...")
    
    for champion in champions:
        club = champion.get('club', '').strip()
        location = champion.get('location', '').strip()
        year = champion.get('year', '')
        
        # Fix club name mismatches
        if club == 'Sheridan Shore Yacht Club':
            champion['club'] = 'Sheridan Shores Yacht Club'
            champion['location'] = 'Wilmette, IL, U.S.A.'
            fixes_applied += 1
            print(f"  {year}: Fixed Sheridan Shore → Sheridan Shores Yacht Club")
        
        elif club == 'Toms RiverYacht Club':
            champion['club'] = 'Toms River Yacht Club'
            champion['location'] = 'Toms River, NJ, U.S.A.'
            fixes_applied += 1
            print(f"  {year}: Fixed Toms RiverYacht Club → Toms River Yacht Club")
        
        elif club == 'Corsica River Yacht Club, Centreville':
            champion['club'] = 'Corsica River Yacht Club'
            champion['location'] = 'Centreville, MD, U.S.A.'
            fixes_applied += 1
            print(f"  {year}: Fixed Corsica River Yacht Club, Centreville → Corsica River Yacht Club")
        
        elif club == 'Miles River Yacht Club,St.Michaels':
            champion['club'] = 'Miles River Yacht Club'
            champion['location'] = 'St. Michaels, MD, U.S.A.'
            fixes_applied += 1
            print(f"  {year}: Fixed Miles River Yacht Club,St.Michaels → Miles River Yacht Club")
        
        # Fix location mismatches for existing clubs
        elif club == 'Sayville Yacht Club' and location == 'NY, U.S.A.':
            champion['location'] = 'Blue Point, NY, U.S.A.'
            fixes_applied += 1
            print(f"  {year}: Fixed Sayville Yacht Club location → Blue Point, NY, U.S.A.")
        
        # Update any other locations to match yacht clubs data
        elif club in yacht_clubs_lookup and location != yacht_clubs_lookup[club]:
            expected_location = yacht_clubs_lookup[club]
            champion['location'] = expected_location
            fixes_applied += 1
            print(f"  {year}: Updated {club} location to match yacht clubs: {expected_location}")
    
    print(f"\nApplied {fixes_applied} alignment fixes")
    
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
    align_champions_with_yachtclubs()
