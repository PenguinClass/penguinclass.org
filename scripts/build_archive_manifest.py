#!/usr/bin/env python3
import os, json, sys

ARCHIVE_ROOT = sys.argv[1] if len(sys.argv) > 1 else "archive"
OUT = os.path.join(ARCHIVE_ROOT, "manifest.json")

def norm(p:str)->str:
    p = p.replace("\\","/").lower()
    if p.startswith("./"): p = p[2:]
    if p.startswith("/"): p = p[1:]
    return p

mapping = {}

for root, _, files in os.walk(ARCHIVE_ROOT):
    for fn in files:
        rel = os.path.relpath(os.path.join(root, fn), ".").replace("\\","/")
        if any(fn.lower().endswith(ext) for ext in (
            ".html",".htm",".pdf",".jpg",".jpeg",".png",".gif",".webp",".svg",".txt",".css",".js"
        )):
            rel_no_prefix = rel[len("archive/"):] if rel.startswith("archive/") else rel
            keys = set()
            keys.add(norm(rel_no_prefix))
            if rel_no_prefix.endswith("index.html"):
                keys.add(norm(rel_no_prefix[:-10]))
                keys.add(norm(rel_no_prefix[:-10] + "/"))
            if rel_no_prefix.endswith(".html"):
                keys.add(norm(rel_no_prefix[:-5]))
            for k in keys:
                mapping[k] = "/" + rel

os.makedirs(ARCHIVE_ROOT, exist_ok=True)
with open(OUT, "w", encoding="utf-8") as f:
    json.dump(mapping, f, separators=(",",":"))
print(f"Wrote {OUT} with {len(mapping)} entries")
