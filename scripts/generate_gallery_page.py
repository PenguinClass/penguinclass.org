#!/usr/bin/env python3
"""
Generate the gallery.md page dynamically based on gallery.json data.

This script reads the gallery.json file and generates a gallery.md page
with dynamic categories and years based on the actual data, using
normalization data to avoid duplicate categories.
"""

import json
import yaml
import argparse
from pathlib import Path
from typing import Dict, List, Set
from collections import defaultdict
import sys
sys.path.append(str(Path(__file__).parent))
from lib.gallery_utils import GalleryUtils

class GalleryPageGenerator:
    def __init__(self, gallery_data_path: str = "assets/data/gallery.json"):
        self.gallery_data_path = Path(gallery_data_path)
        self.gallery_data = {}
        self.utils = GalleryUtils()
        
        # Category icons mapping
        self.category_icons = {
            'Photos': '📸',
            'Championships': '🏆',
            'Regattas': '⛵',
            'Frostbite': '❄️',
            'TAYC': '🏛️',
            'CRYC': '🌊',
            'GIYS': '⚓',
            'Beachwood': '🏖️',
            'Awards': '🏅',
            'Heritage': '📜',
            'Boats': '⛵',
            'BYC': '🏛️',
            'Videos': '🎥',
            'External Videos': '📺',
            'General': '📁'
        }
    
    
    def load_gallery_data(self) -> bool:
        """Load the gallery data from JSON file."""
        if not self.gallery_data_path.exists():
            print(f"Gallery data file not found: {self.gallery_data_path}")
            return False
        
        try:
            with open(self.gallery_data_path, 'r') as f:
                self.gallery_data = json.load(f)
            print(f"Loaded gallery data with {self.gallery_data.get('stats', {}).get('total_media', 0)} items")
            return True
        except Exception as e:
            print(f"Error loading gallery data: {e}")
            return False
    
    def get_category_icon(self, category: str) -> str:
        """Get the appropriate icon for a category."""
        return self.category_icons.get(category, '📁')
    
    def generate_category_section(self) -> str:
        """Generate the Browse by Category section."""
        categories = self.gallery_data.get('categories', {})
        
        # Normalize category names and group by normalized name
        normalized_categories = {}
        for category_name, category_items in categories.items():
            normalized_name = self.utils.normalize_category_name(category_name)
            if normalized_name not in normalized_categories:
                normalized_categories[normalized_name] = []
            normalized_categories[normalized_name].extend(category_items)
        
        # Sort categories by count (descending) then by name
        sorted_categories = sorted(
            normalized_categories.items(),
            key=lambda x: (-len(x[1]), x[0])
        )
        
        category_html = []
        category_html.append('<div class="gallery-categories">')
        
        # Always include "All Photos" first
        total_photos = len(categories.get('Photos', []))
        category_html.append(f'''  <div class="category-card" data-category="photos">
    <h3>📸 All Photos</h3>
    <p id="photos-count">Loading...</p>
    <button class="view-photos-btn" onclick="viewCategory('photos')">View Photos</button>
  </div>''')
        
        # Add other categories (excluding Photos since it's already added)
        for category_name, category_items in sorted_categories:
            if category_name == 'Photos':
                continue
            
            icon = self.get_category_icon(category_name)
            category_id = category_name.lower().replace(' ', '_').replace(',', '').replace('.', '')
            
            category_html.append(f'''  <div class="category-card" data-category="{category_id}">
    <h3>{icon} {category_name}</h3>
    <p id="{category_id}-count">Loading...</p>
    <button class="view-photos-btn" onclick="viewCategory('{category_id}')">View Photos</button>
  </div>''')
        
        category_html.append('</div>')
        return '\n'.join(category_html)
    
    def generate_year_section(self) -> str:
        """Generate the Browse by Year section with decade grouping for better UX."""
        years = self.gallery_data.get('years', {})
        
        if not years:
            return '''<div class="gallery-years">
  <p>No year data available.</p>
</div>'''
        
        # Sort years numerically
        sorted_years = sorted(years.keys(), key=int, reverse=True)
        
        # Group years by decades
        decades = defaultdict(list)
        for year in sorted_years:
            decade = (int(year) // 10) * 10
            decades[decade].append(year)
        
        year_html = []
        year_html.append('<div class="gallery-years">')
        
        # Sort decades in descending order
        sorted_decades = sorted(decades.keys(), reverse=True)
        
        for decade in sorted_decades:
            decade_years = sorted(decades[decade], key=int, reverse=True)
            decade_name = f"{decade}s" if decade < 2000 else f"{decade}-{decade+9}"
            
            year_html.append(f'  <div class="year-section">')
            year_html.append(f'    <h3>{decade_name}</h3>')
            year_html.append(f'    <div class="year-grid">')
            
            for year in decade_years:
                count = len(years[year])
                year_html.append(f'      <button class="year-link" onclick="viewYear(\'{year}\')">{year} ({count} photos)</button>')
            
            year_html.append(f'    </div>')
            year_html.append(f'  </div>')
        
        year_html.append('</div>')
        return '\n'.join(year_html)
    
    def generate_creator_section(self) -> str:
        """Generate the Browse by Creator section."""
        media_index = self.gallery_data.get('media_index', [])
        
        # Group media by creator/credit
        creators = defaultdict(list)
        for item in media_index:
            credit = item.get('credit', 'Unknown photographer')
            creators[credit].append(item)
        
        if not creators:
            return '''<div class="gallery-creators">
  <p>No creator data available.</p>
</div>'''
        
        # Sort creators by count (descending) then by name
        sorted_creators = sorted(
            creators.items(),
            key=lambda x: (-len(x[1]), x[0])
        )
        
        creator_html = []
        creator_html.append('<div class="gallery-creators">')
        
        for creator_name, creator_items in sorted_creators:
            # Create a safe ID for the creator
            creator_id = creator_name.lower().replace(' ', '_').replace(',', '').replace('.', '').replace('(', '').replace(')', '')
            count = len(creator_items)
            
            # Get a representative icon based on creator name
            icon = '📸'  # Default
            if 'unknown' in creator_name.lower():
                icon = '❓'
            elif 'frank' in creator_name.lower() or 'parisi' in creator_name.lower():
                icon = '📷'
            elif 'will' in creator_name.lower() or 'keyworth' in creator_name.lower():
                icon = '🎯'
            elif 'paul' in creator_name.lower() or 'rohrkemper' in creator_name.lower():
                icon = '📸'
            elif 'al' in creator_name.lower() or 'schreitmueller' in creator_name.lower():
                icon = '📷'
            
            creator_html.append(f'''  <div class="creator-card" data-creator="{creator_id}">
    <h3>{icon} {creator_name}</h3>
    <p id="{creator_id}-count">{count} photos</p>
    <button class="view-photos-btn" onclick="viewCreator('{creator_id}')">View Photos</button>
  </div>''')
        
        creator_html.append('</div>')
        return '\n'.join(creator_html)
    
    def update_category_mapping(self) -> str:
        """Generate the updated category mapping for JavaScript."""
        categories = self.gallery_data.get('categories', {})
        
        # Normalize category names
        normalized_categories = {}
        for category_name in categories.keys():
            normalized_name = self.utils.normalize_category_name(category_name)
            normalized_categories[normalized_name] = normalized_name
        
        mapping_lines = []
        mapping_lines.append('  // Map lowercase category names to actual category names in the data')
        mapping_lines.append('  const categoryMap = {')
        
        # Add standard mappings
        standard_mappings = {
            'photos': 'Photos',
            'videos': 'Videos',
            'external_videos': 'External Videos'
        }
        
        for js_name, data_name in standard_mappings.items():
            if data_name in categories:
                mapping_lines.append(f"    '{js_name}': '{data_name}',")
        
        # Add dynamic category mappings
        for category_name in normalized_categories.keys():
            if category_name not in standard_mappings.values():
                js_name = category_name.lower().replace(' ', '_').replace(',', '').replace('.', '')
                mapping_lines.append(f"    '{js_name}': '{category_name}',")
        
        mapping_lines.append('  };')
        return '\n'.join(mapping_lines)
    
    def update_category_counts_function(self) -> str:
        """Generate the updated category counts function."""
        categories = self.gallery_data.get('categories', {})
        
        # Normalize category names
        normalized_categories = {}
        for category_name in categories.keys():
            normalized_name = self.utils.normalize_category_name(category_name)
            normalized_categories[normalized_name] = normalized_name
        
        function_lines = []
        function_lines.append('function updateCategoryCounts() {')
        function_lines.append('  if (!galleryData) return;')
        function_lines.append('  ')
        function_lines.append('  const categoryCounts = {')
        
        # Add standard categories
        function_lines.append("    'photos': galleryData.categories['Photos']?.length || 0,")
        
        # Add dynamic categories
        for category_name in sorted(normalized_categories.keys()):
            if category_name != 'Photos':
                js_name = category_name.lower().replace(' ', '_').replace(',', '').replace('.', '')
                function_lines.append(f"    '{js_name}': galleryData.categories['{category_name}']?.length || 0,")
        
        function_lines.append('  };')
        function_lines.append('  ')
        function_lines.append('  // Update each category count')
        function_lines.append('  for (const [category, count] of Object.entries(categoryCounts)) {')
        function_lines.append('    const element = document.getElementById(`${category}-count`);')
        function_lines.append('    if (element) {')
        function_lines.append('      if (category === \'photos\') {')
        function_lines.append('        element.textContent = `${count} photos from all events and activities`;')
        function_lines.append('      } else {')
        function_lines.append('        element.textContent = `${count} photos from ${category} events`;')
        function_lines.append('      }')
        function_lines.append('    }')
        function_lines.append('  }')
        function_lines.append('}')
        
        return '\n'.join(function_lines)
    
    def add_caption_field_to_gallery_data(self):
        """Add caption field to all media items in gallery data."""
        media_index = self.gallery_data.get('media_index', [])
        for item in media_index:
            if 'caption' not in item:
                item['caption'] = ''
        
        # Also add to categories, years, events, and collections
        for category_items in self.gallery_data.get('categories', {}).values():
            for item in category_items:
                if 'caption' not in item:
                    item['caption'] = ''
        
        for year_items in self.gallery_data.get('years', {}).values():
            for item in year_items:
                if 'caption' not in item:
                    item['caption'] = ''
        
        for event_items in self.gallery_data.get('events', {}).values():
            for item in event_items:
                if 'caption' not in item:
                    item['caption'] = ''
        
        for collection in self.gallery_data.get('collections', {}).values():
            for item in collection.get('media', []):
                if 'caption' not in item:
                    item['caption'] = ''
    
    def generate_gallery_page(self, output_path: str = "pages/gallery.md", create_backup: bool = False) -> bool:
        """Generate the complete gallery.md page."""
        if not self.load_gallery_data():
            return False
        
        # Add caption field to all media items
        self.add_caption_field_to_gallery_data()
        
        # Read the existing gallery.md
        template_path = Path("pages/gallery.md")
        
        # Create backup if requested (before reading template)
        if create_backup:
            output_path_obj = Path(output_path)
            if output_path_obj.exists():
                from datetime import datetime
                backup_path = output_path_obj.with_name(f'{output_path_obj.stem}.{datetime.now().strftime("%Y%m%d-%H%M%S")}-backup.md')
                output_path_obj.rename(backup_path)
                print(f"Created backup: {backup_path}")
                # Update template path to use the backup
                template_path = backup_path
        
        if not template_path.exists():
            print(f"Gallery file not found: {template_path}")
            return False
        
        with open(template_path, 'r') as f:
            template_content = f.read()
        
        # Generate dynamic sections
        category_section = self.generate_category_section()
        year_section = self.generate_year_section()
        creator_section = self.generate_creator_section()
        category_mapping = self.update_category_mapping()
        category_counts_function = self.update_category_counts_function()
        
        # Get current stats
        stats = self.gallery_data.get('stats', {})
        total_media = stats.get('total_media', 0)
        date_range = stats.get('date_range', {})
        earliest = date_range.get('earliest', 'unknown')
        latest = date_range.get('latest', 'unknown')
        
        # Update the content with new sections
        updated_content = self.update_gallery_content(
            template_content, 
            category_section, 
            year_section, 
            creator_section,
            category_mapping,
            category_counts_function,
            f"{earliest} - {latest}"
        )
        
        # Save the updated file
        output_path = Path(output_path)
        output_path.parent.mkdir(exist_ok=True)
        
        with open(output_path, 'w') as f:
            f.write(updated_content)
        
        print(f"✅ Generated gallery page: {output_path}")
        print(f"📊 Updated with {len(self.gallery_data.get('categories', {}))} categories and {len(self.gallery_data.get('years', {}))} years")
        print(f"📅 Date range: {earliest} - {latest}")
        print(f"📸 Total media: {total_media}")
        
        return True
    
    def update_gallery_content(self, content: str, category_section: str, year_section: str, 
                             creator_section: str, category_mapping: str, category_counts_function: str, 
                             date_range: str) -> str:
        """Update the gallery content with new sections."""
        import re
        
        # Replace category section
        category_pattern = r'## Browse by Category.*?(?=## Browse by Year|$)'
        content = re.sub(category_pattern, f'## Browse by Category\n\n{category_section}\n\n', content, flags=re.DOTALL)
        
        # Replace year section
        year_pattern = r'## Browse by Year.*?(?=## Browse by Creator|<!-- disabled|$)'
        content = re.sub(year_pattern, f'## Browse by Year\n\n{year_section}\n\n', content, flags=re.DOTALL)
        
        # Add creator section if it doesn't exist
        if '## Browse by Creator' not in content:
            # Find where to insert it (after year section, before disabled sections)
            insert_point = content.find('<!-- disabled')
            if insert_point == -1:
                insert_point = len(content)
            content = content[:insert_point] + f'## Browse by Creator\n\n{creator_section}\n\n' + content[insert_point:]
        else:
            # Replace existing creator section
            creator_pattern = r'## Browse by Creator.*?(?=<!-- disabled|$)'
            content = re.sub(creator_pattern, f'## Browse by Creator\n\n{creator_section}\n\n', content, flags=re.DOTALL)
        
        # Update JavaScript sections - be more precise to avoid duplicates
        # Replace category mapping - find the first occurrence only
        mapping_start = content.find('const categoryMap = {')
        if mapping_start != -1:
            mapping_end = content.find('};', mapping_start) + 2
            content = content[:mapping_start] + category_mapping + content[mapping_end:]
        
        # Replace category counts function - find the first occurrence only
        counts_start = content.find('function updateCategoryCounts() {')
        if counts_start != -1:
            # Find the matching closing brace
            brace_count = 0
            counts_end = counts_start
            for i, char in enumerate(content[counts_start:], counts_start):
                if char == '{':
                    brace_count += 1
                elif char == '}':
                    brace_count -= 1
                    if brace_count == 0:
                        counts_end = i + 1
                        break
            content = content[:counts_start] + category_counts_function + content[counts_end:]
        
        # Update date range
        content = re.sub(r'Date Range.*?(\d{4} - \d{4})', f'Date Range**: {date_range}', content)
        
        return content

def main():
    parser = argparse.ArgumentParser(description='Generate gallery.md page from gallery.json data')
    parser.add_argument('--gallery-data', default='assets/data/gallery.json',
                       help='Path to gallery.json file')
    parser.add_argument('--output', default='pages/gallery.md',
                       help='Output path for gallery.md file')
    parser.add_argument('--backup', action='store_true',
                       help='Create backup of existing gallery.md')
    
    args = parser.parse_args()
    
    # Generate the gallery page
    generator = GalleryPageGenerator(args.gallery_data)
    success = generator.generate_gallery_page(args.output, create_backup=args.backup)
    
    return 0 if success else 1

if __name__ == "__main__":
    from datetime import datetime
    exit(main())