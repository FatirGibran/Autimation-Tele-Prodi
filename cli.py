import argparse
import sys
import json
from pathlib import Path

from config import settings
from parser import parse_telegram_input, parse_llm_response
from seo_validator import YoastSEOValidator
from sanitizer import HTMLSanitizer
from storage import StorageManager

from exporter import ArticleExporter

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

def cmd_stats(args):
    stats = storage.get_statistics()
    print("=== Statistik Database Editorial ===")
    print(f"Total Artikel      : {stats['total_articles']}")
    print(f"Terpublikasi/WP    : {stats['published_count']}")
    print(f"Siap Terbit (Ready): {stats['ready_count']}")
    print(f"Perlu Review       : {stats['needs_review_count']}")

def cmd_search(args):
    results = storage.search_articles(args.query, limit=args.limit)
    if not results:
        print(f"Tidak ditemukan artikel dengan kata kunci '{args.query}'.")
        return

    print(f"Ditemukan {len(results)} artikel untuk query '{args.query}':")
    print(f"{'ID':<4} | {'TANGGAL':<12} | {'KEYPHRASE':<30} | {'SLUG'}")
    print("-" * 75)
    for a in results:
        print(f"{a['id']:<4} | {a['publish_date']:<12} | {a['focus_keyphrase'][:28]:<30} | {a['slug']}")

def cmd_export(args):
    article = storage.get_article_by_slug(args.slug)
    if not article:
        print(f"Error: Artikel dengan slug '{args.slug}' tidak ditemukan di database.")
        sys.exit(1)

    out_dir = Path(args.out)
    paths = ArticleExporter.export_bundle(
        output_dir=out_dir,
        slug=article["slug"],
        metadata=article,
        html_content=article.get("html_content", "")
    )
    print(f"Export selesai ke direktori: {out_dir}")
    for k, p in paths.items():
        print(f" - [{k}]: {p}")

def cmd_validate(args):
    html_path = Path(args.html)
    if not html_path.exists():
        print(f"Error: File '{args.html}' tidak ditemukan.")
        sys.exit(1)

    html_content = html_path.read_text(encoding="utf-8")
    _, sanitizer_warnings = HTMLSanitizer.sanitize(html_content)

    meta = {}
    if args.meta:
        meta_path = Path(args.meta)
        if not meta_path.exists():
            print(f"Error: File metadata '{args.meta}' tidak ditemukan.")
            sys.exit(1)
        with open(meta_path, encoding="utf-8") as f:
            data = json.load(f)
            meta = data.get("yoast_seo", data)

    seo_report = YoastSEOValidator.evaluate(meta, html_content) if meta else None
    is_valid = (seo_report["is_all_green"] if seo_report else True) and (len(sanitizer_warnings) == 0)

    if args.json_output:
        output_payload = {
            "valid": is_valid,
            "sanitizer_warnings": sanitizer_warnings,
            "seo_report": seo_report
        }
        print(json.dumps(output_payload, indent=2))
    else:
        status_str = "VALID (SIAP TERBIT)" if is_valid else "TIDAK VALID"
        print(f"Hasil Validasi: {status_str}")
        if sanitizer_warnings:
            print(f"Peringatan Sanitasi ({len(sanitizer_warnings)}):")
            for w in sanitizer_warnings:
                print(f" - {w}")
        if seo_report:
            print(f"Skor SEO: {seo_report['score']}/100")
            if seo_report["errors"]:
                print(f"Error SEO ({len(seo_report['errors'])}):")
                for e in seo_report["errors"]:
                    print(f" ! {e}")

    if not is_valid:
        sys.exit(1)


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

    # Stats command
    stats_parser = subparsers.add_parser("stats", help="Tampilkan statistik ringkas database editorial")
    stats_parser.set_defaults(func=cmd_stats)

    # Search command
    search_parser = subparsers.add_parser("search", help="Cari artikel berdasarkan kata kunci")
    search_parser.add_argument("--query", required=True, help="Kata kunci pencarian")
    search_parser.add_argument("--limit", type=int, default=20, help="Batas jumlah hasil")
    search_parser.set_defaults(func=cmd_search)

    # Export command
    export_parser = subparsers.add_parser("export", help="Export artikel ke format bundle (HTML, Standalone, MD, Elementor)")
    export_parser.add_argument("--slug", required=True, help="Slug artikel di database")
    export_parser.add_argument("--out", default="output", help="Direktori tujuan export")
    export_parser.set_defaults(func=cmd_export)

    # Validate command
    val_parser = subparsers.add_parser("validate", help="Validasi kepatuhan HTML dan SEO artikel secara komprehensif")
    val_parser.add_argument("--html", required=True, help="Path ke file HTML")
    val_parser.add_argument("--meta", help="Path opsional ke file JSON metadata")
    val_parser.add_argument("--json", dest="json_output", action="store_true", help="Format output sebagai JSON")
    val_parser.set_defaults(func=cmd_validate)

    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
