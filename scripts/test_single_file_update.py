#!/usr/bin/env python3
"""
Test updating a single _results file to debug the approach.
"""
import os
import re
import yaml
from pathlib import Path

def load_yachtclubs():
    """Load yacht clubs data for location lookup."""
    yachtclubs_path = Path("_data/yachtclubs.yml")
    if yachtclubs_path.exists():
        with open(yachtclubs_path, 'r', encoding='utf-8') as f:
            return yaml.safe_load(f) or []
    return []

def get_club_from_filename(filename):
    """Try to determine club from filename."""
    name_lower = filename.lower()
    
    # Map filename patterns to club names
    if 'tayc' in name_lower:
        return 'Tred Avon Yacht Club'
    elif 'corsica' in name_lower:
        return 'Corsica River Yacht Club'
    elif 'cambridge' in name_lower:
        return 'Cambridge Yacht Club'
    elif 'beachwood' in name_lower:
        return 'Beachwood Yacht Club'
    elif 'gibson' in name_lower or 'giys' in name_lower:
        return 'Gibson Island Yacht Squadron'
    elif 'miles' in name_lower or 'mryc' in name_lower:
        return 'Miles River Yacht Club'
    elif 'potomac' in name_lower or 'prsa' in name_lower:
        return 'Potomac River Sailing Association'
    elif 'oxford' in name_lower:
        return 'Tred Avon Yacht Club'
    elif 'bay-ridge' in name_lower:
        return 'Bay Ridge Yacht Club'
    elif 'baltimore' in name_lower or 'byc' in name_lower:
        return 'Baltimore Yacht Club'
    elif 'annapolis' in name_lower or 'ayc' in name_lower:
        return 'Annapolis Yacht Club'
    elif 'severn' in name_lower or 'ssa' in name_lower:
        return 'Severn Sailing Association'
    elif 'west-river' in name_lower or 'wrsc' in name_lower:
        return 'West River Sailing Club'
    elif 'island-creek' in name_lower:
        return 'Island Creek Yacht Club'
    elif 'trippe' in name_lower or 'tcpfr' in name_lower:
        return 'Trippe Creek Penguin Frostbite Regatta'
    elif 'lawson' in name_lower:
        return 'Gibson Island Yacht Squadron'
    elif 'admir' in name_lower or 'byrd' in name_lower:
        return 'Admiral Byrd Yacht Club'
    
    return None

def get_location_from_club(club, yachtclubs):
    """Get location from club name using yachtclubs.yml data."""
    if not club or not yachtclubs:
        return None
    
    for yachtclub in yachtclubs:
        if yachtclub.get('name', '').lower() == club.lower():
            return yachtclub.get('location', '')
    
    return None

def extract_results_url_from_content(content):
    """Extract results URL from content."""
    # Look for "View Results" links
    patterns = [
        r'\[View Results\]\(([^)]+)\)',
        r'\[Results\]\(([^)]+)\)',
        r'\[Full Results\]\(([^)]+)\)',
    ]
    
    for pattern in patterns:
        try:
            match = re.search(pattern, content, re.IGNORECASE)
            if match:
                url = match.group(1).strip()
                if url and not url.startswith(('http://', 'https://', '/')):
                    url = '/' + url
                return url
        except:
            continue
    
    return None

def test_file_update(filename):
    """Test updating a single file."""
    print(f"Testing update for {filename}")
    
    # Load yacht clubs
    yachtclubs = load_yachtclubs()
    print(f"Loaded {len(yachtclubs)} yacht clubs")
    
    file_path = Path("_results") / filename
    if not file_path.exists():
        print(f"File not found: {filename}")
        return
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Extract front matter
        if not content.startswith('---'):
            print("No front matter found")
            return
        
        parts = content.split('---', 2)
        if len(parts) < 3:
            print("Malformed front matter")
            return
        
        front_matter_text = parts[1]
        content_body = parts[2]
        
        # Parse front matter
        front_matter = yaml.safe_load(front_matter_text) or {}
        
        print(f"Current front matter:")
        print(f"  club: '{front_matter.get('club', '')}'")
        print(f"  location: '{front_matter.get('location', '')}'")
        print(f"  results_url: '{front_matter.get('results_url', '')}'")
        
        # Check what needs updating
        updates = {}
        
        # Check club
        if not front_matter.get('club'):
            club = get_club_from_filename(filename)
            if club:
                updates['club'] = club
                print(f"  Would add club: {club}")
        
        # Check location
        if not front_matter.get('location') and updates.get('club'):
            location = get_location_from_club(updates['club'], yachtclubs)
            if location:
                updates['location'] = location
                print(f"  Would add location: {location}")
        
        # Check results_url
        if not front_matter.get('results_url'):
            results_url = extract_results_url_from_content(content_body)
            if results_url:
                updates['results_url'] = results_url
                print(f"  Would add results_url: {results_url}")
        
        if updates:
            print(f"Would update with: {updates}")
        else:
            print("No updates needed")
            
    except Exception as e:
        print(f"Error: {e}")

def main():
    """Test with a few specific files."""
    test_files = [
        "2013-heritage-regatta.md",
        "2013-icpfr-regatta.md",
        "2015-president-s-cup.md"
    ]
    
    for filename in test_files:
        test_file_update(filename)
        print("-" * 50)

if __name__ == "__main__":
    main()
