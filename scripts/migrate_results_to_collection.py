#!/usr/bin/env python3
import os, re, yaml, pathlib

SRC = "pages/results"
DST = "_results"
os.makedirs(DST, exist_ok=True)

fm_re = re.compile(r"^---\s*\n(.*?)\n---\s*\n", re.S)

def read_post(p):
    txt = open(p, "r", encoding="utf-8").read()
    m = fm_re.match(txt)
    if m:
        fm = yaml.safe_load(m.group(1)) or {}
        body = txt[m.end():]
    else:
        fm, body = {}, txt
    return fm, body

for root, _, files in os.walk(SRC):
    for fn in files:
        if not fn.endswith(".md"): continue
        p = os.path.join(root, fn)
        fm, body = read_post(p)
        fm.setdefault("layout", "result")

        # derive year and slug
        year = fm.get("year")
        if not year:
            m = re.search(r"\b(19\d{2}|20\d{2})\b", p)
            if m: year = int(m.group(1)); fm["year"] = year

        title = fm.get("title", pathlib.Path(fn).stem).strip()
        slug = re.sub(r"[^a-z0-9]+", "-", title.lower()).strip("-")
        # stable id
        if "id" not in fm:
            if "international" in slug and year:
                fm["id"] = f"intl-{year}"
                fm["is_championship"] = True
                fm.setdefault("series", "International Championship")
            else:
                fm["id"] = f"{slug}-{year or 'na'}"

        # keep legacy URL via redirect_from
        rel_old = "/" + os.path.relpath(p, ".").replace("\\","/")
        rf = fm.get("redirect_from", [])
        if isinstance(rf, str): rf = [rf]
        if rel_old not in rf: rf.append(rel_old)
        fm["redirect_from"] = rf

        out_name = f"{fm.get('year','0000')}-{slug}.md"
        out_path = os.path.join(DST, out_name)
        with open(out_path, "w", encoding="utf-8") as f:
            f.write("---\n")
            f.write(yaml.safe_dump(fm, sort_keys=False).strip())
            f.write("\n---\n")
            f.write(body)
        print("migrated:", out_path)

# leave a note in old dir
os.makedirs(SRC, exist_ok=True)
with open(os.path.join(SRC, "README.md"), "w", encoding="utf-8") as f:
    f.write("Results migrated into the `_results/` collection; redirects preserved.\n")


