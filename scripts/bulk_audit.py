#!/usr/bin/env python3
import sys
import json
import argparse
from pathlib import Path
from typing import Dict, Any, List

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from seo_validator import YoastSEOValidator

def audit_directory(dir_path: Path) -> Dict[str, Any]:
    if not dir_path.exists():
        raise FileNotFoundError(f"Directory not found: {dir_path}")

    html_files = sorted(dir_path.glob("*.html"))
    results: List[Dict[str, Any]] = []

    for html_file in html_files:
        if html_file.name.endswith("_standalone.html"):
            continue

        base_name = html_file.stem
        # Look for matching metadata json: <name>-metadata.json or <name>.json
        meta_candidates = [
            dir_path / f"{base_name}-metadata.json",
            dir_path / f"{base_name}.json"
        ]
        meta_path = next((p for p in meta_candidates if p.exists()), None)
        if not meta_path:
            continue

        html_content = html_file.read_text(encoding="utf-8")
        try:
            with open(meta_path, encoding="utf-8") as f:
                meta_data = json.load(f)
                yoast_meta = meta_data.get("yoast_seo", meta_data)

            report = YoastSEOValidator.evaluate(yoast_meta, html_content)
            results.append({
                "file": html_file.name,
                "title": yoast_meta.get("seo_title", base_name),
                "score": report["score"],
                "is_all_green": report["is_all_green"],
                "error_count": len(report["errors"]),
                "errors": report["errors"]
            })
        except Exception as e:
            results.append({
                "file": html_file.name,
                "title": base_name,
                "score": 0,
                "is_all_green": False,
                "error_count": 1,
                "errors": [str(e)]
            })

    all_passed = all(r["is_all_green"] for r in results) if results else True
    return {
        "scanned_files": len(results),
        "all_passed": all_passed,
        "results": results
    }

def main():
    parser = argparse.ArgumentParser(description="Bulk SEO Audit Automation Utility")
    parser.add_argument("--dir", default=str(PROJECT_ROOT / "articles"), help="Directory containing articles")
    parser.add_argument("--json", action="store_true", help="Output summary in JSON format")

    args = parser.parse_args()
    summary = audit_directory(Path(args.dir))

    if args.json:
        print(json.dumps(summary, indent=2))
    else:
        print(f"Scanned {summary['scanned_files']} article pair(s):")
        print(f"{'STATUS':<6} | {'SCORE':<5} | {'FILE'}")
        print("-" * 65)
        for r in summary["results"]:
            icon = "PASS" if r["is_all_green"] else "FAIL"
            print(f"{icon:<6} | {r['score']:<5} | {r['file']}")

        if not summary["all_passed"]:
            print("\nErrors encountered:")
            for r in summary["results"]:
                if r["errors"]:
                    print(f"[{r['file']}]: {r['errors']}")

    sys.exit(0 if summary["all_passed"] else 1)

if __name__ == "__main__":
    main()
