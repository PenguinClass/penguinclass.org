#!/usr/bin/env python3
"""
Fix path issues in legacy website files for hosting from Jekyll repo.

This script identifies and fixes:
1. Relative src/href paths that need /archive/legacy-website/ prefix
2. Broken external links
3. Microsoft Office-specific markup issues
4. Other hosting-related problems
"""

import os
import re
import pathlib
from typing import List, Tuple, Dict
from urllib.parse import urlparse

ROOT = pathlib.Path("archive/legacy-website")
EXTS = {".html", ".htm", ".css", ".js"}

# Patterns to find problematic paths
RELATIVE_SRC_PATTERN = re.compile(r'src="([^/][^"]*)"', re.IGNORECASE)
RELATIVE_HREF_PATTERN = re.compile(r'href="([^/][^"]*)"', re.IGNORECASE)
CSS_URL_PATTERN = re.compile(r'url\(["\']?([^/][^"\')\s]*?)["\']?\)', re.IGNORECASE)

# External domains that might be broken
BROKEN_DOMAINS = {
    'fastcounter.linkexchange.com',
    'mailcenter2.comcast.net', 
    'potomacriversailing.org'
}

# Microsoft Office specific patterns to flag
MSO_PATTERNS = [
    r'<!--\[if mso[^>]*>',
    r'<v:[^>]*>',
    r'o:gfxdata=',
    r'mso-[^=]*=',
    r'<o:[^>]*>',
    r'<w:[^>]*>'
]

def analyze_file(file_path: pathlib.Path) -> Dict:
    """Analyze a single file for path issues."""
    issues = {
        'relative_src': [],
        'relative_href': [],
        'css_urls': [],
        'broken_external': [],
        'mso_issues': [],
        'file_size': 0
    }
    
    try:
        content = file_path.read_text(encoding='utf-8', errors='ignore')
        issues['file_size'] = len(content)
        
        # Find relative src attributes
        for match in RELATIVE_SRC_PATTERN.finditer(content):
            src_path = match.group(1)
            if not src_path.startswith(('http://', 'https://', 'mailto:', '#')):
                issues['relative_src'].append((match.start(), match.end(), src_path))
        
        # Find relative href attributes  
        for match in RELATIVE_HREF_PATTERN.finditer(content):
            href_path = match.group(1)
            if not href_path.startswith(('http://', 'https://', 'mailto:', '#')):
                issues['relative_href'].append((match.start(), match.end(), href_path))
        
        # Find CSS url() references
        for match in CSS_URL_PATTERN.finditer(content):
            url_path = match.group(1)
            if not url_path.startswith(('http://', 'https://', 'data:')):
                issues['css_urls'].append((match.start(), match.end(), url_path))
        
        # Find broken external links
        for match in re.finditer(r'(src|href)="(https?://[^"]*)"', content, re.IGNORECASE):
            url = match.group(2)
            domain = urlparse(url).netloc
            if domain in BROKEN_DOMAINS:
                issues['broken_external'].append((match.start(), match.end(), url))
        
        # Find Microsoft Office specific issues
        for pattern in MSO_PATTERNS:
            for match in re.finditer(pattern, content, re.IGNORECASE):
                issues['mso_issues'].append((match.start(), match.end(), match.group(0)))
                
    except Exception as e:
        issues['error'] = str(e)
    
    return issues

def generate_report() -> None:
    """Generate a comprehensive report of all issues found."""
    print("=== LEGACY WEBSITE PATH ANALYSIS REPORT ===\n")
    
    total_files = 0
    files_with_issues = 0
    total_issues = 0
    
    issue_summary = {
        'relative_src': 0,
        'relative_href': 0, 
        'css_urls': 0,
        'broken_external': 0,
        'mso_issues': 0
    }
    
    # Analyze all files
    for file_path in sorted(ROOT.rglob("*")):
        if not file_path.is_file() or file_path.suffix.lower() not in EXTS:
            continue
            
        total_files += 1
        issues = analyze_file(file_path)
        
        if any(issues[key] for key in issue_summary.keys()):
            files_with_issues += 1
            rel_path = file_path.relative_to(ROOT)
            print(f"\n📁 {rel_path}")
            
            for issue_type, count in issue_summary.items():
                if issues[issue_type]:
                    issue_count = len(issues[issue_type])
                    total_issues += issue_count
                    issue_summary[issue_type] += issue_count
                    
                    print(f"  ❌ {issue_type.replace('_', ' ').title()}: {issue_count}")
                    
                    # Show first few examples
                    for i, (start, end, value) in enumerate(issues[issue_type][:3]):
                        print(f"    • {value}")
                    if len(issues[issue_type]) > 3:
                        print(f"    • ... and {len(issues[issue_type]) - 3} more")
    
    # Summary
    print(f"\n=== SUMMARY ===")
    print(f"Total files analyzed: {total_files}")
    print(f"Files with issues: {files_with_issues}")
    print(f"Total issues found: {total_issues}")
    print(f"\nIssue breakdown:")
    for issue_type, count in issue_summary.items():
        if count > 0:
            print(f"  • {issue_type.replace('_', ' ').title()}: {count}")

def fix_paths_in_file(file_path: pathlib.Path, dry_run: bool = True) -> Dict:
    """Fix path issues in a single file."""
    try:
        content = file_path.read_text(encoding='utf-8', errors='ignore')
        original_content = content
        changes = []
        
        # Fix relative src attributes
        def fix_src(match):
            src_path = match.group(1)
            if not src_path.startswith(('http://', 'https://', 'mailto:', '#')):
                new_path = f"/archive/legacy-website/{src_path}"
                changes.append(f"src: {src_path} -> {new_path}")
                return f'src="{new_path}"'
            return match.group(0)
        
        content = RELATIVE_SRC_PATTERN.sub(fix_src, content)
        
        # Fix relative href attributes
        def fix_href(match):
            href_path = match.group(1)
            if not href_path.startswith(('http://', 'https://', 'mailto:', '#')):
                new_path = f"/archive/legacy-website/{href_path}"
                changes.append(f"href: {href_path} -> {new_path}")
                return f'href="{new_path}"'
            return match.group(0)
        
        content = RELATIVE_HREF_PATTERN.sub(fix_href, content)
        
        # Fix CSS url() references
        def fix_css_url(match):
            url_path = match.group(1)
            if not url_path.startswith(('http://', 'https://', 'data:')):
                new_path = f"/archive/legacy-website/{url_path}"
                changes.append(f"CSS url: {url_path} -> {new_path}")
                return f'url("{new_path}")'
            return match.group(0)
        
        content = CSS_URL_PATTERN.sub(fix_css_url, content)
        
        # Write changes if not dry run
        if not dry_run and content != original_content:
            file_path.write_text(content, encoding='utf-8')
        
        return {
            'changed': content != original_content,
            'changes': changes
        }
        
    except Exception as e:
        return {'error': str(e)}

def main():
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == '--fix':
        print("=== FIXING LEGACY WEBSITE PATHS ===\n")
        dry_run = False
    else:
        print("=== ANALYZING LEGACY WEBSITE PATHS (DRY RUN) ===\n")
        print("Use --fix to actually make changes\n")
        dry_run = True
    
    if dry_run:
        generate_report()
    else:
        # Fix paths
        fixed_files = 0
        total_changes = 0
        
        for file_path in sorted(ROOT.rglob("*")):
            if not file_path.is_file() or file_path.suffix.lower() not in EXTS:
                continue
                
            result = fix_paths_in_file(file_path, dry_run=False)
            
            if result.get('changed'):
                fixed_files += 1
                rel_path = file_path.relative_to(ROOT)
                print(f"✅ Fixed {rel_path}")
                
                for change in result['changes']:
                    print(f"  • {change}")
                    total_changes += 1
        
        print(f"\n=== FIX COMPLETE ===")
        print(f"Files fixed: {fixed_files}")
        print(f"Total changes: {total_changes}")

if __name__ == "__main__":
    main()
