#!/usr/bin/env bash
set -euo pipefail
pip3 install -r scripts/requirements.txt
python3 scripts/scrape_champions_and_results.py \
  --source archive/champions.html \
  --out-yaml _data/champions.yml \
  --out-json assets/data/champions.json \
  --emit-markdown


