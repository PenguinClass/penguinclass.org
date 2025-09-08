#!/usr/bin/env python3
import argparse, os, re, sys, time, yaml, json
from bs4 import BeautifulSoup
import requests

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

def parse_table(table):
    """Parse a champions table and return list of champion data."""
    items = []
    rows = table.find_all("tr")
    
    for row in rows[1:]:  # Skip header row
        cells = row.find_all(["td", "th"])
        if len(cells) < 6:
            continue
            
        # Extract text from cells
        year_cell = cells[0].get_text(strip=True)
        skipper_cell = cells[1].get_text(strip=True)
        crew_cell = cells[2].get_text(strip=True)
        club_location_cell = cells[3].get_text(strip=True)  # Column 4: International Host Club/Location
        na_crew_cell = cells[4].get_text(strip=True)       # Column 5: North American Champion
        na_location_cell = cells[5].get_text(strip=True)   # Column 6: North American Location
        
        # Extract year
        year_match = re.search(r'(\d{4})', year_cell)
        if not year_match:
            continue
        year = int(year_match.group(1))
        
        # Skip war years
        if year in [1942, 1943, 1944]:
            continue
            
        # Clean club/location data
        club_location = clean_club_name(club_location_cell)
        
        # Parse skipper and crew
        skipper = skipper_cell.strip()
        crew = crew_cell.strip()
        
        # Create international champion entry
        if skipper and skipper != "Suspended for WW II":
            items.append({
                "year": year,
                "result_id": f"intl-{year}",
                "skipper": skipper,
                "crew": crew,
                "club": "",  # Will be parsed from club_location
                "location": "",  # Will be parsed from club_location
                "boat": "",
                "results_url": ""
            })
        
        # Create North American champion entry if data exists
        if na_crew_cell and na_location_cell and na_crew_cell.strip() and na_location_cell.strip():
            # Parse skipper and crew from NA data
            na_skipper = na_crew_cell.strip()
            na_crew = ""
            if "&" in na_crew_cell:
                parts = na_crew_cell.split("&")
                na_skipper = parts[0].strip()
                na_crew = parts[1].strip() if len(parts) > 1 else ""
            
            items.append({
                "year": year,
                "result_id": f"northamerica-{year}",
                "skipper": na_skipper,
                "crew": na_crew,
                "club": "",
                "location": na_location_cell.strip(),
                "boat": "",
                "results_url": ""
            })
    
    return items

def parse_list_items(soup):
    """Parse list items if no tables found."""
    items = []
    list_items = soup.find_all("li")
    
    for li in list_items:
        text = li.get_text(strip=True)
        year_match = re.search(r'(\d{4})', text)
        if year_match:
            year = int(year_match.group(1))
            if year in [1942, 1943, 1944]:
                continue
                
            # Extract skipper and crew
            skipper_match = re.search(r'([A-Z][a-z]+ [A-Z][a-z]+)', text)
            crew_match = re.search(r'with ([A-Z][a-z]+ [A-Z][a-z]+)', text)
            
            skipper = skipper_match.group(1) if skipper_match else ""
            crew = crew_match.group(1) if crew_match else ""
            
            if skipper:
                items.append({
                    "year": year,
                    "result_id": f"intl-{year}",
                    "skipper": skipper,
                    "crew": crew,
                    "club": "",
                    "location": "",
                    "boat": "",
                    "results_url": ""
                })
    
    return items

def absolutize(base_url, items):
    """Convert relative URLs to absolute URLs."""
    for item in items:
        if item.get("results_url") and not item["results_url"].startswith(("http://", "https://")):
            if item["results_url"].startswith("/"):
                item["results_url"] = base_url.rstrip("/") + item["results_url"]
            else:
                item["results_url"] = base_url.rstrip("/") + "/" + item["results_url"]
    return items

def enrich_from_regattanetwork(items):
    """Enrich data from RegattaNetwork if available."""
    # This could be expanded to fetch additional data
    # For now, just return items as-is
    return items

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--source", default="archive/legacy-website/champions.html")
    ap.add_argument("--out-yaml", default="_data/champions.yml")
    ap.add_argument("--out-json", default="assets/data/champions.json")
    ap.add_argument("--emit-markdown", action="store_true")
    args = ap.parse_args()

    # load HTML
    html, base = "", ""
    if os.path.exists(args.source):
        base = "https://www.penguinclass.com/"
        html = open(args.source, "r", encoding="utf-8", errors="ignore").read()
    else:
        url = "https://www.penguinclass.com/champions.html"
        r = requests.get(url, timeout=20, headers={"User-Agent":"Mozilla/5.0"})
        r.raise_for_status()
        html = r.text; base = url

    soup = BeautifulSoup(html, "lxml")
    items = []
    
    # Try to find tables first
    tables = soup.find_all("table")
    if tables:
        for table in tables:
            table_items = parse_table(table)
            items.extend(table_items)
    
    # If no tables found, try list items
    if not items:
        items = parse_list_items(soup)
    
    if not items:
        print("ERROR: No champion data found", file=sys.stderr)
        sys.exit(1)

    items = absolutize(base, items)
    items = enrich_from_regattanetwork(items)

    # Group by result_id to avoid duplicates
    unique_items = {}
    for item in items:
        result_id = item["result_id"]
        if result_id not in unique_items:
            unique_items[result_id] = item
        else:
            # Merge data if we have more complete information
            existing = unique_items[result_id]
            for key in ["skipper", "crew", "club", "location", "boat", "results_url"]:
                if not existing.get(key) and item.get(key):
                    existing[key] = item[key]

    # Convert back to list and sort by year
    champions = list(unique_items.values())
    champions.sort(key=lambda x: x["year"], reverse=True)

    # Parse club/location from the combined field
    for champ in champions:
        if "club_location" in champ:
            # This would need to be implemented based on the actual data structure
            pass

    os.makedirs(os.path.dirname(args.out_yaml), exist_ok=True)
    with open(args.out_yaml, "w", encoding="utf-8") as f:
        yaml.safe_dump(champions, f, sort_keys=False, allow_unicode=True, width=1200)

    os.makedirs(os.path.dirname(args.out_json), exist_ok=True)
    with open(args.out_json, "w", encoding="utf-8") as f:
        json.dump(champions, f, ensure_ascii=False)

    print(f"wrote {args.out_yaml} and {args.out_json} ({len(champions)} champions)")

    if args.emit_markdown:
        os.makedirs("_results", exist_ok=True)
        for c in champions:
            y = c["year"]
            series = "International Championship" if "intl-" in c["result_id"] else "North American Championship"
            path = os.path.join("_results", f"{y}-{series.lower().replace(' ', '-')}.md")
            fm = {
                "layout": "result",
                "id": c["result_id"],
                "title": f"{series} {y}",
                "date": f"{y}-01-01",
                "year": y,
                "series": series,
                "is_championship": True,
                "venue": "",
                "location": c.get("location", ""),
                "results_url": c.get("results_url", ""),
            }
            if not os.path.exists(path):
                with open(path, "w", encoding="utf-8") as f:
                    f.write("---\n")
                    f.write(yaml.safe_dump(fm, sort_keys=False).strip())
                    f.write("\n---\nShort event summary goes here.\n")
                print("created:", path)

if __name__ == "__main__":
    main()
