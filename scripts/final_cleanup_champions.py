#!/usr/bin/env python3
"""
Final cleanup of champions.yml to properly separate club names from locations
and apply specific geographic corrections.
"""

import yaml
import re

def clean_club_and_location(club, location):
    """Clean and separate club names from locations."""
    
    # Specific corrections first
    if club == "SSA" and location == "Annapolis MD":
        return "Severn Sailing Association", "Annapolis, MD"
    
    if club == "Cambridge, MD":
        return "Cambridge Yacht Club", "Cambridge, MD"
    
    # Handle 1976 Argentina case
    if "1976" in str(club) or "Olivos" in str(club):
        return "Yacht Club Olivos", "Buenos Aires, Argentina"
    
    # Handle 1991 Brazil case  
    if "1991" in str(club) or "Rio de Janeiro" in str(club):
        return "Rio de Janeiro Yacht Club", "Rio de Janeiro, Brazil"
    
    # Handle 1997 Brazil case
    if "1997" in str(club) or "Rio Grande" in str(club):
        return "Clube Naval", "Rio de Janeiro, Brazil"
    
    # Expand YC to Yacht Club
    if club and "YC" in club and "Yacht Club" not in club:
        club = club.replace("YC", "Yacht Club")
    
    # If club is just a city/state, move it to location
    if club and not any(word in club.lower() for word in ['club', 'association', 'sailing', 'yacht', 'society']):
        if location:
            location = f"{club}, {location}"
        else:
            location = club
        club = ""
    
    # If location contains club-like terms, move them to club
    if location:
        location_parts = location.split(',')
        club_parts = []
        location_parts_clean = []
        
        for part in location_parts:
            part = part.strip()
            if any(word in part.lower() for word in ['club', 'association', 'sailing', 'yacht', 'society']):
                club_parts.append(part)
            else:
                location_parts_clean.append(part)
        
        if club_parts:
            if club:
                club = f"{', '.join(club_parts)}, {club}"
            else:
                club = ', '.join(club_parts)
        
        location = ', '.join(location_parts_clean) if location_parts_clean else ""
    
    # Clean up empty strings
    club = club.strip() if club else ""
    location = location.strip() if location else ""
    
    return club, location

def main():
    print("Loading champions data...")
    
    with open('_data/champions.yml', 'r') as f:
        champions = yaml.safe_load(f)
    
    print(f"Processing {len(champions)} champion entries...")
    
    cleaned_count = 0
    
    for champion in champions:
        original_club = champion.get('club', '')
        original_location = champion.get('location', '')
        
        new_club, new_location = clean_club_and_location(original_club, original_location)
        
        if new_club != original_club or new_location != original_location:
            champion['club'] = new_club
            champion['location'] = new_location
            cleaned_count += 1
            print(f"  {champion.get('year', 'Unknown')}: '{original_club}' + '{original_location}' → '{new_club}' + '{new_location}'")
    
    print(f"\nCleaned {cleaned_count} entries")
    
    # Write cleaned data
    with open('_data/champions.yml', 'w') as f:
        yaml.dump(champions, f, default_flow_style=False, sort_keys=False)
    
    print("Updated _data/champions.yml")
    
    # Regenerate JSON
    import json
    with open('assets/data/champions.json', 'w') as f:
        json.dump(champions, f, ensure_ascii=False, indent=2)
    
    print("Regenerated assets/data/champions.json")
    print("Done!")

if __name__ == "__main__":
    main()
