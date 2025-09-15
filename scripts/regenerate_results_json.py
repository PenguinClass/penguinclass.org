#!/usr/bin/env python3
"""
Regenerate assets/data/results.json from the _results collection.
"""
import os
import re
import json
import yaml
from pathlib import Path

def process_results_collection():
    """Process _results collection files and generate JSON data."""
    
    results = []
    results_dir = Path("_results")
    
    if not results_dir.exists():
        print("_results directory not found!")
        return results
    
    # Process all .md files in _results
    for file_path in results_dir.glob("*.md"):
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
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
            
            # Extract information from front matter
            year = front_matter.get('year', '')
            title = front_matter.get('title', '')
            series = front_matter.get('series', '')
            club = front_matter.get('club', '')
            location = front_matter.get('location', '')
            results_url = front_matter.get('results_url', '')
            
            # Generate ID from year and series
            if year and series:
                # Create a clean ID from year and series
                clean_series = re.sub(r'[^a-z0-9]', '', series.lower())
                result_id = f"{year}-{clean_series}"
            else:
                # Fallback to filename without extension
                result_id = file_path.stem
            
            results.append({
                "id": result_id,
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

def main():
    """Main function."""
    print("Regenerating assets/data/results.json from _results collection...")
    
    # Process _results collection
    results = process_results_collection()
    
    if not results:
        print("No results found!")
        return
    
    # Sort by year (most recent first)
    results.sort(key=lambda x: x.get("year", 0), reverse=True)
    
    print(f"Found {len(results)} results")
    
    # Create output directory if it doesn't exist
    output_dir = Path("assets/data")
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Write to JSON file
    output_file = output_dir / "results.json"
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    
    print(f"Created {output_file}")
    
    # Show some examples
    print("\nSample results:")
    for result in results[:10]:
        print(f"  {result['year']} - {result['series']} - {result['club']} - {result['source']}")
    
    # Show year range
    years = [r['year'] for r in results if r['year']]
    if years:
        print(f"\nYear range: {min(years)} - {max(years)}")
    
    print("Done!")

if __name__ == "__main__":
    main()
