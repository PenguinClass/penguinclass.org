# penguinclass.org

International Penguin Class Dinghy Association website (Jekyll) with a full legacy archive redirect via 404.

## Quick start
```bash
git clone https://github.com/penguinclass/penguinclass.org.git
cd penguinclass.org
bundle install
bundle exec jekyll serve
```

## Archive workflow
1. Mirror `penguinclass.com` locally (see `archive/README.md`).
2. Copy mirrored files into `archive/` preserving structure.
3. Build manifest:
```bash
python3 scripts/build_archive_manifest.py archive
```
4. Commit and push.
