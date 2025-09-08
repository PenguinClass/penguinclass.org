#!/usr/bin/env python3
import argparse, os, re, sys, yaml, json
from bs4 import BeautifulSoup

def clean_club_name(club_text):
    """Clean and expand club abbreviations and standardize names."""
    if not club_text:
        return ""
    
    club_text = club_text.strip()
    
    # Specific club mappings
    club_mappings = {
        "AYC": "Annapolis Yacht Club, Annapolis, MD",
        "BYC": "Baltimore Yacht Club, Baltimore, MD", 
        "CYC": "Cambridge Yacht Club, Cambridge, MD",
        "MRYC": "Miles River Yacht Club, St. Michaels, MD",
        "TAYC": "Tred Avon Yacht Club, Oxford, MD",
        "WRSC": "West River Sailing Club, Galesville, MD",
        "SSA, Annapolis MD": "Severn Sailing Association, Annapolis, MD",
        "Sayville MD": "Sayville Yacht Club, Sayville, MD",
        "Sea Side NJ": "Seaside Park Yacht Club, Seaside Park, NJ",
        "Mattituck YC, NY": "Mattituck Yacht Club, Mattituck, NY"
    }
    
    # Check for exact matches first
    if club_text in club_mappings:
        return club_mappings[club_text]
    
    # Special year-specific corrections
    if "1976" in club_text and "Buenos Aires" in club_text:
        return "Yacht Club Olivos, Buenos Aires, Argentina"
    if "1991" in club_text and "Rio de Janeiro" in club_text:
        return "Rio de Janeiro Yacht Club, Rio de Janeiro, Brazil"
    if "1997" in club_text and "Rio Grande, Brazil" in club_text:
        return "Clube Naval, Rio de Janeiro, Brazil"
    
    # Expand YC abbreviation to Yacht Club
    club_text = re.sub(r'\bYC\b', 'Yacht Club', club_text)
    
    # Handle "Cambridge, MD" -> "Cambridge Yacht Club, Cambridge, MD"
    if club_text == "Cambridge, MD":
        return "Cambridge Yacht Club, Cambridge, MD"
    
    return club_text

def extract_north_american_champions(html_file):
    """Extract North American Champions from columns 5 and 6 where data exists"""

    with open(html_file, 'r', encoding='utf-8', errors='ignore') as f:
        html_content = f.read()

    soup = BeautifulSoup(html_content, 'lxml')

    tables = soup.find_all('table')
    target_table = None

    for table in tables:
        if table.find(string=re.compile(r'North American Champ', re.I)):
            target_table = table
            break

    if not target_table:
        print("Could not find North American Champions table")
        return []

    rows = target_table.find_all('tr')
    if len(rows) < 2:
        print("Table has insufficient rows")
        return []

    champions = []

    for row in rows[1:]:
        cells = row.find_all(['td', 'th'])
        if len(cells) < 6:
            continue

        # Check if there's actual data in columns 5 and 6 (North American data)
        col_5 = cells[4].get_text(strip=True) if len(cells) > 4 else ""  # North American Champ
        col_6 = cells[5].get_text(strip=True) if len(cells) > 5 else ""  # North American Location

        # Skip rows where both North American columns are empty
        if not col_5 and not col_6:
            continue

        year_cell = cells[0]
        year_link = year_cell.find('a')
        if not year_link:
            continue

        year_text = year_link.get_text(strip=True)
        year_match = re.search(r'(\d{4})', year_text)
        if not year_match:
            continue

        year = int(year_match.group(1))
        
        # Skip 1941 as requested
        if year == 1941:
            continue

        skipper = ""
        crew = ""
        results_url = ""

        if col_5:
            col_5_links = cells[4].find_all('a')
            for link in col_5_links:
                href = link.get('href', '')
                if href and ('NA' in href or 'NAl' in href):
                    results_url = href
                    link_text = link.get_text(strip=True)
                    if '&' in link_text:
                        parts = link_text.split('&')
                        skipper = parts[0].strip()
                        crew = parts[1].strip()
                    else:
                        skipper = link_text
                    break

        # Clean the location data
        location = clean_club_name(col_6) if col_6 else ""

        skipper = re.sub(r'\s+', ' ', skipper).strip()
        crew = re.sub(r'\s+', ' ', crew).strip()
        location = re.sub(r'\s+', ' ', location).strip()

        if skipper and results_url:
            champion = {
                "year": year,
                "result_id": f"northamerica-{year}",
                "skipper": skipper,
                "crew": crew,
                "club": "",
                "location": location,
                "boat": "",
                "results_url": results_url
            }
            champions.append(champion)
            print(f"Extracted: {year} - {skipper} & {crew} at {location} -> {results_url}")

    return champions

def update_champions_yml(champions, yaml_file):
    """Update the champions.yml file with new North American champions"""
    
    # Load existing data
    if os.path.exists(yaml_file):
        with open(yaml_file, 'r', encoding='utf-8') as f:
            existing_champions = yaml.safe_load(f) or []
    else:
        existing_champions = []
    
    # Create lookup by result_id
    existing_by_id = {c.get("result_id"): c for c in existing_champions}
    
    # Update or add North American champions
    updated = False
    for na_champ in champions:
        result_id = na_champ["result_id"]
        if result_id in existing_by_id:
            # Update existing entry
            existing = existing_by_id[result_id]
            for key, value in na_champ.items():
                if value and not existing.get(key):
                    existing[key] = value
                    updated = True
                    print(f"Updated {result_id}: {key} = {value}")
        else:
            # Add new entry
            existing_champions.append(na_champ)
            updated = True
            print(f"Added new {result_id}")
    
    if updated:
        # Sort by year (newest first)
        existing_champions.sort(key=lambda x: x.get("year", 0), reverse=True)
        
        # Write back to file
        with open(yaml_file, 'w', encoding='utf-8') as f:
            yaml.safe_dump(existing_champions, f, sort_keys=False, allow_unicode=True, width=1200)
        print(f"Updated {yaml_file}")
    else:
        print("No updates needed")
    
    return existing_champions

def regenerate_json(champions, json_file):
    """Regenerate the champions.json file"""
    os.makedirs(os.path.dirname(json_file), exist_ok=True)
    
    with open(json_file, 'w', encoding='utf-8') as f:
        json.dump(champions, f, ensure_ascii=False, indent=2)
    
    print(f"Regenerated {json_file}")

def create_result_pages(champions):
    """Create _results/*.md files for North American champions"""
    os.makedirs("_results", exist_ok=True)
    
    created_count = 0
    for champ in champions:
        if not champ.get("result_id", "").startswith("northamerica-"):
            continue
            
        year = champ["year"]
        filename = f"{year}-north-american-championship.md"
        filepath = os.path.join("_results", filename)
        
        if not os.path.exists(filepath):
            front_matter = {
                "layout": "result",
                "id": champ["result_id"],
                "title": f"North American Championship {year}",
                "date": f"{year}-01-01",
                "year": year,
                "series": "North American Championship",
                "is_championship": True,
                "venue": "",
                "location": champ.get("location", ""),
                "results_url": champ.get("results_url", ""),
            }
            
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write("---\n")
                f.write(yaml.safe_dump(front_matter, sort_keys=False).strip())
                f.write("\n---\nNorth American Championship event summary goes here.\n")
            
            created_count += 1
            print(f"Created: {filepath}")
    
    if created_count > 0:
        print(f"Created {created_count} new result pages")
    else:
        print("No new result pages needed")

def main():
    parser = argparse.ArgumentParser(description="Extract North American Champions from champions.html")
    parser.add_argument("--html", default="archive/legacy-website/champions.html", help="Path to champions.html")
    parser.add_argument("--yaml", default="_data/champions.yml", help="Path to champions.yml")
    parser.add_argument("--json", default="assets/data/champions.json", help="Path to champions.json")
    parser.add_argument("--create-pages", action="store_true", help="Create _results/*.md files")
    
    args = parser.parse_args()
    
    if not os.path.exists(args.html):
        print(f"ERROR: HTML file not found: {args.html}")
        sys.exit(1)
    
    print("Extracting North American Champions...")
    na_champions = extract_north_american_champions(args.html)
    
    if not na_champions:
        print("No North American champions found")
        sys.exit(1)
    
    print(f"Found {len(na_champions)} North American champions")
    
    # Update champions.yml
    all_champions = update_champions_yml(na_champions, args.yaml)
    
    # Regenerate JSON
    regenerate_json(all_champions, args.json)
    
    # Create result pages if requested
    if args.create_pages:
        create_result_pages(all_champions)
    
    print("Done!")

if __name__ == "__main__":
    main()
