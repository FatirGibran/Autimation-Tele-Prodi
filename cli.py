import argparse
import sys
import json
from pathlib import Path

from config import settings
from parser import parse_telegram_input, parse_llm_response
from seo_validator import YoastSEOValidator
from sanitizer import HTMLSanitizer
from storage import StorageManager

storage = StorageManager(settings.db_path)

def cmd_audit(args):
    html_path = Path(args.html)
    meta_path = Path(args.meta)

    if not html_path.exists() or not meta_path.exists():
        print("Error: File HTML atau Metadata tidak ditemukan.")
        sys.exit(1)

    html_content = html_path.read_text(encoding="utf-8")
    with open(meta_path, encoding="utf-8") as f:
        meta_data = json.load(f)
        yoast_meta = meta_data.get("yoast_seo", meta_data)

    report = YoastSEOValidator.evaluate(yoast_meta, html_content)
    print(f"Yoast SEO Status: {'ALL GREEN' if report['is_all_green'] else 'NEEDS ATTENTION'}")
    print(f"Score: {report['score']}/100")
    print("\nChecks:")
    for k, v in report["checks"].items():
        status = "PASSED" if v["passed"] else "FAILED"
        print(f" - [{status}] {k}: {v}")

    if report["errors"]:
        print("\nErrors:")
        for e in report["errors"]:
            print(f" ! {e}")

def cmd_list(args):
    articles = storage.list_articles(limit=args.limit)
    if not articles:
        print("Tidak ada riwayat artikel tersimpan di database.")
        return

    print(f"{'ID':<4} | {'TANGGAL':<12} | {'KEYPHRASE':<30} | {'STATUS':<10} | {'SLUG'}")
    print("-" * 80)
    for a in articles:
        print(f"{a['id']:<4} | {a['publish_date']:<12} | {a['focus_keyphrase'][:28]:<30} | {a['status']:<10} | {a['slug']}")

def main():
    parser = argparse.ArgumentParser(description="CLI Otomasi Editorial Prodi")
    subparsers = parser.add_subparsers(dest="command", required=True)

    # Audit command
    audit_parser = subparsers.add_parser("audit", help="Audit file HTML dan Metadata Yoast SEO")
    audit_parser.add_argument("--html", required=True, help="Path ke file .html")
    audit_parser.add_argument("--meta", required=True, help="Path ke file .json metadata")
    audit_parser.set_defaults(func=cmd_audit)

    # List command
    list_parser = subparsers.add_parser("list", help="Tampilkan daftar artikel di database")
    list_parser.add_argument("--limit", type=int, default=20, help="Jumlah maksimal data")
    list_parser.set_defaults(func=cmd_list)

    args = parser.parse_args()
    args.func(args)

if __name__ == "__main__":
    main()
