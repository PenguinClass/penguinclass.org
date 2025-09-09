#!/usr/bin/env python3
"""
Compare yacht clubs data with champions data to identify mismatches and propose changes.
"""

import yaml
import difflib
from collections import defaultdict

def find_closest_match(target, options, threshold=0.8):
    """Find the closest match in options for target string."""
    matches = difflib.get_close_matches(target, options, n=1, cutoff=threshold)
    return matches[0] if matches else None

def compare_yachtclubs_champions():
    """Compare yacht clubs with champions data and propose changes."""
    
    # Load yacht clubs data
    with open('_data/yachtclubs.yml', 'r') as f:
        yacht_clubs = yaml.safe_load(f)
    
    # Load champions data
    with open('_data/champions.yml', 'r') as f:
        champions = yaml.safe_load(f)
    
    # Create yacht clubs lookup
    yacht_clubs_lookup = {club['name']: club['location'] for club in yacht_clubs}
    yacht_clubs_names = list(yacht_clubs_lookup.keys())
    
    print("=== YACHT CLUBS vs CHAMPIONS COMPARISON ===\n")
    
    # Collect all clubs and locations from champions
    champions_clubs = set()
    champions_locations = set()
    
    for champion in champions:
        club = champion.get('club', '').strip()
        location = champion.get('location', '').strip()
        
        if club:
            champions_clubs.add(club)
        if location:
            champions_locations.add(location)
    
    print("1. CLUBS IN CHAMPIONS BUT NOT IN YACHT CLUBS:")
    print("=" * 50)
    
    missing_clubs = []
    for club in sorted(champions_clubs):
        if club not in yacht_clubs_lookup:
            # Try to find a close match
            closest_match = find_closest_match(club, yacht_clubs_names)
            if closest_match:
                print(f"  '{club}' → closest match: '{closest_match}'")
            else:
                print(f"  '{club}' → NO CLOSE MATCH FOUND")
            missing_clubs.append(club)
    
    if not missing_clubs:
        print("  All clubs in champions are present in yacht clubs!")
    
    print(f"\n2. CLUBS IN YACHT CLUBS BUT NOT IN CHAMPIONS:")
    print("=" * 50)
    
    unused_clubs = []
    for club in sorted(yacht_clubs_names):
        if club not in champions_clubs:
            print(f"  '{club}' (location: {yacht_clubs_lookup[club]})")
            unused_clubs.append(club)
    
    if not unused_clubs:
        print("  All yacht clubs are used in champions!")
    
    print(f"\n3. LOCATION MISMATCHES:")
    print("=" * 50)
    
    location_mismatches = []
    for champion in champions:
        club = champion.get('club', '').strip()
        location = champion.get('location', '').strip()
        year = champion.get('year', '')
        
        if club and location and club in yacht_clubs_lookup:
            expected_location = yacht_clubs_lookup[club]
            if location != expected_location:
                location_mismatches.append({
                    'year': year,
                    'club': club,
                    'champions_location': location,
                    'yachtclubs_location': expected_location
                })
                print(f"  {year}: '{club}'")
                print(f"    Champions: '{location}'")
                print(f"    YachtClubs: '{expected_location}'")
                print()
    
    if not location_mismatches:
        print("  No location mismatches found!")
    
    print(f"\n4. PROPOSED CHANGES TO CHAMPIONS.YML:")
    print("=" * 50)
    
    if location_mismatches:
        print("  # Fix location mismatches:")
        for mismatch in location_mismatches:
            print(f"  # {mismatch['year']}: {mismatch['club']}")
            print(f"  #   Change: '{mismatch['champions_location']}' → '{mismatch['yachtclubs_location']}'")
            print()
    
    if missing_clubs:
        print("  # Add missing clubs to yacht clubs:")
        for club in missing_clubs:
            # Find a location for this club from champions data
            club_locations = []
            for champion in champions:
                if champion.get('club', '').strip() == club:
                    location = champion.get('location', '').strip()
                    if location:
                        club_locations.append(location)
            
            if club_locations:
                # Use most common location
                from collections import Counter
                most_common_location = Counter(club_locations).most_common(1)[0][0]
                print(f"  # - name: {club}")
                print(f"  #   location: {most_common_location}")
                print()
    
    print(f"\n5. SUMMARY:")
    print("=" * 50)
    print(f"  Total yacht clubs: {len(yacht_clubs_names)}")
    print(f"  Total clubs in champions: {len(champions_clubs)}")
    print(f"  Missing clubs: {len(missing_clubs)}")
    print(f"  Unused clubs: {len(unused_clubs)}")
    print(f"  Location mismatches: {len(location_mismatches)}")

if __name__ == "__main__":
    compare_yachtclubs_champions()
