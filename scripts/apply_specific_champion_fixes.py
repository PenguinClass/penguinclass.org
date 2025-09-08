#!/usr/bin/env python3
"""
Apply specific fixes to champions.yml and update yacht clubs database.
"""

import yaml
import json
from collections import defaultdict

def apply_specific_fixes():
    """Apply the specific fixes mentioned by the user."""
    
    with open('_data/champions.yml', 'r') as f:
        champions = yaml.safe_load(f)
    
    fixes_applied = 0
    
    for champion in champions:
        year = champion.get('year', '')
        result_id = champion.get('result_id', '')
        
        # Fix result_id format from intl-YYYY to international-YYYY
        if result_id.startswith('intl-'):
            champion['result_id'] = result_id.replace('intl-', 'international-')
            fixes_applied += 1
            print(f"  {year}: Fixed result_id format")
        
        # Fix 1948, 1950, 1958 internationals
        if year in [1948, 1950, 1958] and (result_id.startswith('intl') or result_id.startswith('international')):
            champion['club'] = 'Mantoloking Yacht Club'
            champion['location'] = 'Mantoloking, NJ, U.S.A.'
            fixes_applied += 1
            print(f"  {year}: Fixed international club and location")
        
        # Fix 1951 international
        elif year == 1951 and (result_id.startswith('intl') or result_id.startswith('international')):
            champion['club'] = 'San Diego Yacht Club'
            champion['location'] = 'San Diego, CA, U.S.A.'
            fixes_applied += 1
            print(f"  {year}: Fixed 1951 international club and location")
        
        # Fix 1952, 1956 internationals
        elif year in [1952, 1956] and (result_id.startswith('intl') or result_id.startswith('international')):
            champion['club'] = 'Biloxi Yacht Club'
            champion['location'] = 'Biloxi, MS, U.S.A.'
            fixes_applied += 1
            print(f"  {year}: Fixed international club and location")
        
        # Fix 1966 international
        elif year == 1966 and (result_id.startswith('intl') or result_id.startswith('international')):
            champion['club'] = 'Little Egg Harbor Yacht Club'
            champion['location'] = 'Beach Haven, N. J., U.S.A.'
            fixes_applied += 1
            print(f"  {year}: Fixed 1966 international club and location")
        
        # Fix 1969 and 2003 internationals
        elif year in [1969, 2003] and (result_id.startswith('intl') or result_id.startswith('international')):
            champion['club'] = 'Sheridan Shores Yacht Club'
            champion['location'] = 'Wilmette, IL, U.S.A.'
            fixes_applied += 1
            print(f"  {year}: Fixed international club and location")
        
        # Fix 1996 international
        elif year == 1996 and (result_id.startswith('intl') or result_id.startswith('international')):
            champion['club'] = 'Columbia Yacht Club'
            champion['location'] = 'Chicago, IL, U.S.A.'
            fixes_applied += 1
            print(f"  {year}: Fixed 1996 international club and location")
        
        # Fix 1995, 1999 internationals
        elif year in [1995, 1999] and (result_id.startswith('intl') or result_id.startswith('international')):
            champion['club'] = 'Centerport Yacht Club'
            champion['location'] = 'Centerport, NY, U.S.A.'
            fixes_applied += 1
            print(f"  {year}: Fixed international club and location")
        
        # Fix 1976 north american
        elif year == 1976 and result_id.startswith('north'):
            champion['club'] = 'Toms River Yacht Club'
            fixes_applied += 1
            print(f"  {year}: Fixed 1976 north american club")
        
        # Fix 1979 north american
        elif year == 1979 and result_id.startswith('north'):
            champion['club'] = 'Bay Head Yacht Club'
            fixes_applied += 1
            print(f"  {year}: Fixed 1979 north american club")
        
        # Fix 1991 north american (there might be multiple entries)
        elif year == 1991 and result_id.startswith('north'):
            if 'Seaside' in champion.get('location', ''):
                champion['club'] = 'Seaside Park Yacht Club'
                champion['location'] = 'Seaside, NJ, U.S.A.'
                fixes_applied += 1
                print(f"  {year}: Fixed 1991 north american (Seaside) club and location")
            elif 'Corsica' in champion.get('club', '') or 'Centreville' in champion.get('location', ''):
                champion['club'] = 'Corsica River Yacht Club'
                champion['location'] = 'Centreville, MD, U.S.A.'
                fixes_applied += 1
                print(f"  {year}: Fixed 1991 north american (Corsica) club and location")
    
    print(f"\nApplied {fixes_applied} specific fixes")
    
    # Write updated champions data
    with open('_data/champions.yml', 'w') as f:
        yaml.dump(champions, f, default_flow_style=False, sort_keys=False)
    
    print("Updated _data/champions.yml")
    
    return champions

def build_updated_yacht_clubs(champions):
    """Build updated yacht clubs data from all champions data."""
    
    print("\nBuilding updated yacht clubs database...")
    
    club_locations = defaultdict(list)
    
    for champion in champions:
        club = champion.get('club', '').strip()
        location = champion.get('location', '').strip()
        
        if club and location:
            club_locations[club].append(location)
    
    # Find most common location for each club
    yacht_clubs = []
    for club, locations in club_locations.items():
        if locations:
            # Count occurrences of each location
            location_counts = defaultdict(int)
            for loc in locations:
                location_counts[loc] += 1
            
            # Get most common location
            most_common_location = max(location_counts.items(), key=lambda x: x[1])[0]
            
            yacht_clubs.append({
                'name': club,
                'location': most_common_location
            })
    
    # Sort by club name
    yacht_clubs.sort(key=lambda x: x['name'])
    
    print(f"Created yacht clubs database with {len(yacht_clubs)} clubs")
    
    # Write yacht clubs data
    with open('_data/yachtclubs.yml', 'w') as f:
        yaml.dump(yacht_clubs, f, default_flow_style=False, sort_keys=False)
    
    print("Updated _data/yachtclubs.yml")
    
    return yacht_clubs

def verify_data_consistency(champions, yacht_clubs):
    """Verify that all clubs and locations are consistent."""
    
    print("\nVerifying data consistency...")
    
    club_lookup = {club['name']: club['location'] for club in yacht_clubs}
    issues_found = 0
    
    for champion in champions:
        club = champion.get('club', '').strip()
        location = champion.get('location', '').strip()
        
        if club and location:
            # Check if this club-location combination exists in yacht clubs
            if club in club_lookup:
                expected_location = club_lookup[club]
                if location != expected_location:
                    print(f"  Inconsistency: {club} has location '{location}' but yacht clubs has '{expected_location}'")
                    issues_found += 1
    
    if issues_found == 0:
        print("  No inconsistencies found - data is consistent!")
    else:
        print(f"  Found {issues_found} inconsistencies")

def main():
    print("Applying specific champion fixes and updating yacht clubs database...")
    
    # Apply specific fixes
    champions = apply_specific_fixes()
    
    # Build updated yacht clubs database
    yacht_clubs = build_updated_yacht_clubs(champions)
    
    # Verify data consistency
    verify_data_consistency(champions, yacht_clubs)
    
    # Regenerate JSON
    with open('assets/data/champions.json', 'w') as f:
        json.dump(champions, f, ensure_ascii=False, indent=2)
    
    print("Regenerated assets/data/champions.json")
    print("Done!")

if __name__ == "__main__":
    main()
