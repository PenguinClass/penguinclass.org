# Archive
Place the full mirrored legacy content of penguinclass.com here, preserving folders and filenames.

## Mirror commands (run locally)
# wget example:
wget --mirror --convert-links --adjust-extension --page-requisites --no-parent   https://www.penguinclass.com/ -P legacy_mirror

# Move into repo:
rsync -av legacy_mirror/www.penguinclass.com/ ./archive/

# Build manifest:
python3 scripts/build_archive_manifest.py archive
