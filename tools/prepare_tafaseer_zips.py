"""
Utility script to create compressed .zip archives for all non-bundled Tafaseer databases.
Run this script to generate zip archives ready to upload to:
- Primary: https://albayan.tecwindow.net/tafaseer/
- Backup: https://github.com/tecwindow/albayan-data/
"""

import os
import sys
import zipfile
from pathlib import Path

# Setup paths
PROJECT_ROOT = Path(__file__).resolve().parent.parent
TAFASEER_DIR = PROJECT_ROOT / "database" / "tafaseer"
OUTPUT_DIR = PROJECT_ROOT / "dist_tafaseer_zips"

OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# The 7 tafaseer to be hosted online (muyassar is bundled with installer)
TARGET_FILES = {
    "baghawy.db": "baghawy.zip",
    "jalalayn.DB": "jalalayn.zip",
    "katheer.db": "katheer.zip",
    "mukhtasar.db": "mukhtasar.zip",
    "qortoby.db": "qortoby.zip",
    "sa3dy.db": "sa3dy.zip",
    "tabary.db": "tabary.zip",
}

print("=" * 60)
print("Creating compressed Tafaseer ZIP packages...")
print("=" * 60)

total_orig_bytes = 0
total_zip_bytes = 0

for db_filename, zip_filename in TARGET_FILES.items():
    source_path = TAFASEER_DIR / db_filename
    if not source_path.exists():
        # Try lowercase or uppercase
        alt = TAFASEER_DIR / db_filename.lower()
        if alt.exists():
            source_path = alt
        else:
            print(f"[-] Warning: Source not found: {source_path}")
            continue

    dest_zip_path = OUTPUT_DIR / zip_filename
    internal_arcname = Path(zip_filename).stem.lower() + ".db"

    orig_size = source_path.stat().st_size
    total_orig_bytes += orig_size

    with zipfile.ZipFile(dest_zip_path, "w", zipfile.ZIP_DEFLATED, compresslevel=9) as zf:
        zf.write(source_path, arcname=internal_arcname)

    zip_size = dest_zip_path.stat().st_size
    total_zip_bytes += zip_size

    reduction = ((orig_size - zip_size) / orig_size) * 100
    print(
        f"[+] {zip_filename:15} | Orig: {orig_size / (1024*1024):6.2f} MB -> "
        f"Zip: {zip_size / (1024*1024):5.2f} MB ({reduction:.1f}% saved)"
    )

print("-" * 60)
total_orig_mb = total_orig_bytes / (1024 * 1024)
total_zip_mb = total_zip_bytes / (1024 * 1024)
total_saved_pct = ((total_orig_bytes - total_zip_bytes) / total_orig_bytes) * 100
print(f"Total Original: {total_orig_mb:.2f} MB")
print(f"Total Compressed: {total_zip_mb:.2f} MB ({total_saved_pct:.1f}% bandwidth saved)")
print(f"All packages saved in: {OUTPUT_DIR.resolve()}")
print("=" * 60)
