#!/usr/bin/env python3
"""
Unified gallery management script for both generating and importing gallery data.

This script can operate in two modes:
1. Generate mode: Process existing analysis data to create gallery.json
2. Import mode: Import media from a specific directory with custom metadata

Usage:
    # Generate mode (default)
    python gallery_manager.py

    # Import mode
    python gallery_manager.py import /path/to/media --date 2024-01-01 --event "Championship" --credit "John Doe"
"""

import json
import argparse
from pathlib import Path
from datetime import datetime
import sys
sys.path.append(str(Path(__file__).parent))
from lib.gallery_importer import GalleryImporter

class GalleryManager:
    """Unified gallery manager for both generate and import operations."""
    
    def __init__(self):
        self.importer = GalleryImporter()
    
    def load_analysis_data(self) -> dict:
        """Load the photo analysis data for generate mode."""
        analysis_file = Path("tmp/gallery_analysis.json")
        if not analysis_file.exists():
            print("Error: tmp/gallery_analysis.json not found. Run analyze_photos.py first.")
            return {}
        
        with open(analysis_file, 'r') as f:
            return json.load(f)
    
    def generate_mode(self):
        """Run in generate mode - process analysis data to create gallery.json."""
        print("🔄 Running in GENERATE mode...")
        print("Loading media analysis data...")
        analysis_data = self.load_analysis_data()
        
        if not analysis_data:
            print("❌ No analysis data found. Exiting.")
            return False
        
        print("Generating enhanced gallery data structure...")
        gallery_data = self.importer.generate_gallery_data(analysis_data)
        
        if not gallery_data:
            print("❌ No gallery data generated. Exiting.")
            return False
        
        # Save the gallery data
        output_file = Path("assets/data/gallery.json")
        output_file.parent.mkdir(exist_ok=True)
        
        with open(output_file, 'w') as f:
            json.dump(gallery_data, f, indent=2)
        
        print(f"✅ Enhanced gallery data saved to {output_file}")
        
        # Print summary
        stats = gallery_data['stats']
        print(f"\n📊 Gallery Summary:")
        print(f"Total media: {stats['total_media']}")
        print(f"Photos: {stats['photos']}")
        print(f"Videos: {stats['videos']}")
        print(f"External videos: {stats['external_videos']}")
        print(f"Duplicates removed: {stats['total_duplicates_removed']}")
        print(f"Years: {stats['years_count']}")
        print(f"Events: {stats['events_count']}")
        print(f"Date range: {stats['date_range']['earliest']} - {stats['date_range']['latest']}")
        
        # Print credit statistics
        credits = stats['credits']
        print(f"\n📸 Credit Statistics:")
        print(f"Credited media: {credits['total_credited']}")
        print(f"Unknown credits: {credits['total_unknown']}")
        print(f"Unique credits: {credits['unique_credits']}")
        print(f"Top credits:")
        for credit, count in credits['top_credits'][:5]:
            print(f"  - {credit}: {count} items")
        
        # Print collection summaries
        print(f"\n📁 Collections:")
        for name, collection in gallery_data['collections'].items():
            print(f"  {collection['title']}: {len(collection['media'])} items")
        
        return True
    
    def import_mode(self, import_path: str, date: str = None, source: str = None, 
                   credit: str = None, event: str = None, location: str = None,
                   pattern: str = None, output_file: str = None, merge_to_main: bool = False):
        """Run in import mode - import media from a specific directory."""
        print("🔄 Running in IMPORT mode...")
        
        # Create importer with import-specific parameters
        importer = GalleryImporter(
            import_path=import_path,
            date=date,
            source=source,
            credit=credit,
            event=event,
            location=location,
            pattern=pattern
        )
        
        gallery_data = importer.generate_gallery_data()
        
        if not gallery_data:
            print("❌ No data to save.")
            return False
        
        if merge_to_main:
            # Merge directly into main gallery
            importer.merge_to_main_gallery(gallery_data)
        else:
            # Save as separate import file
            if not output_file:
                output_file = f"assets/data/gallery-import-{datetime.now().strftime('%Y%m%d-%H%M%S')}.json"
            
            output_path = Path(output_file)
            output_path.parent.mkdir(exist_ok=True)
            
            with open(output_path, 'w') as f:
                json.dump(gallery_data, f, indent=2)
            
            print(f"✅ Gallery data saved to {output_path}")
        
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
        
        return True

def main():
    parser = argparse.ArgumentParser(
        description='Unified gallery management script for generating and importing gallery data',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Generate mode (default)
  python gallery_manager.py

  # Import mode
  python gallery_manager.py import /path/to/media --date 2024-01-01 --event "Championship" --credit "John Doe"
  
  # Import and merge to main gallery
  python gallery_manager.py import /path/to/media --merge --event "Regatta" --location "TAYC"
        """
    )
    
    subparsers = parser.add_subparsers(dest='mode', help='Operation mode')
    
    # Generate mode (default)
    generate_parser = subparsers.add_parser('generate', help='Generate gallery data from analysis (default mode)')
    
    # Import mode
    import_parser = subparsers.add_parser('import', help='Import media from a directory')
    import_parser.add_argument('import_path', help='Path to directory containing media files')
    import_parser.add_argument('--date', help='Date of the event (YYYY-MM-DD format)')
    import_parser.add_argument('--source', default='import', help='Source of the media (default: import)')
    import_parser.add_argument('--credit', help='Photographer/videographer credit')
    import_parser.add_argument('--event', help='Event name')
    import_parser.add_argument('--location', help='Event location')
    import_parser.add_argument('--pattern', help='Filename pattern to filter files (supports wildcards like *.jpg, *championship*, etc.)')
    import_parser.add_argument('--output', help='Output JSON file path')
    import_parser.add_argument('--merge', action='store_true', 
                             help='Merge directly into main gallery.json instead of creating separate import file')
    
    args = parser.parse_args()
    
    manager = GalleryManager()
    
    # If no mode specified, default to generate
    if args.mode is None or args.mode == 'generate':
        success = manager.generate_mode()
    elif args.mode == 'import':
        success = manager.import_mode(
            import_path=args.import_path,
            date=args.date,
            source=args.source,
            credit=args.credit,
            event=args.event,
            location=args.location,
            pattern=args.pattern,
            output_file=args.output,
            merge_to_main=args.merge
        )
    else:
        print(f"❌ Unknown mode: {args.mode}")
        return 1
    
    return 0 if success else 1

if __name__ == "__main__":
    exit(main())
