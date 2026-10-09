#!/usr/bin/env python3
"""
Automated hyperlink and anchor consistency auditor for academic publications.
Audits HTML documents for:
- Local fragment anchor consistency (href="#target" must match an existing element id or name)
- Internal link HTTPS protocol enforcement
- Low-information anchor text detection (e.g. 'klik di sini', 'link', 'baca di sini')
- External link rel="noopener noreferrer" security attribute compliance
- Missing or malformed href attributes
"""

import sys
import re
import json
import argparse
from pathlib import Path
from typing import Dict, Any, List, Set
from bs4 import BeautifulSoup
from urllib.parse import urlparse


GENERIC_ANCHOR_TEXTS = {
    "klik di sini", "klik disini", "click here", "di sini", "disini",
    "link", "tautan", "baca", "selengkapnya", "read more", "here", "info"
}

ALLOWED_INTERNAL_DOMAINS = {
    "bif-pwt.telkomuniversity.ac.id",
    "telkomuniversity.ac.id",
    "ittelkom-pwt.ac.id"
}


def audit_hyperlinks(html_content: str, source_label: str = "content") -> Dict[str, Any]:
    """
    Audits an HTML string for link integrity, anchor targets, and security attributes.
    """
    soup = BeautifulSoup(html_content, "html.parser")
    anchors = soup.find_all("a")

    # Collect all available element ids and anchor names in the document
    available_ids: Set[str] = set()
    for el in soup.find_all(True):
        if el.get("id"):
            available_ids.add(el["id"].strip())
        if el.name == "a" and el.get("name"):
            available_ids.add(el["name"].strip())

    issues: List[str] = []
    warnings: List[str] = []
    total_links = 0
    internal_links = 0
    external_links = 0
    fragment_links = 0

    for a in anchors:
        href = (a.get("href") or "").strip()
        text = a.get_text().strip().lower()

        if not href:
            issues.append(f"Anchor '<a ...>{a.get_text()[:30]}</a>' tidak memiliki atribut href yang valid.")
            continue

        total_links += 1

        # Check for generic/empty anchor text
        if not text and not a.find_all(["img", "svg"]):
            warnings.append(f"Tautan ke '{href}' tidak memiliki anchor text atau elemen gambar deskriptif.")
        elif text in GENERIC_ANCHOR_TEXTS:
            warnings.append(f"Anchor text tidak deskriptif ('{a.get_text().strip()}') menuju '{href}'; disarankan menggunakan teks bermakna.")

        # 1. Local fragment anchor verification
        if href.startswith("#"):
            fragment_links += 1
            frag_id = href[1:]
            if not frag_id:
                warnings.append("Atribut href berisi '#' kosong tanpa target id yang spesifik.")
            elif frag_id not in available_ids:
                issues.append(f"Anchor lokal '{href}' merujuk target id yang tidak ditemukan dalam dokumen.")

        # 2. HTTP/HTTPS Protocol and External/Internal checks
        elif href.startswith(("http://", "https://")):
            parsed = urlparse(href)
            netloc = parsed.netloc.lower()
            is_internal = any(netloc == d or netloc.endswith("." + d) for d in ALLOWED_INTERNAL_DOMAINS)

            if is_internal:
                internal_links += 1
                if parsed.scheme == "http":
                    issues.append(f"Tautan internal '{href}' menggunakan HTTP tidak aman; wajib menggunakan HTTPS.")
            else:
                external_links += 1
                rel_attr = a.get("rel") or []
                rel_set = set(rel_attr) if isinstance(rel_attr, list) else set(rel_attr.split())
                if "noopener" not in rel_set and "noreferrer" not in rel_set:
                    warnings.append(f"Tautan eksternal '{href}' tidak memiliki rel='noopener noreferrer'.")
        elif href.startswith(("/", "./", "../")):
            internal_links += 1

    return {
        "source": source_label,
        "total_links": total_links,
        "internal_links": internal_links,
        "external_links": external_links,
        "fragment_links": fragment_links,
        "issues": issues,
        "warnings": warnings,
        "is_valid": len(issues) == 0,
    }


def main():
    parser = argparse.ArgumentParser(description="Auditor Konsistensi Hyperlink dan Anchor Target Konten Editorial")
    parser.add_argument("path", help="Path file HTML atau direktori yang akan diaudit")
    parser.add_argument("--strict", action="store_true", help="Gagalkan audit (exit code 1) jika ada warning")
    parser.add_argument("--json", action="store_true", help="Output hasil dalam format JSON")

    args = parser.parse_args()
    target = Path(args.path)

    if not target.exists():
        print(f"Error: Jalur '{args.path}' tidak ditemukan.", file=sys.stderr)
        sys.exit(1)

    html_files = [target] if target.is_file() else list(target.glob("**/*.html"))

    if not html_files:
        print("Tidak ada berkas .html yang ditemukan untuk diaudit.")
        sys.exit(0)

    results = []
    has_critical_error = False
    has_warning_error = False

    for f in html_files:
        content = f.read_text(encoding="utf-8", errors="ignore")
        report = audit_hyperlinks(content, source_label=str(f))
        results.append(report)
        if not report["is_valid"]:
            has_critical_error = True
        if report["warnings"]:
            has_warning_error = True

    if args.json:
        print(json.dumps(results, indent=2, ensure_ascii=False))
    else:
        for r in results:
            status = "✅ LOLOS" if r["is_valid"] and not r["warnings"] else ("⚠️ PERINGATAN" if r["is_valid"] else "❌ GAGAL")
            print(f"\nAudit: {r['source']} [{status}]")
            print(f" - Total Tautan: {r['total_links']} (Internal: {r['internal_links']}, Eksternal: {r['external_links']}, Fragment: {r['fragment_links']})")
            if r["issues"]:
                print(" - Masalah Kritis:")
                for i in r["issues"]:
                    print(f"   [!] {i}")
            if r["warnings"]:
                print(" - Peringatan Kualitas:")
                for w in r["warnings"]:
                    print(f"   [*] {w}")

    if has_critical_error or (args.strict and has_warning_error):
        sys.exit(1)
    sys.exit(0)


if __name__ == "__main__":
    main()
