#!/usr/bin/env bash
set -euo pipefail
pip3 install -r scripts/requirements.txt
python3 scripts/import_champions_pipeline.py \
  --html archive/legacy-website/champions.html \
  --emit-results \
  "$@"

