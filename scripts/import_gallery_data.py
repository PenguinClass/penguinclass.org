#!/usr/bin/env python3
"""
Import gallery data for a specific directory with custom metadata.

This script creates gallery data for a specific directory with configurable
metadata like date, source, credit, etc.
"""

import json
import argparse
from pathlib import Path
from datetime import datetime
import sys
sys.path.append(str(Path(__file__).parent))
from lib.gallery_importer import GalleryImporter
class ImportGalleryImporter:
    """Wrapper class for import functionality using the common GalleryImporter."""
    
    def __init__(self, import_path: str, date: str = None, source: str = None, 
                 credit: str = None, event: str = None, location: str = None, 
                 pattern: str = None):
        self.importer = GalleryImporter(
            import_path=import_path,
            date=date,
            source=source,
            credit=credit,
            event=event,
            location=location,
            pattern=pattern
        )
    
    def save_gallery_data(self, output_file: str = None, merge_to_main: bool = False):
        """Save the gallery data to a JSON file or merge into main gallery."""
        gallery_data = self.importer.generate_gallery_data()
        
        if not gallery_data:
            print("No data to save.")
            return
        
        if merge_to_main:
            # Merge directly into main gallery
            self.importer.merge_to_main_gallery(gallery_data)
        else:
            # Save as separate import file
            if not output_file:
                output_file = f"assets/data/gallery-import-{datetime.now().strftime('%Y%m%d-%H%M%S')}.json"
            
            output_path = Path(output_file)
            output_path.parent.mkdir(exist_ok=True)
            
            with open(output_path, 'w') as f:
                json.dump(gallery_data, f, indent=2)
            
            print(f"Gallery data saved to {output_path}")
        
        # Print summary
        stats = gallery_data['stats']
        print(f"\n📊 Import Summary:")
        print(f"Total media: {stats['total_media']}")
        print(f"Photos: {stats['photos']}")
        print(f"Videos: {stats['videos']}")
        print(f"Years: {stats['years_count']}")
        print(f"Events: {stats['events_count']}")
        print(f"Date range: {stats['date_range']['earliest']} - {stats['date_range']['latest']}")
        
        if 'import_info' in stats:
            import_info = stats['import_info']
            print(f"\n📁 Import Information:")
            print(f"Date: {import_info['date']}")
            print(f"Source: {import_info['source']}")
            print(f"Credit: {import_info['credit']}")
            print(f"Event: {import_info['event']}")
            print(f"Location: {import_info['location']}")
            print(f"Path: {import_info['import_path']}")
        
        # Print collection summaries
        print(f"\n📁 Collections:")
        for name, collection in gallery_data['collections'].items():
            print(f"  {collection['title']}: {len(collection['media'])} items")

def main():
    parser = argparse.ArgumentParser(description='Import gallery data for a specific directory')
    parser.add_argument('import_path', help='Path to directory containing media files')
    parser.add_argument('--date', help='Date of the event (YYYY-MM-DD format)')
    parser.add_argument('--source', default='import', help='Source of the media (default: import)')
    parser.add_argument('--credit', help='Photographer/videographer credit')
    parser.add_argument('--event', help='Event name')
    parser.add_argument('--location', help='Event location')
    parser.add_argument('--pattern', help='Filename pattern to filter files (supports wildcards like *.jpg, *championship*, etc.)')
    parser.add_argument('--output', help='Output JSON file path')
    parser.add_argument('--merge', action='store_true', 
                       help='Merge directly into main gallery.json instead of creating separate import file')
    
    args = parser.parse_args()
    
    # Create importer
    importer = ImportGalleryImporter(
        import_path=args.import_path,
        date=args.date,
        source=args.source,
        credit=args.credit,
        event=args.event,
        location=args.location,
        pattern=args.pattern
    )
    
    # Save gallery data
    importer.save_gallery_data(args.output, merge_to_main=args.merge)

if __name__ == "__main__":
    main()
