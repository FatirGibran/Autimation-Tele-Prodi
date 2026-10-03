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

def cmd_optimize(args):
    result = storage.optimize_and_check_integrity()
    print("=== Optimasi & Pemeliharaan Database ===")
    print(f"Status Integritas SQLite : {result['integrity_check']}")
    print(f"Status Pemadatan (VACUUM): {'Berhasil' if result['vacuumed'] else 'Gagal'}")

def cmd_sitemap(args):
    articles = storage.list_articles(limit=1000)
    out_path = Path(args.out)
    sitemap_xml = ArticleExporter.generate_sitemap_xml(articles, base_url=args.base_url)
    out_path.write_text(sitemap_xml, encoding="utf-8")
    print(f"Sitemap XML berhasil dibuat untuk {len(articles)} artikel -> {out_path}")

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


def cmd_trash(args):
    if args.action == "list":
        trashed = storage.list_trash(limit=args.limit)
        if not trashed:
            print("Kotak sampah kosong.")
            return
        print(f"{'ID':<4} | {'TANGGAL':<12} | {'KEYPHRASE':<30} | {'SLUG'}")
        print("-" * 75)
        for a in trashed:
            print(f"{a['id']:<4} | {a['publish_date']:<12} | {a['focus_keyphrase'][:28]:<30} | {a['slug']}")
    elif args.action == "delete":
        if not args.id:
            print("Error: Argumen --id wajib disertakan untuk tindakan delete.")
            sys.exit(1)
        ok = storage.soft_delete_article(args.id)
        print(f"Artikel ID {args.id} {'berhasil dipindahkan ke sampah' if ok else 'gagal/tidak ditemukan'}.")
    elif args.action == "restore":
        if not args.id:
            print("Error: Argumen --id wajib disertakan untuk tindakan restore.")
            sys.exit(1)
        ok = storage.restore_article(args.id)
        print(f"Artikel ID {args.id} {'berhasil dipulihkan dari sampah' if ok else 'gagal/tidak ditemukan'}.")


def cmd_density(args):
    html_path = Path(args.html)
    if not html_path.exists():
        print(f"Error: File HTML '{args.html}' tidak ditemukan.")
        sys.exit(1)
    html_content = html_path.read_text(encoding="utf-8")
    body_text = YoastSEOValidator.extract_text(html_content)
    result = YoastSEOValidator.evaluate_keyword_density(args.keyphrase, body_text)
    print("=== Analisis Kerapatan Kata Kunci (Yoast SEO) ===")
    print(f"Focus Keyphrase   : {args.keyphrase}")
    print(f"Kemunculan (Count): {result['count']}")
    print(f"Persentase        : {result['density_percentage']}%")
    print(f"Status Evaluasi   : {result['status'].upper()}")
    print(f"Saran Editorial   : {result['advice']}")


def cmd_feed(args):
    articles = storage.list_articles(limit=args.limit)
    out_path = Path(args.out)
    info = {
        "title": args.title,
        "base_url": args.base_url,
        "feed_url": f"{args.base_url}/{out_path.name}"
    }
    if args.format == "atom":
        content = ArticleExporter.generate_atom_feed(articles, info)
    else:
        content = ArticleExporter.generate_json_feed(articles, info)
    out_path.write_text(content, encoding="utf-8")
    print(f"Feed syndication format {args.format.upper()} berhasil diekspor ({len(articles)} artikel) -> {out_path}")


def cmd_meta(args):
    if args.action == "get":
        val = storage.get_article_meta(args.id, args.key)
        if args.key:
            print(f"Artikel ID {args.id} [{args.key}]: {val}")
        else:
            print(f"=== Metadata Artikel ID {args.id} ===")
            for k, v in (val or {}).items():
                print(f" - {k}: {v}")
    elif args.action == "set":
        if not args.key or args.value is None:
            print("Error: Argumen --key dan --value wajib disertakan.")
            sys.exit(1)
        storage.set_article_meta(args.id, args.key, args.value)
        print(f"Metadata berhasil disimpan: [{args.key}] = {args.value}")
    elif args.action == "delete":
        if not args.key:
            print("Error: Argumen --key wajib disertakan.")
            sys.exit(1)
        ok = storage.delete_article_meta(args.id, args.key)
        print(f"Metadata [{args.key}] {'berhasil dihapus' if ok else 'tidak ditemukan'}.")


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

    # Optimize command
    opt_parser = subparsers.add_parser("optimize", help="Jalankan pemeriksaan integritas dan kompresi VACUUM database SQLite")
    opt_parser.set_defaults(func=cmd_optimize)

    # Sitemap command
    sm_parser = subparsers.add_parser("sitemap", help="Generate berkas sitemap.xml dari seluruh artikel di database")
    sm_parser.add_argument("--out", default="sitemap.xml", help="Path berkas output XML sitemap")
    sm_parser.add_argument("--base-url", default="https://bif-pwt.telkomuniversity.ac.id", help="Base URL website prodi")
    sm_parser.set_defaults(func=cmd_sitemap)

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

    # Trash command
    trash_parser = subparsers.add_parser("trash", help="Kelola kotak sampah artikel (list, delete, restore)")
    trash_parser.add_argument("--action", choices=["list", "delete", "restore"], default="list", help="Tindakan kotak sampah")
    trash_parser.add_argument("--id", type=int, help="ID artikel")
    trash_parser.add_argument("--limit", type=int, default=20, help="Batas artikel yang ditampilkan")
    trash_parser.set_defaults(func=cmd_trash)

    # Density command
    density_parser = subparsers.add_parser("density", help="Analisis kerapatan fokus kata kunci konten HTML")
    density_parser.add_argument("--html", required=True, help="Path ke file HTML")
    density_parser.add_argument("--keyphrase", required=True, help="Fokus kata kunci")
    density_parser.set_defaults(func=cmd_density)

    # Feed command
    feed_parser = subparsers.add_parser("feed", help="Generate syndication feed (Atom atau JSON Feed v1.1)")
    feed_parser.add_argument("--format", choices=["atom", "json"], default="atom", help="Format feed")
    feed_parser.add_argument("--out", default="feed.xml", help="Path berkas output feed")
    feed_parser.add_argument("--title", default="S1 Teknik Informatika Telkom University Purwokerto", help="Judul kanal feed")
    feed_parser.add_argument("--base-url", default="https://bif-pwt.telkomuniversity.ac.id", help="Base URL website prodi")
    feed_parser.add_argument("--limit", type=int, default=50, help="Jumlah artikel maksimal")
    feed_parser.set_defaults(func=cmd_feed)

    # Meta command
    meta_parser = subparsers.add_parser("meta", help="Kelola custom metadata pasangan key-value artikel")
    meta_parser.add_argument("--id", type=int, required=True, help="ID artikel")
    meta_parser.add_argument("--action", choices=["get", "set", "delete"], default="get", help="Tindakan metadata")
    meta_parser.add_argument("--key", help="Kunci metadata")
    meta_parser.add_argument("--value", help="Nilai metadata")
    meta_parser.set_defaults(func=cmd_meta)

    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
