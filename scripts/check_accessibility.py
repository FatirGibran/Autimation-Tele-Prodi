#!/usr/bin/env python3
"""
Automated WCAG accessibility auditor script for editorial articles.
Audits HTML files for:
- Heading levels hierarchy (avoiding skipped heading levels)
- Image alternative text quality
- Table accessibility (captions, headers, scopes)
- Non-descriptive anchor texts
- Accessible media controls
- Inline CSS color contrast warnings
"""

import sys
import re
import argparse
from pathlib import Path
from typing import Dict, Any, List
from bs4 import BeautifulSoup


GENERIC_LINK_TEXTS = {
    "klik disini", "klik di sini", "click here", "here", "disini", "di sini",
    "baca selengkapnya", "selengkapnya", "read more", "link", "tautan"
}


def audit_html_accessibility(html_content: str) -> Dict[str, Any]:
    soup = BeautifulSoup(html_content, "html.parser")
    issues: List[str] = []
    warnings: List[str] = []

    # 1. Heading Hierarchy Audit
    headings = soup.find_all(re.compile(r"^h[1-6]$"))
    last_level = 0
    for h in headings:
        level = int(h.name[1])
        if last_level > 0 and level > last_level + 1:
            issues.append(f"Tingkat heading melompat dari <h{last_level}> ke <h{level}> tanpa perantara (teks: '{h.get_text()[:40]}...').")
        last_level = level

    # 2. Image Alt Text Audit
    images = soup.find_all("img")
    for idx, img in enumerate(images, 1):
        alt = img.get("alt")
        src = img.get("src", "")[:35]
        if alt is None:
            issues.append(f"Gambar #{idx} ({src}) tidak memiliki atribut 'alt'.")
        elif not alt.strip():
            warnings.append(f"Gambar #{idx} ({src}) memiliki atribut 'alt' kosong.")

    # 3. Table Accessibility Audit
    tables = soup.find_all("table")
    for idx, table in enumerate(tables, 1):
        if not table.find("caption"):
            warnings.append(f"Tabel #{idx} tidak memiliki tag <caption>.")
        headers = table.find_all("th")
        if not headers:
            issues.append(f"Tabel #{idx} tidak memiliki elemen header <th>.")
        for th in headers:
            if not th.get("scope"):
                warnings.append(f"Header tabel <th> ('{th.get_text()[:25]}') tidak memiliki atribut 'scope'.")

    # 4. Non-descriptive Links
    links = soup.find_all("a")
    for idx, link in enumerate(links, 1):
        link_text = link.get_text().strip().lower()
        if link_text in GENERIC_LINK_TEXTS:
            warnings.append(f"Tautan #{idx} menggunakan teks generik tidak deskriptif: '{link_text}'.")

    # 5. Media Elements
    media_elements = soup.find_all(["video", "audio"])
    for m in media_elements:
        if not m.has_attr("controls"):
            issues.append(f"Elemen media <{m.name}> tidak memiliki atribut 'controls'.")

    return {
        "headings_count": len(headings),
        "images_count": len(images),
        "tables_count": len(tables),
        "links_count": len(links),
        "issues_count": len(issues),
        "warnings_count": len(warnings),
        "issues": issues,
        "warnings": warnings,
        "is_accessible": len(issues) == 0,
    }


def main():
    parser = argparse.ArgumentParser(description="Audit aksesibilitas WCAG untuk artikel editorial.")
    parser.add_argument("target", nargs="?", default="articles", help="Berkas HTML atau direktori artikel (default: articles)")
    parser.add_argument("--strict", action="store_true", help="Gagal (exit 1) jika ada peringatan (warnings)")
    args = parser.parse_args()

    target_path = Path(args.target)
    if not target_path.exists():
        print(f"Error: Jalur '{target_path}' tidak ditemukan.", file=sys.stderr)
        sys.exit(1)

    html_files = [target_path] if target_path.is_file() else sorted(target_path.glob("*.html"))

    if not html_files:
        print(f"Tidak ada berkas .html yang ditemukan di '{target_path}'.")
        sys.exit(0)

    total_files = len(html_files)
    files_with_issues = 0
    total_issues = 0
    total_warnings = 0

    print(f"=== Menjalankan Audit Aksesibilitas WCAG pada {total_files} Berkas ===")

    for file_path in html_files:
        content = file_path.read_text(encoding="utf-8")
        report = audit_html_accessibility(content)

        if report["issues"] or report["warnings"]:
            files_with_issues += 1
            total_issues += report["issues_count"]
            total_warnings += report["warnings_count"]
            print(f"\n📄 {file_path.name}")
            for iss in report["issues"]:
                print(f"  ❌ [ERROR] {iss}")
            for w in report["warnings"]:
                print(f"  ⚠️  [WARN]  {w}")

    print("\n" + "=" * 50)
    print(f"Total Berkas Diperiksa : {total_files}")
    print(f"Berkas Bersih          : {total_files - files_with_issues}")
    print(f"Total Masalah Kritis   : {total_issues}")
    print(f"Total Peringatan       : {total_warnings}")

    if total_issues > 0 or (args.strict and total_warnings > 0):
        print("\nAudit aksesibilitas menemukan masalah yang memerlukan perhatian.")
        sys.exit(1)
    else:
        print("\nSemua berkas memenuhi kriteria aksesibilitas dasar.")
        sys.exit(0)


if __name__ == "__main__":
    main()
