#!/usr/bin/env python3
"""
Fix URLs in champions.yml and other files to use the correct domain and paths.
"""

import yaml
import json
import re
import os

def fix_urls_in_champions():
    """Fix URLs in champions.yml file."""
    
    print("Fixing URLs in champions.yml...")
    
    with open('_data/champions.yml', 'r') as f:
        champions = yaml.safe_load(f)
    
    fixes_applied = 0
    
    for champion in champions:
        results_url = champion.get('results_url', '')
        
        if results_url:
            original_url = results_url
            
            # Fix file:///C:/Users/krafft/Documents/My%20Documents/CSK/Penguin/ URLs
            if results_url.startswith('file:///C:/Users/krafft/Documents/My%20Documents/CSK/Penguin/'):
                filename = results_url.split('/')[-1]
                results_url = f'archive/legacy-website/{filename}'
                champion['results_url'] = results_url
                fixes_applied += 1
                print(f"  {champion.get('year', 'Unknown')}: Fixed file:// URL → {results_url}")
            
            # Fix penguinclass.com URLs
            elif 'penguinclass.com' in results_url:
                results_url = results_url.replace('http://www.penguinclass.com/', 'archive/legacy-website/')
                results_url = results_url.replace('https://www.penguinclass.com/', 'archive/legacy-website/')
                results_url = results_url.replace('http://penguinclass.com/', 'archive/legacy-website/')
                results_url = results_url.replace('https://penguinclass.com/', 'archive/legacy-website/')
                champion['results_url'] = results_url
                fixes_applied += 1
                print(f"  {champion.get('year', 'Unknown')}: Fixed penguinclass.com URL → {results_url}")
    
    print(f"Applied {fixes_applied} URL fixes to champions.yml")
    
    # Write updated champions data
    with open('_data/champions.yml', 'w') as f:
        yaml.dump(champions, f, default_flow_style=False, sort_keys=False)
    
    print("Updated _data/champions.yml")
    
    # Regenerate JSON
    with open('assets/data/champions.json', 'w') as f:
        json.dump(champions, f, ensure_ascii=False, indent=2)
    
    print("Regenerated assets/data/champions.json")
    
    return fixes_applied

def fix_urls_in_other_files():
    """Fix URLs in other relevant files."""
    
    files_to_fix = [
        '_data/links.yml',
        'pages/penguin/modern-v-classic.md',
        'archive/index.md'
    ]
    
    total_fixes = 0
    
    for file_path in files_to_fix:
        if os.path.exists(file_path):
            print(f"\nFixing URLs in {file_path}...")
            
            with open(file_path, 'r') as f:
                content = f.read()
            
            original_content = content
            fixes_in_file = 0
            
            # Fix file:///C:/Users/krafft/Documents/My%20Documents/CSK/Penguin/ URLs
            if 'file:///C:/Users/krafft/Documents/My%20Documents/CSK/Penguin/' in content:
                content = re.sub(
                    r'file:///C:/Users/krafft/Documents/My%20Documents/CSK/Penguin/([^"\s]+)',
                    r'archive/legacy-website/\1',
                    content
                )
                fixes_in_file += content.count('archive/legacy-website/') - original_content.count('archive/legacy-website/')
            
            # Fix penguinclass.com URLs
            if 'penguinclass.com' in content:
                content = re.sub(
                    r'https?://(?:www\.)?penguinclass\.com/([^"\s]+)',
                    r'archive/legacy-website/\1',
                    content
                )
                fixes_in_file += original_content.count('penguinclass.com') - content.count('penguinclass.com')
            
            if content != original_content:
                with open(file_path, 'w') as f:
                    f.write(content)
                print(f"  Applied {fixes_in_file} URL fixes")
                total_fixes += fixes_in_file
            else:
                print(f"  No URL fixes needed")
    
    return total_fixes

def main():
    print("Starting URL cleanup...")
    
    # Fix champions data
    champions_fixes = fix_urls_in_champions()
    
    # Fix other files
    other_fixes = fix_urls_in_other_files()
    
    print(f"\nURL cleanup complete!")
    print(f"  Champions data: {champions_fixes} fixes")
    print(f"  Other files: {other_fixes} fixes")
    print(f"  Total: {champions_fixes + other_fixes} fixes")

if __name__ == "__main__":
    main()
