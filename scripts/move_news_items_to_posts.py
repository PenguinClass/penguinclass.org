#!/usr/bin/env python3
"""
Move dues, waiver, and schedule items from _results to _posts collection.
These are news items, not race results.
"""

import os
import shutil
import re
from pathlib import Path

def move_news_items():
    """Move news items from _results to _posts."""
    
    results_dir = Path("_results")
    posts_dir = Path("_posts")
    
    # Keywords that indicate news items rather than results
    news_keywords = ['dues', 'waiver', 'schedule', 'minutes', 'meeting', 'notice', 'nor']
    
    moved_count = 0
    
    if not results_dir.exists():
        print("_results directory not found!")
        return
    
    # Ensure _posts directory exists
    posts_dir.mkdir(exist_ok=True)
    
    # Find files to move
    for file_path in results_dir.glob("*.md"):
        filename = file_path.name.lower()
        
        # Check if this is a news item
        is_news = any(keyword in filename for keyword in news_keywords)
        
        if is_news:
            # Read the file to extract date and title
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # Extract year from filename
                year_match = re.search(r'(\d{4})', file_path.name)
                if not year_match:
                    print(f"Skipping {file_path.name} - no year found")
                    continue
                
                year = year_match.group(1)
                
                # Extract title from front matter
                title = "News Item"
                if content.startswith('---'):
                    parts = content.split('---', 2)
                    if len(parts) >= 2:
                        front_matter = parts[1]
                        title_match = re.search(r'title:\s*["\']([^"\']+)["\']', front_matter)
                        if title_match:
                            title = title_match.group(1)
                
                # Create slug from title
                slug = re.sub(r'[^a-z0-9]+', '-', title.lower()).strip('-')
                
                # Create new filename with date
                new_filename = f"{year}-01-01-{slug}.md"
                new_path = posts_dir / new_filename
                
                # Update front matter for post format
                updated_content = content.replace('layout: result', 'layout: post')
                
                # Add excerpt if not present
                if 'excerpt:' not in updated_content:
                    updated_content = updated_content.replace(
                        '---\n',
                        '---\nexcerpt: "News item from the Penguin Class archives."\n'
                    )
                
                # Write to _posts
                with open(new_path, 'w', encoding='utf-8') as f:
                    f.write(updated_content)
                
                # Remove from _results
                file_path.unlink()
                
                print(f"Moved: {file_path.name} -> {new_filename}")
                moved_count += 1
                
            except Exception as e:
                print(f"Error processing {file_path.name}: {e}")
    
    print(f"\nMoved {moved_count} news items to _posts collection")

if __name__ == "__main__":
    move_news_items()

