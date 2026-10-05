#!/usr/bin/env python3
"""
Dead link and broken anchor validator for editorial articles.
Scans HTML content for broken in-page anchors, malformed URLs, and missing media targets.
"""

import sys
import argparse
from pathlib import Path
from typing import Dict, Any
from bs4 import BeautifulSoup


def check_html_links_and_anchors(html_content: str) -> Dict[str, Any]:
    soup = BeautifulSoup(html_content, "html.parser")

    declared_anchors = set()
    for tag in soup.find_all(True):
        if tag.get("id"):
            declared_anchors.add(tag["id"])
        if tag.name == "a" and tag.get("name"):
            declared_anchors.add(tag["name"])

    broken_anchors = []
    malformed_links = []
    insecure_http_links = []
    empty_links = []
    total_links = 0

    for a in soup.find_all("a", href=True):
        total_links += 1
        href = a["href"].strip()

        if not href or href == "#":
            empty_links.append(str(a))
            continue

        if href.startswith("#"):
            target_id = href[1:]
            if target_id not in declared_anchors:
                broken_anchors.append({
                    "anchor": href,
                    "text": a.get_text(strip=True),
                    "element": str(a)
                })
        elif href.startswith("http://"):
            insecure_http_links.append(href)
        elif not (href.startswith("https://") or href.startswith("mailto:") or href.startswith("tel:") or href.startswith("/")):
            malformed_links.append(href)

    broken_images = []
    for img in soup.find_all("img"):
        src = img.get("src", "").strip()
        if not src:
            broken_images.append({"element": str(img), "reason": "Missing or empty src attribute"})
        elif not (src.startswith("http://") or src.startswith("https://") or src.startswith("/") or src.startswith("data:")):
            broken_images.append({"element": str(img), "src": src, "reason": "Malformed src URL scheme"})

    return {
        "total_links_evaluated": total_links,
        "broken_in_page_anchors": broken_anchors,
        "empty_or_placeholder_links": empty_links,
        "malformed_links": malformed_links,
        "insecure_http_links": insecure_http_links,
        "broken_images": broken_images,
        "is_healthy": len(broken_anchors) == 0 and len(malformed_links) == 0 and len(broken_images) == 0,
    }


def main():
    parser = argparse.ArgumentParser(description="Audit HTML files for dead anchors and malformed links")
    parser.add_argument("target", nargs="?", default="articles", help="File HTML atau direktori artikel")
    parser.add_argument("--strict", action="store_true", help="Keluar dengan exit code 1 jika ada isu link")
    args = parser.parse_args()

    target_path = Path(args.target)
    if not target_path.exists():
        print(f"Target tidak ditemukan: {target_path}")
        sys.exit(1)

    html_files = [target_path] if target_path.is_file() else list(target_path.glob("**/*.html"))

    if not html_files:
        print(f"Tidak ada berkas .html yang ditemukan di {target_path}")
        return

    has_issues = False
    print(f"Memeriksa {len(html_files)} berkas HTML...\n")

    for f in html_files:
        content = f.read_text(encoding="utf-8")
        report = check_html_links_and_anchors(content)

        if not report["is_healthy"] or report["empty_or_placeholder_links"] or report["insecure_http_links"]:
            has_issues = True
            print(f"❌ {f.name}:")
            if report["broken_in_page_anchors"]:
                print(f"   - Broken Anchors ({len(report['broken_in_page_anchors'])}):")
                for item in report["broken_in_page_anchors"]:
                    print(f"     * {item['anchor']} (teks: '{item['text']}')")
            if report["malformed_links"]:
                print(f"   - Malformed Links ({len(report['malformed_links'])}):")
                for link in report["malformed_links"]:
                    print(f"     * {link}")
            if report["broken_images"]:
                print(f"   - Image Issues ({len(report['broken_images'])}):")
                for img in report["broken_images"]:
                    print(f"     * {img['reason']}")
            if report["insecure_http_links"]:
                print(f"   - Insecure HTTP Links ({len(report['insecure_http_links'])}):")
                for link in report["insecure_http_links"]:
                    print(f"     * {link}")
            if report["empty_or_placeholder_links"]:
                print(f"   - Placeholder Links href='#' ({len(report['empty_or_placeholder_links'])})")
        else:
            print(f"✅ {f.name} ({report['total_links_evaluated']} links OK)")

    if has_issues and args.strict:
        sys.exit(1)


if __name__ == "__main__":
    main()
