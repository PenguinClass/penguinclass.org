#!/usr/bin/env python3
"""
Fix remaining specific issues in champions.yml that weren't handled in the main cleanup.
"""

import yaml
import json

def fix_remaining_issues():
    """Fix the remaining specific issues."""
    
    with open('_data/champions.yml', 'r') as f:
        champions = yaml.safe_load(f)
    
    fixes_applied = 0
    
    for champion in champions:
        year = champion.get('year', '')
        result_id = champion.get('result_id', '')
        
        # Fix 1961 international
        if year == 1961 and result_id.startswith('intl'):
            champion['club'] = 'Crescent Sail Yacht Club'
            champion['location'] = 'Grosse Pointe, Michigan, U.S.A.'
            fixes_applied += 1
            print(f"  {year}: Fixed 1961 international club and location")
        
        # Fix 1982 international club
        elif year == 1982 and result_id.startswith('intl'):
            champion['club'] = 'Yacht Club Paulista'
            fixes_applied += 1
            print(f"  {year}: Fixed 1982 international club")
        
        # Fix 2003 international
        elif year == 2003 and result_id.startswith('intl'):
            champion['club'] = 'SHERIDAN SHORES YACHT CLUB'
            champion['location'] = 'Wilmette, IL, U.S.A.'
            fixes_applied += 1
            print(f"  {year}: Fixed 2003 international club and location")
        
        # Fix yacht club spacing issues
        club = champion.get('club', '')
        if 'YachtClub' in club:
            champion['club'] = club.replace('YachtClub', 'Yacht Club')
            fixes_applied += 1
            print(f"  {year}: Fixed yacht club spacing in '{club}'")
    
    print(f"\nApplied {fixes_applied} additional fixes")
    
    # Write updated data
    with open('_data/champions.yml', 'w') as f:
        yaml.dump(champions, f, default_flow_style=False, sort_keys=False)
    
    print("Updated _data/champions.yml")
    
    # Regenerate JSON
    with open('assets/data/champions.json', 'w') as f:
        json.dump(champions, f, ensure_ascii=False, indent=2)
    
    print("Regenerated assets/data/champions.json")
    print("Done!")

if __name__ == "__main__":
    fix_remaining_issues()
