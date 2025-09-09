#!/usr/bin/env python3
"""
Create missing _results/*.md files from archive HTML files that aren't already in the collection.
"""

import os
import json
import re
from pathlib import Path
from bs4 import BeautifulSoup

def extract_info_from_html(file_path):
    """Extract information from HTML file."""
    try:
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()
        
        soup = BeautifulSoup(content, 'html.parser')
        
        # Extract title from page title or h1
        title = ""
        title_tag = soup.find('title')
        if title_tag:
            title = title_tag.get_text().strip()
        
        h1_tag = soup.find('h1')
        if h1_tag and not title:
            title = h1_tag.get_text().strip()
        
        # Extract year from filename or content
        year = None
        year_match = re.search(r'(\d{4})', os.path.basename(file_path))
        if year_match:
            year = int(year_match.group(1))
        
        # Determine series type
        filename = os.path.basename(file_path).lower()
        series = "Regatta"
        
        if "international" in filename or "intl" in filename:
            series = "International Championship"
        elif "north-american" in filename or "north american" in filename:
            series = "North American Championship"
        elif "annual" in filename:
            series = "Annual Regatta"
        elif "frostbite" in filename:
            series = "Frostbite Series"
        elif "heritage" in filename:
            series = "Heritage Regatta"
        elif "spring" in filename:
            series = "Spring Series"
        elif "rum" in filename or "bucket" in filename:
            series = "Rum Bucket Regatta"
        elif "revival" in filename:
            series = "Revival Regatta"
        elif "icpfr" in filename:
            series = "ICPFR Regatta"
        elif "tayc" in filename:
            series = "TAYC Regatta"
        elif "corsica" in filename:
            series = "Corsica Regatta"
        elif "president" in filename or "pres cup" in filename:
            series = "President's Cup"
        elif "memorial" in filename:
            series = "Memorial Regatta"
        elif "turkey" in filename or "trot" in filename:
            series = "Turkey Trot Regatta"
        elif "comet" in filename and "penguin" in filename:
            series = "Comet & Penguin Invitational"
        elif "beachwood" in filename:
            series = "Beachwood Revival"
        elif "cambridge" in filename:
            series = "Cambridge Regatta"
        elif "gibson" in filename or "giys" in filename:
            series = "GIYS Regatta"
        elif "miles" in filename or "mryc" in filename:
            series = "Miles River Regatta"
        elif "potomac" in filename or "prsa" in filename:
            series = "Potomac Regatta"
        elif "oxford" in filename:
            series = "Oxford Regatta"
        elif "bay ridge" in filename:
            series = "Bay Ridge Regatta"
        elif "admir" in filename or "byrd" in filename:
            series = "Admiral Byrd Regatta"
        elif "lawson" in filename:
            series = "Lawson Rum Bucket"
        elif "trippe" in filename or "tcpfr" in filename:
            series = "Trippe Creek Regatta"
        elif "island creek" in filename:
            series = "Island Creek Regatta"
        elif "west river" in filename or "wrsc" in filename:
            series = "West River Regatta"
        elif "baltimore" in filename or "byc" in filename:
            series = "Baltimore Regatta"
        elif "annapolis" in filename or "ayc" in filename:
            series = "Annapolis Regatta"
        elif "severn" in filename or "ssa" in filename:
            series = "Severn Regatta"
        elif "cbyra" in filename:
            series = "CBYRA Regatta"
        elif "highpoint" in filename:
            series = "High Point Series"
        elif "schedule" in filename:
            series = "Schedule"
        elif "nor" in filename or "notice" in filename:
            series = "Notice of Race"
        elif "minutes" in filename or "meeting" in filename:
            series = "Meeting Minutes"
        elif "dues" in filename:
            series = "Dues Information"
        elif "waiver" in filename:
            series = "Waiver Form"
        elif "specification" in filename or "spec" in filename:
            series = "Specification"
        elif "plan" in filename:
            series = "Plans"
        elif "wanted" in filename:
            series = "Wanted"
        elif "sale" in filename:
            series = "For Sale"
        elif "officer" in filename:
            series = "Officers"
        elif "champion" in filename:
            series = "Championship"
        
        # Extract club and location
        club = ""
        location = ""
        
        if "tayc" in filename:
            club = "Tred Avon Yacht Club"
            location = "Oxford, MD, U.S.A."
        elif "corsica" in filename or "cryc" in filename:
            club = "Corsica River Yacht Club"
            location = "Centreville, MD, U.S.A."
        elif "cambridge" in filename:
            club = "Cambridge Yacht Club"
            location = "Cambridge, MD, U.S.A."
        elif "beachwood" in filename:
            club = "Beachwood Yacht Club"
            location = "Toms River, NJ, U.S.A."
        elif "gibson" in filename or "giys" in filename:
            club = "Gibson Island Yacht Squadron"
            location = "Gibson Island, MD, U.S.A."
        elif "miles" in filename or "mryc" in filename:
            club = "Miles River Yacht Club"
            location = "St. Michaels, MD, U.S.A."
        elif "potomac" in filename or "prsa" in filename:
            club = "Potomac River Sailing Association"
            location = "Washington, DC, U.S.A."
        elif "oxford" in filename:
            club = "Tred Avon Yacht Club"
            location = "Oxford, MD, U.S.A."
        elif "bay ridge" in filename:
            club = "Bay Ridge Yacht Club"
            location = "Annapolis, MD, U.S.A."
        elif "baltimore" in filename or "byc" in filename:
            club = "Baltimore Yacht Club"
            location = "Baltimore, MD, U.S.A."
        elif "annapolis" in filename or "ayc" in filename:
            club = "Annapolis Yacht Club"
            location = "Annapolis, MD, U.S.A."
        elif "severn" in filename or "ssa" in filename:
            club = "Severn Sailing Association"
            location = "Annapolis, MD, U.S.A."
        elif "west river" in filename or "wrsc" in filename:
            club = "West River Sailing Club"
            location = "Galesville, MD, U.S.A."
        elif "island creek" in filename:
            club = "Island Creek Yacht Club"
            location = "Island Creek, MD, U.S.A."
        elif "trippe" in filename or "tcpfr" in filename:
            club = "Trippe Creek Penguin Frostbite Regatta"
            location = "Trippe Creek, MD, U.S.A."
        elif "lawson" in filename:
            club = "Gibson Island Yacht Squadron"
            location = "Gibson Island, MD, U.S.A."
        elif "admir" in filename or "byrd" in filename:
            club = "Admiral Byrd Yacht Club"
            location = "Annapolis, MD, U.S.A."
        
        return {
            'year': year,
            'title': title or f"{year} {series}",
            'series': series,
            'club': club,
            'location': location,
            'filename': os.path.basename(file_path)
        }
        
    except Exception as e:
        print(f"Error processing {file_path}: {e}")
        return None

def get_existing_results():
    """Get list of existing result files in _results collection."""
    results_dir = Path("_results")
    existing = set()
    
    if results_dir.exists():
        for file_path in results_dir.glob("*.md"):
            existing.add(file_path.stem)
    
    return existing

def create_result_file(info, archive_file):
    """Create a _results/*.md file from archive information."""
    
    if not info or not info['year']:
        return False
    
    # Create filename
    series_slug = re.sub(r'[^a-z0-9]+', '-', info['series'].lower()).strip('-')
    filename = f"{info['year']}-{series_slug}.md"
    file_path = Path("_results") / filename
    
    # Skip if already exists
    if file_path.exists():
        return False
    
    # Create front matter
    front_matter = f"""---
year: {info['year']}
title: "{info['title']}"
series: "{info['series']}"
club: "{info['club']}"
location: "{info['location']}"
results_url: "archive/legacy-website/{info['filename']}"
---

# {info['title']}

**Year:** {info['year']}  
**Series:** {info['series']}  
**Club:** {info['club']}  
**Location:** {info['location']}  

[View Results](archive/legacy-website/{info['filename']})

## Event Details

This event was held in {info['year']} at {info['location']}.

## Results

Results are available in the original format: [View Results](archive/legacy-website/{info['filename']})
"""
    
    # Write file
    try:
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(front_matter)
        return True
    except Exception as e:
        print(f"Error writing {file_path}: {e}")
        return False

def main():
    print("Creating missing _results/*.md files from archive...")
    
    # Get existing results
    existing = get_existing_results()
    print(f"Found {len(existing)} existing result files")
    
    # Process archive files
    archive_dir = Path("archive/legacy-website")
    created_count = 0
    skipped_count = 0
    
    # Find HTML files that look like results
    for file_path in archive_dir.glob("*.htm*"):
        filename = file_path.name.lower()
        
        # Skip if not a result-like file
        if not any(keyword in filename for keyword in [
            'result', 'regatta', 'championship', 'series', 'frostbite', 
            'heritage', 'spring', 'rum', 'bucket', 'revival', 'icpfr',
            'annual', 'international', 'intl', 'nor', 'notice', 'race',
            'tayc', 'corsica', 'cambridge', 'gibson', 'miles', 'potomac',
            'oxford', 'bay', 'baltimore', 'annapolis', 'severn', 'west',
            'island', 'trippe', 'lawson', 'admir', 'byrd', 'president',
            'memorial', 'turkey', 'trot', 'comet', 'beachwood', 'schedule',
            'minutes', 'meeting', 'dues', 'waiver', 'spec', 'plan',
            'wanted', 'sale', 'officer', 'champion', 'highpoint', 'cbyra'
        ]):
            continue
        
        # Extract year from filename
        year_match = re.search(r'(\d{4})', filename)
        if not year_match:
            continue
        
        year = int(year_match.group(1))
        
        # Skip if we already have a result file for this year and series
        series_slug = "regatta"  # default
        if "international" in filename or "intl" in filename:
            series_slug = "international-championship"
        elif "north-american" in filename or "north american" in filename:
            series_slug = "north-american-championship"
        elif "annual" in filename:
            series_slug = "annual-regatta"
        elif "frostbite" in filename:
            series_slug = "frostbite-series"
        elif "heritage" in filename:
            series_slug = "heritage-regatta"
        elif "spring" in filename:
            series_slug = "spring-series"
        elif "rum" in filename or "bucket" in filename:
            series_slug = "rum-bucket-regatta"
        elif "revival" in filename:
            series_slug = "revival-regatta"
        elif "icpfr" in filename:
            series_slug = "icpfr-regatta"
        elif "tayc" in filename:
            series_slug = "tayc-regatta"
        elif "corsica" in filename:
            series_slug = "corsica-regatta"
        elif "president" in filename or "pres cup" in filename:
            series_slug = "presidents-cup"
        elif "memorial" in filename:
            series_slug = "memorial-regatta"
        elif "turkey" in filename or "trot" in filename:
            series_slug = "turkey-trot-regatta"
        elif "comet" in filename and "penguin" in filename:
            series_slug = "comet-penguin-invitational"
        elif "beachwood" in filename:
            series_slug = "beachwood-revival"
        elif "cambridge" in filename:
            series_slug = "cambridge-regatta"
        elif "gibson" in filename or "giys" in filename:
            series_slug = "giys-regatta"
        elif "miles" in filename or "mryc" in filename:
            series_slug = "miles-river-regatta"
        elif "potomac" in filename or "prsa" in filename:
            series_slug = "potomac-regatta"
        elif "oxford" in filename:
            series_slug = "oxford-regatta"
        elif "bay ridge" in filename:
            series_slug = "bay-ridge-regatta"
        elif "baltimore" in filename or "byc" in filename:
            series_slug = "baltimore-regatta"
        elif "annapolis" in filename or "ayc" in filename:
            series_slug = "annapolis-regatta"
        elif "severn" in filename or "ssa" in filename:
            series_slug = "severn-regatta"
        elif "west river" in filename or "wrsc" in filename:
            series_slug = "west-river-regatta"
        elif "island creek" in filename:
            series_slug = "island-creek-regatta"
        elif "trippe" in filename or "tcpfr" in filename:
            series_slug = "trippe-creek-regatta"
        elif "lawson" in filename:
            series_slug = "lawson-rum-bucket"
        elif "admir" in filename or "byrd" in filename:
            series_slug = "admir-byrd-regatta"
        
        expected_filename = f"{year}-{series_slug}"
        
        if expected_filename in existing:
            skipped_count += 1
            continue
        
        # Extract info and create file
        info = extract_info_from_html(file_path)
        if info and create_result_file(info, file_path):
            print(f"Created: {expected_filename}.md")
            created_count += 1
        else:
            skipped_count += 1
    
    print(f"\nCreated {created_count} new result files")
    print(f"Skipped {skipped_count} files (already exist or couldn't process)")
    print("Done!")

if __name__ == "__main__":
    main()

