#!/usr/bin/env python3
"""
Build a comprehensive results database from all available result files.
"""

import os
import json
import re
from pathlib import Path

def extract_result_info(filename):
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
    elif "north" in name.lower() or "na" in name.lower():
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
    
    # Extract club/location info
    club = ""
    location = ""
    
    if "tayc" in name.lower():
        club = "Tred Avon Yacht Club"
        location = "Oxford, MD, U.S.A."
    elif "corsica" in name.lower():
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
    
    return {
        "year": int(year) if year else None,
        "series": series,
        "club": club,
        "location": location,
        "filename": filename,
        "results_url": f"archive/legacy-website/{filename}"
    }

def build_results_database():
    """Build comprehensive results database."""
    
    results = []
    archive_dir = Path("archive/legacy-website")
    
    if not archive_dir.exists():
        print("Archive directory not found!")
        return results
    
    # Find all result files
    result_files = []
    for file_path in archive_dir.glob("*result*"):
        if file_path.is_file() and file_path.suffix.lower() in ['.html', '.htm']:
            result_files.append(file_path.name)
    
    # Also look for other regatta files
    for file_path in archive_dir.glob("*"):
        if file_path.is_file() and file_path.suffix.lower() in ['.html', '.htm']:
            name = file_path.name.lower()
            if any(keyword in name for keyword in [
                'annual', 'regatta', 'championship', 'series', 'frostbite', 
                'heritage', 'spring', 'rum', 'bucket', 'revival', 'icpfr'
            ]):
                if file_path.name not in result_files:
                    result_files.append(file_path.name)
    
    print(f"Found {len(result_files)} result files")
    
    # Process each file
    for filename in sorted(result_files):
        result_info = extract_result_info(filename)
        if result_info["year"]:
            results.append(result_info)
            print(f"  {result_info['year']} - {result_info['series']} - {result_info['club']}")
    
    return results

def main():
    print("Building results database...")
    
    results = build_results_database()
    
    # Sort by year (most recent first)
    results.sort(key=lambda x: x["year"], reverse=True)
    
    print(f"\nGenerated {len(results)} result entries")
    
    # Write to JSON file
    with open('assets/data/results.json', 'w') as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    
    print("Created assets/data/results.json")
    print("Done!")

if __name__ == "__main__":
    main()
