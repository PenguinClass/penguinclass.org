#!/usr/bin/env python3
"""
Fix remaining SSA and Cambridge cases in champions.yml.
"""

import yaml

def fix_remaining_cases():
    """Fix remaining SSA and Cambridge cases."""
    
    with open('_data/champions.yml', 'r') as f:
        champions = yaml.safe_load(f)
    
    fixes_applied = 0
    
    for champion in champions:
        club = champion.get('club', '')
        location = champion.get('location', '')
        
        # Fix SSA cases where club is empty but location contains SSA
        if not club and 'SSA' in location and 'Annapolis' in location:
            champion['club'] = 'Severn Sailing Association'
            champion['location'] = 'Annapolis, MD'
            fixes_applied += 1
            print(f"  {champion.get('year', 'Unknown')}: Fixed SSA in location → Severn Sailing Association, Annapolis, MD")
        
        # Fix Cambridge cases where club is empty but location is just Cambridge, MD
        elif not club and location == 'Cambridge, MD':
            champion['club'] = 'Cambridge Yacht Club'
            champion['location'] = 'Cambridge, MD'
            fixes_applied += 1
            print(f"  {champion.get('year', 'Unknown')}: Fixed Cambridge, MD → Cambridge Yacht Club, Cambridge, MD")
    
    print(f"\nApplied {fixes_applied} additional fixes")
    
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
    fix_remaining_cases()
