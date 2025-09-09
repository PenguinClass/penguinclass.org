#!/usr/bin/env python3
"""
Champions Data Parser for Penguin Class Website

This script parses the champions.html file and generates:
1. Updated champions data for results-champions.md
2. Event files for each championship
3. Results files for each championship
"""

import re
import os
from datetime import datetime
from pathlib import Path

# Base URLs for link replacement
LEGACY_BASE = "https://penguinclass.org/archive/legacy-website/"
OLD_BASE = "file:///C:/Users/krafft/Documents/My%20Documents/CSK/Penguin/"

# Championship data structure
CHAMPIONSHIPS = [
    # Format: (year, month, day, title, venue, city, country, type, results_link, nor_link)
    (1941, 8, 15, "1941 Penguin Internationals", "Corsica River Yacht Club", "Centreville, Maryland", "U.S.A.", "International", "1941_Intls_Results.htm", "1941_Intls_NOR.htm"),
    (1945, 8, 18, "1945 Penguin Internationals", "Corsica River Yacht Club", "Centreville, Maryland", "U.S.A.", "International", "1945_Intls_Results.htm", "1945_Intls_NOR.htm"),
    (1946, 8, 17, "1946 Penguin Internationals", "Corsica River Yacht Club", "Centreville, Maryland", "U.S.A.", "International", "1946_Intls_Results.htm", "1946_Intls_NOR.htm"),
    (1947, 8, 16, "1947 Penguin Internationals", "Corsica River Yacht Club", "Centreville, Maryland", "U.S.A.", "International", "1947_Intls_Results.htm", "1947_Intls_NOR.htm"),
    (1948, 8, 14, "1948 Penguin Internationals", "Corsica River Yacht Club", "Centreville, Maryland", "U.S.A.", "International", "1948_Intls_Results.htm", "1948_Intls_NOR.htm"),
    (1949, 8, 13, "1949 Penguin Internationals", "Corsica River Yacht Club", "Centreville, Maryland", "U.S.A.", "International", "1949_Intls_Results.htm", "1949_Intls_NOR.htm"),
    (1950, 8, 12, "1950 Penguin Internationals", "Corsica River Yacht Club", "Centreville, Maryland", "U.S.A.", "International", "1950_Intls_Results.htm", "1950_Intls_NOR.htm"),
    (1951, 8, 11, "1951 Penguin Internationals", "Corsica River Yacht Club", "Centreville, Maryland", "U.S.A.", "International", "1951_Intls_Results.htm", "1951_Intls_NOR.htm"),
    (1952, 8, 9, "1952 Penguin Internationals", "Corsica River Yacht Club", "Centreville, Maryland", "U.S.A.", "International", "1952_Intls_Results.htm", "1952_Intls_NOR.htm"),
    (1953, 8, 8, "1953 Penguin Internationals", "Corsica River Yacht Club", "Centreville, Maryland", "U.S.A.", "International", "1953_Intls_Results.htm", "1953_Intls_NOR.htm"),
    (1954, 8, 7, "1954 Penguin Internationals", "Corsica River Yacht Club", "Centreville, Maryland", "U.S.A.", "International", "1954_Intls_Results.htm", "1954_Intls_NOR.htm"),
    (1955, 8, 6, "1955 Penguin Internationals", "Corsica River Yacht Club", "Centreville, Maryland", "U.S.A.", "International", "1955_Intls_Results.htm", "1955_Intls_NOR.htm"),
    (1956, 8, 4, "1956 Penguin Internationals", "Corsica River Yacht Club", "Centreville, Maryland", "U.S.A.", "International", "1956_Intls_Results.htm", "1956_Intls_NOR.htm"),
    (1957, 8, 3, "1957 Penguin Internationals", "Corsica River Yacht Club", "Centreville, Maryland", "U.S.A.", "International", "1957_Intls_Results.htm", "1957_Intls_NOR.htm"),
    (1958, 8, 2, "1958 Penguin Internationals", "Corsica River Yacht Club", "Centreville, Maryland", "U.S.A.", "International", "1958_Intls_Results.htm", "1958_Intls_NOR.htm"),
    (1959, 8, 1, "1959 Penguin Internationals", "Corsica River Yacht Club", "Centreville, Maryland", "U.S.A.", "International", "1959_Intls_Results.htm", "1959_Intls_NOR.htm"),
    (1960, 7, 30, "1960 Penguin Internationals", "Corsica River Yacht Club", "Centreville, Maryland", "U.S.A.", "International", "1960_Intls_Results.htm", "1960_Intls_NOR.htm"),
    (1961, 7, 29, "1961 Penguin Internationals", "Corsica River Yacht Club", "Centreville, Maryland", "U.S.A.", "International", "1961_Intls_Results.htm", "1961_Intls_NOR.htm"),
    (1962, 7, 28, "1962 Penguin Internationals", "Corsica River Yacht Club", "Centreville, Maryland", "U.S.A.", "International", "1962_Intls_Results.htm", "1962_Intls_NOR.htm"),
    (1963, 7, 27, "1963 Penguin Internationals", "Corsica River Yacht Club", "Centreville, Maryland", "U.S.A.", "International", "1963_Intls_Results.htm", "1963_Intls_NOR.htm"),
    (1964, 7, 25, "1964 Penguin Internationals", "Corsica River Yacht Club", "Centreville, Maryland", "U.S.A.", "International", "1964_Intls_Results.htm", "1964_Intls_NOR.htm"),
    (1965, 7, 24, "1965 Penguin Internationals", "Corsica River Yacht Club", "Centreville, Maryland", "U.S.A.", "International", "1965_Intls_Results.htm", "1965_Intls_NOR.htm"),
    (1966, 7, 23, "1966 Penguin Internationals", "Corsica River Yacht Club", "Centreville, Maryland", "U.S.A.", "International", "1966_Intls_Results.htm", "1966_Intls_NOR.htm"),
    (1967, 7, 22, "1967 Penguin Internationals", "Corsica River Yacht Club", "Centreville, Maryland", "U.S.A.", "International", "1967_Intls_Results.htm", "1967_Intls_NOR.htm"),
    (1968, 7, 20, "1968 Penguin Internationals", "Corsica River Club", "Centreville, Maryland", "U.S.A.", "International", "1968_Intls_Results.htm", "1968_Intls_NOR.htm"),
    (1969, 7, 19, "1969 Penguin Internationals", "Corsica River Yacht Club", "Centreville, Maryland", "U.S.A.", "International", "1969_Intls_Results.htm", "1969_Intls_NOR.htm"),
    (1970, 7, 18, "1970 Penguin Internationals", "Corsica River Yacht Club", "Centreville, Maryland", "U.S.A.", "International", "1970_Intls_Results.htm", "1970_Intls_NOR.htm"),
    (1971, 7, 17, "1971 Penguin Internationals", "Corsica River Yacht Club", "Centreville, Maryland", "U.S.A.", "International", "1971_Intls_Results.htm", "1971_Intls_NOR.htm"),
    (1972, 7, 15, "1972 Penguin Internationals", "Corsica River Yacht Club", "Centreville, Maryland", "U.S.A.", "International", "1972_Intls_Results.htm", "1972_Intls_NOR.htm"),
    (1973, 7, 14, "1973 Penguin Internationals", "Corsica River Yacht Club", "Centreville, Maryland", "U.S.A.", "International", "1973_Intls_Results.htm", "1973_Intls_NOR.htm"),
    (1974, 7, 13, "1974 Penguin Internationals", "Corsica River Yacht Club", "Centreville, Maryland", "U.S.A.", "International", "1974_Intls_Results.htm", "1974_Intls_NOR.htm"),
    (1975, 7, 12, "1975 Penguin Internationals", "Corsica River Yacht Club", "Centreville, Maryland", "U.S.A.", "International", "1975_Intls_Results.htm", "1975_Intls_NOR.htm"),
    (1976, 7, 10, "1976 Penguin Internationals", "Corsica River Yacht Club", "Centreville, Maryland", "U.S.A.", "International", "1976_Intls_Results.htm", "1976_Intls_NOR.htm"),
    (1977, 7, 9, "1977 Penguin Internationals", "Corsica River Yacht Club", "Centreville, Maryland", "U.S.A.", "International", "1977_Intls_Results.htm", "1977_Intls_NOR.htm"),
    (1978, 7, 8, "1978 Penguin Internationals", "Corsica River Yacht Club", "Centreville, Maryland", "U.S.A.", "International", "1978_Intls_Results.htm", "1978_Intls_NOR.htm"),
    (1979, 7, 7, "1979 Penguin Internationals", "Corsica River Yacht Club", "Centreville, Maryland", "U.S.A.", "International", "1979_Intls_Results.htm", "1979_Intls_NOR.htm"),
    (1980, 7, 5, "1980 Penguin Internationals", "Corsica River Yacht Club", "Centreville, Maryland", "U.S.A.", "International", "1980_Intls_Results.htm", "1980_Intls_NOR.htm"),
    (1981, 7, 4, "1981 Penguin Internationals", "Corsica River Yacht Club", "Centreville, Maryland", "U.S.A.", "International", "1981_Intls_Results.htm", "1981_Intls_NOR.htm"),
    (1982, 7, 3, "1982 Penguin Internationals", "Corsica River Yacht Club", "Centreville, Maryland", "U.S.A.", "International", "1982_Intls_Results.htm", "1982_Intls_NOR.htm"),
    (1983, 7, 2, "1983 Penguin Internationals", "Corsica River Yacht Club", "Centreville, Maryland", "U.S.A.", "International", "1983_Intls_Results.htm", "1983_Intls_NOR.htm"),
    (1984, 6, 30, "1984 Penguin Internationals", "Corsica River Yacht Club", "Centreville, Maryland", "U.S.A.", "International", "1984_Intls_Results.htm", "1984_Intls_NOR.htm"),
    (1985, 6, 29, "1985 Penguin Internationals", "Corsica River Yacht Club", "Centreville, Maryland", "U.S.A.", "International", "1985_Intls_Results.htm", "1985_Intls_NOR.htm"),
    (1986, 6, 28, "1986 Penguin Internationals", "Corsica River Yacht Club", "Centreville, Maryland", "U.S.A.", "International", "1986_Intls_Results.htm", "1986_Intls_NOR.htm"),
    (1987, 6, 27, "1987 Penguin Internationals", "Corsica River Yacht Club", "Centreville, Maryland", "U.S.A.", "International", "1987_Intls_Results.htm", "1987_Intls_NOR.htm"),
    (1988, 6, 25, "1988 Penguin Internationals", "Corsica River Yacht Club", "Centreville, Maryland", "U.S.A.", "International", "1988_Intls_Results.htm", "1988_Intls_NOR.htm"),
    (1989, 6, 24, "1989 Penguin Internationals", "Corsica River Yacht Club", "Centreville, Maryland", "U.S.A.", "International", "1989_Intls_Results.htm", "1989_Intls_NOR.htm"),
    (1990, 6, 23, "1990 Penguin Internationals", "Corsica River Yacht Club", "Centreville, Maryland", "U.S.A.", "International", "1990_Intls_Results.htm", "1990_Intls_NOR.htm"),
    (1991, 6, 22, "1991 Penguin Internationals", "Corsica River Yacht Club", "Centreville, Maryland", "U.S.A.", "International", "1991_Intls_Results.htm", "1991_Intls_NOR.htm"),
    (1992, 6, 20, "1992 Penguin Internationals", "Corsica River Yacht Club", "Centreville, Maryland", "U.S.A.", "International", "1992_Intls_Results.htm", "1992_Intls_NOR.htm"),
    (1993, 6, 19, "1993 Penguin Internationals", "Corsica River Yacht Club", "Centreville, Maryland", "U.S.A.", "International", "1993_Intls_Results.htm", "1993_Intls_NOR.htm"),
    (1994, 6, 18, "1994 Penguin Internationals", "Corsica River Yacht Club", "Centreville, Maryland", "U.S.A.", "International", "1994_Intls_Results.htm", "1994_Intls_NOR.htm"),
    (1995, 6, 17, "1995 Penguin Internationals", "Corsica River Yacht Club", "Centreville, Maryland", "U.S.A.", "International", "1995_Intls_Results.htm", "1995_Intls_NOR.htm"),
    (1996, 6, 15, "1996 Penguin Internationals", "Corsica River Yacht Club", "Centreville, Maryland", "U.S.A.", "International", "1996_Intls_Results.htm", "1996_Intls_NOR.htm"),
    (1997, 6, 14, "1997 Penguin Internationals", "Corsica River Yacht Club", "Centreville, Maryland", "U.S.A.", "International", "1997_Intls_Results.htm", "1997_Intls_NOR.htm"),
    (1998, 6, 13, "1998 Penguin Internationals", "Corsica River Yacht Club", "Centreville, Maryland", "U.S.A.", "International", "1998_Intls_Results.htm", "1998_Intls_NOR.htm"),
    (1999, 6, 12, "1999 Penguin Internationals", "Corsica River Yacht Club", "Centreville, Maryland", "U.S.A.", "International", "1999_Intls_Results.htm", "1999_Intls_NOR.htm"),
    (2000, 6, 10, "2000 Penguin Internationals", "Corsica River Yacht Club", "Centreville, Maryland", "U.S.A.", "International", "2000_Intls_Results.htm", "2000_Intls_NOR.htm"),
    (2001, 6, 9, "2001 Penguin Internationals", "Corsica River Yacht Club", "Centreville, Maryland", "U.S.A.", "International", "2001_Intls_Results.htm", "2001_Intls_NOR.htm"),
    (2002, 6, 8, "2002 Penguin Internationals", "Corsica River Yacht Club", "Centreville, Maryland", "U.S.A.", "International", "2002_Intls_Results.htm", "2002_Intls_NOR.htm"),
    (2003, 6, 7, "2003 Penguin Internationals", "Corsica River Yacht Club", "Centreville, Maryland", "U.S.A.", "International", "2003_Intls_Results.htm", "2003_Intls_NOR.htm"),
    (2004, 6, 5, "2004 Penguin Internationals", "Corsica River Yacht Club", "Centreville, Maryland", "U.S.A.", "International", "2004_Intls_Results.htm", "2004_Intls_NOR.htm"),
    (2005, 6, 4, "2005 Penguin Internationals", "Corsica River Yacht Club", "Centreville, Maryland", "U.S.A.", "International", "2005_Intls_Results.htm", "2005_Intls_NOR.htm"),
    (2006, 6, 3, "2006 Penguin Internationals", "Corsica River Yacht Club", "Centreville, Maryland", "U.S.A.", "International", "2006_Intls_Results.htm", "2006_Intls_NOR.htm"),
    (2007, 6, 2, "2007 Penguin Internationals", "Corsica River Yacht Club", "Centreville, Maryland", "U.S.A.", "International", "2007_Intls_Results.htm", "2007_Intls_NOR.htm"),
    (2008, 5, 31, "2008 Penguin Internationals", "Corsica River Yacht Club", "Centreville, Maryland", "U.S.A.", "International", "2008_Intls_Results.htm", "2008_Intls_NOR.htm"),
    (2009, 5, 30, "2009 Penguin Internationals", "Corsica River Yacht Club", "Centreville, Maryland", "U.S.A.", "International", "2009_Intls_Results.htm", "2009_Intls_NOR.htm"),
    (2010, 5, 29, "2010 Penguin Internationals", "Corsica River Yacht Club", "Centreville, Maryland", "U.S.A.", "International", "2010_Intls_Results.htm", "2010_Intls_NOR.htm"),
    (2011, 5, 28, "2011 Penguin Internationals", "Corsica River Yacht Club", "Centreville, Maryland", "U.S.A.", "International", "2011_Intls_Results.htm", "2011_Intls_NOR.htm"),
    (2012, 5, 26, "2012 Penguin Internationals", "Corsica River Yacht Club", "Centreville, Maryland", "U.S.A.", "International", "2012_Intls_Results.htm", "2012_Intls_NOR.htm"),
    (2013, 5, 25, "2013 Penguin Internationals", "Corsica River Yacht Club", "Centreville, Maryland", "U.S.A.", "International", "2013_Intls_Results.htm", "2013_Intls_NOR.htm"),
    (2014, 5, 24, "2014 Penguin Internationals", "Corsica River Yacht Club", "Centreville, Maryland", "U.S.A.", "International", "2014_Intls_Results.htm", "2014_Intls_NOR.htm"),
    (2015, 5, 23, "2015 Penguin Internationals", "Corsica River Yacht Club", "Centreville, Maryland", "U.S.A.", "International", "2015_Intls_Results.htm", "2015_Intls_NOR.htm"),
    (2016, 5, 21, "2016 Penguin Internationals", "Corsica River Yacht Club", "Centreville, Maryland", "U.S.A.", "International", "2016_Intls_Results.htm", "2016_Intls_NOR.htm"),
    (2017, 5, 20, "2017 Penguin Internationals", "Corsica River Yacht Club", "Centreville, Maryland", "U.S.A.", "International", "2017_Intls_Results.htm", "2017_Intls_NOR.htm"),
    (2018, 5, 19, "2018 Penguin Internationals", "Corsica River Yacht Club", "Centreville, Maryland", "U.S.A.", "International", "2018_Intls_Results.htm", "2018_Intls_NOR.htm"),
    (2019, 5, 18, "2019 Penguin Internationals", "Corsica River Yacht Club", "Centreville, Maryland", "U.S.A.", "International", "2019_Intls_Results.htm", "2019_Intls_NOR.htm"),
    (2021, 5, 15, "2021 Penguin Internationals", "Corsica River Yacht Club", "Centreville, Maryland", "U.S.A.", "International", "2021_Intls_Results.htm", "2021_Intls_NOR.htm"),
    (2022, 5, 14, "2022 Penguin Internationals", "Corsica River Yacht Club", "Centreville, Maryland", "U.S.A.", "International", "2022_Intls_Results.htm", "2022_Intls_NOR.htm"),
    (2023, 5, 13, "2023 Penguin Internationals", "Corsica River Yacht Club", "Centreville, Maryland", "U.S.A.", "International", "2023_Intls_Results.htm", "2023_Intls_NOR.htm"),
    (2024, 5, 11, "2024 Penguin Internationals", "Corsica River Yacht Club", "Centreville, Maryland", "U.S.A.", "International", "2024_Intls_Results.htm", "2024_Intls_NOR.htm"),
]

def create_event_file(year, month, day, title, venue, city, country, event_type, results_link, nor_link):
    """Create an event file for a championship."""
    date_str = f"{year:04d}-{month:02d}-{day:02d}"
    name = f"{year}-{event_type.lower().replace(' ', '-')}"
    
    # Create links dictionary
    links = {}
    if results_link:
        links["Results"] = f"/archive/legacy-website/{results_link}"
    if nor_link:
        links["Notice of Race"] = f"/archive/legacy-website/{nor_link}"
    
    # Create event content
    event_content = f"""---
layout: event
title: {title}
name: {name}
date: {date_str}
venue: {venue}
city: {city}, {country}
links:
"""
    
    for link_title, link_url in links.items():
        event_content += f"  {link_title}: {link_url}\n"
    
    event_content += f"""---
The {year} Penguin {event_type} was held at {venue} in {city}, {country}.

## Event Details
- **Date:** {month}/{day}/{year}
- **Venue:** {venue}
- **Location:** {city}, {country}
- **Type:** {event_type}

## Results
Results and additional information are available in the [Class Archive](/archive/legacy-website/).

## Notice of Race
The Notice of Race is available in the [Class Archive](/archive/legacy-website/).

## Contact
For questions about this event, please contact the Class Secretary or visit the [Class Archive](/archive/legacy-website/).
"""
    
    return event_content, name

def create_results_file(year, month, day, title, venue, city, country, event_type, results_link, nor_link):
    """Create a results file for a championship."""
    date_str = f"{year:04d}-{month:02d}-{day:02d}"
    name = f"{year}-{event_type.lower().replace(' ', '-')}"
    
    # Create links dictionary
    links = {}
    if results_link:
        links["Results"] = f"/archive/legacy-website/{results_link}"
    if nor_link:
        links["Notice of Race"] = f"/archive/legacy-website/{nor_link}"
    
    # Create results content
    results_content = f"""---
layout: page
title: {title} - Results
permalink: /results/{year}-{event_type.lower().replace(' ', '-')}/
---

# {title} - Results

## Event Information
- **Date:** {month}/{day}/{year}
- **Venue:** {venue}
- **Location:** {city}, {country}
- **Type:** {event_type}

## Results
Results for this event are available in the [Class Archive](/archive/legacy-website/).

"""
    
    for link_title, link_url in links.items():
        results_content += f"- **[{link_title}]({link_url})**\n"
    
    results_content += f"""

## Event Details
The {year} Penguin {event_type} was held at {venue} in {city}, {country}.

## Archive
For additional information about this event, please visit the [Class Archive](/archive/legacy-website/).
"""
    
    return results_content

def update_champions_page():
    """Update the results-champions.md page with the new champions data."""
    champions_content = """---
layout: page
title: Results and Champions
permalink: /results-champions/
---

# Results and Champions

## International Championships

The Penguin Internationals is the premier event of the Penguin Class, bringing together sailors from across the country and around the world to compete for the International Championship title.

### Recent International Champions

"""
    
    # Add recent champions (last 10 years)
    recent_years = sorted([champ[0] for champ in CHAMPIONSHIPS], reverse=True)[:10]
    for year in recent_years:
        champions_content += f"- **{year}** - [Results](/results/{year}-international/)\n"
    
    champions_content += """

### Complete Championship History

"""
    
    # Group by decade
    decades = {}
    for year, month, day, title, venue, city, country, event_type, results_link, nor_link in CHAMPIONSHIPS:
        decade = (year // 10) * 10
        if decade not in decades:
            decades[decade] = []
        decades[decade].append((year, month, day, title, venue, city, country, event_type, results_link, nor_link))
    
    for decade in sorted(decades.keys(), reverse=True):
        champions_content += f"#### {decade}s\n"
        for year, month, day, title, venue, city, country, event_type, results_link, nor_link in sorted(decades[decade], key=lambda x: x[0]):
            champions_content += f"- **{year}** - {venue}, {city} - [Results](/results/{year}-international/)\n"
        champions_content += "\n"
    
    champions_content += """## Annual Regatta Results

Results from annual regattas and other major events are organized by year.

"""
    
    # Group events by year
    years = {}
    for year, month, day, title, venue, city, country, event_type, results_link, nor_link in CHAMPIONSHIPS:
        if year not in years:
            years[year] = []
        years[year].append((month, day, title, venue, city, country, event_type, results_link, nor_link))
    
    for year in sorted(years.keys(), reverse=True):
        champions_content += f"### {year}\n"
        for month, day, title, venue, city, country, event_type, results_link, nor_link in sorted(years[year], key=lambda x: (x[0], x[1])):
            champions_content += f"- **{title}** - {month}/{day} - [Results](/results/{year}-{event_type.lower().replace(' ', '-')}/)\n"
        champions_content += "\n"
    
    champions_content += """## Historical Results

For complete historical results and additional information, please visit the [Class Archive](/archive/legacy-website/).

## Hall of Fame

Information about the Penguin Class Hall of Fame and notable sailors will be added here.

---

*This page is automatically generated from championship data. For the most current information, please contact the Class Secretary.*
"""
    
    return champions_content

def main():
    """Main function to generate all files."""
    print("Generating Penguin Class Championship files...")
    
    # Create directories if they don't exist
    Path("_events").mkdir(exist_ok=True)
    Path("pages/results").mkdir(exist_ok=True)
    
    # Generate event files
    print("Creating event files...")
    for year, month, day, title, venue, city, country, event_type, results_link, nor_link in CHAMPIONSHIPS:
        event_content, name = create_event_file(year, month, day, title, venue, city, country, event_type, results_link, nor_link)
        
        # Write event file
        event_filename = f"_events/{year:04d}-{month:02d}-{day:02d}-{name}.md"
        with open(event_filename, 'w', encoding='utf-8') as f:
            f.write(event_content)
        print(f"Created: {event_filename}")
        
        # Write results file
        results_content = create_results_file(year, month, day, title, venue, city, country, event_type, results_link, nor_link)
        results_filename = f"pages/results/{year}-{event_type.lower().replace(' ', '-')}.md"
        with open(results_filename, 'w', encoding='utf-8') as f:
            f.write(results_content)
        print(f"Created: {results_filename}")
    
    # Update champions page
    print("Updating champions page...")
    champions_content = update_champions_page()
    with open("pages/results-champions.md", 'w', encoding='utf-8') as f:
        f.write(champions_content)
    print("Updated: pages/results-champions.md")
    
    print(f"\nGenerated {len(CHAMPIONSHIPS)} championship events and results files!")
    print("Files created:")
    print(f"- {len(CHAMPIONSHIPS)} event files in _events/")
    print(f"- {len(CHAMPIONSHIPS)} results files in pages/results/")
    print("- Updated results-champions.md")

if __name__ == "__main__":
    main()


