#!/usr/bin/env python3
"""
Build a comprehensive results database from both _results collection and archive files.
"""

import os
import json
import re
import yaml
from pathlib import Path

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
            
            # Look for club and location in content
            club_match = re.search(r'\*\*Club:\*\*\s*(.+)', content)
            if club_match:
                club = club_match.group(1).strip()
            
            location_match = re.search(r'\*\*Location:\*\*\s*(.+)', content)
            if location_match:
                location = location_match.group(1).strip()
            
            # Look for results URL
            results_url = ""
            url_match = re.search(r'\[View Results\]\(([^)]+)\)', content)
            if url_match:
                results_url = url_match.group(1)
            
            results.append({
                "year": int(year) if year else None,
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
    
    # Process each file
    for filename in sorted(result_files):
        result_info = extract_result_info_from_filename(filename)
        if result_info["year"]:
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
    
    print("Done!")

if __name__ == "__main__":
    main()
