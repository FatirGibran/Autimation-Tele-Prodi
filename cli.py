import argparse
import sys
import json
from pathlib import Path

from config import settings
from parser import (
    parse_telegram_input,
    parse_llm_response,
    calculate_radar_range_equation,
    parse_wirausaha_merdeka_evaluation,
    calculate_edfa_amplifier_gain,
    calculate_otdr_fiber_events,
    calculate_mimo_channel_capacity,
    parse_iisma_evaluation,
    calculate_fspl_and_link_budget,
    calculate_optical_chromatic_dispersion,
    parse_proyek_kemanusiaan_evaluation,
    calculate_polarization_mode_dispersion,
    calculate_cost231_hata_path_loss,
    parse_studi_independen_evaluation,
    calculate_optical_four_wave_mixing,
    calculate_erlang_traffic_capacity,
    parse_pkm_mbkm_evaluation,
    calculate_optical_cross_phase_modulation,
    calculate_5g_nr_numerology_timing,
    parse_pmm_mbkm_evaluation,
    calculate_optical_srs_threshold,
    calculate_5g_nr_eirp_psd,
    parse_praktisi_mengajar_evaluation
)
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


def cmd_note(args):
    if args.action == "add":
        if not args.id or not args.author or not args.text:
            print("Error: --id, --author, dan --text wajib disertakan untuk menambahkan catatan.")
            sys.exit(1)
        note_id = storage.add_editorial_note(args.id, args.author, args.text)
        print(f"Catatan editorial berhasil ditambahkan [ID: {note_id}] ke artikel #{args.id}")
    elif args.action == "delete":
        if not args.note_id:
            print("Error: --note-id wajib disertakan untuk menghapus catatan.")
            sys.exit(1)
        deleted = storage.delete_editorial_note(args.note_id)
        if deleted:
            print(f"Catatan editorial #{args.note_id} berhasil dihapus.")
        else:
            print(f"Catatan editorial #{args.note_id} tidak ditemukan.")
    else:
        if not args.id:
            print("Error: --id artikel wajib disertakan untuk melihat catatan.")
            sys.exit(1)
        notes = storage.list_editorial_notes(args.id)
        if not notes:
            print(f"Tidak ada catatan editorial untuk artikel #{args.id}.")
            return
        print(f"=== Catatan Editorial Artikel #{args.id} ===")
        for n in notes:
            print(f"[{n['id']}] {n['author']} ({n['created_at']}): {n['note_text']}")


def cmd_zola(args):
    article = storage.get_article_by_slug(args.slug)
    if not article:
        print(f"Error: Artikel dengan slug '{args.slug}' tidak ditemukan di database.")
        sys.exit(1)
    out_path = Path(args.out) if args.out else Path(f"{args.slug}.md")
    out_path.parent.mkdir(parents=True, exist_ok=True)
    tags = storage.get_article_tags(article["id"])
    meta = {
        "seo_title": article.get("seo_title", ""),
        "meta_description": article.get("meta_description", ""),
        "slug": article.get("slug", ""),
        "publish_date": article.get("publish_date", ""),
        "category": article.get("category", ""),
        "tags": tags
    }
    zola_md = ArticleExporter.to_zola_markdown(meta, article.get("html_content", ""))
    out_path.write_text(zola_md, encoding="utf-8")
    print(f"Export Zola markdown berhasil -> {out_path}")


def cmd_webhook_logs(args):
    logs = storage.get_recent_webhook_logs(limit=args.limit)
    if not logs:
        print("Belum ada riwayat pengiriman webhook di database.")
        return
    print(f"{'ID':<4} | {'STATUS':<6} | {'EVENT':<20} | {'TARGET':<35} | {'WAKTU'}")
    print("-" * 85)
    for l in logs:
        print(f"{l['id']:<4} | {l['status_code']:<6} | {l['event']:<20} | {l['target_url'][:33]:<35} | {l['created_at']}")


def cmd_reviewer(args):
    if args.action == "assign":
        if not args.id or not args.name or not args.email:
            print("Error: --id, --name, dan --email wajib disertakan untuk penugasan reviewer.")
            sys.exit(1)
        rev_id = storage.assign_article_reviewer(args.id, args.name, args.email)
        print(f"Reviewer '{args.name}' berhasil ditugaskan [ID Review: {rev_id}] ke artikel #{args.id}.")
    elif args.action == "status":
        if not args.review_id or not args.status:
            print("Error: --review-id dan --status wajib disertakan untuk update status review.")
            sys.exit(1)
        ok = storage.update_reviewer_status(args.review_id, args.status)
        if ok:
            print(f"Status review #{args.review_id} berhasil diubah menjadi '{args.status}'.")
        else:
            print(f"Penugasan review #{args.review_id} tidak ditemukan.")
    else:
        if not args.id:
            print("Error: --id artikel wajib disertakan untuk melihat daftar reviewer.")
            sys.exit(1)
        reviewers = storage.list_article_reviewers(args.id)
        if not reviewers:
            print(f"Belum ada reviewer yang ditugaskan ke artikel #{args.id}.")
            return
        print(f"=== Daftar Reviewer Artikel #{args.id} ===")
        for r in reviewers:
            print(f"[{r['id']}] {r['reviewer_name']} <{r['reviewer_email']}> | Status: {r['status']}")


def cmd_pelican(args):
    article = storage.get_article_by_slug(args.slug)
    if not article:
        print(f"Error: Artikel dengan slug '{args.slug}' tidak ditemukan di database.")
        sys.exit(1)
    out_path = Path(args.out) if args.out else Path(f"{args.slug}.md")
    out_path.parent.mkdir(parents=True, exist_ok=True)
    tags = storage.get_article_tags(article["id"])
    meta = {
        "seo_title": article.get("seo_title", ""),
        "meta_description": article.get("meta_description", ""),
        "slug": article.get("slug", ""),
        "publish_date": article.get("publish_date", ""),
        "category": article.get("category", ""),
        "tags": tags
    }
    pelican_md = ArticleExporter.to_pelican_markdown(meta, article.get("html_content", ""))
    out_path.write_text(pelican_md, encoding="utf-8")
    print(f"Export Pelican markdown berhasil -> {out_path}")


def cmd_checklist(args):
    if not args.id:
        print("Error: --id artikel wajib disertakan untuk manajemen checklist.")
        sys.exit(1)
    if args.action == "set":
        if not args.key or not args.label:
            print("Error: --key dan --label wajib disertakan untuk verifikasi checklist.")
            sys.exit(1)
        storage.set_checklist_item(args.id, args.key, args.label, bool(args.checked), args.by or "")
        state_str = "SELESAI (V)" if args.checked else "BELUM (X)"
        print(f"Checklist '{args.key}' untuk artikel #{args.id} diatur ke [{state_str}].")
    else:
        items = storage.get_checklist_status(args.id)
        if not items:
            print(f"Belum ada checklist editorial untuk artikel #{args.id}.")
            return
        print(f"=== Status Checklist Editorial Artikel #{args.id} ===")
        for item in items:
            mark = "[V]" if item["is_checked"] else "[ ]"
            verifier = f" (oleh: {item['checked_by']})" if item["checked_by"] else ""
            print(f"{mark} {item['item_key']}: {item['item_label']}{verifier}")


def cmd_snippet(args):
    if args.action == "save":
        if not args.key or not args.title or not args.html:
            print("Error: --key, --title, dan --html wajib disertakan untuk menyimpan snippet.")
            sys.exit(1)
        sid = storage.save_content_snippet(args.key, args.title, args.html, args.category or "general")
        print(f"Snippet '{args.key}' berhasil disimpan (ID: {sid}).")
    elif args.action == "get":
        if not args.key:
            print("Error: --key wajib disertakan untuk mengambil snippet.")
            sys.exit(1)
        s = storage.get_content_snippet(args.key)
        if not s:
            print(f"Snippet dengan key '{args.key}' tidak ditemukan.")
            sys.exit(1)
        print(f"=== Snippet: {s['snippet_title']} ({s['snippet_key']}) ===")
        print(f"Kategori : {s['category']}")
        print(f"Konten   : {s['snippet_html']}")
    else:
        snippets = storage.list_content_snippets(category=args.category)
        if not snippets:
            print("Belum ada snippet konten tersimpan.")
            return
        print(f"{'KEY':<25} | {'KATEGORI':<15} | {'JUDUL'}")
        print("-" * 65)
        for s in snippets:
            print(f"{s['snippet_key']:<25} | {s['category']:<15} | {s['snippet_title']}")


def cmd_docusaurus(args):
    article = storage.get_article_by_slug(args.slug)
    if not article:
        print(f"Error: Artikel dengan slug '{args.slug}' tidak ditemukan di database.")
        sys.exit(1)
    out_path = Path(args.out) if args.out else Path(f"{args.slug}.md")
    out_path.parent.mkdir(parents=True, exist_ok=True)
    tags = storage.get_article_tags(article["id"])
    meta = {
        "seo_title": article.get("seo_title", ""),
        "topic": article.get("topic", ""),
        "meta_description": article.get("meta_description", ""),
        "slug": article.get("slug", ""),
        "sidebar_label": args.label or article.get("topic", ""),
        "sidebar_position": args.position or 1,
        "tags": tags
    }
    doc_md = ArticleExporter.to_docusaurus_markdown(meta, article.get("html_content", ""))
    out_path.write_text(doc_md, encoding="utf-8")
    print(f"Export Docusaurus markdown berhasil -> {out_path}")


def cmd_comment(args):
    if args.action == "add":
        if not args.id or not args.author or not args.text:
            print("Error: --id, --author, dan --text wajib disertakan untuk menambahkan komentar.")
            sys.exit(1)
        cid = storage.add_editorial_comment(args.id, args.author, args.text, args.paragraph)
        print(f"Komentar editorial berhasil ditambahkan (ID: {cid}) untuk artikel #{args.id}.")
    elif args.action == "resolve":
        if not args.comment_id:
            print("Error: --comment-id wajib disertakan untuk menyelesaikan komentar.")
            sys.exit(1)
        ok = storage.resolve_editorial_comment(args.comment_id)
        if ok:
            print(f"Komentar #{args.comment_id} berhasil diselesaikan.")
        else:
            print(f"Komentar #{args.comment_id} tidak ditemukan.")
            sys.exit(1)
    else:
        if not args.id:
            print("Error: --id artikel wajib disertakan untuk melihat komentar.")
            sys.exit(1)
        comments = storage.list_editorial_comments(args.id, include_resolved=not args.unresolved_only)
        if not comments:
            print(f"Belum ada komentar editorial untuk artikel #{args.id}.")
            return
        print(f"=== Komentar Editorial Artikel #{args.id} ===")
        for c in comments:
            res_mark = "[V]" if c["is_resolved"] else "[ ]"
            p_idx = f" (Paragraf {c['paragraph_index']})" if c["paragraph_index"] is not None else ""
            print(f"{res_mark} #{c['id']} oleh {c['author']}{p_idx}: {c['comment_text']}")


def cmd_achievement(args):
    if args.action == "add":
        if not args.name or not args.rank or not args.team or not args.year:
            print("Error: --name, --rank, --team, dan --year wajib disertakan untuk mencatat prestasi.")
            sys.exit(1)
        members = [m.strip() for m in args.members.split(",") if m.strip()] if args.members else []
        aid = storage.record_competition_achievement(
            competition_name=args.name,
            award_rank=args.rank,
            team_name=args.team,
            team_members=members,
            supervisor=args.supervisor or "",
            year=args.year,
            organizer=args.organizer or ""
        )
        print(f"Prestasi kompetisi berhasil dicatat (ID: {aid}) untuk tim '{args.team}'.")
    else:
        achievements = storage.list_competition_achievements(year=args.year)
        if not achievements:
            print("Belum ada catatan prestasi kompetisi mahasiswa.")
            return
        print("=== Rekam Jejak Prestasi Kompetisi Mahasiswa ===")
        for a in achievements:
            members_str = ", ".join(a["team_members"]) if a["team_members"] else "-"
            print(f"#{a['id']} [{a['year']}] {a['award_rank']} - {a['competition_name']} | Tim: {a['team_name']} ({members_str})")


def cmd_mkdocs(args):
    article = storage.get_article_by_slug(args.slug)
    if not article:
        print(f"Error: Artikel dengan slug '{args.slug}' tidak ditemukan di database.")
        sys.exit(1)

    out_path = Path(args.out) if args.out else Path(f"{args.slug}.md")
    tags = article.get("tags") or []
    if isinstance(tags, str):
        try:
            tags = json.loads(tags)
        except Exception:
            tags = [t.strip() for t in tags.split(",") if t.strip()]

    meta = {
        "seo_title": article.get("seo_title", ""),
        "topic": article.get("topic", ""),
        "meta_description": article.get("meta_description", ""),
        "slug": article.get("slug", ""),
        "tags": tags
    }
    mk_md = ArticleExporter.to_mkdocs_markdown(meta, article.get("html_content", ""))
    out_path.write_text(mk_md, encoding="utf-8")
    print(f"Export MkDocs markdown berhasil -> {out_path}")


def cmd_safety_log(args):
    if args.action == "add":
        if not args.lab or not args.inspector or args.score is None:
            print("Error: --lab, --inspector, dan --score wajib disertakan untuk inspeksi K3 lab.")
            sys.exit(1)
        import datetime
        date_str = args.date or datetime.date.today().isoformat()
        sid = storage.record_safety_inspection(
            lab_name=args.lab,
            inspector=args.inspector,
            inspection_date=date_str,
            compliance_score=float(args.score),
            is_passed=args.passed,
            notes=args.notes or ""
        )
        print(f"Log inspeksi K3 lab berhasil dicatat (ID: {sid}) untuk '{args.lab}'.")
    else:
        inspections = storage.list_safety_inspections(lab_name=args.lab)
        if not inspections:
            print("Belum ada catatan inspeksi K3 laboratorium.")
            return
        print("=== Log Inspeksi Keselamatan Kerja & K3 Lab ===")
        for s in inspections:
            status_str = "LULUS" if s["is_passed"] else "PERBAIKAN"
            print(f"#{s['id']} [{s['inspection_date']}] {s['lab_name']} - Skor: {s['compliance_score']}% [{status_str}] - Insp: {s['inspector']}")


def cmd_mbkm(args):
    if args.action == "add":
        if not args.name or not args.nim or not args.program or not args.partner:
            print("Error: --name, --nim, --program, dan --partner wajib disertakan untuk mencatat konversi MBKM.")
            sys.exit(1)
        sem = int(args.semester) if args.semester else 6
        sks = int(args.sks) if args.sks else 20
        gpa = float(args.gpa) if args.gpa else 3.75
        mid = storage.record_mbkm_credit_transfer(
            program_name=args.program,
            partner_institution=args.partner,
            student_name=args.name,
            nim=args.nim,
            semester=sem,
            total_sks=sks,
            converted_gpa=gpa,
            courses=[],
            sk_number=args.sk or ""
        )
        print(f"Konversi kredit MBKM berhasil dicatat (ID: {mid}) untuk {args.name} ({args.nim}).")
    else:
        transfers = storage.list_mbkm_credit_transfers(nim=args.nim)
        if not transfers:
            print("Belum ada catatan konversi kredit MBKM.")
            return
        print("=== Rekam Jejak Konversi Kredit MBKM ===")
        for t in transfers:
            print(f"#{t['id']} [{t['program_name']} - {t['partner_institution']}] {t['student_name']} ({t['nim']}) - {t['total_sks']} SKS | IPK: {t['converted_gpa']:.2f}")


def cmd_yudisium(args):
    if args.action == "add":
        if not args.name or not args.nim or not args.thesis or args.ipk is None or args.sks is None or not args.predicate:
            print("Error: --name, --nim, --thesis, --ipk, --sks, dan --predicate wajib disertakan untuk mencatat yudisium.")
            sys.exit(1)
        import datetime
        date_str = args.date or datetime.date.today().isoformat()
        code_str = args.code or f"YUD-{args.nim}"
        yid = storage.record_yudisium_clearance(
            student_name=args.name,
            nim=args.nim,
            thesis_title=args.thesis,
            ipk=float(args.ipk),
            earned_sks=int(args.sks),
            graduation_predicate=args.predicate,
            yudisium_date=date_str,
            verification_code=code_str,
            is_cleared=True
        )
        print(f"Kelulusan yudisium berhasil dicatat (ID: {yid}) untuk {args.name} ({args.nim}).")
    elif args.action == "check":
        if not args.nim:
            print("Error: --nim wajib disertakan untuk memeriksa status yudisium.")
            sys.exit(1)
        rec = storage.get_yudisium_clearance_by_nim(args.nim)
        if not rec:
            print(f"Data kelulusan yudisium untuk NIM '{args.nim}' tidak ditemukan.")
            return
        status_label = "LULUS / CLEARED" if rec.get("is_cleared") else "PENDING"
        print(f"Status Yudisium {rec['student_name']} ({rec['nim']}): {status_label} | IPK: {rec['ipk']} | Predikat: {rec['graduation_predicate']} | Kode: {rec['verification_code']}")
    else:
        clearances = storage.list_yudisium_clearances(predicate=args.predicate)
        if not clearances:
            print("Belum ada catatan kelulusan yudisium mahasiswa.")
            return
        print("=== Rekam Jejak Kelulusan Yudisium Mahasiswa ===")
        for y in clearances:
            print(f"#{y['id']} [{y['yudisium_date']}] {y['student_name']} ({y['nim']}) - IPK: {y['ipk']} ({y['graduation_predicate']}) - Verifikasi: {y['verification_code']}")


def cmd_starlight(args):
    article = storage.get_article_by_slug(args.slug)
    if not article:
        print(f"Error: Artikel dengan slug '{args.slug}' tidak ditemukan di database.")
        sys.exit(1)

    out_path = Path(args.out) if args.out else Path(f"{args.slug}.md")
    meta = {
        "seo_title": article.get("seo_title", ""),
        "topic": article.get("topic", ""),
        "meta_description": article.get("meta_description", ""),
        "sidebar_label": args.label or article.get("topic") or article.get("seo_title", ""),
        "sidebar_order": args.order
    }
    sl_md = ArticleExporter.to_starlight_markdown(meta, article.get("html_content", ""))
    out_path.write_text(sl_md, encoding="utf-8")
    print(f"Export Astro Starlight markdown berhasil -> {out_path}")


def cmd_kkn(args):
    if args.action == "add":
        if not args.group or not args.village or not args.district or not args.regency or not args.supervisor or args.students is None or not args.theme or not args.flagship:
            print("Error: --group, --village, --district, --regency, --supervisor, --students, --theme, dan --flagship wajib disertakan untuk mencatat penempatan KKN.")
            sys.exit(1)
        kid = storage.record_kkn_project(
            group_code=args.group,
            village_name=args.village,
            district_name=args.district,
            regency_name=args.regency,
            supervisor_dpl=args.supervisor,
            student_count=int(args.students),
            thematic_focus=args.theme,
            flagship_program=args.flagship
        )
        print(f"Penempatan KKN tematik berhasil dicatat (ID: {kid}) untuk kelompok {args.group} di Desa {args.village}.")
    else:
        projects = storage.list_kkn_projects(regency_name=args.regency)
        if not projects:
            print("Belum ada catatan penempatan KKN tematik mahasiswa.")
            return
        print("=== Rekam Jejak Program KKN Tematik Mahasiswa ===")
        for p in projects:
            print(f"#{p['id']} [{p['group_code']}] Desa {p['village_name']}, {p['regency_name']} - DPL: {p['supervisor_dpl']} ({p['student_count']} Mhs) | Fokus: {p['thematic_focus']}")


def cmd_bkd(args):
    if args.action == "add":
        if not args.name or not args.nidn or not args.rank or not args.semester or args.teaching is None or args.research is None or args.service is None or args.supporting is None or args.total is None:
            print("Error: Parameter beban BKD dosen tidak lengkap.")
            sys.exit(1)
        bid = storage.record_faculty_bkd(
            lecturer_name=args.name,
            nidn=args.nidn,
            academic_rank=args.rank,
            semester=args.semester,
            teaching_credits=float(args.teaching),
            research_credits=float(args.research),
            service_credits=float(args.service),
            supporting_credits=float(args.supporting),
            total_sks=float(args.total),
            is_compliant=bool(args.compliant)
        )
        status_label = "MEMENUHI" if args.compliant else "BELUM MEMENUHI"
        print(f"Beban kerja dosen (BKD) berhasil dicatat (ID: {bid}) untuk {args.name} ({args.nidn}) [{status_label}].")
    else:
        records = storage.list_faculty_bkd_records(semester=args.semester)
        if not records:
            print("Belum ada catatan kepatuhan BKD dosen.")
            return
        print("=== Rekam Jejak Kepatuhan Beban Kerja Dosen (BKD) ===")
        for r in records:
            status_mark = "MEMENUHI" if r["is_compliant"] else "TIDAK MEMENUHI"
            print(f"#{r['id']} [{r['semester']}] {r['lecturer_name']} ({r['nidn']}) - {r['total_sks']} SKS [{status_mark}]")


def cmd_hexo(args):
    article = storage.get_article_by_slug(args.slug)
    if not article:
        print(f"Error: Artikel dengan slug '{args.slug}' tidak ditemukan di database.")
        sys.exit(1)

    out_path = Path(args.out) if args.out else Path(f"{args.slug}.md")
    tags = article.get("tags") or []
    if isinstance(tags, str):
        try:
            tags = json.loads(tags)
        except Exception:
            tags = [t.strip() for t in tags.split(",") if t.strip()]

    meta = {
        "seo_title": article.get("seo_title", ""),
        "topic": article.get("topic", ""),
        "publish_date": article.get("publish_date", ""),
        "category": article.get("category", ""),
        "tags": tags
    }
    hexo_md = ArticleExporter.to_hexo_markdown(meta, article.get("html_content", ""))
    out_path.write_text(hexo_md, encoding="utf-8")
    print(f"Export Hexo markdown berhasil -> {out_path}")


def cmd_bima(args):
    if args.action == "add":
        if not args.title or not args.name or not args.nidn or not args.scheme or args.requested is None or args.year is None:
            print("Error: --title, --name, --nidn, --scheme, --requested, dan --year wajib disertakan untuk mencatat usulan hibah BIMA.")
            sys.exit(1)
        gid = storage.record_bima_grant(
            project_title=args.title,
            lead_researcher=args.name,
            lead_nidn=args.nidn,
            scheme_name=args.scheme,
            requested_budget=float(args.requested),
            approved_budget=float(args.approved or 0.0),
            fiscal_year=int(args.year),
            proposal_status=args.status,
            contract_number=args.contract
        )
        print(f"Usulan hibah BIMA berhasil dicatat (ID: {gid}) untuk '{args.title}' [{args.name}].")
    else:
        grants = storage.list_bima_grants(fiscal_year=args.year, status=args.status if args.status != "submitted" else None)
        if not grants:
            print("Belum ada catatan usulan hibah BIMA Kemdikbud.")
            return
        print("=== Rekam Jejak Usulan Hibah Penelitian BIMA Kemdikbud ===")
        for g in grants:
            print(f"#{g['id']} [{g['fiscal_year']}] {g['project_title']} - {g['lead_researcher']} ({g['lead_nidn']}) | Skema: {g['scheme_name']} [{g['proposal_status']}]")


def cmd_kp(args):
    if args.action == "add":
        if not args.name or not args.nim or not args.company or not args.sector or args.weeks is None or not args.project:
            print("Error: --name, --nim, --company, --sector, --weeks, dan --project wajib disertakan untuk mencatat penempatan kerja praktik.")
            sys.exit(1)
        kpid = storage.record_kp_placement(
            student_name=args.name,
            nim=args.nim,
            company_name=args.company,
            industry_sector=args.sector,
            duration_weeks=int(args.weeks),
            project_title=args.project,
            company_mentor=args.mentor,
            placement_status=args.status
        )
        print(f"Penempatan kerja praktik berhasil dicatat (ID: {kpid}) untuk {args.name} ({args.nim}) di {args.company}.")
    else:
        placements = storage.list_kp_placements(placement_status=args.status if args.status != "approved" else None, company_name=args.company)
        if not placements:
            print("Belum ada catatan penempatan kerja praktik mahasiswa.")
            return
        print("=== Rekam Jejak Penempatan Kerja Praktik (KP) Mahasiswa ===")
        for p in placements:
            print(f"#{p['id']} [{p['nim']}] {p['student_name']} @ {p['company_name']} ({p['industry_sector']}) - {p['project_title']} [{p['placement_status']}]")


def cmd_vitepress(args):
    article = storage.get_article_by_slug(args.slug)
    if not article:
        print(f"Error: Artikel dengan slug '{args.slug}' tidak ditemukan di database.")
        sys.exit(1)

    out_path = Path(args.out) if args.out else Path(f"{args.slug}.md")
    meta = {
        "seo_title": article.get("seo_title", ""),
        "topic": article.get("topic", ""),
        "meta_description": article.get("meta_description", ""),
        "publish_date": article.get("publish_date", "")
    }
    vp_md = ArticleExporter.to_vitepress_markdown(meta, article.get("html_content", ""))
    out_path.write_text(vp_md, encoding="utf-8")
    print(f"Export VitePress markdown berhasil -> {out_path}")


def cmd_accreditation(args):
    if args.action == "add":
        if not args.program or not args.agency or not args.rating or not args.sk or not args.expiry:
            print("Error: --program, --agency, --rating, --sk, dan --expiry wajib disertakan untuk mencatat akreditasi.")
            sys.exit(1)
        aid = storage.record_accreditation(
            program_name=args.program,
            agency=args.agency,
            rating=args.rating,
            sk_number=args.sk,
            expiry_date=args.expiry,
            issued_date=args.issued,
            is_active=bool(args.active)
        )
        print(f"Catatan akreditasi prodi berhasil disimpan (ID: {aid}) untuk '{args.program}'.")
    else:
        records = storage.list_accreditations(agency=args.agency)
        if not records:
            print("Belum ada catatan akreditasi program studi.")
            return
        print("=== Rekam Jejak Akreditasi Program Studi ===")
        for r in records:
            status_mark = "AKTIF" if r["is_active"] else "KADALUARSA"
            print(f"#{r['id']} [{r['agency']}] {r['program_name']} - Peringkat: {r['rating']} (SK: {r['sk_number']}) [{status_mark}]")


def cmd_scholarship(args):
    if args.action == "add":
        if not args.name or not args.nim or not args.type or not args.sponsor or args.amount is None or not args.semester or not args.year:
            print("Error: Parameter beasiswa mahasiswa tidak lengkap.")
            sys.exit(1)
        sid = storage.record_scholarship(
            student_name=args.name,
            nim=args.nim,
            scholarship_type=args.type,
            sponsor_name=args.sponsor,
            amount=float(args.amount),
            semester=args.semester,
            academic_year=args.year,
            status=args.status or "active"
        )
        print(f"Alokasi beasiswa mahasiswa berhasil dicatat (ID: {sid}) untuk {args.name} ({args.nim}).")
    else:
        records = storage.list_scholarships(scholarship_type=args.type, status=args.status if args.status != "all" else None)
        if not records:
            print("Belum ada catatan alokasi beasiswa mahasiswa.")
            return
        print("=== Rekam Jejak Alokasi Beasiswa Mahasiswa ===")
        for s in records:
            print(f"#{s['id']} [{s['academic_year']} - {s['semester']}] {s['student_name']} ({s['nim']}) - {s['sponsor_name']} ({s['scholarship_type']}) | Rp {s['amount']:,.0f} [{s['status']}]")


def cmd_jekyll(args):
    article = storage.get_article_by_slug(args.slug)
    if not article:
        print(f"Error: Artikel dengan slug '{args.slug}' tidak ditemukan di database.")
        sys.exit(1)

    out_path = Path(args.out) if args.out else Path(f"{args.slug}.md")
    tags = article.get("tags") or []
    if isinstance(tags, str):
        try:
            tags = json.loads(tags)
        except Exception:
            tags = [t.strip() for t in tags.split(",") if t.strip()]

    meta = {
        "seo_title": article.get("seo_title", ""),
        "topic": article.get("topic", ""),
        "publish_date": article.get("publish_date", ""),
        "category": article.get("category", ""),
        "tags": tags,
        "layout": args.layout or "post"
    }
    jekyll_md = ArticleExporter.to_jekyll_markdown(meta, article.get("html_content", ""))
    out_path.write_text(jekyll_md, encoding="utf-8")
    print(f"Export Jekyll markdown berhasil -> {out_path}")

def cmd_honors(args):
    if args.action == "add":
        if not args.name or not args.nim or args.ipk is None or not args.predicate or not args.thesis or not args.year:
            print("Error: Argumen --name, --nim, --ipk, --predicate, --thesis, dan --year wajib diisi untuk penambahan data.")
            sys.exit(1)
        data = {
            "student_name": args.name,
            "nim": args.nim,
            "ipk": args.ipk,
            "honor_predicate": args.predicate,
            "thesis_title": args.thesis,
            "study_duration_semesters": args.duration or 8,
            "graduation_year": args.year
        }
        hid = storage.record_graduation_honor(data)
        print(f"Catatan yudisium berhasil ditambahkan dengan ID: {hid}")
    else:
        honors = storage.list_graduation_honors(
            graduation_year=args.year,
            predicate_keyword=args.predicate
        )
        if not honors:
            print("Tidak ada catatan yudisium kelulusan yang ditemukan.")
            return
        print(f"{'ID':<4} | {'NIM':<10} | {'IPK':<5} | {'PREDIKAT':<30} | {'NAMA':<20} | {'TAHUN'}")
        print("-" * 85)
        for h in honors:
            print(f"{h['id']:<4} | {h['nim']:<10} | {h['ipk']:<5.2f} | {h['honor_predicate'][:28]:<30} | {h['student_name'][:18]:<20} | {h['graduation_year']}")

def cmd_tridharma(args):
    if args.action == "add":
        if not args.lecturer or not args.nidn or not args.title or args.amount is None or not args.year or not args.target:
            print("Error: Argumen --lecturer, --nidn, --title, --amount, --year, dan --target wajib diisi untuk penambahan data.")
            sys.exit(1)
        data = {
            "lecturer_name": args.lecturer,
            "nidn": args.nidn,
            "project_title": args.title,
            "grant_amount": args.amount,
            "fiscal_year": args.year,
            "publication_target": args.target,
            "status": args.status or "active"
        }
        gid = storage.record_tridharma_grant(data)
        print(f"Catatan hibah riset tridharma berhasil ditambahkan dengan ID: {gid}")
    else:
        grants = storage.list_tridharma_grants(
            fiscal_year=args.year,
            status=args.status
        )
        if not grants:
            print("Tidak ada catatan hibah riset tridharma yang ditemukan.")
            return
        print(f"{'ID':<4} | {'NIDN':<10} | {'DANA (IDR)':<14} | {'TAHUN':<6} | {'DOSEN':<20} | {'STATUS'}")
        print("-" * 75)
        for g in grants:
            print(f"{g['id']:<4} | {g['nidn']:<10} | {g['grant_amount']:<14,.0f} | {g['fiscal_year']:<6} | {g['lecturer_name'][:18]:<20} | {g['status']}")

def cmd_quartz(args):
    article = storage.get_article_by_slug(args.slug)
    if not article:
        print(f"Error: Artikel dengan slug '{args.slug}' tidak ditemukan di database.")
        sys.exit(1)

    out_path = Path(args.out) if args.out else Path(f"{args.slug}.md")
    tags = article.get("tags") or []
    if isinstance(tags, str):
        try:
            tags = json.loads(tags)
        except Exception:
            tags = [t.strip() for t in tags.split(",") if t.strip()]

    meta = {
        "seo_title": article.get("seo_title", ""),
        "topic": article.get("topic", ""),
        "publish_date": article.get("publish_date", ""),
        "category": article.get("category", ""),
        "tags": tags
    }
    quartz_md = ArticleExporter.to_quartz_markdown(meta, article.get("html_content", ""))
    out_path.write_text(quartz_md, encoding="utf-8")
    print(f"Export Quartz markdown berhasil -> {out_path}")

def cmd_fast_track(args):
    if args.action == "add":
        if not args.name or not args.nim or args.ipk is None or args.sks is None or args.toefl is None or not args.specialization:
            print("Error: Argumen --name, --nim, --ipk, --sks, --toefl, dan --specialization wajib diisi.")
            sys.exit(1)
        sid = storage.record_fast_track_student(
            student_name=args.name,
            nim=args.nim,
            ipk=args.ipk,
            completed_sks=args.sks,
            toefl_score=args.toefl,
            masters_specialization=args.specialization,
            status=args.status or "Eligible"
        )
        print(f"Kandidat fast-track berhasil dicatat dengan ID: {sid}")
    else:
        students = storage.list_fast_track_students(status=args.status)
        if not students:
            print("Tidak ada data kandidat fast-track ditemukan.")
            return
        print(f"{'ID':<4} | {'NIM':<10} | {'IPK':<5} | {'SKS':<4} | {'TOEFL':<5} | {'NAMA':<20} | {'STATUS'}")
        print("-" * 75)
        for s in students:
            print(f"{s['id']:<4} | {s['nim']:<10} | {s['ipk']:<5.2f} | {s['completed_sks']:<4} | {s['toefl_score']:<5} | {s['student_name'][:18]:<20} | {s['status']}")

def cmd_calibration(args):
    if args.action == "add":
        if not args.name or not args.sn or not args.lab or not args.last or not args.due or not args.cert:
            print("Error: Argumen --name, --sn, --lab, --last, --due, dan --cert wajib diisi.")
            sys.exit(1)
        cid = storage.record_lab_calibration_compliance(
            equipment_name=args.name,
            serial_number=args.sn,
            lab_room=args.lab,
            last_calibration_date=args.last,
            next_due_date=args.due,
            calibration_status=args.status or "Valid",
            cert_number=args.cert
        )
        print(f"Data kalibrasi peralatan berhasil dicatat dengan ID: {cid}")
    else:
        cals = storage.list_lab_calibration_compliance(status=args.status)
        if not cals:
            print("Tidak ada catatan kepatuhan kalibrasi lab ditemukan.")
            return
        print(f"{'ID':<4} | {'NO SERI':<15} | {'JATUH TEMPO':<12} | {'STATUS':<10} | {'ALAT':<25} | {'RUANG LAB'}")
        print("-" * 85)
        for c in cals:
            print(f"{c['id']:<4} | {c['serial_number'][:14]:<15} | {c['next_due_date']:<12} | {c['calibration_status']:<10} | {c['equipment_name'][:23]:<25} | {c['lab_room']}")

def cmd_hki(args):
    if args.action == "add":
        if not args.title or not args.creators or not args.type or not args.app_num or not args.reg_num or not args.date:
            print("Error: Argumen --title, --creators, --type, --app-num, --reg-num, dan --date wajib diisi.")
            sys.exit(1)
        creators_list = [c.strip() for c in args.creators.split(",") if c.strip()]
        hid = storage.record_lecturer_hki(
            work_title=args.title,
            creators=creators_list,
            creation_type=args.type,
            application_number=args.app_num,
            registration_number=args.reg_num,
            registration_date=args.date,
            rubric_points=args.points or 0.0
        )
        print(f"Pencatatan HKI/Hak Cipta berhasil disimpan dengan ID: {hid}")
    else:
        hkis = storage.list_lecturer_hki_records(creation_type=args.type)
        if not hkis:
            print("Tidak ada catatan HKI/Hak Cipta yang ditemukan.")
            return
        print(f"{'ID':<4} | {'NO PENCATATAN':<16} | {'JENIS':<18} | {'POIN':<5} | {'JUDUL CIPTAAN'}")
        print("-" * 80)
        for h in hkis:
            print(f"{h['id']:<4} | {h['registration_number']:<16} | {h['creation_type'][:16]:<18} | {h.get('rubric_points', 0.0):<5.1f} | {h['work_title'][:30]}")

def cmd_msib(args):
    if args.action == "add":
        if not args.name or not args.nim or not args.partner or not args.role or args.grade is None or not args.letter or args.sks is None:
            print("Error: Argumen --name, --nim, --partner, --role, --grade, --letter, dan --sks wajib diisi.")
            sys.exit(1)
        mid = storage.record_msib_internship(
            student_name=args.name,
            nim=args.nim,
            industry_partner=args.partner,
            internship_role=args.role,
            mentor_grade=args.grade,
            letter_grade=args.letter,
            converted_sks=args.sks,
            duration_months=args.duration or 6,
            status=args.status or "Completed"
        )
        print(f"Catatan magang MSIB berhasil disimpan dengan ID: {mid}")
    else:
        internships = storage.list_msib_internships(partner=args.partner)
        if not internships:
            print("Tidak ada catatan magang MSIB yang ditemukan.")
            return
        print(f"{'ID':<4} | {'NIM':<10} | {'SKS':<4} | {'NILAI':<5} | {'MITRA':<25} | {'NAMA':<20} | {'STATUS'}")
        print("-" * 85)
        for m in internships:
            print(f"{m['id']:<4} | {m['nim']:<10} | {m['converted_sks']:<4} | {m['letter_grade']:<5} | {m['industry_partner'][:23]:<25} | {m['student_name'][:18]:<20} | {m['status']}")

def cmd_pkm(args):
    if args.action == "add":
        if not args.title or not args.leader or not args.nidn or not args.partner or not args.location or args.proposed is None or args.approved is None or not args.year or not args.focus:
            print("Error: Argumen --title, --leader, --nidn, --partner, --location, --proposed, --approved, --year, dan --focus wajib diisi.")
            sys.exit(1)
        pid = storage.record_pkm_grant(
            project_title=args.title,
            team_leader=args.leader,
            nidn=args.nidn,
            partner_name=args.partner,
            target_location=args.location,
            proposed_budget=args.proposed,
            approved_budget=args.approved,
            fiscal_year=args.year,
            focus_area=args.focus,
            status=args.status or "Approved"
        )
        print(f"Catatan hibah PKM berhasil disimpan dengan ID: {pid}")
    else:
        grants = storage.list_pkm_grants(fiscal_year=args.year, status=args.status)
        if not grants:
            print("Tidak ada catatan hibah PKM yang ditemukan.")
            return
        print(f"{'ID':<4} | {'NIDN':<10} | {'DANA (IDR)':<14} | {'TAHUN':<6} | {'KETUA':<20} | {'STATUS'}")
        print("-" * 75)
        for g in grants:
            print(f"{g['id']:<4} | {g['nidn']:<10} | {g['approved_budget']:<14,.0f} | {g['fiscal_year']:<6} | {g['team_leader'][:18]:<20} | {g['status']}")

def cmd_fso(args):
    if args.action == "add":
        if not args.name or args.distance is None or args.tx is None or args.rx is None or args.geo is None or args.loss is None or args.margin is None:
            print("Error: Argumen --name, --distance, --tx, --rx, --geo, --loss, dan --margin wajib diisi.")
            sys.exit(1)
        fid = storage.record_fso_link_budget(
            link_name=args.name,
            link_distance_km=args.distance,
            tx_power_dbm=args.tx,
            rx_power_dbm=args.rx,
            geometric_loss_db=args.geo,
            atmospheric_loss_db=args.loss,
            link_margin_db=args.margin,
            status=args.status or ("Viable" if args.margin >= 3.0 else "Unviable")
        )
        print(f"Catatan link budget FSO berhasil disimpan dengan ID: {fid}")
    else:
        records = storage.list_fso_link_budgets(status=args.status)
        if not records:
            print("Tidak ada catatan link budget FSO yang ditemukan.")
            return
        print(f"{'ID':<4} | {'JARAK (KM)':<10} | {'MARGIN (DB)':<12} | {'STATUS':<10} | {'NAMA LINK'}")
        print("-" * 65)
        for r in records:
            print(f"{r['id']:<4} | {r['link_distance_km']:<10.2f} | {r['link_margin_db']:<12.2f} | {r['status']:<10} | {r['link_name'][:30]}")

def cmd_satellite(args):
    if args.action == "add":
        if not args.name or args.freq is None or args.range is None or args.eirp is None or args.gt is None or args.bw is None or args.cnr is None or args.margin is None:
            print("Error: Argumen --name, --freq, --range, --eirp, --gt, --bw, --cnr, dan --margin wajib diisi.")
            sys.exit(1)
        bid = storage.record_satellite_link_budget(
            satellite_name=args.name,
            downlink_freq_ghz=args.freq,
            slant_range_km=args.range,
            tx_eirp_dbw=args.eirp,
            rx_g_over_t_db_k=args.gt,
            bandwidth_mhz=args.bw,
            cnr_db=args.cnr,
            link_margin_db=args.margin,
            is_viable=args.margin >= 0.0,
            status=args.status or ("Feasible" if args.margin >= 0.0 else "Margin Deficient")
        )
        print(f"Catatan link budget satelit berhasil disimpan dengan ID: {bid}")
    else:
        viable_filter = True if args.viable else (False if args.unviable else None)
        budgets = storage.list_satellite_link_budgets(is_viable=viable_filter)
        if not budgets:
            print("Tidak ada catatan link budget satelit yang ditemukan.")
            return
        print(f"{'ID':<4} | {'FREQ':<8} | {'C/N (DB)':<10} | {'MARGIN':<10} | {'STATUS':<15} | {'SATELIT'}")
        print("-" * 75)
        for b in budgets:
            print(f"{b['id']:<4} | {b['downlink_freq_ghz']:<8.2f} | {b['cnr_db']:<10.2f} | {b['link_margin_db']:<+10.2f} | {b['status'][:14]:<15} | {b['satellite_name'][:25]}")

def cmd_mengajar(args):
    if args.action == "add":
        if not args.name or not args.nim or not args.school or not args.level or args.hours is None or args.score is None or not args.grade or args.sks is None:
            print("Error: Argumen --name, --nim, --school, --level, --hours, --score, --grade, dan --sks wajib diisi.")
            sys.exit(1)
        kid = storage.record_kampus_mengajar_student(
            student_name=args.name,
            nim=args.nim,
            target_school=args.school,
            school_level=args.level,
            teaching_hours=args.hours,
            composite_score=args.score,
            letter_grade=args.grade,
            converted_sks=args.sks,
            status=args.status or "Completed with Full Recognition"
        )
        print(f"Catatan Kampus Mengajar berhasil disimpan dengan ID: {kid}")
    else:
        students = storage.list_kampus_mengajar_students(status=args.status)
        if not students:
            print("Tidak ada catatan Kampus Mengajar yang ditemukan.")
            return
        print(f"{'ID':<4} | {'NIM':<10} | {'SKS':<4} | {'NILAI':<5} | {'SKOR':<6} | {'NAMA':<20} | {'SEKOLAH'}")
        print("-" * 80)
        for s in students:
            print(f"{s['id']:<4} | {s['nim']:<10} | {s['converted_sks']:<4} | {s['letter_grade']:<5} | {s['composite_score']:<6.1f} | {s['student_name'][:18]:<20} | {s['target_school']}")


def cmd_rf_intermod(args):
    if args.action == "add":
        if not args.name or args.pin is None or args.gain is None or args.iip3 is None or args.pout is None or args.imd3 is None:
            print("Error: Argumen --name, --pin, --gain, --iip3, --pout, dan --imd3 wajib diisi.")
            sys.exit(1)
        rid = storage.record_rf_intermod_distortion(
            component_name=args.name,
            input_power_dbm=args.pin,
            gain_db=args.gain,
            iip3_dbm=args.iip3,
            fundamental_pout_dbm=args.pout,
            imd3_suppression_dbc=args.imd3,
            linearity_status=args.status or ("Linear" if args.imd3 >= 35.0 else "Nonlinear"),
            is_linear=args.imd3 >= 35.0
        )
        print(f"Catatan distorsi intermodulasi RF berhasil disimpan dengan ID: {rid}")
    else:
        linear_filter = True if args.linear else (False if args.nonlinear else None)
        records = storage.list_rf_intermod_records(is_linear=linear_filter)
        if not records:
            print("Tidak ada catatan distorsi intermodulasi RF yang ditemukan.")
            return
        print(f"{'ID':<4} | {'IIP3':<8} | {'POUT':<8} | {'IMD3 (DBC)':<12} | {'STATUS':<15} | {'KOMPONEN'}")
        print("-" * 75)
        for r in records:
            print(f"{r['id']:<4} | {r['iip3_dbm']:<8.1f} | {r['fundamental_pout_dbm']:<8.1f} | {r['imd3_suppression_dbc']:<12.1f} | {r['linearity_status'][:14]:<15} | {r['component_name'][:25]}")


def cmd_radar(args):
    if args.action == "add":
        if not args.name or args.power is None or args.gain is None or args.rcs is None or args.freq is None:
            print("Error: Argumen --name, --power, --gain, --rcs, dan --freq wajib diisi.")
            sys.exit(1)
        smin = args.smin if args.smin is not None else -100.0
        calc = calculate_radar_range_equation(
            peak_power_kw=args.power,
            antenna_gain_dbi=args.gain,
            radar_cross_section_m2=args.rcs,
            freq_ghz=args.freq,
            min_detectable_signal_dbm=smin
        )
        rec_id = storage.record_radar_detection({
            "radar_name": args.name,
            "peak_power_kw": args.power,
            "antenna_gain_dbi": args.gain,
            "rcs_m2": args.rcs,
            "freq_ghz": args.freq,
            "min_detectable_signal_dbm": smin,
            "max_range_km": calc["max_range_km"],
            "round_trip_delay_us": calc["round_trip_delay_us"]
        })
        print(f"Catatan radar berhasil disimpan dengan ID: {rec_id} (R_max: {calc['max_range_km']:.2f} km)")
    else:
        records = storage.list_radar_detections(limit=args.limit or 50)
        if not records:
            print("Tidak ada catatan telemetri radar yang ditemukan.")
            return
        print(f"{'ID':<4} | {'FREQ':<8} | {'POWER':<8} | {'R_MAX (KM)':<12} | {'SISTEM RADAR'}")
        print("-" * 65)
        for r in records:
            print(f"{r['id']:<4} | {r['freq_ghz']:<8.2f} | {r['peak_power_kw']:<8.1f} | {r['max_range_km']:<12.2f} | {r['radar_name']}")


def cmd_wmk(args):
    if args.action == "add":
        if not args.name or not args.nim or not args.startup or not args.sector:
            print("Error: Argumen --name, --nim, --startup, dan --sector wajib diisi.")
            sys.exit(1)
        m_score = args.mentor if args.mentor is not None else 85.0
        p_score = args.pitch if args.pitch is not None else 85.0
        eval_res = parse_wirausaha_merdeka_evaluation(
            student_name=args.name,
            nim=args.nim,
            startup_name=args.startup,
            business_sector=args.sector,
            mentor_score=m_score,
            pitch_score=p_score
        )
        wid = storage.record_wmk_startup({
            "student_name": args.name,
            "nim": args.nim,
            "startup_name": args.startup,
            "business_sector": args.sector,
            "mentor_score": m_score,
            "pitch_score": p_score,
            "composite_score": eval_res["composite_score"],
            "converted_sks": eval_res["converted_sks"],
            "letter_grade": eval_res["letter_grade"],
            "status": eval_res["status"]
        })
        print(f"Catatan Wirausaha Merdeka berhasil disimpan dengan ID: {wid}")
    else:
        startups = storage.list_wmk_startups(limit=args.limit or 50)
        if not startups:
            print("Tidak ada catatan Wirausaha Merdeka yang ditemukan.")
            return
        print(f"{'ID':<4} | {'NIM':<10} | {'SKS':<4} | {'NILAI':<5} | {'STARTUP':<20} | {'SEKTOR'}")
        print("-" * 75)
        for s in startups:
            print(f"{s['id']:<4} | {s['nim']:<10} | {s['converted_sks']:<4} | {s['letter_grade']:<5} | {s['startup_name'][:18]:<20} | {s['business_sector']}")


def cmd_edfa(args):
    if args.action == "add":
        if not args.name or args.pin is None or args.pump is None or args.gain is None:
            print("Error: Argumen --name, --pin, --pump, dan --gain wajib diisi.")
            sys.exit(1)
        calc = calculate_edfa_amplifier_gain(
            input_power_dbm=args.pin,
            pump_power_mw=args.pump,
            small_signal_gain_db=args.gain
        )
        eid = storage.record_edfa_amplifier({
            "device_name": args.name,
            "input_power_dbm": args.pin,
            "pump_power_mw": args.pump,
            "small_signal_gain_db": args.gain,
            "actual_gain_db": calc["actual_gain_db"],
            "output_power_dbm": calc["output_power_dbm"],
            "noise_figure_db": calc["noise_figure_db"],
            "operating_regime": calc["operating_regime"]
        })
        print(f"Catatan EDFA berhasil disimpan dengan ID: {eid} (Gain: +{calc['actual_gain_db']:.2f} dB)")
    else:
        records = storage.list_edfa_amplifiers(limit=args.limit or 50)
        if not records:
            print("Tidak ada catatan penguat EDFA yang ditemukan.")
            return
        print(f"{'ID':<4} | {'PIN (DBM)':<10} | {'GAIN (DB)':<10} | {'POUT (DBM)':<11} | {'NF (DB)':<8} | {'PERANGKAT'}")
        print("-" * 75)
        for r in records:
            print(f"{r['id']:<4} | {r['input_power_dbm']:<10.1f} | {r['actual_gain_db']:<+10.2f} | {r['output_power_dbm']:<11.2f} | {r['noise_figure_db']:<8.2f} | {r['device_name']}")


def cmd_otdr(args):
    if args.action == "add":
        if not args.name or args.length is None or args.loss is None:
            print("Error: Argumen --name, --length, dan --loss wajib diisi.")
            sys.exit(1)
        splices = args.splices if args.splices is not None else 4
        conn = args.conn if args.conn is not None else 2
        wl = args.wl if args.wl is not None else 1550
        calc = calculate_otdr_fiber_events(
            fiber_length_km=args.length,
            total_loss_db=args.loss,
            num_splices=splices,
            num_connectors=conn,
            wavelength_nm=wl
        )
        oid = storage.record_otdr_measurement({
            "link_name": args.name,
            "fiber_length_km": args.length,
            "wavelength_nm": wl,
            "total_loss_db": args.loss,
            "event_loss_db": calc["total_event_loss_db"],
            "attenuation_db_km": calc["attenuation_db_per_km"],
            "quality_status": calc["quality_status"],
            "is_compliant": calc["is_compliant"]
        })
        print(f"Catatan OTDR berhasil disimpan dengan ID: {oid} (Alpha: {calc['attenuation_db_per_km']:.4f} dB/km)")
    else:
        records = storage.list_otdr_measurements(limit=args.limit or 50)
        if not records:
            print("Tidak ada catatan telemetri OTDR yang ditemukan.")
            return
        print(f"{'ID':<4} | {'PANJANG':<10} | {'LOSS (DB)':<10} | {'ALPHA (DB/KM)':<14} | {'STATUS':<20} | {'LINK'}")
        print("-" * 80)
        for r in records:
            print(f"{r['id']:<4} | {r['fiber_length_km']:<10.2f} | {r['total_loss_db']:<10.2f} | {r['attenuation_db_km']:<14.4f} | {r['quality_status'][:18]:<20} | {r['link_name']}")


def cmd_mimo(args):
    if args.action == "add":
        if not args.channel or args.bw is None or args.snr is None:
            print("Error: Argumen --channel, --bw, dan --snr wajib diisi.")
            sys.exit(1)
        tx = args.tx if args.tx is not None else 4
        rx = args.rx if args.rx is not None else 4
        calc = calculate_mimo_channel_capacity(
            bandwidth_mhz=args.bw,
            snr_db=args.snr,
            num_tx_antennas=tx,
            num_rx_antennas=rx
        )
        mid = storage.record_mimo_capacity({
            "channel_name": args.channel,
            "bandwidth_mhz": args.bw,
            "snr_db": args.snr,
            "num_tx": tx,
            "num_rx": rx,
            "spectral_eff_bps_hz": calc["spectral_efficiency_bps_hz"],
            "capacity_gbps": calc["capacity_gbps"],
            "gain_factor": calc["capacity_gain_factor"],
            "status": calc["spatial_multiplexing_status"]
        })
        print(f"Catatan MIMO berhasil disimpan dengan ID: {mid} (Kapasitas: {calc['capacity_gbps']:.3f} Gbps)")
    else:
        records = storage.list_mimo_capacities(limit=args.limit or 50)
        if not records:
            print("Tidak ada catatan kapasitas MIMO yang ditemukan.")
            return
        print(f"{'ID':<4} | {'MIMO':<6} | {'BW (MHZ)':<10} | {'EFF (BPS/HZ)':<14} | {'GBPS':<8} | {'KANAL'}")
        print("-" * 75)
        for r in records:
            print(f"{r['id']:<4} | {r['num_tx']}x{r['num_rx']:<3} | {r['bandwidth_mhz']:<10.1f} | {r['spectral_eff_bps_hz']:<14.2f} | {r['capacity_gbps']:<8.3f} | {r['channel_name']}")


def cmd_iisma(args):
    if args.action == "add":
        if not args.name or not args.nim or not args.host or not args.country or args.gpa is None or args.credits is None:
            print("Error: Argumen --name, --nim, --host, --country, --gpa, dan --credits wajib diisi.")
            sys.exit(1)
        eval_res = parse_iisma_evaluation(
            student_name=args.name,
            nim=args.nim,
            host_university=args.host,
            country=args.country,
            gpa_host=args.gpa,
            credits_taken=args.credits
        )
        iid = storage.record_iisma_student({
            "student_name": args.name,
            "nim": args.nim,
            "host_university": args.host,
            "country": args.country,
            "gpa_host": args.gpa,
            "credits_taken": args.credits,
            "converted_sks": eval_res["converted_sks"],
            "letter_grade": eval_res["letter_grade"],
            "status": eval_res["status"]
        })
        print(f"Catatan IISMA berhasil disimpan dengan ID: {iid} ({eval_res['converted_sks']} SKS Diakui)")
    else:
        students = storage.list_iisma_students(limit=args.limit or 50)
        if not students:
            print("Tidak ada catatan awardee IISMA yang ditemukan.")
            return
        print(f"{'ID':<4} | {'NIM':<10} | {'SKS':<4} | {'NILAI':<5} | {'MAHASISWA':<20} | {'UNIVERSITAS'}")
        print("-" * 80)
        for s in students:
            print(f"{s['id']:<4} | {s['nim']:<10} | {s['converted_sks']:<4} | {s['letter_grade']:<5} | {s['student_name'][:18]:<20} | {s['host_university']}")


def cmd_fspl(args):
    if args.action == "add":
        if not args.name or args.freq is None or args.distance is None:
            print("Error: Argumen --name, --freq, dan --distance wajib diisi.")
            sys.exit(1)
        tx = args.tx if args.tx is not None else 20.0
        gtx = args.gtx if args.gtx is not None else 14.0
        grx = args.grx if args.grx is not None else 14.0
        calc = calculate_fspl_and_link_budget(
            frequency_mhz=args.freq,
            distance_km=args.distance,
            tx_power_dbm=tx,
            tx_gain_dbi=gtx,
            rx_gain_dbi=grx
        )
        fid = storage.record_fspl_link_budget({
            "link_name": args.name,
            "freq_mhz": args.freq,
            "distance_km": args.distance,
            "fspl_db": calc["fspl_db"],
            "rx_power_dbm": calc["rx_power_dbm"],
            "fade_margin_db": calc["fade_margin_db"],
            "is_viable": calc["is_viable"]
        })
        print(f"Catatan FSPL berhasil disimpan dengan ID: {fid} (Fade Margin: {calc['fade_margin_db']:+.2f} dB)")
    else:
        records = storage.list_fspl_link_budgets(limit=args.limit or 50)
        if not records:
            print("Tidak ada catatan FSPL link budget yang ditemukan.")
            return
        print(f"{'ID':<4} | {'FREQ (MHZ)':<12} | {'JARAK (KM)':<10} | {'FSPL (DB)':<10} | {'MARGIN (DB)':<12} | {'LINK'}")
        print("-" * 75)
        for r in records:
            print(f"{r['id']:<4} | {r['freq_mhz']:<12.1f} | {r['distance_km']:<10.2f} | {r['fspl_db']:<10.2f} | {r['fade_margin_db']:<+12.2f} | {r['link_name']}")


def cmd_dispersion(args):
    if args.action == "add":
        if not args.name or args.length is None or args.disp is None:
            print("Error: Argumen --name, --length, dan --disp wajib diisi.")
            sys.exit(1)
        sw = args.sw if args.sw is not None else 0.1
        rate = args.rate if args.rate is not None else 10.0
        calc = calculate_optical_chromatic_dispersion(
            dispersion_param_ps_nm_km=args.disp,
            spectral_width_nm=sw,
            fiber_length_km=args.length,
            bit_rate_gbps=rate
        )
        did = storage.record_optical_dispersion({
            "fiber_name": args.name,
            "length_km": args.length,
            "dispersion_param": args.disp,
            "pulse_broadening_ps": calc["pulse_broadening_ps"],
            "max_bit_rate_gbps": calc["max_bit_rate_gbps"],
            "severity": calc["severity"],
            "requires_compensation": calc["requires_compensation"]
        })
        print(f"Catatan dispersi berhasil disimpan dengan ID: {did} (Broadening: {calc['pulse_broadening_ps']:.2f} ps)")
    else:
        records = storage.list_optical_dispersions(limit=args.limit or 50)
        if not records:
            print("Tidak ada catatan dispersi optik yang ditemukan.")
            return
        print(f"{'ID':<4} | {'PANJANG':<10} | {'D (PS/NM-KM)':<14} | {'DELTA_T':<10} | {'MAX GBPS':<10} | {'FIBER'}")
        print("-" * 75)
        for r in records:
            print(f"{r['id']:<4} | {r['length_km']:<10.2f} | {r['dispersion_param']:<14.2f} | {r['pulse_broadening_ps']:<10.2f} | {r['max_bit_rate_gbps']:<10.2f} | {r['fiber_name']}")


def cmd_kemanusiaan(args):
    if args.action == "add":
        if not args.name or not args.nim or not args.org:
            print("Error: Argumen --name, --nim, dan --org wajib diisi.")
            sys.exit(1)
        loc = args.loc if args.loc else "Jawa Tengah"
        hours = args.hours if args.hours is not None else 400
        mentor = args.mentor if args.mentor is not None else 85.0
        field = args.field if args.field is not None else 85.0
        eval_res = parse_proyek_kemanusiaan_evaluation({
            "student_name": args.name,
            "nim": args.nim,
            "partner_org": args.org,
            "location": loc,
            "field_hours": hours,
            "score_mentor": mentor,
            "score_field": field,
            "score_impact": 85.0
        })
        kid = storage.record_proyek_kemanusiaan({
            "student_name": args.name,
            "nim": args.nim,
            "partner_org": args.org,
            "location": loc,
            "field_hours": hours,
            "composite_score": eval_res["composite_score"],
            "converted_sks": eval_res["converted_sks"],
            "letter_grade": eval_res["letter_grade"],
            "status": eval_res["status"]
        })
        print(f"Catatan Proyek Kemanusiaan berhasil disimpan dengan ID: {kid} ({eval_res['converted_sks']} SKS Diakui)")
    else:
        records = storage.list_proyek_kemanusiaan(limit=args.limit or 50)
        if not records:
            print("Tidak ada catatan Proyek Kemanusiaan yang ditemukan.")
            return
        print(f"{'ID':<4} | {'NIM':<10} | {'SKS':<4} | {'NILAI':<5} | {'MAHASISWA':<20} | {'MITRA'}")
        print("-" * 75)
        for r in records:
            print(f"{r['id']:<4} | {r['nim']:<10} | {r['converted_sks']:<4} | {r['letter_grade']:<5} | {r['student_name'][:18]:<20} | {r['partner_org']}")


def cmd_pmd(args):
    if args.action == "add":
        if not args.name or args.length is None or args.coeff is None:
            print("Error: Argumen --name, --length, dan --coeff wajib diisi.")
            sys.exit(1)
        rate = args.rate if args.rate is not None else 10.0
        calc = calculate_polarization_mode_dispersion(
            pmd_coeff_ps_sqrt_km=args.coeff,
            fiber_length_km=args.length,
            bit_rate_gbps=rate
        )
        pid = storage.record_optical_pmd({
            "fiber_name": args.name,
            "length_km": args.length,
            "pmd_coeff": args.coeff,
            "mean_dgd_ps": calc["mean_dgd_ps"],
            "max_bit_rate_gbps": calc["max_bit_rate_gbps"],
            "outage_risk": calc["outage_risk"],
            "is_safe": calc["is_compliant"]
        })
        print(f"Catatan PMD berhasil disimpan dengan ID: {pid} (Mean DGD: {calc['mean_dgd_ps']:.3f} ps)")
    else:
        records = storage.list_optical_pmd(limit=args.limit or 50)
        if not records:
            print("Tidak ada catatan PMD serat optik yang ditemukan.")
            return
        print(f"{'ID':<4} | {'PANJANG':<10} | {'COEFF':<10} | {'DGD (PS)':<10} | {'GBPS':<10} | {'FIBER'}")
        print("-" * 75)
        for r in records:
            print(f"{r['id']:<4} | {r['length_km']:<10.2f} | {r['pmd_coeff']:<10.3f} | {r['mean_dgd_ps']:<10.3f} | {r['max_bit_rate_gbps']:<10.2f} | {r['fiber_name']}")


def cmd_cost231(args):
    if args.action == "add":
        if not args.area or args.freq is None or args.distance is None:
            print("Error: Argumen --area, --freq, dan --distance wajib diisi.")
            sys.exit(1)
        hb = args.hb if args.hb is not None else 30.0
        hm = args.hm if args.hm is not None else 1.5
        is_metro = getattr(args, "metro", False)
        calc = calculate_cost231_hata_path_loss(
            frequency_mhz=args.freq,
            base_station_height_m=hb,
            mobile_height_m=hm,
            distance_km=args.distance,
            is_metropolitan=is_metro
        )
        cid = storage.record_cost231_propagation({
            "area_name": args.area,
            "freq_mhz": args.freq,
            "distance_km": args.distance,
            "base_station_height_m": hb,
            "mobile_height_m": hm,
            "path_loss_db": calc["path_loss_db"],
            "coverage_quality": calc["coverage_quality"],
            "is_metro": is_metro
        })
        print(f"Catatan COST231 berhasil disimpan dengan ID: {cid} (Path Loss: {calc['path_loss_db']:.2f} dB)")
    else:
        records = storage.list_cost231_propagations(limit=args.limit or 50)
        if not records:
            print("Tidak ada catatan propagasi COST231 yang ditemukan.")
            return
        print(f"{'ID':<4} | {'FREQ (MHZ)':<12} | {'JARAK (KM)':<10} | {'LOSS (DB)':<10} | {'AREA'}")
        print("-" * 65)
        for r in records:
            print(f"{r['id']:<4} | {r['freq_mhz']:<12.1f} | {r['distance_km']:<10.2f} | {r['path_loss_db']:<10.2f} | {r['area_name']}")


def cmd_independen(args):
    if args.action == "add":
        if not args.name or not args.nim or not args.partner:
            print("Error: Argumen --name, --nim, dan --partner wajib diisi.")
            sys.exit(1)
        track = args.track if args.track else "AI & Cloud Engineering"
        hours = args.hours if args.hours is not None else 400
        mentor = args.mentor if args.mentor is not None else 85.0
        project = args.project if args.project is not None else 85.0
        defense = args.defense if args.defense is not None else 85.0
        eval_res = parse_studi_independen_evaluation({
            "student_name": args.name,
            "nim": args.nim,
            "partner_name": args.partner,
            "track_name": track,
            "learning_hours": hours,
            "score_mentor": mentor,
            "score_project": project,
            "score_defense": defense
        })
        sid = storage.record_studi_independen({
            "student_name": args.name,
            "nim": args.nim,
            "partner_name": args.partner,
            "track_name": track,
            "learning_hours": hours,
            "composite_score": eval_res["composite_score"],
            "converted_sks": eval_res["converted_sks"],
            "letter_grade": eval_res["letter_grade"],
            "status": eval_res["status"]
        })
        print(f"Catatan Studi Independen berhasil disimpan dengan ID: {sid} ({eval_res['converted_sks']} SKS Diakui)")
    else:
        records = storage.list_studi_independen(limit=args.limit or 50)
        if not records:
            print("Tidak ada catatan Studi Independen yang ditemukan.")
            return
        print(f"{'ID':<4} | {'NIM':<10} | {'SKS':<4} | {'NILAI':<5} | {'MAHASISWA':<20} | {'MITRA'}")
        print("-" * 75)
        for r in records:
            print(f"{r['id']:<4} | {r['nim']:<10} | {r['converted_sks']:<4} | {r['letter_grade']:<5} | {r['student_name'][:18]:<20} | {r['partner_name']}")


def cmd_fwm(args):
    if args.action == "add":
        if args.spacing is None or args.length is None or args.disp is None:
            print("Error: Argumen --spacing, --length, dan --disp wajib diisi.")
            sys.exit(1)
        slope = args.slope if args.slope is not None else 0.08
        att = args.att if args.att is not None else 0.2
        pwr = args.pwr if args.pwr is not None else 0.0
        calc = calculate_optical_four_wave_mixing(
            channel_spacing_ghz=args.spacing,
            fiber_length_km=args.length,
            chromatic_dispersion_ps_nm_km=args.disp,
            dispersion_slope_ps_nm2_km=slope,
            attenuation_db_km=att,
            channel_power_dbm=pwr
        )
        fid = storage.record_optical_fwm({
            "channel_spacing_ghz": args.spacing,
            "fiber_length_km": args.length,
            "dispersion_ps_nm_km": args.disp,
            "fwm_efficiency_pct": calc["fwm_efficiency_pct"],
            "crosstalk_suppression_dbc": calc["crosstalk_suppression_dbc"],
            "fwm_risk": calc["fwm_risk"],
            "is_compliant": calc["is_compliant"]
        })
        print(f"Catatan FWM berhasil disimpan dengan ID: {fid} (Efisiensi: {calc['fwm_efficiency_pct']:.3f}%)")
    else:
        records = storage.list_optical_fwm(limit=args.limit or 50)
        if not records:
            print("Tidak ada catatan FWM serat optik yang ditemukan.")
            return
        print(f"{'ID':<4} | {'SPACING (GHZ)':<14} | {'PANJANG':<10} | {'D (PS/NM*KM)':<14} | {'EFISIENSI (%)':<14} | {'RISIKO'}")
        print("-" * 80)
        for r in records:
            print(f"{r['id']:<4} | {r['channel_spacing_ghz']:<14.1f} | {r['fiber_length_km']:<10.2f} | {r['dispersion_ps_nm_km']:<14.3f} | {r['fwm_efficiency_pct']:<14.3f} | {r['fwm_risk']}")


def cmd_erlang(args):
    if args.action == "add":
        if args.traffic is None or args.channels is None:
            print("Error: Argumen --traffic dan --channels wajib diisi.")
            sys.exit(1)
        holding = args.holding if args.holding is not None else 120.0
        calc = calculate_erlang_traffic_capacity(
            offered_traffic_erlangs=args.traffic,
            num_channels=args.channels,
            avg_holding_time_sec=holding
        )
        eid = storage.record_erlang_traffic({
            "offered_traffic_erlangs": args.traffic,
            "num_channels": args.channels,
            "blocking_pct": calc["blocking_pct"],
            "carried_traffic_erlangs": calc["carried_traffic_erlangs"],
            "grade_of_service_status": calc["grade_of_service_status"],
            "is_acceptable": calc["is_acceptable"]
        })
        print(f"Catatan Erlang berhasil disimpan dengan ID: {eid} (Blocking: {calc['blocking_pct']:.2f}%)")
    else:
        records = storage.list_erlang_traffics(limit=args.limit or 50)
        if not records:
            print("Tidak ada catatan trafik Erlang yang ditemukan.")
            return
        print(f"{'ID':<4} | {'TRAFIK (ERL)':<14} | {'KANAL':<8} | {'BLOCKING (%)':<14} | {'CARRIED':<10} | {'STATUS GOS'}")
        print("-" * 75)
        for r in records:
            print(f"{r['id']:<4} | {r['offered_traffic_erlangs']:<14.2f} | {r['num_channels']:<8} | {r['blocking_pct']:<14.2f} | {r['carried_traffic_erlangs']:<10.2f} | {r['grade_of_service_status']}")


def cmd_pimnas(args):
    if args.action == "add":
        if not args.name or not args.nim:
            print("Error: Argumen --name dan --nim wajib diisi.")
            sys.exit(1)
        scheme = args.scheme if args.scheme else "PKM-KC"
        title = args.title if args.title else "Inovasi Perangkat Nirkabel Cerdas"
        is_pimnas = getattr(args, "pimnas", False)
        medal = args.medal if args.medal else ""
        proposal = args.proposal if args.proposal is not None else 85.0
        progress = args.progress if args.progress is not None else 85.0
        presentation = args.presentation if args.presentation is not None else 85.0
        eval_res = parse_pkm_mbkm_evaluation({
            "student_name": args.name,
            "nim": args.nim,
            "scheme": scheme,
            "proposal_title": title,
            "qualified_pimnas": is_pimnas,
            "medal": medal,
            "score_proposal": proposal,
            "score_progress": progress,
            "score_presentation": presentation
        })
        pid = storage.record_pkm_achievement({
            "student_name": args.name,
            "nim": args.nim,
            "scheme": scheme,
            "proposal_title": title,
            "qualified_pimnas": is_pimnas,
            "medal": medal,
            "composite_score": eval_res["composite_score"],
            "converted_sks": eval_res["converted_sks"],
            "letter_grade": eval_res["letter_grade"],
            "status": eval_res["status"]
        })
        print(f"Catatan PKM/PIMNAS berhasil disimpan dengan ID: {pid} ({eval_res['converted_sks']} SKS Diakui)")
    else:
        records = storage.list_pkm_achievements(limit=args.limit or 50)
        if not records:
            print("Tidak ada catatan prestasi PKM/PIMNAS yang ditemukan.")
            return
        print(f"{'ID':<4} | {'NIM':<10} | {'SKEMA':<10} | {'SKS':<4} | {'NILAI':<5} | {'MAHASISWA':<20} | {'STATUS'}")
        print("-" * 80)
        for r in records:
            print(f"{r['id']:<4} | {r['nim']:<10} | {r['scheme']:<10} | {r['converted_sks']:<4} | {r['letter_grade']:<5} | {r['student_name'][:18]:<20} | {r['status']}")


def cmd_xpm(args):
    if args.action == "add":
        if args.pump is None or args.probe is None or args.length is None:
            print("Error: Argumen --pump, --probe, dan --length wajib diisi.")
            sys.exit(1)
        att = args.att if args.att is not None else 0.2
        calc = calculate_optical_cross_phase_modulation(
            pump_power_mw=args.pump,
            probe_power_mw=args.probe,
            fiber_length_km=args.length,
            attenuation_db_km=att
        )
        xid = storage.record_optical_xpm({
            "pump_power_mw": args.pump,
            "probe_power_mw": args.probe,
            "fiber_length_km": args.length,
            "phi_xpm_deg": calc["phi_xpm_deg"],
            "xpm_risk": calc["xpm_risk"],
            "is_acceptable": calc["is_acceptable"]
        })
        print(f"Catatan XPM berhasil disimpan dengan ID: {xid} (Pergeseran: {calc['phi_xpm_deg']:.1f}°)")
    else:
        records = storage.list_optical_xpm(limit=args.limit or 50)
        if not records:
            print("Tidak ada catatan XPM serat optik yang ditemukan.")
            return
        print(f"{'ID':<4} | {'PUMP (MW)':<12} | {'PROBE (MW)':<12} | {'PANJANG':<10} | {'XPM (DEG)':<12} | {'RISIKO'}")
        print("-" * 75)
        for r in records:
            print(f"{r['id']:<4} | {r['pump_power_mw']:<12.2f} | {r['probe_power_mw']:<12.2f} | {r['fiber_length_km']:<10.2f} | {r['phi_xpm_deg']:<12.1f} | {r['xpm_risk']}")


def cmd_numerology(args):
    if args.action == "add":
        if args.mu is None:
            print("Error: Argumen --mu wajib diisi.")
            sys.exit(1)
        band = args.band if args.band else "n78 Mid-Band"
        rb = args.rb if args.rb is not None else 100
        calc = calculate_5g_nr_numerology_timing(numerology_mu=args.mu, num_resource_blocks=rb)
        nid = storage.record_nr_numerology({
            "band_name": band,
            "numerology_mu": args.mu,
            "scs_khz": calc["subcarrier_spacing_khz"],
            "slot_duration_ms": calc["slot_duration_ms"],
            "frequency_range": calc["frequency_range"]
        })
        print(f"Catatan Numerologi 5G NR berhasil disimpan dengan ID: {nid} (SCS: {calc['subcarrier_spacing_khz']} kHz)")
    else:
        records = storage.list_nr_numerologies(limit=args.limit or 50)
        if not records:
            print("Tidak ada catatan numerologi 5G NR yang ditemukan.")
            return
        print(f"{'ID':<4} | {'MU':<4} | {'SCS (KHZ)':<12} | {'DURASI SLOT':<14} | {'BAND':<18} | {'RANGE'}")
        print("-" * 75)
        for r in records:
            print(f"{r['id']:<4} | {r['numerology_mu']:<4} | {r['scs_khz']:<12} | {r['slot_duration_ms']:<14.4f} | {r['band_name'][:16]:<18} | {r['frequency_range']}")


def cmd_pmm(args):
    if args.action == "add":
        if not args.name or not args.nim or not args.host:
            print("Error: Argumen --name, --nim, dan --host wajib diisi.")
            sys.exit(1)
        nusantara = args.nusantara if args.nusantara is not None else 85.0
        academic = args.academic if args.academic is not None else 85.0
        mentor = args.mentor if args.mentor is not None else 85.0
        eval_res = parse_pmm_mbkm_evaluation({
            "student_name": args.name,
            "nim": args.nim,
            "host_university": args.host,
            "nusantara_module_score": nusantara,
            "academic_courses_score": academic,
            "host_mentor_score": mentor
        })
        pid = storage.record_pmm_evaluation({
            "student_name": args.name,
            "nim": args.nim,
            "host_university": args.host,
            "composite_score": eval_res["composite_score"],
            "letter_grade": eval_res["letter_grade"],
            "converted_sks": eval_res["converted_sks"],
            "status": eval_res["status"]
        })
        print(f"Catatan PMM berhasil disimpan dengan ID: {pid} ({eval_res['converted_sks']} SKS Diakui)")
    else:
        records = storage.list_pmm_evaluations(limit=args.limit or 50)
        if not records:
            print("Tidak ada catatan evaluasi PMM yang ditemukan.")
            return
        print(f"{'ID':<4} | {'NIM':<10} | {'SKS':<4} | {'NILAI':<5} | {'MAHASISWA':<18} | {'HOST UNIVERSITY'}")
        print("-" * 80)
        for r in records:
            print(f"{r['id']:<4} | {r['nim']:<10} | {r['converted_sks']:<4} | {r['letter_grade']:<5} | {r['student_name'][:16]:<18} | {r['host_university']}")


def cmd_srs(args):
    if args.action == "add":
        if args.length is None:
            print("Error: Argumen --length (panjang serat optik dalam km) wajib diisi.")
            sys.exit(1)
        fiber_name = args.fiber if args.fiber else "Standard SMF-28"
        pwr = args.power if args.power is not None else 100.0
        att = args.att if args.att is not None else 0.2
        area = args.area if args.area is not None else 80.0
        calc = calculate_optical_srs_threshold(
            fiber_length_km=args.length,
            attenuation_db_km=att,
            effective_area_um2=area,
            input_power_mw=pwr
        )
        sid = storage.record_optical_srs(
            fiber_name=fiber_name,
            input_power_mw=pwr,
            threshold_power_mw=calc["threshold_power_mw"],
            fiber_length_km=args.length,
            effective_area_um2=area,
            raman_gain_coeff=1.0e-13,
            srs_margin_db=calc["srs_margin_db"],
            srs_risk=calc["srs_risk"],
            is_safe=calc["is_safe"]
        )
        print(f"Catatan SRS berhasil disimpan dengan ID: {sid} (Ambang: {calc['threshold_power_mw']:.2f} mW, Margin: {calc['srs_margin_db']:+.2f} dB)")
    else:
        records = storage.list_optical_srs(limit=args.limit or 50)
        if not records:
            print("Tidak ada catatan ambang batas SRS yang ditemukan.")
            return
        print(f"{'ID':<4} | {'FIBER':<18} | {'DAYA (MW)':<10} | {'AMBANG':<10} | {'MARGIN (DB)':<12} | {'RISIKO'}")
        print("-" * 80)
        for r in records:
            print(f"{r['id']:<4} | {r['fiber_name'][:16]:<18} | {r['input_power_mw']:<10.1f} | {r['threshold_power_mw']:<10.1f} | {r['srs_margin_db']:<12.2f} | {r['srs_risk']}")


def cmd_eirp(args):
    if args.action == "add":
        if args.power is None or args.gain is None:
            print("Error: Argumen --power dan --gain wajib diisi.")
            sys.exit(1)
        cell = args.cell if args.cell else "NR-CELL-BDG-01"
        bw = args.bw if args.bw is not None else 20.0
        loss = args.loss if args.loss is not None else 2.0
        calc = calculate_5g_nr_eirp_psd(
            conducted_power_dbm=args.power,
            antenna_gain_dbi=args.gain,
            cable_loss_db=loss,
            bandwidth_mhz=bw
        )
        eid = storage.record_nr_eirp(
            cell_id=cell,
            conducted_power_dbm=args.power,
            antenna_gain_dbi=args.gain,
            channel_bandwidth_mhz=bw,
            eirp_dbm=calc["eirp_dbm"],
            eirp_watt=calc.get("eirp_watts", calc.get("eirp_watt", 0.0)),
            psd_eirp_dbm_mhz=calc["psd_eirp_dbm_mhz"],
            regulatory_status=calc["regulatory_status"],
            is_compliant=calc["is_compliant"]
        )
        print(f"Catatan 5G NR EIRP berhasil disimpan dengan ID: {eid} (EIRP: {calc['eirp_dbm']:.2f} dBm)")
    else:
        records = storage.list_nr_eirps(limit=args.limit or 50)
        if not records:
            print("Tidak ada catatan EIRP 5G NR yang ditemukan.")
            return
        print(f"{'ID':<4} | {'CELL ID':<16} | {'EIRP (DBM)':<12} | {'EIRP (W)':<10} | {'PSD (DBM/MHZ)':<14} | {'STATUS'}")
        print("-" * 80)
        for r in records:
            print(f"{r['id']:<4} | {r['cell_id'][:14]:<16} | {r['eirp_dbm']:<12.2f} | {r['eirp_watt']:<10.2f} | {r['psd_eirp_dbm_mhz']:<14.2f} | {r['regulatory_status']}")


def cmd_praktisi(args):
    if args.action == "add":
        if not args.course or not args.code or not args.practitioner or not args.company:
            print("Error: Argumen --course, --code, --practitioner, dan --company wajib diisi.")
            sys.exit(1)
        lecturer = args.lecturer if args.lecturer else "Dosen Pengampu"
        hours = args.hours if args.hours is not None else 12
        case_score = args.case if args.case is not None else 85.0
        prac_score = args.assessment if args.assessment is not None else 85.0
        stud_score = args.student if args.student is not None else 85.0

        eval_res = parse_praktisi_mengajar_evaluation({
            "course_name": args.course,
            "course_code": args.code,
            "practitioner_name": args.practitioner,
            "industry_company": args.company,
            "lecturer_name": lecturer,
            "teaching_hours": hours,
            "case_study_score": case_score,
            "practitioner_assessment": prac_score,
            "student_evaluation": stud_score
        })
        pid = storage.record_praktisi_mengajar(
            course_name=args.course,
            course_code=args.code,
            practitioner_name=args.practitioner,
            industry_company=args.company,
            lecturer_name=lecturer,
            teaching_hours=hours,
            composite_score=eval_res["composite_score"],
            letter_grade=eval_res["letter_grade"],
            converted_sks=eval_res["converted_sks"],
            status=eval_res["status"]
        )
        print(f"Catatan Praktisi Mengajar berhasil disimpan dengan ID: {pid} ({eval_res['converted_sks']} SKS Diakui, Grade: {eval_res['letter_grade']})")
    else:
        records = storage.list_praktisi_mengajar(limit=args.limit or 50)
        if not records:
            print("Tidak ada catatan Praktisi Mengajar yang ditemukan.")
            return
        print(f"{'ID':<4} | {'KODE':<8} | {'MATA KULIAH':<20} | {'PRAKTISI':<18} | {'SKS':<4} | {'GRADE'}")
        print("-" * 75)
        for r in records:
            print(f"{r['id']:<4} | {r['course_code']:<8} | {r['course_name'][:18]:<20} | {r['practitioner_name'][:16]:<18} | {r['converted_sks']:<4} | {r['letter_grade']}")



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

    # Note command
    note_parser = subparsers.add_parser("note", help="Kelola catatan kolaborasi editorial artikel (list, add, delete)")
    note_parser.add_argument("--action", choices=["list", "add", "delete"], default="list", help="Tindakan catatan")
    note_parser.add_argument("--id", type=int, help="ID artikel")
    note_parser.add_argument("--note-id", type=int, help="ID catatan untuk dihapus")
    note_parser.add_argument("--author", help="Penulis/editor catatan")
    note_parser.add_argument("--text", help="Isi teks catatan")
    note_parser.set_defaults(func=cmd_note)

    # Zola command
    zola_parser = subparsers.add_parser("zola", help="Export artikel ke format Markdown kompatibel Zola SSG")
    zola_parser.add_argument("--slug", required=True, help="Slug artikel di database")
    zola_parser.add_argument("--out", help="Path berkas output Markdown Zola")
    zola_parser.set_defaults(func=cmd_zola)

    # Webhook-logs command
    wh_parser = subparsers.add_parser("webhook-logs", help="Tampilkan riwayat log pengiriman webhook publikasi")
    wh_parser.add_argument("--limit", type=int, default=10, help="Jumlah maksimal riwayat log")
    wh_parser.set_defaults(func=cmd_webhook_logs)

    # Reviewer command
    rev_parser = subparsers.add_parser("reviewer", help="Kelola penugasan peer reviewer editorial artikel (assign, status, list)")
    rev_parser.add_argument("--action", choices=["assign", "status", "list"], default="list", help="Tindakan manajemen reviewer")
    rev_parser.add_argument("--id", type=int, help="ID artikel")
    rev_parser.add_argument("--review-id", type=int, help="ID penugasan review")
    rev_parser.add_argument("--name", help="Nama reviewer")
    rev_parser.add_argument("--email", help="Email reviewer")
    rev_parser.add_argument("--status", help="Status baru review")
    rev_parser.set_defaults(func=cmd_reviewer)

    # Pelican command
    pelican_parser = subparsers.add_parser("pelican", help="Export artikel ke format Markdown kompatibel Pelican SSG")
    pelican_parser.add_argument("--slug", required=True, help="Slug artikel di database")
    pelican_parser.add_argument("--out", help="Path berkas output Markdown Pelican")
    pelican_parser.set_defaults(func=cmd_pelican)

    # Checklist command
    chk_parser = subparsers.add_parser("checklist", help="Kelola checklist verifikasi alur kerja editorial artikel (list, set)")
    chk_parser.add_argument("--action", choices=["list", "set"], default="list", help="Tindakan checklist")
    chk_parser.add_argument("--id", type=int, required=True, help="ID artikel")
    chk_parser.add_argument("--key", help="Kunci unik item checklist")
    chk_parser.add_argument("--label", help="Label deskripsi checklist")
    chk_parser.add_argument("--checked", action="store_true", help="Tandai checklist telah selesai/diverifikasi")
    chk_parser.add_argument("--by", help="Nama verifikator item checklist")
    chk_parser.set_defaults(func=cmd_checklist)

    # Snippet command
    snippet_parser = subparsers.add_parser("snippet", help="Kelola library snippet konten editorial (list, save, get)")
    snippet_parser.add_argument("--action", choices=["list", "save", "get"], default="list", help="Tindakan snippet")
    snippet_parser.add_argument("--key", help="Kunci unik snippet")
    snippet_parser.add_argument("--title", help="Judul snippet")
    snippet_parser.add_argument("--html", help="HTML konten snippet")
    snippet_parser.add_argument("--category", help="Kategori snippet")
    snippet_parser.set_defaults(func=cmd_snippet)

    # Docusaurus command
    docu_parser = subparsers.add_parser("docusaurus", help="Export artikel ke format Markdown kompatibel Docusaurus")
    docu_parser.add_argument("--slug", required=True, help="Slug artikel di database")
    docu_parser.add_argument("--out", help="Path berkas output Markdown Docusaurus")
    docu_parser.add_argument("--label", help="Label sidebar Docusaurus")
    docu_parser.add_argument("--position", type=int, default=1, help="Posisi urutan pada sidebar")
    docu_parser.set_defaults(func=cmd_docusaurus)

    # Comment command
    comment_parser = subparsers.add_parser("comment", help="Kelola komentar review editorial artikel (list, add, resolve)")
    comment_parser.add_argument("--action", choices=["list", "add", "resolve"], default="list", help="Tindakan komentar review")
    comment_parser.add_argument("--id", type=int, help="ID artikel")
    comment_parser.add_argument("--comment-id", type=int, help="ID komentar")
    comment_parser.add_argument("--author", help="Nama editor / reviewer")
    comment_parser.add_argument("--text", help="Isi komentar editorial")
    comment_parser.add_argument("--paragraph", type=int, help="Indeks paragraf target")
    comment_parser.add_argument("--unresolved-only", action="store_true", help="Tampilkan hanya komentar yang belum diselesaikan")
    comment_parser.set_defaults(func=cmd_comment)

    # Achievement command
    ach_parser = subparsers.add_parser("achievement", help="Kelola catatan prestasi kompetisi mahasiswa (list, add)")
    ach_parser.add_argument("--action", choices=["list", "add"], default="list", help="Tindakan prestasi kompetisi")
    ach_parser.add_argument("--name", help="Nama kompetisi")
    ach_parser.add_argument("--rank", help="Peringkat atau penghargaan yang diraih")
    ach_parser.add_argument("--team", help="Nama tim kompetisi")
    ach_parser.add_argument("--members", help="Daftar nama anggota tim dipisahkan koma")
    ach_parser.add_argument("--supervisor", help="Dosen pembimbing tim")
    ach_parser.add_argument("--year", type=int, help="Tahun penyelenggaraan")
    ach_parser.add_argument("--organizer", help="Lembaga penyelenggara kompetisi")
    ach_parser.set_defaults(func=cmd_achievement)

    # Mkdocs command
    mkdocs_parser = subparsers.add_parser("mkdocs", help="Export artikel ke format Markdown kompatibel MkDocs")
    mkdocs_parser.add_argument("--slug", required=True, help="Slug artikel di database")
    mkdocs_parser.add_argument("--out", help="Path berkas output Markdown MkDocs")
    mkdocs_parser.set_defaults(func=cmd_mkdocs)

    # Safety-log command
    safety_parser = subparsers.add_parser("safety-log", help="Kelola catatan inspeksi keselamatan kerja K3 lab (list, add)")
    safety_parser.add_argument("--action", choices=["list", "add"], default="list", help="Tindakan log inspeksi K3")
    safety_parser.add_argument("--lab", help="Nama laboratorium")
    safety_parser.add_argument("--inspector", help="Nama personil inspektur K3")
    safety_parser.add_argument("--score", type=float, help="Skor pemenuhan keselamatan K3 (0-100)")
    safety_parser.add_argument("--passed", action="store_true", help="Tandai lulus inspeksi K3")
    safety_parser.add_argument("--date", help="Tanggal inspeksi (YYYY-MM-DD)")
    safety_parser.add_argument("--notes", help="Catatan temuan inspeksi keselamatan")
    safety_parser.set_defaults(func=cmd_safety_log)

    # MBKM command
    mbkm_parser = subparsers.add_parser("mbkm", help="Kelola rekognisi konversi kredit MBKM mahasiswa (list, add)")
    mbkm_parser.add_argument("--action", choices=["list", "add"], default="list", help="Tindakan konversi MBKM")
    mbkm_parser.add_argument("--program", help="Nama program MBKM (misal: MSIB Magang Merdeka)")
    mbkm_parser.add_argument("--partner", help="Nama mitra institusi atau industri")
    mbkm_parser.add_argument("--name", help="Nama mahasiswa")
    mbkm_parser.add_argument("--nim", help="Nomor Induk Mahasiswa")
    mbkm_parser.add_argument("--semester", type=int, default=6, help="Semester pelaksanaan MBKM")
    mbkm_parser.add_argument("--sks", type=int, default=20, help="Total SKS rekognisi")
    mbkm_parser.add_argument("--gpa", type=float, default=3.75, help="Indeks prestasi rata-rata konversi")
    mbkm_parser.add_argument("--sk", help="Nomor SK Rekognisi MBKM")
    mbkm_parser.set_defaults(func=cmd_mbkm)

    # Yudisium command
    yudisium_parser = subparsers.add_parser("yudisium", help="Kelola rekam kelulusan yudisium mahasiswa (list, add, check)")
    yudisium_parser.add_argument("--action", choices=["list", "add", "check"], default="list", help="Tindakan yudisium")
    yudisium_parser.add_argument("--name", help="Nama mahasiswa")
    yudisium_parser.add_argument("--nim", help="Nomor Induk Mahasiswa")
    yudisium_parser.add_argument("--thesis", help="Judul tugas akhir / skripsi mahasiswa")
    yudisium_parser.add_argument("--ipk", type=float, help="Indeks Prestasi Kumulatif kelulusan")
    yudisium_parser.add_argument("--sks", type=int, help="Total SKS kelulusan")
    yudisium_parser.add_argument("--predicate", help="Predikat kelulusan (Pujian/Sangat Memuaskan/Memuaskan)")
    yudisium_parser.add_argument("--date", help="Tanggal yudisium (YYYY-MM-DD)")
    yudisium_parser.add_argument("--code", help="Kode verifikasi ijazah/yudisium")
    yudisium_parser.set_defaults(func=cmd_yudisium)

    # Starlight command
    starlight_parser = subparsers.add_parser("starlight", help="Export artikel ke format Markdown kompatibel Astro Starlight")
    starlight_parser.add_argument("--slug", required=True, help="Slug artikel di database")
    starlight_parser.add_argument("--out", help="Path berkas output Markdown Starlight")
    starlight_parser.add_argument("--label", help="Label sidebar Starlight")
    starlight_parser.add_argument("--order", type=int, default=1, help="Urutan prioritas pada sidebar")
    starlight_parser.set_defaults(func=cmd_starlight)

    # KKN command
    kkn_parser = subparsers.add_parser("kkn", help="Kelola rekam penempatan KKN tematik mahasiswa (list, add)")
    kkn_parser.add_argument("--action", choices=["list", "add"], default="list", help="Tindakan KKN")
    kkn_parser.add_argument("--group", help="Kode kelompok KKN")
    kkn_parser.add_argument("--village", help="Nama desa mitra")
    kkn_parser.add_argument("--district", help="Nama kecamatan")
    kkn_parser.add_argument("--regency", help="Nama kabupaten")
    kkn_parser.add_argument("--supervisor", help="Nama dosen pembimbing lapangan (DPL)")
    kkn_parser.add_argument("--students", type=int, help="Jumlah mahasiswa peserta")
    kkn_parser.add_argument("--theme", help="Tema program KKN tematik")
    kkn_parser.add_argument("--flagship", help="Program unggulan luaran KKN")
    kkn_parser.set_defaults(func=cmd_kkn)

    # BKD command
    bkd_parser = subparsers.add_parser("bkd", help="Kelola rekam kepatuhan Beban Kerja Dosen (list, add)")
    bkd_parser.add_argument("--action", choices=["list", "add"], default="list", help="Tindakan BKD")
    bkd_parser.add_argument("--name", help="Nama dosen")
    bkd_parser.add_argument("--nidn", help="NIDN dosen")
    bkd_parser.add_argument("--rank", help="Jabatan fungsional akademik")
    bkd_parser.add_argument("--semester", help="Semester evaluasi BKD")
    bkd_parser.add_argument("--teaching", type=float, help="SKS bidang pendidikan/pengajaran")
    bkd_parser.add_argument("--research", type=float, help="SKS bidang penelitian")
    bkd_parser.add_argument("--service", type=float, help="SKS bidang pengabdian masyarakat")
    bkd_parser.add_argument("--supporting", type=float, help="SKS bidang penunjang")
    bkd_parser.add_argument("--total", type=float, help="Total SKS beban kerja")
    bkd_parser.add_argument("--compliant", action="store_true", help="Status kepatuhan BKD memenuhi ambang batas")
    bkd_parser.set_defaults(func=cmd_bkd)

    # Hexo command
    hexo_parser = subparsers.add_parser("hexo", help="Export artikel ke format Markdown kompatibel Hexo static blog")
    hexo_parser.add_argument("--slug", required=True, help="Slug artikel di database")
    hexo_parser.add_argument("--out", help="Path berkas output Markdown Hexo")
    hexo_parser.set_defaults(func=cmd_hexo)

    # BIMA command
    bima_parser = subparsers.add_parser("bima", help="Kelola usulan hibah penelitian BIMA Kemdikbud (list, add)")
    bima_parser.add_argument("--action", choices=["list", "add"], default="list", help="Tindakan usulan hibah BIMA")
    bima_parser.add_argument("--title", help="Judul proyek penelitian")
    bima_parser.add_argument("--name", help="Nama ketua peneliti")
    bima_parser.add_argument("--nidn", help="NIDN ketua peneliti")
    bima_parser.add_argument("--scheme", help="Skema hibah penelitian")
    bima_parser.add_argument("--requested", type=float, help="Anggaran usulan (IDR)")
    bima_parser.add_argument("--approved", type=float, default=0.0, help="Anggaran disetujui (IDR)")
    bima_parser.add_argument("--year", type=int, help="Tahun anggaran pelaksanaan")
    bima_parser.add_argument("--status", default="submitted", help="Status usulan proposal")
    bima_parser.add_argument("--contract", help="Nomor kontrak perjanjian hibah")
    bima_parser.set_defaults(func=cmd_bima)

    # KP command
    kp_parser = subparsers.add_parser("kp", help="Kelola penempatan kerja praktik mahasiswa (list, add)")
    kp_parser.add_argument("--action", choices=["list", "add"], default="list", help="Tindakan penempatan kerja praktik")
    kp_parser.add_argument("--name", help="Nama mahasiswa")
    kp_parser.add_argument("--nim", help="Nomor Induk Mahasiswa")
    kp_parser.add_argument("--company", help="Nama perusahaan / industri mitra")
    kp_parser.add_argument("--sector", help="Sektor bidang industri")
    kp_parser.add_argument("--weeks", type=int, default=8, help="Durasi pelaksanaan dalam minggu")
    kp_parser.add_argument("--project", help="Judul proyek kerja praktik")
    kp_parser.add_argument("--mentor", help="Nama pembimbing lapangan")
    kp_parser.add_argument("--status", default="approved", help="Status penempatan KP")
    kp_parser.set_defaults(func=cmd_kp)

    # VitePress command
    vitepress_parser = subparsers.add_parser("vitepress", help="Export artikel ke format Markdown kompatibel VitePress")
    vitepress_parser.add_argument("--slug", required=True, help="Slug artikel di database")
    vitepress_parser.add_argument("--out", help="Path berkas output Markdown VitePress")
    vitepress_parser.set_defaults(func=cmd_vitepress)

    # Accreditation command
    acc_parser = subparsers.add_parser("accreditation", help="Kelola catatan akreditasi program studi (list, add)")
    acc_parser.add_argument("--action", choices=["list", "add"], default="list", help="Tindakan akreditasi")
    acc_parser.add_argument("--program", help="Nama program studi")
    acc_parser.add_argument("--agency", help="Lembaga akreditasi (LAM INFOKOM / BAN-PT)")
    acc_parser.add_argument("--rating", help="Peringkat akreditasi (Unggul/Baik Sekali/Baik)")
    acc_parser.add_argument("--sk", help="Nomor SK Akreditasi")
    acc_parser.add_argument("--expiry", help="Tanggal kadaluarsa akreditasi (YYYY-MM-DD)")
    acc_parser.add_argument("--issued", help="Tanggal penerbitan SK akreditasi")
    acc_parser.add_argument("--active", action="store_true", default=True, help="Status keaktifan masa berlaku akreditasi")
    acc_parser.set_defaults(func=cmd_accreditation)

    # Scholarship command
    sch_parser = subparsers.add_parser("scholarship", help="Kelola catatan alokasi beasiswa mahasiswa (list, add)")
    sch_parser.add_argument("--action", choices=["list", "add"], default="list", help="Tindakan beasiswa")
    sch_parser.add_argument("--name", help="Nama mahasiswa penerima")
    sch_parser.add_argument("--nim", help="Nomor Induk Mahasiswa penerima")
    sch_parser.add_argument("--type", help="Jenis beasiswa (pemerintah/industri/alumni/internal)")
    sch_parser.add_argument("--sponsor", help="Nama lembaga atau perusahaan sponsor")
    sch_parser.add_argument("--amount", type=float, help="Nominal bantuan beasiswa (IDR)")
    sch_parser.add_argument("--semester", help="Semester penerimaan beasiswa")
    sch_parser.add_argument("--year", help="Tahun akademik beasiswa")
    sch_parser.add_argument("--status", default="active", help="Status alokasi beasiswa")
    sch_parser.set_defaults(func=cmd_scholarship)

    # Jekyll command
    jekyll_parser = subparsers.add_parser("jekyll", help="Export artikel ke format Markdown kompatibel Jekyll static blog")
    jekyll_parser.add_argument("--slug", required=True, help="Slug artikel di database")
    jekyll_parser.add_argument("--out", help="Path berkas output Markdown Jekyll")
    jekyll_parser.add_argument("--layout", default="post", help="Layout Jekyll (default: post)")
    jekyll_parser.set_defaults(func=cmd_jekyll)

    # Honors command
    honors_parser = subparsers.add_parser("honors", help="Kelola catatan yudisium kelulusan berpredikat kehormatan (list, add)")
    honors_parser.add_argument("--action", choices=["list", "add"], default="list", help="Tindakan yudisium")
    honors_parser.add_argument("--name", help="Nama wisudawan")
    honors_parser.add_argument("--nim", help="Nomor Induk Mahasiswa")
    honors_parser.add_argument("--ipk", type=float, help="Indeks Prestasi Kumulatif")
    honors_parser.add_argument("--predicate", help="Predikat yudisium kelulusan")
    honors_parser.add_argument("--thesis", help="Judul tugas akhir")
    honors_parser.add_argument("--duration", type=int, default=8, help="Masa studi dalam semester")
    honors_parser.add_argument("--year", type=int, help="Tahun kelulusan")
    honors_parser.set_defaults(func=cmd_honors)

    # Tridharma command
    tridharma_parser = subparsers.add_parser("tridharma", help="Kelola catatan hibah riset internal tridharma (list, add)")
    tridharma_parser.add_argument("--action", choices=["list", "add"], default="list", help="Tindakan hibah riset")
    tridharma_parser.add_argument("--lecturer", help="Nama ketua peneliti")
    tridharma_parser.add_argument("--nidn", help="NIDN ketua peneliti")
    tridharma_parser.add_argument("--title", help="Judul proyek penelitian")
    tridharma_parser.add_argument("--amount", type=float, help="Besaran dana hibah disetujui (IDR)")
    tridharma_parser.add_argument("--year", type=int, help="Tahun anggaran pelaksanaan")
    tridharma_parser.add_argument("--target", help="Target luaran publikasi / paten")
    tridharma_parser.add_argument("--status", default="active", help="Status hibah riset")
    tridharma_parser.set_defaults(func=cmd_tridharma)

    # Quartz command
    quartz_parser = subparsers.add_parser("quartz", help="Export artikel ke format Markdown kompatibel Quartz digital garden")
    quartz_parser.add_argument("--slug", required=True, help="Slug artikel di database")
    quartz_parser.add_argument("--out", help="Path berkas output Markdown Quartz")
    quartz_parser.set_defaults(func=cmd_quartz)

    # Fast-track command
    ft_parser = subparsers.add_parser("fast-track", help="Kelola data seleksi program magister fast-track (list, add)")
    ft_parser.add_argument("--action", choices=["list", "add"], default="list", help="Tindakan fast-track")
    ft_parser.add_argument("--name", help="Nama lengkap mahasiswa")
    ft_parser.add_argument("--nim", help="Nomor Induk Mahasiswa")
    ft_parser.add_argument("--ipk", type=float, help="Indeks Prestasi Kumulatif")
    ft_parser.add_argument("--sks", type=int, help="Jumlah SKS lulus")
    ft_parser.add_argument("--toefl", type=int, help="Skor TOEFL")
    ft_parser.add_argument("--specialization", help="Peminatan magister")
    ft_parser.add_argument("--status", default="Eligible", help="Status kelayakan fast-track")
    ft_parser.set_defaults(func=cmd_fast_track)

    # Calibration command
    cal_parser = subparsers.add_parser("calibration", help="Kelola kepatuhan kalibrasi alat lab telekomunikasi (list, add)")
    cal_parser.add_argument("--action", choices=["list", "add"], default="list", help="Tindakan kalibrasi")
    cal_parser.add_argument("--name", help="Nama peralatan laboratorium")
    cal_parser.add_argument("--sn", help="Nomor seri peralatan")
    cal_parser.add_argument("--lab", help="Ruang laboratorium")
    cal_parser.add_argument("--last", help="Tanggal kalibrasi terakhir (YYYY-MM-DD)")
    cal_parser.add_argument("--due", help="Tanggal jatuh tempo kalibrasi (YYYY-MM-DD)")
    cal_parser.add_argument("--status", default="Valid", help="Status kalibrasi (Valid, Expired, Due Soon)")
    cal_parser.add_argument("--cert", help="Nomor sertifikat kalibrasi")
    cal_parser.set_defaults(func=cmd_calibration)

    # HKI command
    hki_parser = subparsers.add_parser("hki", help="Kelola pencatatan hak cipta dan kekayaan intelektual dosen (list, add)")
    hki_parser.add_argument("--action", choices=["list", "add"], default="list", help="Tindakan HKI")
    hki_parser.add_argument("--title", help="Judul ciptaan / karya intelektual")
    hki_parser.add_argument("--creators", help="Daftar pencipta dipisahkan koma")
    hki_parser.add_argument("--type", help="Jenis ciptaan (Program Komputer, Buku, Modul)")
    hki_parser.add_argument("--app-num", help="Nomor permohonan DJKI")
    hki_parser.add_argument("--reg-num", help="Nomor pencatatan sertifikat DJKI")
    hki_parser.add_argument("--date", help="Tanggal pencatatan")
    hki_parser.add_argument("--points", type=float, default=0.0, help="Poin BKD / SINTA")
    hki_parser.set_defaults(func=cmd_hki)

    # MSIB command
    msib_parser = subparsers.add_parser("msib", help="Kelola rekam magang bersertifikat MSIB (list, add)")
    msib_parser.add_argument("--action", choices=["list", "add"], default="list", help="Tindakan MSIB")
    msib_parser.add_argument("--name", help="Nama mahasiswa")
    msib_parser.add_argument("--nim", help="Nomor Induk Mahasiswa")
    msib_parser.add_argument("--partner", help="Nama mitra industri MSIB")
    msib_parser.add_argument("--role", help="Posisi / peran magang")
    msib_parser.add_argument("--grade", type=float, help="Nilai mentor industri")
    msib_parser.add_argument("--letter", help="Konversi nilai huruf (A/AB/B)")
    msib_parser.add_argument("--sks", type=int, help="Jumlah SKS konversi")
    msib_parser.add_argument("--duration", type=int, default=6, help="Durasi magang dalam bulan")
    msib_parser.add_argument("--status", default="Completed", help="Status magang")
    msib_parser.set_defaults(func=cmd_msib)

    # PKM command
    pkm_parser = subparsers.add_parser("pkm", help="Kelola usulan hibah pengabdian masyarakat PKM (list, add)")
    pkm_parser.add_argument("--action", choices=["list", "add"], default="list", help="Tindakan hibah PKM")
    pkm_parser.add_argument("--title", help="Judul proyek pengabdian")
    pkm_parser.add_argument("--leader", help="Nama ketua tim pelaksana")
    pkm_parser.add_argument("--nidn", help="NIDN ketua tim")
    pkm_parser.add_argument("--partner", help="Nama mitra sasaran")
    pkm_parser.add_argument("--location", help="Lokasi pelaksanaan PKM")
    pkm_parser.add_argument("--proposed", type=float, help="Anggaran usulan (IDR)")
    pkm_parser.add_argument("--approved", type=float, help="Anggaran disetujui (IDR)")
    pkm_parser.add_argument("--year", type=int, help="Tahun pelaksanaan")
    pkm_parser.add_argument("--focus", help="Bidang fokus PKM")
    pkm_parser.add_argument("--status", default="Approved", help="Status hibah")
    pkm_parser.set_defaults(func=cmd_pkm)

    # FSO command
    fso_parser = subparsers.add_parser("fso", help="Kelola kalkulasi link budget laser optik ruang bebas FSO (list, add)")
    fso_parser.add_argument("--action", choices=["list", "add"], default="list", help="Tindakan FSO link budget")
    fso_parser.add_argument("--name", help="Nama link FSO")
    fso_parser.add_argument("--distance", type=float, help="Jarak link (km)")
    fso_parser.add_argument("--tx", type=float, help="Daya pancar Tx (dBm)")
    fso_parser.add_argument("--rx", type=float, help="Daya terima Rx (dBm)")
    fso_parser.add_argument("--geo", type=float, help="Rugi geometrik (dB)")
    fso_parser.add_argument("--loss", type=float, help="Rugi redaman atmosfer (dB)")
    fso_parser.add_argument("--margin", type=float, help="Link margin (dB)")
    fso_parser.add_argument("--status", help="Status kelayakan link")
    fso_parser.set_defaults(func=cmd_fso)

    # Satellite command
    sat_parser = subparsers.add_parser("satellite", help="Kelola kalkulasi link budget satelit & stasiun bumi (list, add)")
    sat_parser.add_argument("--action", choices=["list", "add"], default="list", help="Tindakan link budget satelit")
    sat_parser.add_argument("--name", help="Nama satelit transponder")
    sat_parser.add_argument("--freq", type=float, help="Frekuensi downlink (GHz)")
    sat_parser.add_argument("--range", type=float, help="Jarak miring slant range (km)")
    sat_parser.add_argument("--eirp", type=float, help="EIRP satelit (dBW)")
    sat_parser.add_argument("--gt", type=float, help="Figure of merit G/T antena stasiun bumi (dB/K)")
    sat_parser.add_argument("--bw", type=float, help="Lebar pita transponder (MHz)")
    sat_parser.add_argument("--cnr", type=float, help="Carrier-to-Noise Ratio (dB)")
    sat_parser.add_argument("--margin", type=float, help="Fade link margin (dB)")
    sat_parser.add_argument("--status", help="Status kelayakan link")
    sat_parser.add_argument("--viable", action="store_true", help="Filter hanya link yang layak")
    sat_parser.add_argument("--unviable", action="store_true", help="Filter hanya link yang tidak layak")
    sat_parser.set_defaults(func=cmd_satellite)

    # Mengajar command
    mengajar_parser = subparsers.add_parser("mengajar", help="Kelola evaluasi & rekognisi SKS program Kampus Mengajar MBKM (list, add)")
    mengajar_parser.add_argument("--action", choices=["list", "add"], default="list", help="Tindakan Kampus Mengajar")
    mengajar_parser.add_argument("--name", help="Nama lengkap mahasiswa")
    mengajar_parser.add_argument("--nim", help="Nomor Induk Mahasiswa")
    mengajar_parser.add_argument("--school", help="Nama sekolah penugasan")
    mengajar_parser.add_argument("--level", help="Jenjang sekolah (SD/SMP/SMA)")
    mengajar_parser.add_argument("--hours", type=int, help="Jumlah jam penugasan")
    mengajar_parser.add_argument("--score", type=float, help="Skor komposit evaluasi")
    mengajar_parser.add_argument("--grade", help="Nilai huruf mutu (A/AB/B)")
    mengajar_parser.add_argument("--sks", type=int, help="Jumlah SKS konversi")
    mengajar_parser.add_argument("--status", help="Status kelulusan")
    mengajar_parser.set_defaults(func=cmd_mengajar)

    # RF-Intermod command
    rf_parser = subparsers.add_parser("rf-intermod", help="Kelola kalkulasi linearitas & distorsi intermodulasi RF (list, add)")
    rf_parser.add_argument("--action", choices=["list", "add"], default="list", help="Tindakan distorsi intermodulasi RF")
    rf_parser.add_argument("--name", help="Nama modul / komponen RF")
    rf_parser.add_argument("--pin", type=float, help="Daya input fundamental (dBm)")
    rf_parser.add_argument("--gain", type=float, help="Penguatan RF (dB)")
    rf_parser.add_argument("--iip3", type=float, help="Input IP3 (dBm)")
    rf_parser.add_argument("--pout", type=float, help="Daya output fundamental (dBm)")
    rf_parser.add_argument("--imd3", type=float, help="Supresi intermodulasi IMD3 (dBc)")
    rf_parser.add_argument("--status", help="Status linearitas")
    rf_parser.add_argument("--linear", action="store_true", help="Filter hanya komponen linear")
    rf_parser.add_argument("--nonlinear", action="store_true", help="Filter hanya komponen nonlinear")
    rf_parser.set_defaults(func=cmd_rf_intermod)

    # Radar command
    radar_parser = subparsers.add_parser("radar", help="Kelola kalkulasi telemetri persamaan jangkauan radar (list, add)")
    radar_parser.add_argument("--action", choices=["list", "add"], default="list", help="Tindakan telemetri radar")
    radar_parser.add_argument("--name", help="Nama sistem radar")
    radar_parser.add_argument("--power", type=float, help="Peak transmit power (kW)")
    radar_parser.add_argument("--gain", type=float, help="Gain antena pengarah (dBi)")
    radar_parser.add_argument("--rcs", type=float, help="Radar cross-section target (m²)")
    radar_parser.add_argument("--freq", type=float, help="Frekuensi kerja carrier (GHz)")
    radar_parser.add_argument("--smin", type=float, default=-100.0, help="Sinyal minimum penerima (dBm)")
    radar_parser.add_argument("--limit", type=int, default=50, help="Batas jumlah rekaman ditampilkan")
    radar_parser.set_defaults(func=cmd_radar)

    # WMK command
    wmk_parser = subparsers.add_parser("wmk", help="Kelola evaluasi & konversi SKS MBKM Wirausaha Merdeka (list, add)")
    wmk_parser.add_argument("--action", choices=["list", "add"], default="list", help="Tindakan evaluasi Wirausaha Merdeka")
    wmk_parser.add_argument("--name", help="Nama lengkap mahasiswa founder")
    wmk_parser.add_argument("--nim", help="Nomor Induk Mahasiswa")
    wmk_parser.add_argument("--startup", help="Nama produk / startup")
    wmk_parser.add_argument("--sector", help="Sektor bisnis startup")
    wmk_parser.add_argument("--mentor", type=float, help="Skor pembimbing mentor (0-100)")
    wmk_parser.add_argument("--pitch", type=float, help="Skor pitching presentasi (0-100)")
    wmk_parser.add_argument("--limit", type=int, default=50, help="Batas jumlah rekaman ditampilkan")
    wmk_parser.set_defaults(func=cmd_wmk)

    # EDFA command
    edfa_parser = subparsers.add_parser("edfa", help="Kelola kalkulasi saturasi penguat optik EDFA (list, add)")
    edfa_parser.add_argument("--action", choices=["list", "add"], default="list", help="Tindakan penguat EDFA")
    edfa_parser.add_argument("--name", help="Nama perangkat penguat optik")
    edfa_parser.add_argument("--pin", type=float, help="Daya sinyal optik masukan (dBm)")
    edfa_parser.add_argument("--pump", type=float, help="Daya laser pompa pump 980/1480nm (mW)")
    edfa_parser.add_argument("--gain", type=float, help="Penguatan sinyal kecil small-signal gain (dB)")
    edfa_parser.add_argument("--limit", type=int, default=50, help="Batas jumlah rekaman ditampilkan")
    edfa_parser.set_defaults(func=cmd_edfa)

    # OTDR command
    otdr_parser = subparsers.add_parser("otdr", help="Kelola kalkulasi redaman & trace serat optik OTDR (list, add)")
    otdr_parser.add_argument("--action", choices=["list", "add"], default="list", help="Tindakan evaluasi OTDR")
    otdr_parser.add_argument("--name", help="Nama ruas kabel serat optik")
    otdr_parser.add_argument("--length", type=float, help="Panjang bentang kabel optik (km)")
    otdr_parser.add_argument("--loss", type=float, help="Total rugi redaman link optik (dB)")
    otdr_parser.add_argument("--splices", type=int, default=4, help="Jumlah sambungan fusion splice")
    otdr_parser.add_argument("--conn", type=int, default=2, help="Jumlah konektor optik")
    otdr_parser.add_argument("--wl", type=int, default=1550, help="Panjang gelombang uji (nm)")
    otdr_parser.add_argument("--limit", type=int, default=50, help="Batas jumlah rekaman ditampilkan")
    otdr_parser.set_defaults(func=cmd_otdr)

    # MIMO command
    mimo_parser = subparsers.add_parser("mimo", help="Kelola kalkulasi kapasitas kanal antena MIMO (list, add)")
    mimo_parser.add_argument("--action", choices=["list", "add"], default="list", help="Tindakan kapasitas MIMO")
    mimo_parser.add_argument("--channel", help="Nama kanal / link wireless MIMO")
    mimo_parser.add_argument("--bw", type=float, help="Lebar pita frekuensi (MHz)")
    mimo_parser.add_argument("--snr", type=float, help="Signal-to-Noise Ratio kanal (dB)")
    mimo_parser.add_argument("--tx", type=int, default=4, help="Jumlah antena pemancar (Tx)")
    mimo_parser.add_argument("--rx", type=int, default=4, help="Jumlah antena penerima (Rx)")
    mimo_parser.add_argument("--limit", type=int, default=50, help="Batas jumlah rekaman ditampilkan")
    mimo_parser.set_defaults(func=cmd_mimo)

    # IISMA command
    iisma_parser = subparsers.add_parser("iisma", help="Kelola evaluasi & rekognisi SKS program IISMA MBKM (list, add)")
    iisma_parser.add_argument("--action", choices=["list", "add"], default="list", help="Tindakan rekognisi IISMA")
    iisma_parser.add_argument("--name", help="Nama lengkap mahasiswa awardee")
    iisma_parser.add_argument("--nim", help="Nomor Induk Mahasiswa")
    iisma_parser.add_argument("--host", help="Nama universitas mitra luar negeri")
    iisma_parser.add_argument("--country", help="Negara universitas tujuan")
    iisma_parser.add_argument("--gpa", type=float, help="IPK kumulatif host university (skala 4.0)")
    iisma_parser.add_argument("--credits", type=int, help="Jumlah kredit / ECTS yang diselesaikan")
    iisma_parser.add_argument("--limit", type=int, default=50, help="Batas jumlah rekaman ditampilkan")
    iisma_parser.set_defaults(func=cmd_iisma)

    # FSPL command
    fspl_parser = subparsers.add_parser("fspl", help="Kelola kalkulasi link budget nirkabel FSPL (list, add)")
    fspl_parser.add_argument("--action", choices=["list", "add"], default="list", help="Tindakan link budget FSPL")
    fspl_parser.add_argument("--name", help="Nama link / hop wireless")
    fspl_parser.add_argument("--freq", type=float, help="Frekuensi operasi gelombang (MHz)")
    fspl_parser.add_argument("--distance", type=float, help="Jarak lintasan propagasi (km)")
    fspl_parser.add_argument("--tx", type=float, default=20.0, help="Daya pancar pemancar (dBm)")
    fspl_parser.add_argument("--gtx", type=float, default=14.0, help="Gain antena pemancar (dBi)")
    fspl_parser.add_argument("--grx", type=float, default=14.0, help="Gain antena penerima (dBi)")
    fspl_parser.add_argument("--limit", type=int, default=50, help="Batas jumlah rekaman ditampilkan")
    fspl_parser.set_defaults(func=cmd_fspl)

    # Dispersion command
    disp_parser = subparsers.add_parser("dispersion", help="Kelola kalkulasi dispersi kromatik serat optik (list, add)")
    disp_parser.add_argument("--action", choices=["list", "add"], default="list", help="Tindakan dispersi serat optik")
    disp_parser.add_argument("--name", help="Nama link kabel serat optik")
    disp_parser.add_argument("--length", type=float, help="Panjang ruas serat optik (km)")
    disp_parser.add_argument("--disp", type=float, help="Parameter dispersi kromatik D (ps/(nm*km))")
    disp_parser.add_argument("--sw", type=float, default=0.1, help="Lebar spektral sumber optik (nm)")
    disp_parser.add_argument("--rate", type=float, default=10.0, help="Laju bit sinyal modulasi (Gbps)")
    disp_parser.add_argument("--limit", type=int, default=50, help="Batas jumlah rekaman ditampilkan")
    disp_parser.set_defaults(func=cmd_dispersion)

    # Kemanusiaan command
    kemanusiaan_parser = subparsers.add_parser("kemanusiaan", help="Kelola evaluasi & rekognisi MBKM Proyek Kemanusiaan (list, add)")
    kemanusiaan_parser.add_argument("--action", choices=["list", "add"], default="list", help="Tindakan rekognisi Kemanusiaan")
    kemanusiaan_parser.add_argument("--name", help="Nama lengkap mahasiswa relawan")
    kemanusiaan_parser.add_argument("--nim", help="Nomor Induk Mahasiswa")
    kemanusiaan_parser.add_argument("--org", help="Nama organisasi mitra / BPBD")
    kemanusiaan_parser.add_argument("--loc", help="Lokasi wilayah penugasan kemanusiaan")
    kemanusiaan_parser.add_argument("--hours", type=int, default=400, help="Total jam aktivitas lapangan")
    kemanusiaan_parser.add_argument("--mentor", type=float, default=85.0, help="Nilai pembimbing akademik (0-100)")
    kemanusiaan_parser.add_argument("--field", type=float, default=85.0, help="Nilai supervisor lapangan (0-100)")
    kemanusiaan_parser.add_argument("--limit", type=int, default=50, help="Batas jumlah rekaman ditampilkan")
    kemanusiaan_parser.set_defaults(func=cmd_kemanusiaan)

    # PMD command
    pmd_parser = subparsers.add_parser("pmd", help="Kelola kalkulasi dispersi mode polarisasi PMD serat optik (list, add)")
    pmd_parser.add_argument("--action", choices=["list", "add"], default="list", help="Tindakan evaluasi PMD")
    pmd_parser.add_argument("--name", help="Nama link kabel serat optik")
    pmd_parser.add_argument("--length", type=float, help="Panjang bentang kabel optik (km)")
    pmd_parser.add_argument("--coeff", type=float, help="Koefisien PMD serat optik (ps/sqrt(km))")
    pmd_parser.add_argument("--rate", type=float, default=10.0, help="Laju bit transmisi sinyal (Gbps)")
    pmd_parser.add_argument("--limit", type=int, default=50, help="Batas jumlah rekaman ditampilkan")
    pmd_parser.set_defaults(func=cmd_pmd)

    # COST231 command
    cost231_parser = subparsers.add_parser("cost231", help="Kelola kalkulasi rugi propagasi seluler COST 231 Hata (list, add)")
    cost231_parser.add_argument("--action", choices=["list", "add"], default="list", help="Tindakan propagasi COST231")
    cost231_parser.add_argument("--area", help="Nama area jangkauan seluler")
    cost231_parser.add_argument("--freq", type=float, help="Frekuensi radio seluler (MHz)")
    cost231_parser.add_argument("--distance", type=float, help="Jarak ponsel dari BTS (km)")
    cost231_parser.add_argument("--hb", type=float, default=30.0, help="Tinggi efektif antena pemancar BTS (m)")
    cost231_parser.add_argument("--hm", type=float, default=1.5, help="Tinggi antena perangkat mobile penerima (m)")
    cost231_parser.add_argument("--metro", action="store_true", help="Set true jika lingkungan metropolitan kota besar")
    cost231_parser.add_argument("--limit", type=int, default=50, help="Batas jumlah rekaman ditampilkan")
    cost231_parser.set_defaults(func=cmd_cost231)

    # Independen command
    indep_parser = subparsers.add_parser("independen", help="Kelola evaluasi & rekognisi MBKM Studi Independen (list, add)")
    indep_parser.add_argument("--action", choices=["list", "add"], default="list", help="Tindakan rekognisi SIB")
    indep_parser.add_argument("--name", help="Nama lengkap mahasiswa peserta SIB")
    indep_parser.add_argument("--nim", help="Nomor Induk Mahasiswa")
    indep_parser.add_argument("--partner", help="Nama mitra industri / penyelenggara SIB")
    indep_parser.add_argument("--track", default="AI & Cloud Engineering", help="Jalur kompetensi program SIB")
    indep_parser.add_argument("--hours", type=int, default=400, help="Total jam aktivitas pembelajaran")
    indep_parser.add_argument("--mentor", type=float, default=85.0, help="Nilai evaluasi mentor industri (0-100)")
    indep_parser.add_argument("--project", type=float, default=85.0, help="Nilai proyek teknis milestone (0-100)")
    indep_parser.add_argument("--defense", type=float, default=85.0, help="Nilai sidang capstone defense (0-100)")
    indep_parser.add_argument("--limit", type=int, default=50, help="Batas jumlah rekaman ditampilkan")
    indep_parser.set_defaults(func=cmd_independen)

    # FWM command
    fwm_parser = subparsers.add_parser("fwm", help="Kelola kalkulasi efisiensi FWM dan nonlinear optics DWDM (list, add)")
    fwm_parser.add_argument("--action", choices=["list", "add"], default="list", help="Tindakan evaluasi FWM")
    fwm_parser.add_argument("--spacing", type=float, help="Spasi frekuensi antarkanal DWDM (GHz)")
    fwm_parser.add_argument("--length", type=float, help="Panjang bentang serat optik (km)")
    fwm_parser.add_argument("--disp", type=float, help="Dispersi kromatik D (ps/(nm*km))")
    fwm_parser.add_argument("--slope", type=float, default=0.08, help="Kemiringan dispersi slope S (ps/(nm^2*km))")
    fwm_parser.add_argument("--att", type=float, default=0.2, help="Koefisien redaman serat optik (dB/km)")
    fwm_parser.add_argument("--pwr", type=float, default=0.0, help="Daya optik kanal masuk (dBm)")
    fwm_parser.add_argument("--limit", type=int, default=50, help="Batas jumlah rekaman ditampilkan")
    fwm_parser.set_defaults(func=cmd_fwm)

    # Erlang command
    erlang_parser = subparsers.add_parser("erlang", help="Kelola kalkulasi trafik seluler Erlang-B/C trunking (list, add)")
    erlang_parser.add_argument("--action", choices=["list", "add"], default="list", help="Tindakan trafik Erlang")
    erlang_parser.add_argument("--traffic", type=float, help="Intensitas trafik panggilan ditawarkan (Erlang)")
    erlang_parser.add_argument("--channels", type=int, help="Jumlah kanal trafik trunking (c)")
    erlang_parser.add_argument("--holding", type=float, default=120.0, help="Rata-rata waktu holding panggilan (detik)")
    erlang_parser.add_argument("--limit", type=int, default=50, help="Batas jumlah rekaman ditampilkan")
    erlang_parser.set_defaults(func=cmd_erlang)

    # PIMNAS / PKM command
    pimnas_parser = subparsers.add_parser("pimnas", help="Kelola evaluasi & rekognisi MBKM PKM dan PIMNAS (list, add)")
    pimnas_parser.add_argument("--action", choices=["list", "add"], default="list", help="Tindakan rekognisi PKM/PIMNAS")
    pimnas_parser.add_argument("--name", help="Nama lengkap mahasiswa peserta PKM")
    pimnas_parser.add_argument("--nim", help="Nomor Induk Mahasiswa")
    pimnas_parser.add_argument("--scheme", default="PKM-KC", help="Skema PKM (PKM-KC, PKM-RE, dll)")
    pimnas_parser.add_argument("--title", default="Inovasi Perangkat Nirkabel Cerdas", help="Judul proposal PKM")
    pimnas_parser.add_argument("--pimnas", action="store_true", help="Set true jika lolos ke tahap PIMNAS nasional")
    pimnas_parser.add_argument("--medal", default="", help="Medali yang diraih di PIMNAS (Emas/Perak/Perunggu)")
    pimnas_parser.add_argument("--proposal", type=float, default=85.0, help="Nilai proposal (0-100)")
    pimnas_parser.add_argument("--progress", type=float, default=85.0, help="Nilai kemajuan PKP2 (0-100)")
    pimnas_parser.add_argument("--presentation", type=float, default=85.0, help="Nilai presentasi akhir (0-100)")
    pimnas_parser.add_argument("--limit", type=int, default=50, help="Batas jumlah rekaman ditampilkan")
    pimnas_parser.set_defaults(func=cmd_pimnas)

    # XPM command
    xpm_parser = subparsers.add_parser("xpm", help="Kelola kalkulasi pergeseran fase nonlinier XPM serat optik (list, add)")
    xpm_parser.add_argument("--action", choices=["list", "add"], default="list", help="Tindakan evaluasi XPM")
    xpm_parser.add_argument("--pump", type=float, help="Daya optik kanal pompa (mW)")
    xpm_parser.add_argument("--probe", type=float, help="Daya optik kanal probe (mW)")
    xpm_parser.add_argument("--length", type=float, help="Panjang bentang serat optik (km)")
    xpm_parser.add_argument("--att", type=float, default=0.2, help="Koefisien redaman serat optik (dB/km)")
    xpm_parser.add_argument("--limit", type=int, default=50, help="Batas jumlah rekaman ditampilkan")
    xpm_parser.set_defaults(func=cmd_xpm)

    # Numerology command
    num_parser = subparsers.add_parser("numerology", help="Kelola konfigurasi numerologi dan timing 5G NR 3GPP (list, add)")
    num_parser.add_argument("--action", choices=["list", "add"], default="list", help="Tindakan numerologi 5G")
    num_parser.add_argument("--mu", type=int, choices=[0, 1, 2, 3, 4], help="Indeks numerologi mu (0-4)")
    num_parser.add_argument("--band", default="n78 Mid-Band", help="Nama pita kanal frekuensi 5G NR")
    num_parser.add_argument("--rb", type=int, default=100, help="Jumlah alokasi Resource Block (RB)")
    num_parser.add_argument("--limit", type=int, default=50, help="Batas jumlah rekaman ditampilkan")
    num_parser.set_defaults(func=cmd_numerology)

    # PMM command
    pmm_parser = subparsers.add_parser("pmm", help="Kelola evaluasi & rekognisi MBKM Pertukaran Mahasiswa Merdeka (list, add)")
    pmm_parser.add_argument("--action", choices=["list", "add"], default="list", help="Tindakan rekognisi PMM")
    pmm_parser.add_argument("--name", help="Nama lengkap mahasiswa peserta PMM")
    pmm_parser.add_argument("--nim", help="Nomor Induk Mahasiswa")
    pmm_parser.add_argument("--host", help="Nama perguruan tinggi mitra (host)")
    pmm_parser.add_argument("--nusantara", type=float, default=85.0, help="Nilai modul nusantara (0-100)")
    pmm_parser.add_argument("--academic", type=float, default=85.0, help="Nilai mata kuliah akademik host (0-100)")
    pmm_parser.add_argument("--mentor", type=float, default=85.0, help="Nilai mentor host (0-100)")
    pmm_parser.add_argument("--limit", type=int, default=50, help="Batas jumlah rekaman ditampilkan")
    pmm_parser.set_defaults(func=cmd_pmm)

    # SRS command
    srs_parser = subparsers.add_parser("srs", help="Kelola evaluasi ambang batas hamburan Raman terstimulasi (SRS) serat optik (list, add)")
    srs_parser.add_argument("--action", choices=["list", "add"], default="list", help="Tindakan evaluasi SRS")
    srs_parser.add_argument("--fiber", default="Standard SMF-28", help="Tipe serat optik")
    srs_parser.add_argument("--length", type=float, help="Panjang bentang serat optik (km)")
    srs_parser.add_argument("--power", type=float, default=100.0, help="Daya optik kanal masukan (mW)")
    srs_parser.add_argument("--att", type=float, default=0.2, help="Koefisien atenuasi serat optik (dB/km)")
    srs_parser.add_argument("--area", type=float, default=80.0, help="Luas efektif serat optik (um^2)")
    srs_parser.add_argument("--limit", type=int, default=50, help="Batas jumlah rekaman ditampilkan")
    srs_parser.set_defaults(func=cmd_srs)

    # EIRP command
    eirp_parser = subparsers.add_parser("eirp", help="Kelola kepatuhan daya radiasi isotropik efektif (EIRP) 5G NR (list, add)")
    eirp_parser.add_argument("--action", choices=["list", "add"], default="list", help="Tindakan evaluasi EIRP 5G")
    eirp_parser.add_argument("--cell", default="NR-CELL-BDG-01", help="Pengenal sel transceiver 5G NR")
    eirp_parser.add_argument("--power", type=float, help="Daya konduksi pemancar conducted power (dBm)")
    eirp_parser.add_argument("--gain", type=float, help="Penguatan antena transmitter gain (dBi)")
    eirp_parser.add_argument("--loss", type=float, default=2.0, help="Rugi-rugi kabel dan combiner (dB)")
    eirp_parser.add_argument("--bw", type=float, default=20.0, help="Lebar pita saluran channel bandwidth (MHz)")
    eirp_parser.add_argument("--limit", type=int, default=50, help="Batas jumlah rekaman ditampilkan")
    eirp_parser.set_defaults(func=cmd_eirp)

    # Praktisi Mengajar command
    praktisi_parser = subparsers.add_parser("praktisi", help="Kelola kolaborasi industri & rekognisi MBKM Praktisi Mengajar (list, add)")
    praktisi_parser.add_argument("--action", choices=["list", "add"], default="list", help="Tindakan rekognisi Praktisi Mengajar")
    praktisi_parser.add_argument("--course", help="Nama mata kuliah kolaborasi praktisi")
    praktisi_parser.add_argument("--code", help="Kode mata kuliah (misal TT3104)")
    praktisi_parser.add_argument("--practitioner", help="Nama praktisi industri pengampu")
    praktisi_parser.add_argument("--company", help="Nama perusahaan / industri mitra")
    praktisi_parser.add_argument("--lecturer", default="Dosen Pengampu", help="Nama dosen pendamping mata kuliah")
    praktisi_parser.add_argument("--hours", type=int, default=12, help="Jumlah jam tatap muka praktisi")
    praktisi_parser.add_argument("--case", type=float, default=85.0, help="Nilai studi kasus riil industri (0-100)")
    praktisi_parser.add_argument("--assessment", type=float, default=85.0, help="Nilai asesmen kompetensi praktisi (0-100)")
    praktisi_parser.add_argument("--student", type=float, default=85.0, help="Nilai kuesioner evaluasi mahasiswa (0-100)")
    praktisi_parser.add_argument("--limit", type=int, default=50, help="Batas jumlah rekaman ditampilkan")
    praktisi_parser.set_defaults(func=cmd_praktisi)


    args = parser.parse_args()










    args.func(args)



if __name__ == "__main__":
    main()
