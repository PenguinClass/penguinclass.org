#!/usr/bin/env python3
import os, re, sys, time, shutil, yaml, csv, argparse
from pathlib import Path
from urllib.parse import urljoin, urlparse
import requests
from bs4 import BeautifulSoup

Y = lambda p: yaml.safe_load(Path(p).read_text(encoding="utf-8")) if Path(p).exists() else None
W = lambda p,d: Path(p).write_text(yaml.safe_dump(d, sort_keys=False, allow_unicode=True, width=1200), encoding="utf-8")

def fm_split(txt):
    m = re.match(r"^---\s*\n(.*?)\n---\s*\n(.*)$", txt, re.S)
    if not m: return {}, txt
    return yaml.safe_load(m.group(1)) or {}, m.group(2)

def fm_join(fm, body):
    return "---\n" + yaml.safe_dump(fm, sort_keys=False).strip() + "\n---\n" + body

def load_normalization():
    """Load club aliases and split hints from normalization.yml"""
    norm_path = Path("_data/normalization.yml")
    if not norm_path.exists():
        return {}, []
    
    data = Y(norm_path)
    return data.get("club_aliases", {}), data.get("split_hints", [])

def parse_champions_html(html_path, only_years=None):
    """Parse the champions HTML table and extract data"""
    # Try different encodings
    encodings = ['utf-8', 'latin-1', 'cp1252', 'iso-8859-1']
    content = None
    
    for encoding in encodings:
        try:
            with open(html_path, 'r', encoding=encoding) as f:
                content = f.read()
            break
        except UnicodeDecodeError:
            continue
    
    if content is None:
        raise ValueError(f"Could not decode {html_path} with any supported encoding")
    
    soup = BeautifulSoup(content, 'html.parser')
    table = soup.find('table')
    if not table:
        raise ValueError("No table found in HTML")
    
    rows = table.find_all('tr')[1:]  # Skip header
    champions = []
    
    for row in rows:
        cells = [td.get_text(strip=True) for td in row.find_all(['td', 'th'])]
        if len(cells) < 6:
            continue
            
        year = cells[0]
        if not year.isdigit():
            continue
            
        year = int(year)
        if only_years and year not in only_years:
            continue
        
        # Extract results URL from first link that looks like results
        results_url = None
        for link in row.find_all('a', href=True):
            href = link['href']
            if any(pattern in href.lower() for pattern in ['result', 'regattanetwork', '.pdf', '.htm', '.html']):
                results_url = urljoin(str(html_path), href)
                break
        
        # Parse International data
        intl_skipper = cells[1]
        intl_crew = cells[2]
        intl_host = cells[3]
        
        # Parse North American data
        na_champion = cells[4]
        na_location = cells[5]
        
        # Parse NA champion (skipper [& crew])
        na_skipper = na_crew = ""
        if na_champion:
            if " & " in na_champion or " and " in na_champion:
                parts = re.split(r'\s+(?:&|and)\s+', na_champion, 1)
                na_skipper = parts[0].strip()
                na_crew = parts[1].strip() if len(parts) > 1 else ""
            else:
                na_skipper = na_champion.strip()
        
        # Add International champion if present
        if intl_skipper:
            champions.append({
                'year': year,
                'series': 'international',
                'skipper': intl_skipper,
                'crew': intl_crew,
                'host_info': intl_host,
                'results_url': results_url
            })
        
        # Add North American champion if present
        if na_skipper:
            champions.append({
                'year': year,
                'series': 'north-american',
                'skipper': na_skipper,
                'crew': na_crew,
                'host_info': na_location,
                'results_url': results_url
            })
    
    return champions

def normalize_club_location(host_info, club_aliases):
    """Split host_info into club and location using normalization rules"""
    if not host_info:
        return "", ""
    
    # Check for exact alias match first
    for alias, full_name in club_aliases.items():
        if alias.lower() in host_info.lower():
            # Extract location from full name (after last comma)
            parts = full_name.split(',')
            if len(parts) >= 2:
                club = parts[0].strip()
                location = ','.join(parts[1:]).strip()
                return club, location
            return full_name, ""
    
    # Try to split on common patterns
    patterns = [
        r'(.+?),\s*(.+)$',  # "Club, Location"
        r'(.+?)\s+at\s+(.+)$',  # "Club at Location"
        r'(.+?)\s+-\s+(.+)$',  # "Club - Location"
    ]
    
    for pattern in patterns:
        match = re.match(pattern, host_info, re.IGNORECASE)
        if match:
            return match.group(1).strip(), match.group(2).strip()
    
    # If no pattern matches, treat as location only
    return "", host_info

def fetch_regatta_network_meta(url):
    """Fetch metadata from Regatta Network URL"""
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        soup = BeautifulSoup(response.content, 'html.parser')
        
        meta = {}
        
        # Look for date patterns
        text = soup.get_text()
        date_patterns = [
            r'(\w+ \d{1,2}, \d{4})',  # "Month Day, Year"
            r'(\d{1,2}/\d{1,2}/\d{4})',  # "MM/DD/YYYY"
            r'(\d{4}-\d{2}-\d{2})',  # "YYYY-MM-DD"
        ]
        
        for pattern in date_patterns:
            matches = re.findall(pattern, text)
            if matches:
                meta['date'] = matches[0]
                break
        
        # Look for venue/location
        venue_selectors = [
            'h1', 'h2', '.venue', '.location', '.event-title'
        ]
        
        for selector in venue_selectors:
            elements = soup.select(selector)
            for elem in elements:
                text = elem.get_text(strip=True)
                if len(text) > 5 and len(text) < 100:  # Reasonable length
                    meta['venue'] = text
                    break
            if 'venue' in meta:
                break
        
        return meta
    except Exception as e:
        print(f"Warning: Could not fetch Regatta Network metadata from {url}: {e}")
        return {}

def scan_existing_collections():
    """Scan existing collections to avoid duplicates"""
    existing = {
        'results': {},
        'events': {},
        'posts': {}
    }
    
    # Scan _results/*.md
    for p in Path("_results").glob("*.md"):
        fm, _ = fm_split(p.read_text(encoding="utf-8"))
        if 'id' in fm:
            existing['results'][fm['id']] = {
                'file': p,
                'year': fm.get('year'),
                'series': fm.get('series'),
                'permalink': fm.get('permalink')
            }
    
    # Scan _events/*.md
    for p in Path("_events").glob("*.md"):
        fm, _ = fm_split(p.read_text(encoding="utf-8"))
        if 'results_id' in fm:
            existing['events'][fm['results_id']] = {
                'file': p,
                'title': fm.get('title'),
                'date': fm.get('date')
            }
    
    # Scan _posts/*.md
    for p in Path("_posts").glob("*.md"):
        fm, _ = fm_split(p.read_text(encoding="utf-8"))
        if 'title' in fm and 'date' in fm:
            key = f"{fm['title']}_{fm['date']}"
            existing['posts'][key] = {
                'file': p,
                'title': fm.get('title'),
                'date': fm.get('date')
            }
    
    return existing

def create_result_id(year, series):
    """Create canonical result ID"""
    if series == 'international':
        return f"international-{year}"
    elif series == 'north-american':
        return f"north-american-{year}"
    return f"{series}-{year}"

def upsert_champions_data(champions, club_aliases, write=False):
    """Update champions.yml with new data"""
    cpath = Path("_data/champions.yml")
    existing = Y(cpath) if cpath.exists() else []
    
    # Create lookup by result_id
    existing_lookup = {}
    for champ in existing:
        if 'result_id' in champ:
            existing_lookup[champ['result_id']] = champ
    
    changes = []
    updated_champs = []
    
    for champ in champions:
        year = champ['year']
        series = champ['series']
        result_id = create_result_id(year, series)
        
        # Normalize club and location
        club, location = normalize_club_location(champ['host_info'], club_aliases)
        
        # Create new champion record
        new_champ = {
            'year': year,
            'result_id': result_id,
            'series': series.title(),
            'skipper': champ['skipper'],
            'crew': champ['crew'] or '',
            'club': club,
            'location': location,
            'results_url': champ['results_url'] or ''
        }
        
        # Check if we should keep existing or use new
        if result_id in existing_lookup:
            existing_champ = existing_lookup[result_id]
            # Count non-empty fields
            existing_count = sum(1 for v in existing_champ.values() if v and str(v).strip())
            new_count = sum(1 for v in new_champ.values() if v and str(v).strip())
            
            if new_count > existing_count:
                updated_champs.append(new_champ)
                changes.append(f"Updated {result_id} (more complete data)")
            else:
                updated_champs.append(existing_champ)
                changes.append(f"Kept existing {result_id}")
        else:
            updated_champs.append(new_champ)
            changes.append(f"Added {result_id}")
    
    if write and changes:
        # Create backup
        backup = f"{cpath}.backup-{time.strftime('%Y%m%d-%H%M%S')}"
        if cpath.exists():
            shutil.copy(str(cpath), backup)
        
        # Sort by year descending
        updated_champs.sort(key=lambda x: x['year'], reverse=True)
        W(cpath, updated_champs)
    
    return changes

def create_result_file(champ, existing_results, write=False):
    """Create or update result file"""
    year = champ['year']
    series = champ['series']
    result_id = create_result_id(year, series)
    
    if result_id in existing_results:
        return f"Skipped {result_id} (exists)"
    
    # Determine filename and permalink
    if series == 'international':
        filename = f"{year}-international-championship.md"
        permalink = f"/results/{year}-international-championship/"
        title = f"International Penguin Championship {year}"
        series_title = "International Championship"
    else:
        filename = f"{year}-north-american-championship.md"
        permalink = f"/results/{year}-north-american-championship/"
        title = f"North American Championship {year}"
        series_title = "North American Championship"
    
    # Create front matter
    fm = {
        'layout': 'result',
        'id': result_id,
        'title': title,
        'date': f"{year}-01-01",
        'end_date': '',
        'year': year,
        'series': series_title,
        'is_championship': True,
        'venue': '',
        'location': champ.get('location', ''),
        'results_url': champ['results_url'] or ''
    }
    
    # Try to get better date from Regatta Network
    if champ['results_url'] and 'regattanetwork.com' in champ['results_url']:
        meta = fetch_regatta_network_meta(champ['results_url'])
        if 'date' in meta:
            fm['date'] = meta['date']
        if 'venue' in meta:
            fm['venue'] = meta['venue']
    
    content = fm_join(fm, f"\n# {title}\n\nResults for the {series_title} held in {year}.\n")
    
    if write:
        result_path = Path("_results") / filename
        result_path.write_text(content, encoding="utf-8")
    
    return f"Created {filename}"

def create_event_file(champ, existing_events, write=False):
    """Create event file if none exists for this results_id"""
    year = champ['year']
    series = champ['series']
    result_id = create_result_id(year, series)
    
    if result_id in existing_events:
        return f"Skipped {result_id} event (exists)"
    
    if series == 'international':
        title = "International Penguin Championship"
    else:
        title = "North American Championship"
    
    # Create front matter
    fm = {
        'layout': 'event',
        'title': title,
        'date': f"{year}-01-01",
        'end_date': '',
        'venue': '',
        'location': champ.get('location', ''),
        'results_id': result_id
    }
    
    # Try to get better date from Regatta Network
    if champ['results_url'] and 'regattanetwork.com' in champ['results_url']:
        meta = fetch_regatta_network_meta(champ['results_url'])
        if 'date' in meta:
            fm['date'] = meta['date']
        if 'venue' in meta:
            fm['venue'] = meta['venue']
    
    content = fm_join(fm, f"\n# {title} {year}\n\nEvent details for the {title} held in {year}.\n")
    
    if write:
        event_path = Path("_events") / f"{year}-01-01-{series}-championship.md"
        event_path.write_text(content, encoding="utf-8")
    
    return f"Created {title} {year} event"

def create_news_posts(champ, existing_posts, write=False):
    """Create news posts for championship"""
    year = champ['year']
    series = champ['series']
    
    if series == 'international':
        title_base = "International Championship"
    else:
        title_base = "North American Championship"
    
    posts = []
    
    # Pre-race announcement
    pre_title = f"{title_base} {year} — Announcement"
    pre_key = f"{pre_title}_{year}-01-01"
    
    if pre_key not in existing_posts:
        fm = {
            'layout': 'post',
            'title': pre_title,
            'date': f"{year}-01-01",
            'categories': ['championship', 'announcement']
        }
        content = fm_join(fm, f"\n# {pre_title}\n\nAnnouncement for the {title_base} {year}.\n")
        
        if write:
            post_path = Path("_posts") / f"{year}-01-01-{series}-championship-announcement.md"
            post_path.write_text(content, encoding="utf-8")
        
        posts.append(f"Created {pre_title}")
    
    # Post-race results
    post_title = f"{title_base} {year} — Results"
    post_key = f"{post_title}_{year}-12-31"
    
    if post_key not in existing_posts:
        fm = {
            'layout': 'post',
            'title': post_title,
            'date': f"{year}-12-31",
            'categories': ['championship', 'results']
        }
        content = fm_join(fm, f"\n# {post_title}\n\nResults from the {title_base} {year}.\n")
        
        if write:
            post_path = Path("_posts") / f"{year}-12-31-{series}-championship-results.md"
            post_path.write_text(content, encoding="utf-8")
        
        posts.append(f"Created {post_title}")
    
    return posts

def write_report(changes, output_dir="tmp"):
    """Write CSV report of changes"""
    Path(output_dir).mkdir(exist_ok=True)
    report_path = Path(output_dir) / "import_champions_report.csv"
    
    with open(report_path, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(['Action', 'Details'])
        for change in changes:
            writer.writerow(['Change', change])
    
    print(f"Report written to {report_path}")

def main():
    parser = argparse.ArgumentParser(description="Import champions from legacy HTML")
    parser.add_argument("--html", required=True, help="Path to champions.html")
    parser.add_argument("--write", action="store_true", help="Apply changes (otherwise dry run)")
    parser.add_argument("--emit-results", action="store_true", default=True, help="Create result files")
    parser.add_argument("--emit-events", action="store_true", help="Create event files")
    parser.add_argument("--emit-news", action="store_true", help="Create news posts")
    parser.add_argument("--only-years", help="Comma-separated years to process")
    parser.add_argument("--verbose", action="store_true", help="Verbose output")
    
    args = parser.parse_args()
    
    # Parse only_years if provided
    only_years = None
    if args.only_years:
        only_years = [int(y.strip()) for y in args.only_years.split(',')]
    
    print("DRY RUN" if not args.write else "APPLYING CHANGES")
    print("=" * 50)
    
    # Load normalization data
    club_aliases, split_hints = load_normalization()
    if args.verbose:
        print(f"Loaded {len(club_aliases)} club aliases")
    
    # Parse HTML
    champions = parse_champions_html(args.html, only_years)
    print(f"Parsed {len(champions)} champion records")
    
    # Scan existing collections
    existing = scan_existing_collections()
    if args.verbose:
        print(f"Found {len(existing['results'])} existing results")
        print(f"Found {len(existing['events'])} existing events")
        print(f"Found {len(existing['posts'])} existing posts")
    
    # Process champions
    all_changes = []
    
    # Update champions.yml
    champ_changes = upsert_champions_data(champions, club_aliases, args.write)
    all_changes.extend(champ_changes)
    
    # Create result files
    if args.emit_results:
        for champ in champions:
            change = create_result_file(champ, existing['results'], args.write)
            all_changes.append(change)
    
    # Create event files
    if args.emit_events:
        for champ in champions:
            change = create_event_file(champ, existing['events'], args.write)
            all_changes.append(change)
    
    # Create news posts
    if args.emit_news:
        for champ in champions:
            changes = create_news_posts(champ, existing['posts'], args.write)
            all_changes.extend(changes)
    
    # Print summary
    print("\nChanges:")
    for change in all_changes:
        print(f"- {change}")
    
    # Write report
    if args.write:
        write_report(all_changes)
    
    print(f"\nTotal changes: {len(all_changes)}")

if __name__ == "__main__":
    main()
