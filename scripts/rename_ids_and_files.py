#!/usr/bin/env python3
import os, re, sys, time, shutil, yaml
from pathlib import Path

Y = lambda p: yaml.safe_load(Path(p).read_text(encoding="utf-8")) if Path(p).exists() else None
W = lambda p,d: Path(p).write_text(yaml.safe_dump(d, sort_keys=False, allow_unicode=True, width=1200), encoding="utf-8")

def fm_split(txt):
    m = re.match(r"^---\s*\n(.*?)\n---\s*\n(.*)$", txt, re.S)
    if not m: return {}, txt
    return yaml.safe_load(m.group(1)) or {}, m.group(2)

def fm_join(fm, body):
    return "---\n" + yaml.safe_dump(fm, sort_keys=False).strip() + "\n---\n" + body

def canon_id(old_id, year):
    old = (old_id or "").lower()
    if old.startswith("intl-"): return f"international-{year}"
    if old.startswith("northamerica-") or old.startswith("na-"): return f"north-american-{year}"
    if old.startswith("international-"): return old
    if old.startswith("north-american-"): return old
    # fallback guesses
    if "international" in old: return f"international-{year}"
    if "north" in old and "american" in old: return f"north-american-{year}"
    return old

def ensure_redirect_from(fm, old_path):
    rf = fm.get("redirect_from", [])
    if isinstance(rf, str): rf = [rf]
    if old_path not in rf: rf.append(old_path)
    fm["redirect_from"] = rf

def main():
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("--write", action="store_true")
    args = ap.parse_args()

    changes = []

    # 1) Update _data/champions.yml (INTL only)
    cpath = Path("_data/champions.yml")
    if cpath.exists():
        champs = Y(cpath)
        touched = False
        for r in champs or []:
            y = r.get("year")
            if not y: continue
            rid = r.get("result_id","")
            new = canon_id(rid, y)
            if new != rid:
                r["result_id"] = new
                touched = True
                changes.append(f"champions.yml: {rid} -> {new}")
        if touched and args.write:
            backup = f"{cpath}.backup-{time.strftime('%Y%m%d-%H%M%S')}"
            shutil.copy(str(cpath), backup)
            W(cpath, champs)

    # 2) Update _data/champions_na.yml if present
    napath = Path("_data/champions_na.yml")
    if napath.exists():
        na = Y(napath)
        touched = False
        for r in na or []:
            y = r.get("year")
            rid = r.get("result_id","")
            new = canon_id(rid, y)
            if new != rid:
                r["result_id"] = new
                touched = True
                changes.append(f"champions_na.yml: {rid} -> {new}")
        if touched and args.write:
            backup = f"{napath}.backup-{time.strftime('%Y%m%d-%H%M%S')}"
            shutil.copy(str(napath), backup)
            W(napath, na)

    # 3) Update _results/*.md front matter id + filename + permalink, keep redirects
    results_dir = Path("_results")
    if results_dir.exists():
        for p in results_dir.glob("*.md"):
            txt = p.read_text(encoding="utf-8")
            fm, body = fm_split(txt)
            year = fm.get("year")
            old_id = fm.get("id","")
            if not year or not old_id: continue
            new_id = canon_id(old_id, year)
            if new_id != old_id:
                fm["id"] = new_id
                changes.append(f"{p}: id {old_id} -> {new_id}")

            # set canonical permalink based on series
            series = (fm.get("series") or "").lower()
            if "north" in series and "american" in series:
                want_slug = "north-american-championship"
            else:
                want_slug = "international-championship"

            want_name = f"{year}-{want_slug}.md"
            want_link = f"/results/{year}-{want_slug}/"

            # add redirect_from for old permalink and filename
            old_rel = "/" + str(p).replace("\\","/")
            ensure_redirect_from(fm, old_rel)
            if fm.get("permalink") and fm["permalink"] != want_link:
                ensure_redirect_from(fm, fm["permalink"])

            fm["permalink"] = want_link

            # write file (possibly rename)
            out_txt = fm_join(fm, body)
            if args.write:
                if p.name != want_name:
                    newp = p.with_name(want_name)
                    p.write_text(out_txt, encoding="utf-8")
                    # move -> keep old file as thin redirect file if needed, else rename
                    p.rename(newp)
                    p = newp
                else:
                    p.write_text(out_txt, encoding="utf-8")

    # 4) Update _events/*.md results_id + optional filename slug
    events_dir = Path("_events")
    if events_dir.exists():
        for p in events_dir.glob("*.md"):
            txt = p.read_text(encoding="utf-8")
            fm, body = fm_split(txt)
            rid = fm.get("results_id") or fm.get("id")
            year = fm.get("year")
            # try extract year from date if missing
            if not year:
                d = fm.get("date","")
                m = re.match(r"(\d{4})-", str(d))
                if m: year = int(m.group(1))
            if not rid or not year: continue
            new_rid = canon_id(rid, year)
            if new_rid != rid:
                fm["results_id"] = new_rid
                changes.append(f"{p}: results_id {rid} -> {new_rid}")

            title = (fm.get("title") or "").lower()
            if "north" in title and "american" in title:
                slug = "north-american-championship"
            elif "international" in title:
                slug = "international-championship"
            else:
                continue  # leave unrelated events alone

            # rename file slug but keep same date prefix
            m = re.match(r"(\d{4}-\d{2}-\d{2})-", p.name)
            if m:
                want_name = f"{m.group(1)}-{slug}.md"
                if args.write and p.name != want_name:
                    newp = p.with_name(want_name)
                    ensure_redirect_from(fm, "/" + str(p).replace("\\","/"))
                    p.write_text(fm_join(fm, body), encoding="utf-8")
                    p.rename(newp)
                else:
                    if args.write:
                        p.write_text(fm_join(fm, body), encoding="utf-8")

    # 5) Scan content for 'intl-'/'northamerica-' references and list them
    repo_refs = []
    for p in Path(".").rglob("*.*"):
        if any(seg.startswith(".git") for seg in p.parts): continue
        if p.suffix.lower() not in {".md",".html",".yml",".yaml"}: continue
        s = p.read_text(encoding="utf-8", errors="ignore")
        if re.search(r"\bintl-\d{4}\b", s) or re.search(r"\bnorthamerica-\d{4}\b", s):
            repo_refs.append(str(p))
    if repo_refs:
        changes.append("Still contains old ID strings in:")
        changes.extend("  - " + x for x in repo_refs)

    # Report
    print("DRY RUN" if not args.write else "APPLIED")
    if not changes:
        print("No changes needed.")
    else:
        print("\nChanges:")
        for c in changes: print("-", c)

if __name__ == "__main__":
    main()
