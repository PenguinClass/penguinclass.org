#!/usr/bin/env python3
import os, json, pathlib

ROOT = pathlib.Path("archive/legacy-website")
OUT  = pathlib.Path("assets/data/archive-manifest.json")

def variants(p: pathlib.Path):
    # Return normalized web paths for matching requests
    rel = "/" + str(p).replace("\\","/")  # e.g. /archive/legacy-website/path/file.html
    out = {rel}
    if rel.endswith("/index.html"):
        out.add(rel[:-11])            # /archive/legacy-website/path/
        out.add(rel[:-10])            # /archive/legacy-website/path
    if rel.endswith(".html"):
        out.add(rel[:-5])             # /archive/legacy-website/path/file
    return out

def main():
    if not ROOT.exists():
        print(f"Skip: {ROOT} not found")
        return
    paths = set()
    for base, _, files in os.walk(ROOT):
        for fn in files:
            if fn.startswith("."): continue
            p = pathlib.Path(base) / fn
            for v in variants(p):
                # store lowercase for case-insensitive matching
                paths.add(v.lower())
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(sorted(paths)), encoding="utf-8")
    print(f"Wrote {OUT} with {len(paths)} entries")

if __name__ == "__main__":
    main()