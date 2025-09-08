#!/usr/bin/env python3
"""
Regenerate all result files based on current champions data.
"""

import yaml
import os
from datetime import datetime

def generate_result_file(champion):
    """Generate a result file for a champion entry."""
    
    year = champion.get('year', '')
    result_id = champion.get('result_id', '')
    series = champion.get('series', '')
    skipper = champion.get('skipper', '')
    crew = champion.get('crew', '')
    club = champion.get('club', '')
    location = champion.get('location', '')
    boat = champion.get('boat', '')
    results_url = champion.get('results_url', '')
    
    # Determine file name based on result_id
    if result_id.startswith('international-'):
        filename = f"_results/{year}-international-championship.md"
    elif result_id.startswith('north-american-') or result_id.startswith('northamerica-'):
        filename = f"_results/{year}-north-american-championship.md"
    else:
        # Fallback based on series
        if series == 'International':
            filename = f"_results/{year}-international-championship.md"
        elif series == 'North-American':
            filename = f"_results/{year}-north-american-championship.md"
        else:
            return  # Skip if we can't determine the type
    
    # Generate content
    content = f"""---
layout: result
title: {year} {series} Championship
year: {year}
result_id: {result_id}
series: {series}
---

# {year} {series} Championship

## Champion

**Skipper:** {skipper}"""
    
    if crew:
        content += f"\n**Crew:** {crew}"
    
    if club:
        content += f"\n**Club:** {club}"
    
    if location:
        content += f"\n**Location:** {location}"
    
    if boat:
        content += f"\n**Boat:** {boat}"
    
    content += "\n\n## Results"
    
    if results_url:
        content += f"\n\n[View Results]({results_url})"
    else:
        content += "\n\n*Results not available*"
    
    # Add navigation
    content += f"""

## Navigation

- [Back to Results](/results/)
- [Back to Champions](/champions/)
"""
    
    # Write file
    with open(filename, 'w') as f:
        f.write(content)
    
    return filename

def main():
    print("Regenerating result files from champions data...")
    
    # Load champions data
    with open('_data/champions.yml', 'r') as f:
        champions = yaml.safe_load(f)
    
    # Ensure _results directory exists
    os.makedirs('_results', exist_ok=True)
    
    files_created = 0
    
    for champion in champions:
        year = champion.get('year', '')
        result_id = champion.get('result_id', '')
        series = champion.get('series', '')
        
        # Skip suspended entries
        if 'Suspended' in champion.get('skipper', ''):
            continue
        
        # Skip entries without proper identification
        if not year or not result_id:
            continue
        
        filename = generate_result_file(champion)
        if filename:
            files_created += 1
            print(f"  Created: {filename}")
    
    print(f"\nGenerated {files_created} result files")
    print("Done!")

if __name__ == "__main__":
    main()
