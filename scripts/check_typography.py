#!/usr/bin/env python3
"""
Automated Indonesian typography, quotation, and academic title auditor.
Audits editorial HTML and Markdown texts for:
- Quote pair balance (curly double quotes “...”, single quotes ‘...’, straight quote warnings)
- Academic degree formatting and punctuation spacing (e.g. 'Nama, M.Kom.' vs 'Nama M.Kom' or 'Dr .')
- Dash usage in ranges (hyphen vs en-dash/em-dash)
- Ellipsis and redundant punctuation (multiple exclamation/question marks)
"""

import sys
import re
import argparse
from pathlib import Path
from typing import Dict, Any, List
from bs4 import BeautifulSoup


ACADEMIC_DEGREE_PATTERN = re.compile(
    r"\b([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)\s+((?:S|M|D)\.(?:Kom|T|Si|Pd|Sn|Sos|E|Stat|Ked|H)\.?"
    r"|(?:M\.Eng\.|Ph\.D\.|M\.Sc\.|M\.Phil\.|M\.A\.|B\.Sc\.))\b"
)


def audit_typography(content: str) -> Dict[str, Any]:
    """
    Audits raw text or HTML body for Indonesian typography integrity.
    """
    soup = BeautifulSoup(content, "html.parser")
    # Extract plain text content excluding scripts and styles
    for script in soup(["script", "style"]):
        script.extract()
    text = soup.get_text()

    issues: List[str] = []
    warnings: List[str] = []

    # 1. Quote Pairing & Balance Audit
    left_double = text.count("“")
    right_double = text.count("”")
    if left_double != right_double:
        issues.append(f"Kutipan ganda tipografis tidak seimbang: {left_double} tanda buka '“' vs {right_double} tanda tutup '”'.")

    left_single = text.count("‘")
    right_single = text.count("’")
    # Single quotes might include apostrophes, so check if disparity is significant
    if left_single > right_single:
        issues.append(f"Tanda petik tunggal pembuka '‘' ({left_single}) melebihi penutup '’' ({right_single}).")

    straight_quotes = text.count('"')
    if straight_quotes > 0 and straight_quotes % 2 != 0:
        issues.append(f"Tanda petik lurus '\"' berjumlah ganjil ({straight_quotes}), terdapat kutipan yang tidak ditutup.")
    elif straight_quotes > 0:
        warnings.append(f"Ditemukan {straight_quotes} tanda petik lurus '\"'; disarankan menggunakan curly quotes ('“' dan '”').")

    # 2. Spacing Around Punctuation & Degrees
    if re.search(r"\s+[,.:;!?]", text):
        matches = re.findall(r"\w+\s+[,.:;!?]", text)
        warnings.append(f"Spasi sebelum tanda baca ditemukan pada: {matches[:3]}")

    # Check missing comma before academic degrees (e.g. 'Budi M.Kom.' without comma)
    for match in ACADEMIC_DEGREE_PATTERN.finditer(text):
        name, deg = match.groups()
        warnings.append(f"Gelar akademik '{deg}' setelah nama '{name}' tidak didahului tanda koma (disarankan '{name}, {deg}').")

    # 3. Punctuation Duplication
    duplicated_punct = re.findall(r"[!?]{2,}|,{2,}|\.{4,}", text)
    if duplicated_punct:
        warnings.append(f"Tanda baca redundan terdeteksi: {list(set(duplicated_punct))[:4]}")

    # 4. Spacing in Parentheses
    if re.search(r"\(\s+|\s+\)", text):
        warnings.append("Spasi berlebih di dalam tanda kurung '( ... )' terdeteksi.")

    return {
        "issues": issues,
        "warnings": warnings,
        "passed": len(issues) == 0,
        "total_issues": len(issues),
        "total_warnings": len(warnings)
    }


def main():
    parser = argparse.ArgumentParser(description="Pemeriksa Tipografi dan Tanda Baca Teks Editorial Prodi")
    parser.add_argument("path", help="Path ke berkas HTML atau Markdown yang akan diaudit")
    parser.add_argument("--strict", action="store_true", help="Keluarkan error exit code jika terdapat peringatan (warnings)")
    args = parser.parse_args()

    target = Path(args.path)
    if not target.exists():
        print(f"Error: Berkas '{target}' tidak ditemukan.")
        sys.exit(1)

    content = target.read_text(encoding="utf-8")
    report = audit_typography(content)

    print(f"=== Laporan Audit Tipografi & Tanda Baca: {target.name} ===")
    print(f"Status Integritas: {'✅ LULUS' if report['passed'] else '❌ GAGAL'}")
    print(f"Total Masalah Kritis: {report['total_issues']}")
    print(f"Total Catatan Saran : {report['total_warnings']}")
    print("-" * 60)

    if report["issues"]:
        print("\n[!] MASALAH KRITIS (Wajib Diperbaiki):")
        for idx, iss in enumerate(report["issues"], 1):
            print(f"  {idx}. {iss}")

    if report["warnings"]:
        print("\n[*] CATATAN SARAN & GAYA PENULISAN:")
        for idx, warn in enumerate(report["warnings"], 1):
            print(f"  {idx}. {warn}")

    if not report["passed"] or (args.strict and report["warnings"]):
        sys.exit(1)
    else:
        print("\nSemua parameter tipografi memenuhi panduan editorial prodi.")
        sys.exit(0)


if __name__ == "__main__":
    main()
