#!/usr/bin/env python3
"""
Analyze and classify documents in archive/legacy-website for the new documents library.

This script:
1. Finds all document files (.doc*, .pdf, .xls*, minutes, penguin patter)
2. Excludes results files, NORs, and classified ads
3. Classifies documents into categories
4. Generates a structured documents index
"""

import os
import re
import pathlib
from typing import Dict, List, Set
from collections import defaultdict

ROOT = pathlib.Path("archive/legacy-website")
DOC_EXTENSIONS = {".doc", ".docx", ".pdf", ".xls", ".xlsx"}
MINUTES_PATTERNS = ["minutes", "meeting"]
NEWSLETTER_PATTERNS = ["penguin.*patter", "newsletter"]
TECHNICAL_PATTERNS = ["tuning", "rig", "rigging", "construction", "technical", "handbook"]
FORM_PATTERNS = ["waiver", "application", "permission", "form"]
BOAT_PATTERNS = ["hull", "bill.*sale", "boat.*sale", "for.*sale"]

# Patterns to exclude
EXCLUDE_PATTERNS = [
    r"^\d{4}\.pdf$",  # YYYY.pdf (year results)
    r"^\d{4}_?NA.*\.pdf$",  # YYYY_NA.pdf (North American results)
    r"^\d{4}_?Int.*\.pdf$",  # YYYY_Int.pdf (International results)
    r".*NOR.*",  # Notice of Race
    r".*results.*",  # Results files
    r".*classified.*",  # Classified ads
    r".*wanted.*",  # Wanted ads
    r".*for.*sale.*",  # For sale ads
]

def should_exclude(filename: str) -> bool:
    """Check if a file should be excluded from the documents library."""
    filename_lower = filename.lower()
    
    for pattern in EXCLUDE_PATTERNS:
        if re.search(pattern, filename_lower):
            return True
    
    return False

def extract_boat_number(filename: str) -> str:
    """Extract boat number from filename if present."""
    # Look for patterns like "BRA 1234", "USA 5678", or just "1234"
    boat_patterns = [
        r"([A-Z]{3})\s*(\d{1,5})",  # BRA 1234
        r"\b(\d{1,5})\b",  # Just numbers
    ]
    
    for pattern in boat_patterns:
        match = re.search(pattern, filename)
        if match:
            if len(match.groups()) == 2:
                return f"{match.group(1)} {match.group(2)}"
            else:
                return match.group(1)
    
    return None

def classify_document(filename: str, filepath: str) -> Dict:
    """Classify a document into categories."""
    filename_lower = filename.lower()
    filepath_lower = filepath.lower()
    
    # Check for boat-specific documents
    boat_number = extract_boat_number(filename)
    if boat_number and any(pattern in filename_lower for pattern in BOAT_PATTERNS):
        return {
            "category": "boats",
            "boat_number": boat_number,
            "subcategory": "boat_specific"
        }
    
    # Check for minutes
    if any(pattern in filename_lower for pattern in MINUTES_PATTERNS):
        return {"category": "minutes", "subcategory": "meeting_minutes"}
    
    # Check for newsletters
    if any(re.search(pattern, filename_lower) for pattern in NEWSLETTER_PATTERNS):
        return {"category": "newsletter", "subcategory": "penguin_patter"}
    
    # Check for technical documents
    if any(pattern in filename_lower for pattern in TECHNICAL_PATTERNS):
        return {"category": "technical", "subcategory": "tuning_rigging"}
    
    # Check for forms
    if any(pattern in filename_lower for pattern in FORM_PATTERNS):
        return {"category": "forms", "subcategory": "waivers_applications"}
    
    # Default classification
    return {"category": "other", "subcategory": "miscellaneous"}

def analyze_documents() -> Dict:
    """Analyze all documents and return classification results."""
    documents = defaultdict(list)
    excluded_count = 0
    total_count = 0
    
    # Find all document files
    for file_path in ROOT.rglob("*"):
        if not file_path.is_file():
            continue
            
        filename = file_path.name
        file_ext = file_path.suffix.lower()
        
        # Check if it's a document file
        is_doc = (file_ext in DOC_EXTENSIONS or 
                 any(pattern in filename.lower() for pattern in MINUTES_PATTERNS + NEWSLETTER_PATTERNS))
        
        if not is_doc:
            continue
            
        total_count += 1
        
        # Check if should be excluded
        if should_exclude(filename):
            excluded_count += 1
            continue
        
        # Classify the document
        classification = classify_document(filename, str(file_path))
        
        # Create document entry
        doc_entry = {
            "filename": filename,
            "path": str(file_path.relative_to(ROOT)),
            "url": f"/archive/legacy-website/{file_path.relative_to(ROOT)}",
            "size": file_path.stat().st_size,
            "extension": file_ext,
            **classification
        }
        
        documents[classification["category"]].append(doc_entry)
    
    return {
        "documents": dict(documents),
        "stats": {
            "total_found": total_count,
            "excluded": excluded_count,
            "included": total_count - excluded_count,
            "categories": len(documents)
        }
    }

def generate_documents_markdown(analysis: Dict) -> str:
    """Generate markdown content for the documents page."""
    docs = analysis["documents"]
    stats = analysis["stats"]
    
    markdown = f"""---
layout: page
title: Documents
permalink: /documents/
---

# Documents Library

This page provides access to historical documents from the Penguin Class archives. The library contains {stats['included']} documents organized into {stats['categories']} categories.

## Document Categories

"""
    
    # Define category descriptions
    category_descriptions = {
        "boats": "Documents related to specific boats, including hull information, bills of sale, and boat-specific records.",
        "forms": "Official forms, waivers, applications, and permission documents.",
        "minutes": "Meeting minutes from annual meetings and other official gatherings.",
        "newsletter": "Penguin Patter newsletters and other class communications.",
        "technical": "Technical documents including tuning guides, rigging instructions, and construction information.",
        "other": "Miscellaneous documents that don't fit into other categories."
    }
    
    # Generate sections for each category
    for category, docs_list in docs.items():
        if not docs_list:
            continue
            
        markdown += f"### {category.title()}\n\n"
        markdown += f"{category_descriptions.get(category, '')}\n\n"
        
        # Sort documents by filename
        docs_list.sort(key=lambda x: x["filename"])
        
        for doc in docs_list:
            # Format file size
            size_kb = doc["size"] // 1024
            size_str = f"{size_kb} KB" if size_kb < 1024 else f"{size_kb // 1024} MB"
            
            # Add boat number if available
            boat_info = f" (Boat {doc['boat_number']})" if doc.get('boat_number') else ""
            
            markdown += f"- [{doc['filename']}]({doc['url']}){boat_info} - {size_str}\n"
        
        markdown += "\n"
    
    return markdown

def main():
    print("Analyzing documents in archive/legacy-website...")
    
    analysis = analyze_documents()
    stats = analysis["stats"]
    
    print(f"\nDocument Analysis Results:")
    print(f"Total files found: {stats['total_found']}")
    print(f"Excluded (results, NORs, etc.): {stats['excluded']}")
    print(f"Included in library: {stats['included']}")
    print(f"Categories: {stats['categories']}")
    
    print(f"\nDocuments by category:")
    for category, docs in analysis["documents"].items():
        print(f"  {category}: {len(docs)} documents")
    
    # Generate markdown
    markdown_content = generate_documents_markdown(analysis)
    
    # Write to file
    output_file = "pages/documents.md"
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(markdown_content)
    
    print(f"\nGenerated documents index: {output_file}")
    
    # Also save the analysis data as JSON for potential future use
    import json
    with open("documents_analysis.json", 'w', encoding='utf-8') as f:
        json.dump(analysis, f, indent=2, ensure_ascii=False)
    
    print("Saved detailed analysis to: documents_analysis.json")

if __name__ == "__main__":
    main()
