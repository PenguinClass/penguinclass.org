#!/usr/bin/env python3
"""
Validate that all championship result files have club and location data
that matches exactly with _data/yachtclubs.yml entries.
"""

import os
import yaml
import re
from pathlib import Path

def load_yachtclubs():
    """Load yacht clubs database."""
    try:
        with open('_data/yachtclubs.yml', 'r') as f:
            return yaml.safe_load(f)
    except Exception as e:
        print(f"Error loading yachtclubs.yml: {e}")
        return []

def normalize_text(text):
    """Normalize text for comparison."""
    if not text:
        return ""
    return re.sub(r'\s+', ' ', text.strip().lower())

def find_matching_club(club_name, yachtclubs):
    """Find matching club in yachtclubs database."""
    if not club_name:
        return None
    
    normalized_club = normalize_text(club_name)
    
    for club in yachtclubs:
        normalized_db_club = normalize_text(club.get('name', ''))
        if normalized_club == normalized_db_club:
            return club
    
    return None

def find_matching_location(location_name, yachtclubs):
    """Find matching location in yachtclubs database."""
    if not location_name:
        return None
    
    normalized_location = normalize_text(location_name)
    
    for club in yachtclubs:
        normalized_db_location = normalize_text(club.get('location', ''))
        if normalized_location == normalized_db_location:
            return club
    
    return None

def validate_championship_files():
    """Validate all championship files against yachtclubs database."""
    
    yachtclubs = load_yachtclubs()
    if not yachtclubs:
        print("Could not load yachtclubs database!")
        return
    
    print(f"Loaded {len(yachtclubs)} yacht clubs from database")
    print("\nValidating championship files...")
    
    results_dir = Path("_results")
    issues = []
    validated_count = 0
    
    if not results_dir.exists():
        print("_results directory not found!")
        return
    
    # Process all championship files
    for file_path in results_dir.glob("*championship*.md"):
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Skip if no front matter
            if not content.startswith('---'):
                continue
            
            # Split front matter and content
            parts = content.split('---', 2)
            if len(parts) < 3:
                continue
            
            front_matter_text = parts[1]
            content_body = parts[2]
            
            # Extract metadata
            year_match = re.search(r'year:\s*(\d+)', front_matter_text)
            year = year_match.group(1) if year_match else "Unknown"
            
            series_match = re.search(r'series:\s*["\']([^"\']+)["\']', front_matter_text)
            series = series_match.group(1) if series_match else "Unknown"
            
            # Extract club and location from front matter
            club_match = re.search(r'club:\s*["\']([^"\']*)["\']', front_matter_text)
            club_metadata = club_match.group(1).strip() if club_match else ""
            
            location_match = re.search(r'location:\s*["\']([^"\']*)["\']', front_matter_text)
            location_metadata = location_match.group(1).strip() if location_match else ""
            
            # Extract club and location from content
            club_content_match = re.search(r'\*\*Club:\*\*\s*(.+)', content_body)
            club_content = club_content_match.group(1).strip() if club_content_match else ""
            
            location_content_match = re.search(r'\*\*Location:\*\*\s*(.+)', content_body)
            location_content = location_content_match.group(1).strip() if location_content_match else ""
            
            # Check for issues
            file_issues = []
            
            # Check if club metadata matches content
            if club_metadata and club_content and normalize_text(club_metadata) != normalize_text(club_content):
                file_issues.append(f"Club mismatch: metadata='{club_metadata}' vs content='{club_content}'")
            
            # Check if location metadata matches content
            if location_metadata and location_content and normalize_text(location_metadata) != normalize_text(location_content):
                file_issues.append(f"Location mismatch: metadata='{location_metadata}' vs content='{location_content}'")
            
            # Check if club exists in yachtclubs database
            club_to_check = club_metadata or club_content
            if club_to_check:
                matching_club = find_matching_club(club_to_check, yachtclubs)
                if not matching_club:
                    file_issues.append(f"Club not found in yachtclubs.yml: '{club_to_check}'")
                else:
                    # Check if location matches the club's location
                    location_to_check = location_metadata or location_content
                    if location_to_check:
                        db_location = matching_club.get('location', '')
                        if normalize_text(location_to_check) != normalize_text(db_location):
                            file_issues.append(f"Location mismatch with club: expected '{db_location}' but found '{location_to_check}'")
            
            # Check if location exists in yachtclubs database
            location_to_check = location_metadata or location_content
            if location_to_check:
                matching_location = find_matching_location(location_to_check, yachtclubs)
                if not matching_location:
                    file_issues.append(f"Location not found in yachtclubs.yml: '{location_to_check}'")
            
            # Report issues
            if file_issues:
                issues.append({
                    'file': file_path.name,
                    'year': year,
                    'series': series,
                    'issues': file_issues
                })
            else:
                validated_count += 1
                print(f"✓ {file_path.name} ({year} {series})")
        
        except Exception as e:
            issues.append({
                'file': file_path.name,
                'year': 'Unknown',
                'series': 'Unknown',
                'issues': [f"Error processing file: {e}"]
            })
    
    # Report summary
    print(f"\nValidation Summary:")
    print(f"✓ Validated: {validated_count}")
    print(f"✗ Issues found: {len(issues)}")
    
    if issues:
        print(f"\nIssues found:")
        for issue in issues:
            print(f"\n{issue['file']} ({issue['year']} {issue['series']}):")
            for problem in issue['issues']:
                print(f"  - {problem}")
    
    # Show yachtclubs database for reference
    print(f"\nYacht clubs in database:")
    for club in yachtclubs:
        print(f"  - {club.get('name', 'Unknown')} ({club.get('location', 'Unknown')})")

if __name__ == "__main__":
    validate_championship_files()

