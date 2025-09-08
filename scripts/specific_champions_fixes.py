#!/usr/bin/env python3
"""
Apply specific fixes to champions.yml for the cases mentioned by the user.
"""

import yaml
import re

def apply_specific_fixes():
    """Apply the specific corrections mentioned by the user."""
    
    with open('_data/champions.yml', 'r') as f:
        champions = yaml.safe_load(f)
    
    fixes_applied = 0
    
    for champion in champions:
        year = champion.get('year', '')
        club = champion.get('club', '')
        location = champion.get('location', '')
        
        # Fix SSA cases
        if club == 'SSA' and 'Annapolis' in location:
            champion['club'] = 'Severn Sailing Association'
            champion['location'] = 'Annapolis, MD'
            fixes_applied += 1
            print(f"  {year}: Fixed SSA → Severn Sailing Association, Annapolis, MD")
        
        # Fix Cambridge, MD cases
        elif club == 'Cambridge' and 'MD' in location:
            champion['club'] = 'Cambridge Yacht Club'
            champion['location'] = 'Cambridge, MD'
            fixes_applied += 1
            print(f"  {year}: Fixed Cambridge → Cambridge Yacht Club, Cambridge, MD")
        
        # Fix 1976 Argentina case
        elif year == 1976 and ('Olivios' in club or 'Argentina' in location):
            champion['club'] = 'Yacht Club Olivos'
            champion['location'] = 'Buenos Aires, Argentina'
            fixes_applied += 1
            print(f"  {year}: Fixed 1976 Argentina → Yacht Club Olivos, Buenos Aires, Argentina")
        
        # Fix 1991 Brazil case
        elif year == 1991 and ('Rio de Janeiro' in club or 'Brazil' in location):
            champion['club'] = 'Rio de Janeiro Yacht Club'
            champion['location'] = 'Rio de Janeiro, Brazil'
            fixes_applied += 1
            print(f"  {year}: Fixed 1991 Brazil → Rio de Janeiro Yacht Club, Rio de Janeiro, Brazil")
        
        # Fix 1997 Brazil case
        elif year == 1997 and ('Rio Grande' in club or 'Brazil' in location):
            champion['club'] = 'Clube Naval'
            champion['location'] = 'Rio de Janeiro, Brazil'
            fixes_applied += 1
            print(f"  {year}: Fixed 1997 Brazil → Clube Naval, Rio de Janeiro, Brazil")
        
        # Fix remaining YC expansions
        elif 'YC' in club and 'Yacht Club' not in club:
            champion['club'] = club.replace('YC', 'Yacht Club')
            fixes_applied += 1
            print(f"  {year}: Expanded YC → Yacht Club in '{club}'")
    
    print(f"\nApplied {fixes_applied} specific fixes")
    
    # Write updated data
    with open('_data/champions.yml', 'w') as f:
        yaml.dump(champions, f, default_flow_style=False, sort_keys=False)
    
    print("Updated _data/champions.yml")
    
    # Regenerate JSON
    import json
    with open('assets/data/champions.json', 'w') as f:
        json.dump(champions, f, ensure_ascii=False, indent=2)
    
    print("Regenerated assets/data/champions.json")
    print("Done!")

if __name__ == "__main__":
    apply_specific_fixes()
