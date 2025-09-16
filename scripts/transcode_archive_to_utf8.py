#!/usr/bin/env python3
import sys, os, re, pathlib, shutil
from typing import Optional
try:
    import chardet  # type: ignore
except ImportError:
    print("Please: pip3 install chardet", file=sys.stderr); sys.exit(1)

ROOT = pathlib.Path("archive/legacy-website")
EXTS = {".html", ".htm", ".txt", ".css", ".js"}
META_RE  = re.compile(r'(?is)<meta\s+http-equiv=["\']?content-type["\']?\s+content=["\']text/html;\s*charset=([a-z0-9\-\_]+)["\']?\s*/?>')
META2_RE = re.compile(r'(?is)<meta\s+charset=["\']?([a-z0-9\-\_]+)["\']?\s*/?>')
FFFD = "\uFFFD"

def detect_encoding(b: bytes) -> Optional[str]:
    # If it already decodes as utf-8 without errors, return utf-8 quickly
    try:
        b.decode("utf-8")
        return "utf-8"
    except UnicodeDecodeError:
        pass
    res = chardet.detect(b)
    enc = (res.get("encoding") or "").lower()
    # normalize common labels
    if enc in ("iso-8859-1", "latin-1", "ansi_x3.4-1968"):
        enc = "windows-1252"  # most web content actually uses CP1252
    return enc or None

def normalize_meta(html: str) -> str:
    """Ensure a single <meta charset="utf-8"> in <head>; remove legacy http-equiv."""
    out = META_RE.sub("", html)            # drop http-equiv content-type metas
    out = META2_RE.sub("", out)            # drop existing charset metas
    # insert a fresh meta near <head>
    head_re = re.compile(r'(?is)<head[^>]*>')
    if head_re.search(out):
        out = head_re.sub(lambda m: m.group(0) + '\n<meta charset="utf-8">', out, count=1)
    else:
        # no head? prepend minimal meta (rare legacy pages)
        out = '<meta charset="utf-8">\n' + out
    return out

def maybe_fix_mojibake(s: str) -> str:
    """
    Optional light repair: if we see common UTF-8-as-CP1252 mojibake (Ã©, Ã±, â€"),
    try a round-trip fix on small segments. Only apply when many FFFD or mojibake trigrams detected.
    """
    if s.count("Ã") + s.count("â") + s.count("Â") < 3:
        return s
    try:
        # encode back to latin-1 bytes then decode as utf-8
        return s.encode("latin-1", errors="ignore").decode("utf-8", errors="ignore")
    except Exception:
        return s

def process_file(p: pathlib.Path) -> str:
    b = p.read_bytes()
    enc = detect_encoding(b)
    if not enc:
        return f"SKIP ?enc  {p}"
    if enc == "utf-8":
        # still normalize meta for HTML
        if p.suffix.lower() in (".html", ".htm"):
            txt = b.decode("utf-8", errors="strict")
            before = txt
            txt = normalize_meta(txt)
            if FFFD in txt:  # try mojibake fix only if already bad
                txt2 = maybe_fix_mojibake(txt)
                if txt2.count(FFFD) < txt.count(FFFD): txt = txt2
            if txt != before:
                p.write_text(txt, encoding="utf-8", newline="")
                return f"FIX meta {p}"
        return f"OK  utf8 {p}"
    # transcode to utf-8 text
    try:
        txt = b.decode(enc, errors="strict")
    except Exception:
        # fallback: replace errors
        txt = b.decode(enc, errors="replace")
    # normalize meta only for html/htm
    if p.suffix.lower() in (".html", ".htm"):
        txt = normalize_meta(txt)
        # remove FFFD if possible via mojibake fixer
        if FFFD in txt:
            txt2 = maybe_fix_mojibake(txt)
            if txt2.count(FFFD) <= txt.count(FFFD): txt = txt2
    # write back as utf-8 (no BOM)
    p.write_text(txt, encoding="utf-8", newline="")
    return f"XCODE {enc:>10} -> utf8  {p}"

def main():
    if not ROOT.exists():
        print(f"{ROOT} not found", file=sys.stderr); sys.exit(1)
    changed = 0
    for p in sorted(ROOT.rglob("*")):
        if not p.is_file(): continue
        if p.suffix.lower() not in EXTS: continue
        # don't touch Jekyll files accidentally
        head = p.read_bytes()[:3]
        if head.startswith(b"---"):  # file has YAML front matter; skip just in case
            continue
        msg = process_file(p)
        print(msg)
        if msg.startswith(("XCODE","FIX")):
            changed += 1
    print(f"\nDone. Changed {changed} files.")
if __name__ == "__main__":
    main()
