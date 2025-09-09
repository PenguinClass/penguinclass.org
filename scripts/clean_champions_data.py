#!/usr/bin/env python3
import argparse, os, re, sys, time, copy, yaml
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

def load_yaml(path):
    with open(path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f) or []

def dump_yaml(path, data):
    with open(path, "w", encoding="utf-8") as f:
        yaml.safe_dump(data, f, sort_keys=False, allow_unicode=True, width=1200)

def text(x):
    return re.sub(r"\s+", " ", (x or "").strip())

def parse_legacy_rows(html_path):
    """Return dict[year] = {cells: [..], inferred flags, raw fields} from the legacy champions table."""
    with open(html_path, "r", encoding="utf-8", errors="ignore") as f:
        soup = BeautifulSoup(f.read(), "lxml")

    # pick the first substantial table
    tables = [t for t in soup.find_all("table") if t.find("tr")]
    if not tables:
        print(f"ERROR: no tables found in {html_path}", file=sys.stderr)
        return {}
    rows_out = {}
    for t in tables:
        for tr in t.find_all("tr"):
            cells = [text(td.get_text(" ", strip=True)) for td in tr.find_all(["td","th"])]
            if not cells or len(cells) < 3: 
                continue
            # find a 4-digit year in row
            yr = None
            for c in cells:
                m = re.search(r"\b(19\d{2}|20\d{2})\b", c)
                if m: yr = int(m.group(1)); break
            if not yr: 
                continue

            # Actual table structure (6 columns):
            # [Year, Skipper, Crew, Host Club/Location, North American Champ*, Location]
            # Column 4 (Host Club/Location) is International Location
            # Column 5 (NA Champ) and Column 6 (Location) are North American data
            na_crew = na_loc = ""
            if len(cells) >= 6:
                na_crew = cells[4] if len(cells) > 4 else ""  # Column 5: North American Champ
                na_loc = cells[5] if len(cells) > 5 else ""    # Column 6: North American Location

            # Map main columns (best-effort)
            # Assume standard order near front of row
            yr_idx = next((i for i,c in enumerate(cells) if re.search(r"\b(19\d{2}|20\d{2})\b", c)), 0)
            # take a slice of next columns after year index
            after = cells[yr_idx+1:]
            skipper = after[0] if len(after) > 0 else ""
            crew    = after[1] if len(after) > 1 else ""
            club    = after[2] if len(after) > 2 else ""  # This is "Host Club, Location" (International)
            # Note: No separate boat column exists

            rows_out[yr] = {
                "cells": cells,
                "year": yr,
                "skipper": skipper,
                "crew": crew,
                "club_cell": club,
                "na_crew": na_crew,
                "na_location": na_loc,
            }
    return rows_out

SEP_RE = re.compile(r"\s+[-–—]\s+")
def split_club_and_location(club_cell):
    """
    Split a combined 'Club [dash] City, Country' OR 'Club, City, Country' into (club, location).
    Return (club_only, intl_location) or (club_cell, "") if unsure.
    """
    s = text(club_cell)
    if not s:
        return "", ""
    # First, try "Club — City, Country" style
    if SEP_RE.search(s):
        parts = SEP_RE.split(s, maxsplit=1)
        if len(parts) == 2:
            club = text(parts[0])
            loc  = text(parts[1])
            return club, loc
    # Else try by commas: assume last two segments form a location
    parts = [p.strip() for p in s.split(",")]
    if len(parts) >= 3:
        club = ", ".join(parts[:-2]).strip()
        loc  = ", ".join(parts[-2:]).strip()
        if club and loc:
            return club, loc
    if len(parts) == 2:
        # Sometimes "Club, City" (country omitted)
        club, loc = parts[0].strip(), parts[1].strip()
        if club and loc:
            return club, loc
    # Fallback: no reliable split
    return s, ""

def is_non_us_club_location_guess(s):
    """Light heuristic to guess if a location text is non-US (country keywords)."""
    s = s.lower()
    return any(k in s for k in [
        "canada","ontario","quebec","brazil","canadá","argentina","uruguay","chile",
        "uk","united kingdom","england","scotland","wales","ireland",
        "australia","new zealand","japan","china","india","south africa",
        "germany","france","italy","spain","portugal","netherlands","belgium",
        "sweden","norway","denmark","finland","poland","czech","austria","switzerland"
    ])

def clean_champions_data(legacy_rows, champions_yml_path):
    """
    Clean and enhance champions data based on legacy HTML parsing.
    Returns cleaned champions list.
    """
    existing = load_yaml(champions_yml_path)
    
    # Create lookup by year for existing entries
    existing_by_year = {c.get("year"): c for c in existing}
    
    cleaned = []
    
    for year, legacy_data in legacy_rows.items():
        existing_entry = existing_by_year.get(year)
        
        if existing_entry:
            # Enhance existing entry with legacy data if available
            enhanced = copy.deepcopy(existing_entry)
            
            # Try to improve club/location parsing
            club_cell = legacy_data.get("club_cell", "")
            if club_cell and not enhanced.get("club"):
                club, loc = split_club_and_location(club_cell)
                if club and not enhanced.get("club"):
                    enhanced["club"] = clean_club_name(club)
                if loc and not enhanced.get("location"):
                    enhanced["location"] = clean_club_name(loc)
            
            # Check for North American data
            na_crew = legacy_data.get("na_crew", "")
            na_loc = legacy_data.get("na_location", "")
            
            if na_crew or na_loc:
                # Create or update North American entry
                na_result_id = f"northamerica-{year}"
                na_entry = {
                    "year": year,
                    "result_id": na_result_id,
                    "skipper": na_crew.split("&")[0].strip() if "&" in na_crew else na_crew,
                    "crew": na_crew.split("&")[1].strip() if "&" in na_crew else "",
                    "club": "",
                    "location": clean_club_name(na_loc),
                    "boat": "",
                    "results_url": ""
                }
                
                # Check if this NA entry already exists
                existing_na = next((c for c in existing if c.get("result_id") == na_result_id), None)
                if not existing_na:
                    cleaned.append(na_entry)
                    print(f"Added NA champion for {year}: {na_entry['skipper']} at {na_entry['location']}")
            
            cleaned.append(enhanced)
        else:
            # Create new entry from legacy data
            club_cell = legacy_data.get("club_cell", "")
            club, loc = split_club_and_location(club_cell)
            
            new_entry = {
                "year": year,
                "result_id": f"intl-{year}",
                "skipper": legacy_data.get("skipper", ""),
                "crew": legacy_data.get("crew", ""),
                "club": clean_club_name(club),
                "location": clean_club_name(loc),
                "boat": "",
                "results_url": ""
            }
            
            cleaned.append(new_entry)
            print(f"Added new champion for {year}: {new_entry['skipper']} at {new_entry['location']}")
    
    # Sort by year (newest first)
    cleaned.sort(key=lambda x: x.get("year", 0), reverse=True)
    
    return cleaned

def main():
    parser = argparse.ArgumentParser(description="Clean and enhance champions data")
    parser.add_argument("--html", default="archive/legacy-website/champions.html", help="Path to legacy champions HTML")
    parser.add_argument("--yaml", default="_data/champions.yml", help="Path to champions YAML file")
    parser.add_argument("--output", default="_data/champions_cleaned.yml", help="Output path for cleaned data")
    parser.add_argument("--dry-run", action="store_true", help="Show what would be changed without writing")
    
    args = parser.parse_args()
    
    if not os.path.exists(args.html):
        print(f"ERROR: HTML file not found: {args.html}", file=sys.stderr)
        sys.exit(1)
    
    if not os.path.exists(args.yaml):
        print(f"ERROR: YAML file not found: {args.yaml}", file=sys.stderr)
        sys.exit(1)
    
    print("Parsing legacy HTML...")
    legacy_rows = parse_legacy_rows(args.html)
    print(f"Found {len(legacy_rows)} years in legacy data")
    
    print("Cleaning champions data...")
    cleaned_data = clean_champions_data(legacy_rows, args.yaml)
    print(f"Generated {len(cleaned_data)} champion entries")
    
    if args.dry_run:
        print("\nDRY RUN - Would write to:", args.output)
        print("Sample entries:")
        for i, entry in enumerate(cleaned_data[:5]):
            print(f"  {entry}")
    else:
        print(f"\nWriting cleaned data to: {args.output}")
        dump_yaml(args.output, cleaned_data)
        print("Done!")

if __name__ == "__main__":
    main()
