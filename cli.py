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


def cmd_analytics(args):
    data = storage.get_editorial_analytics(days=args.days)
    print(f"=== Analitik Editorial ({data['window_days']} Hari Terakhir) ===")
    print(f"Total Artikel Baru   : {data['total_articles']}")
    print(f"Artikel Terbit       : {data['published_count']}")
    print(f"Kategori Aktif       : {data['active_categories']}")
    print(f"Kecepatan Publikasi  : {data['publishing_velocity_per_day']} artikel/hari")
    print("Distribusi Status    :")
    for status, cnt in data.get("status_breakdown", {}).items():
        print(f" - {status}: {cnt}")


def cmd_prune(args):
    deleted = storage.prune_revisions(retention_days=args.retention_days, keep_minimum=args.keep_minimum)
    print("=== Pembersihan Revisi Database ===")
    print(f"Revisi usang dihapus : {deleted} revisi")


def cmd_hugo(args):
    article = storage.get_article_by_slug(args.slug)
    if not article:
        print(f"Error: Artikel dengan slug '{args.slug}' tidak ditemukan di database.")
        sys.exit(1)

    out_path = Path(args.out) if args.out else Path(f"{args.slug}.md")
    out_path.parent.mkdir(parents=True, exist_ok=True)
    hugo_md = ArticleExporter.to_hugo_markdown(
        metadata=article,
        html_content=article.get("html_content", ""),
        is_draft=article.get("status") == "draft"
    )
    out_path.write_text(hugo_md, encoding="utf-8")
    print(f"Export Hugo markdown berhasil -> {out_path}")


def cmd_schedule(args):
    if args.action == "list":
        schedules = storage.get_pending_schedules()
        if not schedules:
            print("Tidak ada jadwal publikasi pending.")
            return
        print(f"{'ID':<4} | {'ARTICLE_ID':<10} | {'SCHEDULED_AT':<25} | {'STATUS':<10} | {'SLUG'}")
        print("-" * 80)
        for s in schedules:
            print(f"{s['id']:<4} | {s['article_id']:<10} | {s['scheduled_at']:<25} | {s['status']:<10} | {s.get('slug', '')}")
    elif args.action == "add":
        if not args.id or not args.time:
            print("Error: Argumen --id dan --time wajib disertakan untuk tindakan add.")
            sys.exit(1)
        sched_id = storage.schedule_publication(args.id, args.time)
        print(f"Jadwal publikasi berhasil dibuat (Schedule ID {sched_id}) untuk Artikel ID {args.id} pada {args.time}.")
    elif args.action == "cancel":
        if not args.id:
            print("Error: Argumen --id wajib disertakan untuk tindakan cancel.")
            sys.exit(1)
        ok = storage.cancel_schedule(args.id)
        print(f"Jadwal publikasi artikel ID {args.id} {'berhasil dibatalkan' if ok else 'gagal/tidak ditemukan'}.")


def cmd_dump(args):
    out_path = Path(args.out)
    dump_data = storage.export_database_dump()
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(dump_data, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"Database dump berhasil diekspor ({len(dump_data.get('articles', []))} artikel) -> {out_path}")


def cmd_mdx(args):
    article = storage.get_article_by_slug(args.slug)
    if not article:
        print(f"Error: Artikel dengan slug '{args.slug}' tidak ditemukan di database.")
        sys.exit(1)

    framework = getattr(args, "framework", "astro")
    out_path = Path(args.out) if args.out else Path(f"{args.slug}.mdx")
    out_path.parent.mkdir(parents=True, exist_ok=True)
    mdx_content = ArticleExporter.to_mdx(
        metadata=article,
        html_content=article.get("html_content", ""),
        framework=framework
    )
    out_path.write_text(mdx_content, encoding="utf-8")
    print(f"Export MDX ({framework}) berhasil -> {out_path}")


def cmd_lock(args):
    if args.action == "acquire":
        if not args.id or not args.user:
            print("Error: Argumen --id dan --user wajib disertakan.")
            sys.exit(1)
        ok, blocker = storage.acquire_article_lock(args.id, args.user, ttl_seconds=args.ttl)
        if ok:
            print(f"Lock berhasil diperoleh untuk Artikel ID {args.id} oleh '{args.user}' (TTL: {args.ttl} detik).")
        else:
            print(f"Gagal memperoleh lock. Artikel ID {args.id} sedang dikunci oleh '{blocker}'.")
            sys.exit(1)
    elif args.action == "release":
        if not args.id or not args.user:
            print("Error: Argumen --id dan --user wajib disertakan.")
            sys.exit(1)
        ok = storage.release_article_lock(args.id, args.user)
        print(f"Lock artikel ID {args.id} {'berhasil dilepaskan' if ok else 'gagal dilepaskan (user tidak cocok/tidak ada lock)'}.")
    elif args.action == "status":
        if not args.id:
            print("Error: Argumen --id wajib disertakan.")
            sys.exit(1)
        st = storage.get_article_lock_status(args.id)
        if st:
            print(f"Artikel ID {args.id} terkunci oleh '{st['locked_by']}' hingga {st['expires_at']}.")
        else:
            print(f"Artikel ID {args.id} tidak memiliki lock aktif.")


def cmd_replace(args):
    res = storage.batch_replace_content(args.target, args.replace, status_filter=args.status)
    print(f"Batch replace selesai: {res['total_replacements']} penggantian pada {res['articles_updated']} artikel.")


def cmd_schema(args):
    schema_data = ArticleExporter.generate_program_json_ld()
    out_path = Path(args.out)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(schema_data, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"Schema EducationalOccupationalProgram berhasil dibuat -> {out_path}")


def cmd_bookmark(args):
    if args.action == "list":
        bms = storage.list_bookmarks(args.user)
        if not bms:
            print(f"Tidak ada bookmark untuk user '{args.user}'.")
            return
        print(f"=== Bookmark Artikel untuk User: {args.user} ===")
        for b in bms:
            print(f" - [ID {b['article_id']}] {b['seo_title']} (Notes: {b.get('notes') or '-'})")
    elif args.action == "add":
        if not args.id:
            print("Error: Argumen --id wajib untuk add bookmark.")
            sys.exit(1)
        bm_id = storage.add_bookmark(args.id, args.user, args.notes)
        print(f"Bookmark berhasil ditambahkan (ID {bm_id}) untuk artikel ID {args.id}.")
    elif args.action == "remove":
        if not args.id:
            print("Error: Argumen --id wajib untuk remove bookmark.")
            sys.exit(1)
        ok = storage.remove_bookmark(args.id, args.user)
        print(f"Bookmark artikel ID {args.id} {'berhasil dihapus' if ok else 'gagal/tidak ditemukan'}.")


def cmd_cat_stats(args):
    stats = storage.get_category_analytics()
    print("=== Analitik Artikel per Kategori ===")
    print(f"{'KATEGORI':<25} | {'TOTAL ARTIKEL':<15} | {'TOTAL VIEWS':<12} | {'RATA-RATA VIEWS'}")
    print("-" * 75)
    for s in stats:
        cat = s.get("category") or "Uncategorized"
        print(f"{cat:<25} | {s['total_articles']:<15} | {s['total_views']:<12} | {s['avg_views']:.1f}")


def cmd_nuxt(args):
    article = storage.get_article_by_slug(args.slug)
    if not article:
        print(f"Error: Artikel dengan slug '{args.slug}' tidak ditemukan di database.")
        sys.exit(1)
    out_path = Path(args.out) if args.out else Path(f"{args.slug}.md")
    out_path.parent.mkdir(parents=True, exist_ok=True)
    nuxt_md = ArticleExporter.to_nuxt_markdown(
        metadata=article,
        html_content=article.get("html_content", "")
    )
    out_path.write_text(nuxt_md, encoding="utf-8")
    print(f"Export Nuxt markdown berhasil -> {out_path}")


def cmd_subscribe(args):
    if args.action == "list":
        subs = storage.get_subscribers(args.category or "all")
        if not subs:
            print(f"Tidak ada subscriber untuk kategori '{args.category or 'all'}'.")
            return
        print(f"=== Daftar Subscriber (Kategori: {args.category or 'all'}) ===")
        for s in subs:
            print(f" - [{s['channel']}] User: {s['user_id']} (Kategori: {s['category']})")
    elif args.action == "add":
        if not args.user or not args.channel:
            print("Error: Argumen --user dan --channel wajib disertakan.")
            sys.exit(1)
        ok = storage.subscribe_user(args.user, args.channel, args.category or "all")
        print(f"Subscriber '{args.user}' ({args.channel}) {'berhasil didaftarkan' if ok else 'sudah terdaftar'}.")
    elif args.action == "remove":
        if not args.user:
            print("Error: Argumen --user wajib disertakan.")
            sys.exit(1)
        ok = storage.unsubscribe_user(args.user, args.category or "all")
        print(f"Subscriber '{args.user}' {'berhasil dihapus' if ok else 'tidak ditemukan'}.")


def cmd_diff_rev(args):
    diff = storage.compare_revisions(args.id, args.rev_a, args.rev_b)
    if not diff.get("found"):
        print(f"Error: {diff.get('error', 'Revisi tidak ditemukan')}.")
        sys.exit(1)
    print(f"=== Komparasi Revisi Artikel ID {args.id} (Rev {args.rev_a} vs Rev {args.rev_b}) ===")
    print(f" - Rev {args.rev_a}: {diff['rev_a']['word_count']} kata, {diff['rev_a']['char_count']} karakter")
    print(f" - Rev {args.rev_b}: {diff['rev_b']['word_count']} kata, {diff['rev_b']['char_count']} karakter")
    print(f" - Selisih Kata: {diff['deltas']['word_diff']:+d}")
    print(f" - Selisih Karakter: {diff['deltas']['char_diff']:+d}")
    print(f" - Meta Description Berubah: {'Ya' if diff['deltas']['meta_changed'] else 'Tidak'}")


def cmd_svelte(args):
    article = storage.get_article_by_slug(args.slug)
    if not article:
        print(f"Error: Artikel dengan slug '{args.slug}' tidak ditemukan di database.")
        sys.exit(1)
    out_path = Path(args.out) if args.out else Path(f"{args.slug}.svx")
    out_path.parent.mkdir(parents=True, exist_ok=True)
    svelte_md = ArticleExporter.to_sveltekit_markdown(
        metadata=article,
        html_content=article.get("html_content", "")
    )
    out_path.write_text(svelte_md, encoding="utf-8")
    print(f"Export SvelteKit markdown berhasil -> {out_path}")


def cmd_task(args):
    if args.action == "list":
        tasks = storage.list_editorial_tasks(status=args.status or "all")
        if not tasks:
            print(f"Tidak ada task dengan status '{args.status or 'all'}'.")
            return
        print(f"=== Daftar Tugas Editorial (Status: {args.status or 'all'}) ===")
        print(f"{'ID':<4} | {'ARTICLE ID':<10} | {'ASSIGNEE':<15} | {'TYPE':<15} | {'DUE DATE':<12} | {'STATUS'}")
        print("-" * 75)
        for t in tasks:
            print(f"{t['id']:<4} | {t['article_id']:<10} | {t['assignee']:<15} | {t['task_type']:<15} | {t['due_date']:<12} | {t['status']}")
    elif args.action == "add":
        if not args.id or not args.assignee or not args.type or not args.due:
            print("Error: Argumen --id, --assignee, --type, dan --due wajib disertakan.")
            sys.exit(1)
        task_id = storage.create_editorial_task(args.id, args.assignee, args.type, args.due)
        print(f"Tugas editorial #{task_id} berhasil ditugaskan ke {args.assignee}.")
    elif args.action == "update":
        if not args.task_id or not args.status:
            print("Error: Argumen --task-id dan --status wajib disertakan.")
            sys.exit(1)
        ok = storage.update_task_status(args.task_id, args.status)
        print(f"Status tugas #{args.task_id} {'berhasil diperbarui ke ' + args.status if ok else 'gagal diperbarui'}.")


def cmd_view_stats(args):
    views = storage.get_article_views_by_date(args.id, days=args.days or 7)
    if not views:
        print(f"Tidak ada log tayangan untuk artikel ID {args.id} dalam {args.days or 7} hari terakhir.")
        return
    print(f"=== Statistik Tayangan Artikel ID {args.id} ({args.days or 7} Hari Terakhir) ===")
    print(f"{'TANGGAL':<15} | {'TAYANGAN':<10}")
    print("-" * 30)
    for v in views:
        print(f"{v['date']:<15} | {v['views']:<10}")


def cmd_eleventy(args):
    article = storage.get_article_by_slug(args.slug)
    if not article:
        print(f"Error: Artikel dengan slug '{args.slug}' tidak ditemukan di database.")
        sys.exit(1)
    out_path = Path(args.out) if args.out else Path(f"{args.slug}.md")
    out_path.parent.mkdir(parents=True, exist_ok=True)
    eleventy_md = ArticleExporter.to_eleventy_markdown(
        metadata=article,
        html_content=article.get("html_content", "")
    )
    out_path.write_text(eleventy_md, encoding="utf-8")
    print(f"Export Eleventy markdown berhasil -> {out_path}")


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

    # Analytics command
    analytics_parser = subparsers.add_parser("analytics", help="Tampilkan analitik editorial dan kecepatan publikasi")
    analytics_parser.add_argument("--days", type=int, default=30, help="Jendela waktu analisis dalam hari")
    analytics_parser.set_defaults(func=cmd_analytics)

    # Prune command
    prune_parser = subparsers.add_parser("prune", help="Pangkas riwayat revisi artikel yang sudah kadaluarsa")
    prune_parser.add_argument("--retention-days", type=int, default=30, help="Masa retensi revisi dalam hari")
    prune_parser.add_argument("--keep-minimum", type=int, default=2, help="Jumlah minimum revisi yang dipertahankan")
    prune_parser.set_defaults(func=cmd_prune)

    # Hugo command
    hugo_parser = subparsers.add_parser("hugo", help="Export artikel ke format Markdown kompatibel Hugo static site generator")
    hugo_parser.add_argument("--slug", required=True, help="Slug artikel di database")
    hugo_parser.add_argument("--out", help="Path berkas output Markdown Hugo")
    hugo_parser.set_defaults(func=cmd_hugo)

    # Schedule command
    sched_parser = subparsers.add_parser("schedule", help="Kelola antrean publikasi terjadwal artikel")
    sched_parser.add_argument("--action", choices=["list", "add", "cancel"], default="list", help="Tindakan penjadwalan")
    sched_parser.add_argument("--id", type=int, help="ID artikel")
    sched_parser.add_argument("--time", help="Waktu publikasi ISO (YYYY-MM-DDTHH:MM:SS)")
    sched_parser.set_defaults(func=cmd_schedule)

    # Dump command
    dump_parser = subparsers.add_parser("dump", help="Export full database backup dump ke berkas JSON")
    dump_parser.add_argument("--out", default="db_dump.json", help="Path berkas output JSON dump")
    dump_parser.set_defaults(func=cmd_dump)

    # MDX command
    mdx_parser = subparsers.add_parser("mdx", help="Export artikel ke format MDX modern (Astro atau Docusaurus)")
    mdx_parser.add_argument("--slug", required=True, help="Slug artikel di database")
    mdx_parser.add_argument("--framework", choices=["astro", "docusaurus"], default="astro", help="Target framework komponen MDX")
    mdx_parser.add_argument("--out", help="Path berkas output MDX")
    mdx_parser.set_defaults(func=cmd_mdx)

    # Lock command
    lock_parser = subparsers.add_parser("lock", help="Kelola lease lock editing draf artikel")
    lock_parser.add_argument("--action", choices=["acquire", "release", "status"], default="status", help="Tindakan lock")
    lock_parser.add_argument("--id", type=int, help="ID artikel")
    lock_parser.add_argument("--user", help="Identitas pengguna/editor")
    lock_parser.add_argument("--ttl", type=int, default=300, help="Masa aktif lock dalam detik")
    lock_parser.set_defaults(func=cmd_lock)

    # Replace command
    replace_parser = subparsers.add_parser("replace", help="Pencarian dan penggantian massal konten artikel")
    replace_parser.add_argument("--target", required=True, help="Teks target yang dicari")
    replace_parser.add_argument("--replace", required=True, help="Teks pengganti")
    replace_parser.add_argument("--status", help="Filter status artikel (opsional)")
    replace_parser.set_defaults(func=cmd_replace)

    # Schema command
    schema_parser = subparsers.add_parser("schema", help="Generate berkas JSON-LD skema kurikulum program studi")
    schema_parser.add_argument("--out", default="program_schema.json", help="Path berkas output JSON-LD")
    schema_parser.set_defaults(func=cmd_schema)

    # Bookmark command
    bm_parser = subparsers.add_parser("bookmark", help="Kelola reading list dan bookmark artikel pengguna")
    bm_parser.add_argument("--action", choices=["list", "add", "remove"], default="list", help="Tindakan bookmark")
    bm_parser.add_argument("--user", required=True, help="Identitas user")
    bm_parser.add_argument("--id", type=int, help="ID artikel")
    bm_parser.add_argument("--notes", help="Catatan bookmark")
    bm_parser.set_defaults(func=cmd_bookmark)

    # Cat-stats command
    cat_parser = subparsers.add_parser("cat-stats", help="Tampilkan statistik agregat performa pembaca per kategori")
    cat_parser.set_defaults(func=cmd_cat_stats)

    # Nuxt command
    nuxt_parser = subparsers.add_parser("nuxt", help="Export artikel ke format Markdown kompatibel Nuxt Content v2")
    nuxt_parser.add_argument("--slug", required=True, help="Slug artikel di database")
    nuxt_parser.add_argument("--out", help="Path berkas output Markdown Nuxt")
    nuxt_parser.set_defaults(func=cmd_nuxt)

    # Subscribe command
    sub_parser = subparsers.add_parser("subscribe", help="Kelola langganan notifikasi editorial (list, add, remove)")
    sub_parser.add_argument("--action", choices=["list", "add", "remove"], default="list", help="Tindakan subscribe")
    sub_parser.add_argument("--user", help="ID pengguna/penerima")
    sub_parser.add_argument("--channel", default="telegram", help="Kanal notifikasi (telegram/email)")
    sub_parser.add_argument("--category", default="all", help="Kategori artikel")
    sub_parser.set_defaults(func=cmd_subscribe)

    # Diff-rev command
    diff_parser = subparsers.add_parser("diff-rev", help="Bandingkan dua versi revisi tersimpan artikel")
    diff_parser.add_argument("--id", type=int, required=True, help="ID artikel")
    diff_parser.add_argument("--rev-a", type=int, required=True, help="Nomor revisi awal (A)")
    diff_parser.add_argument("--rev-b", type=int, required=True, help="Nomor revisi pembanding (B)")
    diff_parser.set_defaults(func=cmd_diff_rev)

    # Svelte command
    svelte_parser = subparsers.add_parser("svelte", help="Export artikel ke format MDSveX / SvelteKit markdown")
    svelte_parser.add_argument("--slug", required=True, help="Slug artikel di database")
    svelte_parser.add_argument("--out", help="Path berkas output MDSveX")
    svelte_parser.set_defaults(func=cmd_svelte)

    # Task command
    task_parser = subparsers.add_parser("task", help="Kelola penugasan editorial artikel (list, add, update)")
    task_parser.add_argument("--action", choices=["list", "add", "update"], default="list", help="Tindakan task")
    task_parser.add_argument("--id", type=int, help="ID artikel")
    task_parser.add_argument("--task-id", type=int, help="ID tugas")
    task_parser.add_argument("--assignee", help="Nama penerima tugas")
    task_parser.add_argument("--type", help="Jenis tugas (review/proofreading/fact_check)")
    task_parser.add_argument("--due", help="Batas waktu tugas (YYYY-MM-DD)")
    task_parser.add_argument("--status", default="pending", help="Filter atau status baru")
    task_parser.set_defaults(func=cmd_task)

    # View-stats command
    view_parser = subparsers.add_parser("view-stats", help="Tampilkan time-series tayangan harian artikel")
    view_parser.add_argument("--id", type=int, required=True, help="ID artikel")
    view_parser.add_argument("--days", type=int, default=7, help="Rentang hari historis")
    view_parser.set_defaults(func=cmd_view_stats)

    # Eleventy command
    eleventy_parser = subparsers.add_parser("eleventy", help="Export artikel ke format Markdown kompatibel Eleventy SSG")
    eleventy_parser.add_argument("--slug", required=True, help="Slug artikel di database")
    eleventy_parser.add_argument("--out", help="Path berkas output Markdown Eleventy")
    eleventy_parser.set_defaults(func=cmd_eleventy)

    args = parser.parse_args()

    args.func(args)



if __name__ == "__main__":
    main()
