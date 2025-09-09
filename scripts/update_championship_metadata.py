#!/usr/bin/env python3
"""
Update championship result files to extract club and location from content
and add them to the front matter metadata.
"""

import os
import re
from pathlib import Path

def update_championship_metadata():
    """Update championship files to extract metadata from content."""
    
    results_dir = Path("_results")
    updated_count = 0
    
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
            
            # Extract club and location from content
            club = ""
            location = ""
            
            # Look for club in content
            club_match = re.search(r'\*\*Club:\*\*\s*(.+)', content_body)
            if club_match:
                club = club_match.group(1).strip()
            
            # Look for location in content
            location_match = re.search(r'\*\*Location:\*\*\s*(.+)', content_body)
            if location_match:
                location = location_match.group(1).strip()
            
            # Only update if we found club or location
            if club or location:
                # Update front matter
                updated_front_matter = front_matter_text
                
                # Update club in front matter
                if club:
                    if 'club:' in updated_front_matter:
                        updated_front_matter = re.sub(
                            r'club:\s*["\']?[^"\'\n]*["\']?',
                            f'club: "{club}"',
                            updated_front_matter
                        )
                    else:
                        # Add club field
                        updated_front_matter = updated_front_matter.rstrip() + f'\nclub: "{club}"'
                
                # Update location in front matter
                if location:
                    if 'location:' in updated_front_matter:
                        updated_front_matter = re.sub(
                            r'location:\s*["\']?[^"\'\n]*["\']?',
                            f'location: "{location}"',
                            updated_front_matter
                        )
                    else:
                        # Add location field
                        updated_front_matter = updated_front_matter.rstrip() + f'\nlocation: "{location}"'
                
                # Reconstruct file content
                new_content = f"---{updated_front_matter}---{content_body}"
                
                # Write updated file
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(new_content)
                
                print(f"Updated: {file_path.name}")
                print(f"  Club: {club}")
                print(f"  Location: {location}")
                updated_count += 1
        
        except Exception as e:
            print(f"Error processing {file_path.name}: {e}")
    
    print(f"\nUpdated {updated_count} championship files")

if __name__ == "__main__":
    update_championship_metadata()

