#!/usr/bin/env python3
"""
Analyze _results files for mismatches between front matter and content.
Outputs a list of files that have missing or mismatched club/location data.
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
    
    for yachtclub in yachtclubs:
        if yachtclub.get('name', '').lower() == club.lower():
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

def analyze_file(file_path, yachtclubs):
    """Analyze a single file for mismatches."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Extract front matter
        if not content.startswith('---'):
            return None
        
        parts = content.split('---', 2)
        if len(parts) < 3:
            return None
        
        front_matter_text = parts[1]
        content_body = parts[2]
        
        # Parse front matter
        front_matter = yaml.safe_load(front_matter_text) or {}
        
        # Get current values
        current_club = front_matter.get('club', '')
        current_location = front_matter.get('location', '')
        current_results_url = front_matter.get('results_url', '')
        
        # Extract potential values from content
        content_club = extract_club_from_content(content_body)
        content_location = extract_location_from_content(content_body)
        content_results_url = extract_results_url_from_content(content_body)
        
        # Try to get club from filename if not in content
        filename_club = get_club_from_filename(file_path.name)
        if not content_club and filename_club:
            content_club = filename_club
        
        # Try to get location from club if not in content
        if not content_location and content_club:
            content_location = get_location_from_club(content_club, yachtclubs)
        
        # Check for mismatches
        mismatches = []
        
        # Check club
        if not current_club and content_club:
            mismatches.append(f"Missing club: could be '{content_club}'")
        elif current_club and content_club and current_club != content_club:
            mismatches.append(f"Club mismatch: front matter='{current_club}', content='{content_club}'")
        
        # Check location
        if not current_location and content_location:
            mismatches.append(f"Missing location: could be '{content_location}'")
        elif current_location and content_location and current_location != content_location:
            mismatches.append(f"Location mismatch: front matter='{current_location}', content='{content_location}'")
        
        # Check results_url
        if not current_results_url and content_results_url:
            mismatches.append(f"Missing results_url: could be '{content_results_url}'")
        elif current_results_url and content_results_url and current_results_url != content_results_url:
            mismatches.append(f"Results URL mismatch: front matter='{current_results_url}', content='{content_results_url}'")
        
        if mismatches:
            return {
                'filename': file_path.name,
                'current': {
                    'club': current_club,
                    'location': current_location,
                    'results_url': current_results_url
                },
                'suggested': {
                    'club': content_club,
                    'location': content_location,
                    'results_url': content_results_url
                },
                'mismatches': mismatches
            }
        
        return None
        
    except Exception as e:
        return {
            'filename': file_path.name,
            'error': str(e)
        }

def main():
    """Main function."""
    print("Analyzing _results files for mismatches...")
    
    # Load yacht clubs data
    yachtclubs = load_yachtclubs()
    print(f"Loaded {len(yachtclubs)} yacht clubs for location lookup")
    
    # Process all files in _results directory
    results_dir = Path("_results")
    if not results_dir.exists():
        print("_results directory not found!")
        return
    
    mismatches = []
    errors = []
    
    for file_path in sorted(results_dir.glob("*.md")):
        result = analyze_file(file_path, yachtclubs)
        if result:
            if 'error' in result:
                errors.append(result)
            else:
                mismatches.append(result)
    
    # Print results
    print(f"\n=== ANALYSIS RESULTS ===")
    print(f"Total files analyzed: {len(list(results_dir.glob('*.md')))}")
    print(f"Files with mismatches: {len(mismatches)}")
    print(f"Files with errors: {len(errors)}")
    
    if mismatches:
        print(f"\n=== FILES WITH MISMATCHES ===")
        for item in mismatches:
            print(f"\n📁 {item['filename']}")
            print(f"   Current: club='{item['current']['club']}', location='{item['current']['location']}', results_url='{item['current']['results_url']}'")
            print(f"   Suggested: club='{item['suggested']['club']}', location='{item['suggested']['location']}', results_url='{item['suggested']['results_url']}'")
            print(f"   Issues:")
            for mismatch in item['mismatches']:
                print(f"     - {mismatch}")
    
    if errors:
        print(f"\n=== FILES WITH ERRORS ===")
        for item in errors:
            print(f"❌ {item['filename']}: {item['error']}")
    
    print(f"\n=== SUMMARY ===")
    if mismatches:
        print(f"Found {len(mismatches)} files that could benefit from front matter updates:")
        for item in mismatches:
            print(f"  - {item['filename']}")
    else:
        print("No mismatches found - all files appear to have correct front matter!")

if __name__ == "__main__":
    main()
