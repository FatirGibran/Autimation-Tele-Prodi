#!/usr/bin/env python3
"""
Image asset compliance and modern compression checker for editorial articles.
Audits HTML files for missing alt text, non-WebP/AVIF formats, missing lazy loading, and dimension attributes.
"""

import sys
import re
import argparse
from pathlib import Path
from typing import Dict, Any, List
from bs4 import BeautifulSoup


GENERIC_ALT_STRINGS = {"image", "gambar", "foto", "photo", "pic", "picture", "untitled", "img"}


def audit_html_images(html_content: str) -> Dict[str, Any]:
    soup = BeautifulSoup(html_content, "html.parser")
    images = soup.find_all("img")

    issues: List[str] = []
    total_images = len(images)
    modern_format_count = 0
    lazy_loaded_count = 0

    for idx, img in enumerate(images, 1):
        src = img.get("src", "").strip()
        alt = img.get("alt", "").strip()
        loading = img.get("loading", "").strip()

        if not src:
            issues.append(f"Gambar #{idx} tidak memiliki atribut 'src'.")
            continue

        if not alt:
            issues.append(f"Gambar #{idx} ({src[:40]}...) tidak memiliki atribut 'alt'.")
        elif alt.lower() in GENERIC_ALT_STRINGS:
            issues.append(f"Gambar #{idx} memiliki alt text generik: '{alt}'.")

        if loading.lower() == "lazy":
            lazy_loaded_count += 1

        # Check format
        src_lower = src.lower()
        if src_lower.endswith((".webp", ".avif", ".svg")):
            modern_format_count += 1
        elif src_lower.endswith((".bmp", ".tiff")):
            issues.append(f"Gambar #{idx} menggunakan format usang/tidak terkompresi ({src}).")

        # Check dimensions
        has_dims = bool(img.get("width") and img.get("height"))
        if not has_dims and "style" not in img.attrs:
            issues.append(f"Gambar #{idx} ({src[:40]}...) tidak memiliki atribut width/height (risiko CLS).")

    return {
        "total_images": total_images,
        "modern_format_count": modern_format_count,
        "lazy_loaded_count": lazy_loaded_count,
        "issues_count": len(issues),
        "is_compliant": len(issues) == 0,
        "issues": issues,
    }


def main():
    parser = argparse.ArgumentParser(description="Audit HTML images for SEO, accessibility, and modern format compliance")
    parser.add_argument("target", nargs="?", default="articles", help="File HTML atau direktori artikel")
    parser.add_argument("--strict", action="store_true", help="Keluar dengan exit code 1 jika ada isu gambar")
    args = parser.parse_args()

    target_path = Path(args.target)
    if not target_path.exists():
        print(f"Target tidak ditemukan: {target_path}")
        sys.exit(1)

    html_files = [target_path] if target_path.is_file() else list(target_path.glob("**/*.html"))

    if not html_files:
        print(f"Tidak ada berkas HTML ditemukan di {target_path}")
        return

    has_failures = False
    print(f"Memeriksa aset gambar pada {len(html_files)} berkas HTML...\n")

    for f in html_files:
        content = f.read_text(encoding="utf-8")
        report = audit_html_images(content)

        if not report["is_compliant"]:
            has_failures = True
            print(f"⚠️ {f.name} ({report['total_images']} gambar, {report['issues_count']} isu):")
            for issue in report["issues"]:
                print(f"   - {issue}")
        else:
            print(f"✅ {f.name} ({report['total_images']} gambar patuh)")

    if has_failures and args.strict:
        sys.exit(1)


if __name__ == "__main__":
    main()
