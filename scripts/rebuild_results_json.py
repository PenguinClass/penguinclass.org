#!/usr/bin/env python3
"""
Rebuild assets/data/results.json from the _results collection.
"""

import os
import json
import yaml
import glob
from datetime import datetime

def rebuild_results_json():
    """Rebuild results.json from _results collection files."""
    results_dir = "_results"
    output_file = "assets/data/results.json"
    
    results = []
    
    # Process all markdown files in _results directory
    for file_path in glob.glob(os.path.join(results_dir, "*.md")):
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Split front matter and content
            if content.startswith('---'):
                parts = content.split('---', 2)
                if len(parts) >= 3:
                    front_matter = parts[1].strip()
                    body_content = parts[2].strip()
                    
                    # Parse YAML front matter
                    try:
                        data = yaml.safe_load(front_matter)
                        if data:
                            # Extract filename without extension
                            filename = os.path.basename(file_path)
                            name = os.path.splitext(filename)[0]
                            
                            # Create result entry
                            result = {
                                "id": data.get('result_id', ''),
                                "year": data.get('year', ''),
                                "title": data.get('title', ''),
                                "series": data.get('series', ''),
                                "club": data.get('club', ''),
                                "location": data.get('location', ''),
                                "results_url": data.get('results_url', ''),
                                "filename": filename,
                                "source": "collection"
                            }
                            
                            # Remove empty fields
                            result = {k: v for k, v in result.items() if v}
                            
                            results.append(result)
                            
                    except yaml.YAMLError as e:
                        print(f"Error parsing YAML in {file_path}: {e}")
                        
        except Exception as e:
            print(f"Error processing {file_path}: {e}")
    
    # Sort results by year (descending) then by title
    results.sort(key=lambda x: (int(x.get('year', 0)) if str(x.get('year', 0)).isdigit() else 0, x.get('title', '')), reverse=True)
    
    # Write to JSON file
    os.makedirs(os.path.dirname(output_file), exist_ok=True)
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
    
    print(f"Rebuilt {output_file} with {len(results)} results")
    print(f"Results range from {min(int(r.get('year', 0)) for r in results if str(r.get('year', 0)).isdigit())} to {max(int(r.get('year', 0)) for r in results if str(r.get('year', 0)).isdigit())}")

if __name__ == "__main__":
    rebuild_results_json()
