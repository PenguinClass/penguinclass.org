#!/usr/bin/env python3
"""
Comprehensive cleanup of champions.yml data according to user specifications.
"""

import yaml
import json
import re
from collections import defaultdict

def clean_whitespace(text):
    """Replace \n and multiple whitespace with single space."""
    if not text:
        return ""
    return re.sub(r'\s+', ' ', str(text)).strip()

def fix_name_spacing(name):
    """Fix first and last name spacing, handle special cases like MacCausland."""
    if not name:
        return ""
    
    name = clean_whitespace(name)
    
    # Special case: MacCausland should not have spacing
    name = name.replace('Mac Causland', 'MacCausland')
    
    # Add space between first and last names if missing
    # Look for patterns like "JohnSmith" or "MaryJane" and add space
    name = re.sub(r'([a-z])([A-Z])', r'\1 \2', name)
    
    return name

def separate_skipper_crew(skipper, crew):
    """Separate skipper and crew that use comma or slash as separator."""
    def split_person(person_str):
        if not person_str:
            return ""
        
        # Split on comma or slash
        parts = re.split(r'[,/]', person_str)
        if len(parts) > 1:
            # Take the first part as the person
            return clean_whitespace(parts[0])
        return clean_whitespace(person_str)
    
    return split_person(skipper), split_person(crew)

def infer_missing_last_names(skipper, crew):
    """If either skipper or crew is lacking a last name, use the other's last name."""
    if not skipper or not crew:
        return skipper, crew
    
    skipper_parts = skipper.split()
    crew_parts = crew.split()
    
    # If skipper has only first name and crew has last name
    if len(skipper_parts) == 1 and len(crew_parts) > 1:
        skipper = f"{skipper_parts[0]} {crew_parts[-1]}"
    
    # If crew has only first name and skipper has last name
    elif len(crew_parts) == 1 and len(skipper_parts) > 1:
        crew = f"{crew_parts[0]} {skipper_parts[-1]}"
    
    return skipper, crew

def fix_yacht_club_spacing(club):
    """Separate YachtClub into Yacht Club."""
    if not club:
        return ""
    
    club = club.replace('YachtClub', 'Yacht Club')
    club = club.replace('YACHTCLUB', 'YACHT CLUB')
    return club

def augment_location(location):
    """Augment location data with proper formatting and country."""
    if not location:
        return ""
    
    location = clean_whitespace(location)
    
    # Add country if missing
    if location and not any(country in location.upper() for country in ['USA', 'U.S.A.', 'UNITED STATES', 'CANADA', 'BRAZIL', 'ARGENTINA']):
        # If it's a US state, add U.S.A.
        us_states = ['MD', 'VA', 'NY', 'NJ', 'IL', 'CA', 'MI', 'LA', 'CO', 'MS', 'TX', 'FL', 'CT', 'MA', 'RI', 'NC', 'SC', 'GA', 'AL', 'TN', 'KY', 'OH', 'IN', 'WI', 'MN', 'IA', 'MO', 'AR', 'OK', 'KS', 'NE', 'ND', 'SD', 'MT', 'WY', 'ID', 'UT', 'AZ', 'NM', 'NV', 'WA', 'OR', 'AK', 'HI']
        
        if any(state in location.upper() for state in us_states):
            location = f"{location}, U.S.A."
        elif 'Canada' in location or any(prov in location for prov in ['ON', 'QC', 'BC', 'AB', 'MB', 'SK', 'NS', 'NB', 'NL', 'PE', 'YT', 'NT', 'NU']):
            location = f"{location}, Canada"
        elif 'Brazil' in location or any(city in location for city in ['Rio de Janeiro', 'São Paulo', 'Brasília']):
            location = f"{location}, Brazil"
        elif 'Argentina' in location or 'Buenos Aires' in location:
            location = f"{location}, Argentina"
    
    # Fix comma spacing
    location = re.sub(r'\s*,\s*', ', ', location)
    
    return location

def build_yacht_clubs_data(champions):
    """Build yacht clubs data from existing champions data."""
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
    
    return yacht_clubs

def apply_specific_fixes(champion):
    """Apply specific fixes mentioned by the user."""
    year = champion.get('year', '')
    
    # Remove 1941 north american entry
    if year == 1941 and champion.get('result_id', '').startswith('north'):
        return None
    
    # Fix 1961 international
    if year == 1961 and champion.get('result_id', '').startswith('intl'):
        champion['club'] = 'Crescent Sail Yacht Club'
        champion['location'] = 'Grosse Pointe, Michigan, U.S.A.'
    
    # Fix 1982 international
    if year == 1982 and champion.get('result_id', '').startswith('intl'):
        champion['club'] = 'Yacht Club Paulista'
    
    # Fix 1991 north american
    if year == 1991 and champion.get('result_id', '').startswith('north'):
        champion['location'] = 'Seaside Park, Seaside, NJ, U.S.A.'
    
    # Fix 2003 international
    if year == 2003 and champion.get('result_id', '').startswith('intl'):
        champion['club'] = 'SHERIDAN SHORES YACHT CLUB'
        champion['location'] = 'Wilmette, IL, U.S.A.'
    
    return champion

def add_suspended_entries(champions):
    """Add suspended entries for 1942-1944 and 2020."""
    suspended_entries = [
        {
            'year': 1942,
            'result_id': 'intl-1942',
            'series': 'International',
            'skipper': 'Suspended for WW II',
            'crew': '',
            'club': '',
            'location': '',
            'boat': '',
            'results_url': 'archive/legacy-website/1942.pdf'
        },
        {
            'year': 1943,
            'result_id': 'intl-1943',
            'series': 'International',
            'skipper': 'Suspended for WW II',
            'crew': '',
            'club': '',
            'location': '',
            'boat': '',
            'results_url': 'archive/legacy-website/1942.pdf'
        },
        {
            'year': 1944,
            'result_id': 'intl-1944',
            'series': 'International',
            'skipper': 'Suspended for WW II',
            'crew': '',
            'club': '',
            'location': '',
            'boat': '',
            'results_url': 'archive/legacy-website/1942.pdf'
        },
        {
            'year': 2020,
            'result_id': 'intl-2020',
            'series': 'International',
            'skipper': 'Suspended for COVID-19',
            'crew': '',
            'club': '',
            'location': '',
            'boat': '',
            'results_url': ''
        }
    ]
    
    # Add suspended entries
    for entry in suspended_entries:
        champions.append(entry)
    
    return champions

def populate_missing_data(champions, yacht_clubs):
    """Populate missing club or location data using yacht_clubs data."""
    club_lookup = {club['name']: club['location'] for club in yacht_clubs}
    location_lookup = defaultdict(list)
    for club in yacht_clubs:
        location_lookup[club['location']].append(club['name'])
    
    for champion in champions:
        club = champion.get('club', '').strip()
        location = champion.get('location', '').strip()
        
        # If has club but no location, use club's location
        if club and not location and club in club_lookup:
            champion['location'] = club_lookup[club]
        
        # If has location but no club, try to find matching club
        elif location and not club and location in location_lookup:
            # Use the first matching club
            champion['club'] = location_lookup[location][0]

def main():
    print("Starting comprehensive champions cleanup...")
    
    # Load champions data
    with open('_data/champions.yml', 'r') as f:
        champions = yaml.safe_load(f)
    
    print(f"Processing {len(champions)} champion entries...")
    
    # Build yacht clubs data first
    print("Building yacht clubs data...")
    yacht_clubs = build_yacht_clubs_data(champions)
    
    # Clean up each champion entry
    cleaned_champions = []
    fixes_applied = 0
    
    for champion in champions:
        # Apply specific fixes first
        champion = apply_specific_fixes(champion)
        if champion is None:  # Entry was removed
            continue
        
        # Clean whitespace
        champion['skipper'] = clean_whitespace(champion.get('skipper', ''))
        champion['crew'] = clean_whitespace(champion.get('crew', ''))
        champion['club'] = clean_whitespace(champion.get('club', ''))
        champion['location'] = clean_whitespace(champion.get('location', ''))
        
        # Fix name spacing
        champion['skipper'] = fix_name_spacing(champion['skipper'])
        champion['crew'] = fix_name_spacing(champion['crew'])
        
        # Separate skipper and crew
        champion['skipper'], champion['crew'] = separate_skipper_crew(
            champion['skipper'], champion['crew']
        )
        
        # Infer missing last names
        champion['skipper'], champion['crew'] = infer_missing_last_names(
            champion['skipper'], champion['crew']
        )
        
        # Fix yacht club spacing
        champion['club'] = fix_yacht_club_spacing(champion['club'])
        
        # Augment location
        champion['location'] = augment_location(champion['location'])
        
        cleaned_champions.append(champion)
        fixes_applied += 1
    
    # Add suspended entries
    print("Adding suspended entries...")
    cleaned_champions = add_suspended_entries(cleaned_champions)
    
    # Populate missing data using yacht clubs
    print("Populating missing data...")
    populate_missing_data(cleaned_champions, yacht_clubs)
    
    # Sort by year (descending)
    cleaned_champions.sort(key=lambda x: x.get('year', 0), reverse=True)
    
    print(f"Cleaned {fixes_applied} entries, added suspended entries")
    
    # Write cleaned champions data
    with open('_data/champions.yml', 'w') as f:
        yaml.dump(cleaned_champions, f, default_flow_style=False, sort_keys=False)
    
    print("Updated _data/champions.yml")
    
    # Write yacht clubs data
    with open('_data/yachtclubs.yml', 'w') as f:
        yaml.dump(yacht_clubs, f, default_flow_style=False, sort_keys=False)
    
    print("Created _data/yachtclubs.yml")
    
    # Regenerate JSON
    with open('assets/data/champions.json', 'w') as f:
        json.dump(cleaned_champions, f, ensure_ascii=False, indent=2)
    
    print("Regenerated assets/data/champions.json")
    print("Done!")

if __name__ == "__main__":
    main()
