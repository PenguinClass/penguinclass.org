#!/usr/bin/env python3
"""
Deduplicate documents.md by removing entries with identical filename and size.

This script:
1. Parses the documents.md file
2. Identifies duplicate entries (same filename and size)
3. Keeps the entry with the shortest path (preferring root directory over subdirectories)
4. Regenerates the documents.md file without duplicates
"""

import re
import pathlib
from typing import List, Dict, Tuple
from collections import defaultdict

def parse_documents_markdown(file_path: str) -> Tuple[str, List[Dict]]:
    """Parse the documents.md file and extract document entries."""
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Split content into header and document entries
    lines = content.split('\n')
    header_lines = []
    document_entries = []
    
    in_document_section = False
    current_category = None
    
    for line in lines:
        if line.startswith('### '):
            in_document_section = True
            current_category = line.replace('### ', '').strip()
            header_lines.append(line)
        elif line.startswith('## ') or line.startswith('# '):
            in_document_section = False
            current_category = None
            header_lines.append(line)
        elif in_document_section and line.startswith('- ['):
            # Parse document entry: - [filename](url) - size
            match = re.match(r'- \[([^\]]+)\]\(([^)]+)\)(?: - (.+))?', line)
            if match:
                filename = match.group(1)
                url = match.group(2)
                size_info = match.group(3) if match.group(3) else ""
                
                # Extract size in bytes for comparison
                size_bytes = 0
                if 'KB' in size_info:
                    size_bytes = int(float(size_info.replace(' KB', '')) * 1024)
                elif 'MB' in size_info:
                    size_bytes = int(float(size_info.replace(' MB', '')) * 1024 * 1024)
                
                document_entries.append({
                    'line': line,
                    'filename': filename,
                    'url': url,
                    'size_info': size_info,
                    'size_bytes': size_bytes,
                    'category': current_category,
                    'path': url.replace('/archive/legacy-website/', '')
                })
            else:
                header_lines.append(line)
        else:
            header_lines.append(line)
    
    return '\n'.join(header_lines), document_entries

def deduplicate_documents(document_entries: List[Dict]) -> List[Dict]:
    """Remove duplicate documents, keeping the one with the shortest path."""
    # Group documents by filename and size
    groups = defaultdict(list)
    
    for doc in document_entries:
        key = (doc['filename'], doc['size_bytes'])
        groups[key].append(doc)
    
    # For each group, keep the document with the shortest path
    deduplicated = []
    
    for (filename, size_bytes), docs in groups.items():
        if len(docs) == 1:
            # No duplicates, keep as is
            deduplicated.append(docs[0])
        else:
            # Multiple entries with same filename and size
            # Sort by path length (shorter paths first)
            docs.sort(key=lambda x: len(x['path']))
            
            # Keep the first one (shortest path)
            kept_doc = docs[0]
            deduplicated.append(kept_doc)
            
            # Log the duplicates that were removed
            removed_paths = [doc['path'] for doc in docs[1:]]
            print(f"Removed duplicates for '{filename}' ({size_bytes} bytes):")
            for path in removed_paths:
                print(f"  - {path}")
            print(f"  Kept: {kept_doc['path']}")
            print()
    
    return deduplicated

def regenerate_documents_markdown(header: str, document_entries: List[Dict]) -> str:
    """Regenerate the documents.md content with deduplicated entries."""
    lines = header.split('\n')
    result_lines = []
    
    current_category = None
    category_docs = defaultdict(list)
    
    # Group documents by category
    for doc in document_entries:
        category_docs[doc['category']].append(doc)
    
    # Process each line and insert documents when we hit category headers
    for line in lines:
        if line.startswith('### '):
            category = line.replace('### ', '').strip()
            current_category = category
            result_lines.append(line)
            
            # Add category description if it exists
            next_line_idx = lines.index(line) + 1
            if next_line_idx < len(lines) and lines[next_line_idx].strip() and not lines[next_line_idx].startswith('-'):
                result_lines.append(lines[next_line_idx])
                result_lines.append('')  # Empty line after description
            
            # Add documents for this category
            if category in category_docs:
                # Sort documents by filename
                docs = sorted(category_docs[category], key=lambda x: x['filename'])
                for doc in docs:
                    result_lines.append(doc['line'])
                result_lines.append('')  # Empty line after category
        else:
            result_lines.append(line)
    
    return '\n'.join(result_lines)

def update_document_count(content: str, new_count: int) -> str:
    """Update the document count in the header."""
    # Find and replace the count in the header
    pattern = r'contains \d+ documents'
    replacement = f'contains {new_count} documents'
    return re.sub(pattern, replacement, content)

def main():
    input_file = "pages/documents.md"
    output_file = "pages/documents.md"
    
    print("Parsing documents.md...")
    header, document_entries = parse_documents_markdown(input_file)
    
    print(f"Found {len(document_entries)} document entries")
    
    print("Deduplicating documents...")
    deduplicated_entries = deduplicate_documents(document_entries)
    
    print(f"After deduplication: {len(deduplicated_entries)} document entries")
    print(f"Removed {len(document_entries) - len(deduplicated_entries)} duplicate entries")
    
    print("Regenerating documents.md...")
    new_content = regenerate_documents_markdown(header, deduplicated_entries)
    
    # Update the document count in the header
    new_content = update_document_count(new_content, len(deduplicated_entries))
    
    # Write the deduplicated content
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(new_content)
    
    print(f"Updated {output_file} with deduplicated content")

if __name__ == "__main__":
    main()
