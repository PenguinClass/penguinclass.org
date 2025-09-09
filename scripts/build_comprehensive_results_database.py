#!/usr/bin/env python3
"""
Build a comprehensive results database from both _results collection and archive files.
This will include all championship results from _results/*.md AND all regatta results from archive HTML files.
"""

import os
import json
import re
import yaml
from pathlib import Path
from bs4 import BeautifulSoup

def extract_result_info_from_filename(filename):
    """Extract information from result filename."""
    
    # Remove file extension
    name = os.path.splitext(filename)[0]
    
    # Extract year
    year_match = re.search(r'(\d{4})', name)
    year = year_match.group(1) if year_match else None
    
    # Determine event type and series
    series = "Regatta"
    if "international" in name.lower() or "intl" in name.lower():
        series = "International Championship"
    elif "north-american" in name.lower() or "north american" in name.lower():
        series = "North American Championship"
    elif "annual" in name.lower():
        series = "Annual Regatta"
    elif "frostbite" in name.lower():
        series = "Frostbite Series"
    elif "heritage" in name.lower():
        series = "Heritage Regatta"
    elif "spring" in name.lower():
        series = "Spring Series"
    elif "rum" in name.lower() or "bucket" in name.lower():
        series = "Rum Bucket Regatta"
    elif "revival" in name.lower():
        series = "Revival Regatta"
    elif "icpfr" in name.lower():
        series = "ICPFR Regatta"
    elif "tayc" in name.lower():
        series = "TAYC Regatta"
    elif "corsica" in name.lower():
        series = "Corsica Regatta"
    elif "president" in name.lower() or "pres cup" in name.lower():
        series = "President's Cup"
    elif "memorial" in name.lower():
        series = "Memorial Regatta"
    elif "turkey" in name.lower() or "trot" in name.lower():
        series = "Turkey Trot Regatta"
    elif "comet" in name.lower() and "penguin" in name.lower():
        series = "Comet & Penguin Invitational"
    elif "beachwood" in name.lower():
        series = "Beachwood Revival"
    elif "cambridge" in name.lower():
        series = "Cambridge Regatta"
    elif "gibson" in name.lower() or "giys" in name.lower():
        series = "GIYS Regatta"
    elif "miles" in name.lower() or "mryc" in name.lower():
        series = "Miles River Regatta"
    elif "potomac" in name.lower() or "prsa" in name.lower():
        series = "Potomac Regatta"
    elif "oxford" in name.lower():
        series = "Oxford Regatta"
    elif "bay ridge" in name.lower():
        series = "Bay Ridge Regatta"
    elif "admir" in name.lower() or "byrd" in name.lower():
        series = "Admiral Byrd Regatta"
    elif "lawson" in name.lower():
        series = "Lawson Rum Bucket"
    elif "trippe" in name.lower() or "tcpfr" in name.lower():
        series = "Trippe Creek Regatta"
    elif "island creek" in name.lower():
        series = "Island Creek Regatta"
    elif "west river" in name.lower() or "wrsc" in name.lower():
        series = "West River Regatta"
    elif "baltimore" in name.lower() or "byc" in name.lower():
        series = "Baltimore Regatta"
    elif "annapolis" in name.lower() or "ayc" in name.lower():
        series = "Annapolis Regatta"
    elif "severn" in name.lower() or "ssa" in name.lower():
        series = "Severn Regatta"
    elif "cbyra" in name.lower():
        series = "CBYRA Regatta"
    elif "highpoint" in name.lower():
        series = "High Point Series"
    elif "schedule" in name.lower():
        series = "Schedule"
    elif "nor" in name.lower() or "notice" in name.lower():
        series = "Notice of Race"
    elif "minutes" in name.lower() or "meeting" in name.lower():
        series = "Meeting Minutes"
    elif "dues" in name.lower():
        series = "Dues Information"
    elif "waiver" in name.lower():
        series = "Waiver Form"
    elif "specification" in name.lower() or "spec" in name.lower():
        series = "Specification"
    elif "plan" in name.lower():
        series = "Plans"
    elif "wanted" in name.lower():
        series = "Wanted"
    elif "sale" in name.lower():
        series = "For Sale"
    elif "officer" in name.lower():
        series = "Officers"
    elif "champion" in name.lower():
        series = "Championship"
    
    # Extract club and location info
    club = ""
    location = ""
    
    if "tayc" in name.lower():
        club = "Tred Avon Yacht Club"
        location = "Oxford, MD, U.S.A."
    elif "corsica" in name.lower() or "cryc" in name.lower():
        club = "Corsica River Yacht Club"
        location = "Centreville, MD, U.S.A."
    elif "cambridge" in name.lower():
        club = "Cambridge Yacht Club"
        location = "Cambridge, MD, U.S.A."
    elif "beachwood" in name.lower():
        club = "Beachwood Yacht Club"
        location = "Toms River, NJ, U.S.A."
    elif "gibson" in name.lower() or "giys" in name.lower():
        club = "Gibson Island Yacht Squadron"
        location = "Gibson Island, MD, U.S.A."
    elif "miles" in name.lower() or "mryc" in name.lower():
        club = "Miles River Yacht Club"
        location = "St. Michaels, MD, U.S.A."
    elif "potomac" in name.lower() or "prsa" in name.lower():
        club = "Potomac River Sailing Association"
        location = "Washington, DC, U.S.A."
    elif "oxford" in name.lower():
        club = "Tred Avon Yacht Club"
        location = "Oxford, MD, U.S.A."
    elif "bay ridge" in name.lower():
        club = "Bay Ridge Yacht Club"
        location = "Annapolis, MD, U.S.A."
    elif "baltimore" in name.lower() or "byc" in name.lower():
        club = "Baltimore Yacht Club"
        location = "Baltimore, MD, U.S.A."
    elif "annapolis" in name.lower() or "ayc" in name.lower():
        club = "Annapolis Yacht Club"
        location = "Annapolis, MD, U.S.A."
    elif "severn" in name.lower() or "ssa" in name.lower():
        club = "Severn Sailing Association"
        location = "Annapolis, MD, U.S.A."
    elif "west river" in name.lower() or "wrsc" in name.lower():
        club = "West River Sailing Club"
        location = "Galesville, MD, U.S.A."
    elif "island creek" in name.lower():
        club = "Island Creek Yacht Club"
        location = "Island Creek, MD, U.S.A."
    elif "trippe" in name.lower() or "tcpfr" in name.lower():
        club = "Trippe Creek Penguin Frostbite Regatta"
        location = "Trippe Creek, MD, U.S.A."
    elif "lawson" in name.lower():
        club = "Gibson Island Yacht Squadron"
        location = "Gibson Island, MD, U.S.A."
    elif "admir" in name.lower() or "byrd" in name.lower():
        club = "Admiral Byrd Yacht Club"
        location = "Annapolis, MD, U.S.A."
    
    return {
        "year": int(year) if year else None,
        "series": series,
        "club": club,
        "location": location,
        "filename": filename,
        "results_url": f"archive/legacy-website/{filename}"
    }

def process_results_collection():
    """Process _results collection files."""
    
    results = []
    results_dir = Path("_results")
    
    if not results_dir.exists():
        print("_results directory not found!")
        return results
    
    # Process all .md files in _results
    for file_path in results_dir.glob("*.md"):
        try:
            with open(file_path, 'r') as f:
                content = f.read()
            
            # Extract front matter
            if content.startswith('---'):
                parts = content.split('---', 2)
                if len(parts) >= 3:
                    front_matter = yaml.safe_load(parts[1])
                    content_body = parts[2]
                else:
                    continue
            else:
                continue
            
            # Extract information
            year = front_matter.get('year', '')
            title = front_matter.get('title', '')
            series = front_matter.get('series', '')
            
            # Determine series from title if not in front matter
            if not series:
                if "international" in title.lower():
                    series = "International Championship"
                elif "north american" in title.lower():
                    series = "North American Championship"
                else:
                    series = "Championship"
            
            # Extract club and location from content
            club = ""
            location = ""
            
            # Get club and location from front matter
            club = front_matter.get('club', '').strip()
            location = front_matter.get('location', '').strip()
            
            # Get results URL from front matter
            results_url = front_matter.get('results_url', '').strip()
            
            results.append({
                "id": f"{int(year) if year else 0}-{re.sub(r'[^a-z0-9]', '', series.lower())}",
                "year": int(year) if year else None,
                "title": title,
                "series": series,
                "club": club,
                "location": location,
                "filename": file_path.name,
                "results_url": results_url,
                "source": "collection"
            })
            
        except Exception as e:
            print(f"Error processing {file_path}: {e}")
            continue
    
    return results

def process_archive_files():
    """Process archive HTML files."""
    
    results = []
    archive_dir = Path("archive/legacy-website")
    
    if not archive_dir.exists():
        print("Archive directory not found!")
        return results
    
    # Find all result files
    result_files = []
    for file_path in archive_dir.glob("*"):
        if file_path.is_file() and file_path.suffix.lower() in ['.html', '.htm']:
            name = file_path.name.lower()
            # Skip news items (these should be in _posts, not _results)
            if any(news_keyword in name for news_keyword in [
                'dues', 'waiver', 'schedule', 'minutes', 'meeting'
            ]):
                continue
            
            # Include files that look like results, regattas, or important content
            if any(keyword in name for keyword in [
                'result', 'regatta', 'championship', 'series', 'frostbite', 
                'heritage', 'spring', 'rum', 'bucket', 'revival', 'icpfr',
                'annual', 'international', 'intl', 'race',
                'tayc', 'corsica', 'cambridge', 'gibson', 'miles', 'potomac',
                'oxford', 'bay', 'baltimore', 'annapolis', 'severn', 'west',
                'island', 'trippe', 'lawson', 'admir', 'byrd', 'president',
                'memorial', 'turkey', 'trot', 'comet', 'beachwood',
                'wanted', 'sale', 'officer', 'champion', 'highpoint', 'cbyra'
            ]):
                result_files.append(file_path.name)
    
    # Process each file
    for filename in sorted(result_files):
        result_info = extract_result_info_from_filename(filename)
        if result_info["year"]:
            result_info["id"] = f"{result_info['year']}-{re.sub(r'[^a-z0-9]', '', result_info['series'].lower())}"
            result_info["title"] = f"{result_info['year']} {result_info['series']}"
            result_info["source"] = "archive"
            results.append(result_info)
    
    return results

def main():
    print("Building comprehensive results database...")
    
    # Process _results collection
    print("Processing _results collection...")
    collection_results = process_results_collection()
    print(f"Found {len(collection_results)} collection results")
    
    # Process archive files
    print("Processing archive files...")
    archive_results = process_archive_files()
    print(f"Found {len(archive_results)} archive results")
    
    # Combine results, avoiding duplicates
    all_results = []
    seen = set()
    
    # Add collection results first (they're more structured)
    for result in collection_results:
        key = f"{result['year']}-{result['series']}"
        if key not in seen:
            all_results.append(result)
            seen.add(key)
    
    # Add archive results that don't duplicate collection results
    for result in archive_results:
        key = f"{result['year']}-{result['series']}"
        if key not in seen:
            all_results.append(result)
            seen.add(key)
    
    # Sort by year (most recent first)
    all_results.sort(key=lambda x: x["year"], reverse=True)
    
    print(f"\nGenerated {len(all_results)} total result entries")
    
    # Write to JSON file
    with open('assets/data/results.json', 'w') as f:
        json.dump(all_results, f, ensure_ascii=False, indent=2)
    
    print("Created assets/data/results.json")
    
    # Show some examples
    print("\nSample results:")
    for result in all_results[:10]:
        print(f"  {result['year']} - {result['series']} - {result['club']} - {result['source']}")
    
    # Show year range
    years = [r['year'] for r in all_results if r['year']]
    if years:
        print(f"\nYear range: {min(years)} - {max(years)}")
    
    print("Done!")

if __name__ == "__main__":
    main()