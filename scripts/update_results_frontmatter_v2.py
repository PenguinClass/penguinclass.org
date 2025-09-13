#!/usr/bin/env python3
"""
Update _results collection files with missing front matter data by extracting from content.
Version 2: More careful extraction and better use of yachtclubs.yml data.
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

def get_club_from_filename(filename, yachtclubs):
    """Try to determine club from filename using yachtclubs.yml data."""
    name_lower = filename.lower()
    
    # Map filename patterns to club names
    club_mappings = {
        'tayc': 'Tred Avon Yacht Club',
        'corsica': 'Corsica River Yacht Club', 
        'cambridge': 'Cambridge Yacht Club',
        'beachwood': 'Beachwood Yacht Club',
        'gibson': 'Gibson Island Yacht Squadron',
        'giys': 'Gibson Island Yacht Squadron',
        'miles': 'Miles River Yacht Club',
        'mryc': 'Miles River Yacht Club',
        'potomac': 'Potomac River Sailing Association',
        'prsa': 'Potomac River Sailing Association',
        'oxford': 'Tred Avon Yacht Club',
        'bay-ridge': 'Bay Ridge Yacht Club',
        'baltimore': 'Baltimore Yacht Club',
        'byc': 'Baltimore Yacht Club',
        'annapolis': 'Annapolis Yacht Club',
        'ayc': 'Annapolis Yacht Club',
        'severn': 'Severn Sailing Association',
        'ssa': 'Severn Sailing Association',
        'west-river': 'West River Sailing Club',
        'wrsc': 'West River Sailing Club',
        'island-creek': 'Island Creek Yacht Club',
        'trippe': 'Trippe Creek Penguin Frostbite Regatta',
        'tcpfr': 'Trippe Creek Penguin Frostbite Regatta',
        'lawson': 'Gibson Island Yacht Squadron',
        'admir': 'Admiral Byrd Yacht Club',
        'byrd': 'Admiral Byrd Yacht Club',
    }
    
    for pattern, club_name in club_mappings.items():
        if pattern in name_lower:
            return club_name
    
    return None

def get_location_from_club(club, yachtclubs):
    """Get location from club name using yachtclubs.yml data."""
    if not club or not yachtclubs:
        return None
    
    # Try exact match first
    for yachtclub in yachtclubs:
        if yachtclub.get('name', '').lower() == club.lower():
            return yachtclub.get('location', '')
    
    # Try partial match
    for yachtclub in yachtclubs:
        yachtclub_name = yachtclub.get('name', '').lower()
        if club.lower() in yachtclub_name or yachtclub_name in club.lower():
            return yachtclub.get('location', '')
    
    return None

def extract_club_from_content(content):
    """Extract club name from content - only if there's actual meaningful data."""
    # Look for club patterns with actual content
    club_patterns = [
        r'\*\*Club:\*\*\s*([^\n]+)',
        r'\*\*Venue:\*\*\s*([^\n]+)',
        r'\*\*Host:\*\*\s*([^\n]+)',
    ]
    
    for pattern in club_patterns:
        try:
            match = re.search(pattern, content, re.IGNORECASE)
            if match:
                club = match.group(1).strip()
                # Only return if there's actual content (not empty, not just whitespace, not a label)
                if (club and len(club.strip()) > 3 and 
                    not club.strip().endswith(':') and 
                    not club.strip().startswith('[') and
                    not club.strip().startswith('View Results') and
                    club.strip() != ''):
                    return club.strip()
        except re.error:
            continue
    
    return None

def extract_location_from_content(content):
    """Extract location from content - only if there's actual meaningful data."""
    # Look for location patterns with actual content
    location_patterns = [
        r'\*\*Location:\*\*\s*([^\n]+)',
        r'\*\*City:\*\*\s*([^\n]+)',
        r'\*\*Site:\*\*\s*([^\n]+)',
    ]
    
    for pattern in location_patterns:
        try:
            match = re.search(pattern, content, re.IGNORECASE)
            if match:
                location = match.group(1).strip()
                # Only return if there's actual content (not empty, not just whitespace, not a link)
                if (location and len(location.strip()) > 3 and 
                    not location.strip().endswith(':') and 
                    not location.strip().startswith('[') and
                    not location.strip().startswith('View Results') and
                    location.strip() != ''):
                    return location.strip()
        except re.error:
            continue
    
    return None

def extract_results_url_from_content(content):
    """Extract results URL from content."""
    # Look for "View Results" links
    view_results_patterns = [
        r'\[View Results\]\(([^)]+)\)',
        r'\[Results\]\(([^)]+)\)',
        r'\[Full Results\]\(([^)]+)\)',
    ]
    
    for pattern in view_results_patterns:
        try:
            match = re.search(pattern, content, re.IGNORECASE)
            if match:
                url = match.group(1).strip()
                # Ensure URL has leading slash if it's a relative path
                if url and not url.startswith(('http://', 'https://', '/')):
                    url = '/' + url
                return url
        except re.error:
            continue
    
    return None

def update_result_file(file_path, yachtclubs):
    """Update a single result file with missing front matter data."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Extract front matter
        if not content.startswith('---'):
            print(f"Skipping {file_path.name}: No front matter")
            return False
        
        parts = content.split('---', 2)
        if len(parts) < 3:
            print(f"Skipping {file_path.name}: Malformed front matter")
            return False
        
        front_matter_text = parts[1]
        content_body = parts[2]
        
        # Parse front matter
        front_matter = yaml.safe_load(front_matter_text) or {}
        
        # Check what needs to be updated
        needs_update = False
        updates = {}
        
        # Check club - try content first, then filename
        if not front_matter.get('club'):
            club = extract_club_from_content(content_body)
            if not club:
                # Try to get club from filename
                club = get_club_from_filename(file_path.name, yachtclubs)
            if club:
                updates['club'] = club
                needs_update = True
                print(f"  Found club: {club}")
        
        # Check location - try content first, then club lookup
        if not front_matter.get('location'):
            location = extract_location_from_content(content_body)
            if not location and updates.get('club'):
                # Try to get location from club using yachtclubs.yml
                location = get_location_from_club(updates['club'], yachtclubs)
                if location:
                    print(f"  Found location from yachtclubs: {location}")
            if location:
                updates['location'] = location
                needs_update = True
                print(f"  Found location: {location}")
        
        # Check results_url
        if not front_matter.get('results_url'):
            results_url = extract_results_url_from_content(content_body)
            if results_url:
                updates['results_url'] = results_url
                needs_update = True
                print(f"  Found results_url: {results_url}")
        
        # Update front matter if needed
        if needs_update:
            front_matter.update(updates)
            
            # Rebuild the file
            new_front_matter = yaml.safe_dump(front_matter, sort_keys=False, allow_unicode=True, width=1200)
            
            new_content = f"---\n{new_front_matter.strip()}\n---{content_body}"
            
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(new_content)
            
            print(f"Updated {file_path.name}")
            return True
        else:
            print(f"No updates needed for {file_path.name}")
            return False
            
    except Exception as e:
        print(f"Error processing {file_path.name}: {e}")
        return False

def main():
    """Main function."""
    print("Updating _results collection files with missing front matter data (v2)...")
    
    # Load yacht clubs data
    yachtclubs = load_yachtclubs()
    print(f"Loaded {len(yachtclubs)} yacht clubs for location lookup")
    
    # Process all files in _results directory
    results_dir = Path("_results")
    if not results_dir.exists():
        print("_results directory not found!")
        return
    
    updated_count = 0
    total_count = 0
    
    for file_path in sorted(results_dir.glob("*.md")):
        total_count += 1
        print(f"\nProcessing {file_path.name}...")
        
        if update_result_file(file_path, yachtclubs):
            updated_count += 1
    
    print(f"\nCompleted: Updated {updated_count} out of {total_count} files")

if __name__ == "__main__":
    main()
