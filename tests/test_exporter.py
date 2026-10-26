import unittest
import json
from exporter import ArticleExporter

class TestArticleExporter(unittest.TestCase):
    def test_elementor_json_structure(self):
        result = ArticleExporter.to_elementor_json(
            title="Judul Riset",
            html_content="<div class='tu-editorial-container'><p>Konten</p></div>"
        )
        self.assertEqual(result["version"], "0.4")
        self.assertEqual(result["type"], "section")
        self.assertEqual(len(result["content"]), 1)
        widget = result["content"][0]["elements"][0]["elements"][0]
        self.assertEqual(widget["widgetType"], "html")
        self.assertIn("tu-editorial-container", widget["settings"]["html"])

    def test_markdown_frontmatter_generation(self):
        meta = {
            "seo_title": "SEO Title Test",
            "focus_keyphrase": "keyphrase test",
            "slug": "slug-test",
            "meta_description": "Description test 123",
            "category": "Cloud",
            "publish_date": "2026-09-28"
        }
        md = ArticleExporter.to_markdown_with_frontmatter(meta, "<p>Hello</p>")
        self.assertTrue(md.startswith("---"))
        self.assertIn("focus_keyphrase: \"keyphrase test\"", md)
        self.assertIn("<p>Hello</p>", md)

    def test_to_html_document(self):
        meta = {
            "seo_title": "Standalone Doc Title",
            "meta_description": "Standalone meta description.",
            "slug": "standalone-slug"
        }
        doc = ArticleExporter.to_html_document(meta, "<div class='tu-editorial-container'>Body</div>")
        self.assertIn("<!DOCTYPE html>", doc)
        self.assertIn("<title>Standalone Doc Title</title>", doc)
        self.assertIn('property="og:title" content="Standalone Doc Title"', doc)
        self.assertIn("standalone-slug", doc)

    def test_export_bundle(self):
        import tempfile
        from pathlib import Path
        meta = {
            "seo_title": "Bundle Title",
            "meta_description": "Bundle description.",
            "slug": "bundle-slug"
        }
        with tempfile.TemporaryDirectory() as tmp_dir:
            out_dir = Path(tmp_dir)
            paths = ArticleExporter.export_bundle(out_dir, "bundle-slug", meta, "<p>Bundle Content</p>")
            self.assertTrue(paths["html"].exists())
            self.assertTrue(paths["standalone_html"].exists())
            self.assertTrue(paths["markdown"].exists())
            self.assertTrue(paths["elementor_json"].exists())

    def test_generate_json_ld(self):
        import json
        meta = {
            "seo_title": "IoT Smart Campus Telkom",
            "meta_description": "Implementasi sensor cerdas di Purwokerto.",
            "slug": "iot-smart-campus-telkom",
            "publish_date": "2026-09-30",
            "image_url": "https://example.com/banner.jpg"
        }
        json_ld_str = ArticleExporter.generate_json_ld(meta, article_type="ScholarlyArticle")
        data = json.loads(json_ld_str)
        self.assertEqual(data["@context"], "https://schema.org")
        self.assertEqual(data["@type"], "ScholarlyArticle")
        self.assertEqual(data["headline"], "IoT Smart Campus Telkom")
        self.assertIn("https://bif-pwt.telkomuniversity.ac.id/iot-smart-campus-telkom/", data["mainEntityOfPage"]["@id"])
        self.assertEqual(data["image"], ["https://example.com/banner.jpg"])

    def test_generate_rss_feed(self):
        articles = [
            {
                "seo_title": "Riset Wasm & Edge Computing",
                "slug": "riset-wasm-edge",
                "meta_description": "Ulasan performa Wasm di node IoT.",
                "publish_date": "Wed, 30 Sep 2026 12:00:00 +0700",
                "category": "Cloud"
            }
        ]
        rss_xml = ArticleExporter.generate_rss_feed(articles, {
            "title": "Kanal Berita & Riset",
            "link": "https://bif-pwt.telkomuniversity.ac.id"
        })
        self.assertIn('<?xml version="1.0" encoding="UTF-8"?>', rss_xml)
        self.assertIn('<rss version="2.0">', rss_xml)
        self.assertIn('<title>Kanal Berita &amp; Riset</title>', rss_xml)
        self.assertIn('<title>Riset Wasm &amp; Edge Computing</title>', rss_xml)
        self.assertIn('<link>https://bif-pwt.telkomuniversity.ac.id/riset-wasm-edge/</link>', rss_xml)
        self.assertIn('<category>Cloud</category>', rss_xml)

    def test_generate_sitemap_xml(self):
        articles = [
            {"slug": "webassembly-edge", "publish_date": "2026-09-28"},
            {"slug": "ai-kampus-cerdas", "publish_date": "2026-09-29"}
        ]
        sitemap = ArticleExporter.generate_sitemap_xml(articles, base_url="https://bif-pwt.telkomuniversity.ac.id")
        self.assertIn('<?xml version="1.0" encoding="UTF-8"?>', sitemap)
        self.assertIn('<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">', sitemap)
        self.assertIn('<loc>https://bif-pwt.telkomuniversity.ac.id/</loc>', sitemap)
        self.assertIn('<loc>https://bif-pwt.telkomuniversity.ac.id/webassembly-edge/</loc>', sitemap)
        self.assertIn('<lastmod>2026-09-28</lastmod>', sitemap)
        self.assertIn('<loc>https://bif-pwt.telkomuniversity.ac.id/ai-kampus-cerdas/</loc>', sitemap)

    def test_generate_social_meta_tags(self):
        meta = {
            "seo_title": "Tutorial WebAssembly Edge",
            "meta_description": "Panduan komputasi edge berlatensi rendah.",
            "image_url": "https://example.com/banner.png"
        }
        tags = ArticleExporter.generate_social_meta_tags(meta, canonical_url="https://example.com/tutorial")
        self.assertIn('property="og:type" content="article"', tags)
        self.assertIn('property="og:title" content="Tutorial WebAssembly Edge"', tags)
        self.assertIn('name="twitter:card" content="summary_large_image"', tags)
        self.assertIn('property="og:image" content="https://example.com/banner.png"', tags)
        self.assertIn('property="og:url" content="https://example.com/tutorial"', tags)

    def test_generate_breadcrumb_schema(self):
        crumbs = [
            {"name": "Beranda", "url": "https://bif-pwt.telkomuniversity.ac.id"},
            {"name": "Riset", "url": "https://bif-pwt.telkomuniversity.ac.id/riset"},
            {"name": "WebAssembly Edge", "url": "https://bif-pwt.telkomuniversity.ac.id/riset/wasm"}
        ]
        schema = ArticleExporter.generate_breadcrumb_schema(crumbs)
        self.assertEqual(schema["@type"], "BreadcrumbList")
        self.assertEqual(len(schema["itemListElement"]), 3)
        self.assertEqual(schema["itemListElement"][0]["position"], 1)
        self.assertEqual(schema["itemListElement"][0]["name"], "Beranda")
        self.assertEqual(schema["itemListElement"][2]["name"], "WebAssembly Edge")

    def test_generate_atom_feed(self):
        articles = [
            {
                "slug": "riset-edge-ai",
                "seo_title": "Riset Edge AI Terapan",
                "meta_description": "Deskripsi riset edge ai terbaru.",
                "publish_date": "2026-10-01"
            }
        ]
        info = {
            "title": "Kanal Riset Telkom University Purwokerto",
            "base_url": "https://bif-pwt.telkomuniversity.ac.id"
        }
        atom_xml = ArticleExporter.generate_atom_feed(articles, info)
        self.assertIn('<feed xmlns="http://www.w3.org/2005/Atom">', atom_xml)
        self.assertIn('<title>Kanal Riset Telkom University Purwokerto</title>', atom_xml)
        self.assertIn('<id>https://bif-pwt.telkomuniversity.ac.id/riset-edge-ai/</id>', atom_xml)
        self.assertIn('Riset Edge AI Terapan', atom_xml)

    def test_generate_json_feed(self):
        articles = [
            {
                "slug": "berita-pmb",
                "seo_title": "Pendaftaran Mahasiswa Baru 2026",
                "meta_description": "Informasi jalur seleksi PMB.",
                "publish_date": "2026-10-01"
            }
        ]
        info = {
            "title": "Warta PMB Prodi",
            "base_url": "https://bif-pwt.telkomuniversity.ac.id"
        }
        feed_json_str = ArticleExporter.generate_json_feed(articles, info)
        feed_data = json.loads(feed_json_str)
        self.assertEqual(feed_data["version"], "https://jsonfeed.org/version/1.1")
        self.assertEqual(feed_data["title"], "Warta PMB Prodi")
        self.assertEqual(len(feed_data["items"]), 1)
        self.assertEqual(feed_data["items"][0]["title"], "Pendaftaran Mahasiswa Baru 2026")

    def test_to_plain_text(self):
        html = '<div class="tu-editorial-container"><h2>Judul Penting</h2><p>Paragraf <strong>pertama</strong> dengan tautan <a href="#">klik</a>.</p><p>Paragraf kedua.</p></div>'
        plain = ArticleExporter.to_plain_text(html)
        self.assertNotIn("<h2>", plain)
        self.assertNotIn("<p>", plain)
        self.assertIn("Judul Penting", plain)
        self.assertIn("Paragraf pertama dengan tautan klik.", plain)
        self.assertIn("Paragraf kedua.", plain)

    def test_to_hugo_markdown(self):
        meta = {
            "seo_title": "Tutorial Hugo Static Site",
            "meta_description": "Cara membuat blog dengan Hugo.",
            "slug": "tutorial-hugo-static",
            "category": "Web Dev",
            "publish_date": "2026-10-03",
            "tags": ["hugo", "golang", "web"]
        }
        hugo_doc = ArticleExporter.to_hugo_markdown(meta, "<p>Halo Dunia</p>")
        self.assertTrue(hugo_doc.startswith("---"))
        self.assertIn('title: "Tutorial Hugo Static Site"', hugo_doc)
        self.assertIn('slug: "tutorial-hugo-static"', hugo_doc)
        self.assertIn('"hugo"', hugo_doc)
        self.assertIn("<p>Halo Dunia</p>", hugo_doc)

    def test_generate_course_json_ld(self):
        course = {
            "name": "Kecerdasan Buatan Terapan",
            "course_code": "CS-301",
            "description": "Pengantar machine learning dan neural networks.",
            "credits": 3,
            "prerequisites": "Struktur Data & Algoritma"
        }
        json_ld = ArticleExporter.generate_course_json_ld(course)
        self.assertIn('<script type="application/ld+json">', json_ld)
        self.assertIn('"@type": "Course"', json_ld)
        self.assertIn('"courseCode": "CS-301"', json_ld)
        self.assertIn('"numberOfCredits": 3', json_ld)
        self.assertIn("Telkom University Purwokerto", json_ld)

    def test_to_mdx_astro_and_docusaurus(self):
        meta = {
            "seo_title": "Dokumentasi API Prodi",
            "meta_description": "Panduan integrasi sistem informasi.",
            "slug": "api-docs",
            "tags": ["api", "rest", "python"]
        }
        astro_mdx = ArticleExporter.to_mdx(meta, "<p>Isi MDX</p>", framework="astro")
        self.assertIn('pubDate:', astro_mdx)
        self.assertIn('"api"', astro_mdx)
        self.assertIn("<p>Isi MDX</p>", astro_mdx)

        docusaurus_mdx = ArticleExporter.to_mdx(meta, "<p>Isi MDX</p>", framework="docusaurus")
        self.assertIn('slug: /api-docs', docusaurus_mdx)
        self.assertIn('authors: [editorial_team]', docusaurus_mdx)

    def test_generate_enhanced_social_meta(self):
        meta = {
            "seo_title": "Riset Quantum Computing",
            "meta_description": "Eksplorasi algoritma Shor dan Grover.",
            "slug": "riset-quantum",
            "image_url": "https://example.com/quantum.png",
            "publish_date": "2026-10-05T08:00:00Z"
        }
        tags = ArticleExporter.generate_enhanced_social_meta(meta, image_dimensions=(1200, 630))
        self.assertIn('property="og:locale" content="id_ID"', tags)
        self.assertIn('property="og:title" content="Riset Quantum Computing"', tags)
        self.assertIn('property="og:image:width" content="1200"', tags)
        self.assertIn('property="og:image:height" content="630"', tags)
        self.assertIn('name="twitter:card" content="summary_large_image"', tags)

    def test_generate_program_json_ld(self):
        schema = ArticleExporter.generate_program_json_ld()
        self.assertEqual(schema["@type"], "EducationalOccupationalProgram")
        self.assertEqual(schema["name"], "S1 Teknik Informatika")
        self.assertEqual(schema["timeToComplete"], "P4Y")
        self.assertEqual(schema["provider"]["name"], "Telkom University Purwokerto")
        self.assertEqual(schema["educationalCredentialAwarded"], "Sarjana Komputer (S.Kom.)")

    def test_to_nextjs_mdx(self):
        meta = {
            "seo_title": "Belajar Next.js App Router",
            "meta_description": "Panduan server components.",
            "slug": "nextjs-app-router",
            "publish_date": "2026-10-06",
            "tags": ["react", "nextjs"]
        }
        mdx = ArticleExporter.to_nextjs_mdx(meta, "<p>Konten Next.js</p>")
        self.assertIn('export const metadata = {', mdx)
        self.assertIn('title: "Belajar Next.js App Router"', mdx)
        self.assertIn('slug: "nextjs-app-router"', mdx)
        self.assertIn('<p>Konten Next.js</p>', mdx)

    def test_generate_research_project_json_ld(self):
        schema = ArticleExporter.generate_research_project_json_ld(
            name="Sistem IoT Pertanian Cerdas",
            description="Pengembangan sensor kelembapan tanah berbasis LoRaWAN.",
            funder="Kemendikbudristek",
            award_amount="Rp 120.000.000",
            lead_investigator="Dr. Ir. Hendra"
        )
        self.assertEqual(schema["@type"], "ResearchProject")
        self.assertEqual(schema["name"], "Sistem IoT Pertanian Cerdas")
        self.assertEqual(schema["funder"]["name"], "Kemendikbudristek")
        self.assertEqual(schema["funding"]["amount"], "Rp 120.000.000")
        self.assertEqual(schema["employee"]["name"], "Dr. Ir. Hendra")

    def test_to_nuxt_markdown(self):
        meta = {
            "seo_title": "Panduan Nuxt Content 2",
            "meta_description": "Dokumentasi headless CMS.",
            "slug": "panduan-nuxt-content",
            "category": "Frontend",
            "tags": ["vue", "nuxt"]
        }
        md = ArticleExporter.to_nuxt_markdown(meta, "<p>Isi Nuxt</p>")
        self.assertTrue(md.startswith("---"))
        self.assertIn('title: "Panduan Nuxt Content 2"', md)
        self.assertIn('category: "Frontend"', md)
        self.assertIn('- vue', md)
        self.assertIn('<p>Isi Nuxt</p>', md)

    def test_generate_academic_event_json_ld(self):
        schema = ArticleExporter.generate_academic_event_json_ld(
            event_name="Seminar Nasional Kecerdasan Buatan & Big Data 2026",
            description="Seminar eksplorasi masa depan LLM di era otonom.",
            start_time="2026-11-20T09:00:00+07:00",
            end_time="2026-11-20T16:00:00+07:00",
            location_name="Auditorium Gedung IOT Lantai 4",
            speaker_name="Prof. Dr. Wisnu Jatmiko"
        )
        self.assertEqual(schema["@type"], "EducationEvent")
        self.assertEqual(schema["name"], "Seminar Nasional Kecerdasan Buatan & Big Data 2026")
        self.assertEqual(schema["startDate"], "2026-11-20T09:00:00+07:00")
        self.assertEqual(schema["location"]["name"], "Auditorium Gedung IOT Lantai 4")
        self.assertEqual(schema["performer"]["name"], "Prof. Dr. Wisnu Jatmiko")

    def test_to_sveltekit_markdown(self):
        meta = {
            "seo_title": "Implementasi SvelteKit 2",
            "meta_description": "Tutorial arsitektur web modern.",
            "slug": "implementasi-sveltekit-2",
            "category": "Web Dev",
            "tags": ["svelte", "sveltekit"]
        }
        res = ArticleExporter.to_sveltekit_markdown(meta, "<p>Konten SvelteKit</p>")
        self.assertTrue(res.startswith("---"))
        self.assertIn('title: "Implementasi SvelteKit 2"', res)
        self.assertIn('slug: "implementasi-sveltekit-2"', res)
        self.assertIn('"svelte"', res)
        self.assertIn("layout: article", res)
        self.assertIn("<p>Konten SvelteKit</p>", res)

    def test_generate_university_organization_json_ld(self):
        schema = ArticleExporter.generate_university_organization_json_ld(
            name="Telkom University Purwokerto",
            url="https://bif-pwt.telkomuniversity.ac.id",
            faculty_name="Fakultas Informatika",
            accreditation="Unggul"
        )
        self.assertEqual(schema["@type"], "CollegeOrUniversity")
        self.assertEqual(schema["name"], "Telkom University Purwokerto")
        self.assertEqual(schema["department"]["name"], "Fakultas Informatika")
        self.assertEqual(schema["hasCredential"]["name"], "Unggul")
        self.assertEqual(schema["address"]["addressLocality"], "Purwokerto")

    def test_to_eleventy_markdown(self):
        meta = {
            "seo_title": "Panduan Eleventy SSG",
            "meta_description": "Static site generator cepat dan fleksibel.",
            "slug": "panduan-eleventy-ssg",
            "publish_date": "2026-10-08",
            "tags": ["11ty", "ssg", "jamstack"]
        }
        res = ArticleExporter.to_eleventy_markdown(meta, "<p>Konten 11ty Eleventy</p>")
        self.assertTrue(res.startswith("---"))
        self.assertIn('layout: layouts/post.njk', res)
        self.assertIn('title: "Panduan Eleventy SSG"', res)
        self.assertIn('permalink: "/posts/panduan-eleventy-ssg/"', res)
        self.assertIn('- 11ty', res)
        self.assertIn('<p>Konten 11ty Eleventy</p>', res)

    def test_generate_scholarly_article_json_ld(self):
        schema = ArticleExporter.generate_scholarly_article_json_ld(
            title="Optimasi Jaringan 5G Millimeter Wave",
            authors=["Dr. Ir. Hendra", "Fajar Nugraha"],
            abstract="Penelitian ini menganalisis propagasi sinyal pada frekuensi 28 GHz.",
            date_published="2026-10-10",
            doi_url="https://doi.org/10.1109/MW.2026.98765",
            publisher="Telkom University Purwokerto"
        )
        self.assertEqual(schema["@type"], "ScholarlyArticle")
        self.assertEqual(schema["headline"], "Optimasi Jaringan 5G Millimeter Wave")
        self.assertEqual(len(schema["author"]), 2)
        self.assertEqual(schema["author"][0]["name"], "Dr. Ir. Hendra")
        self.assertEqual(schema["publisher"]["name"], "Telkom University Purwokerto")
        self.assertEqual(schema["url"], "https://doi.org/10.1109/MW.2026.98765")

    def test_to_zola_markdown(self):
        meta = {
            "seo_title": "Panduan Rust untuk Pemula",
            "meta_description": "Belajar konsep ownership dan borrowing.",
            "slug": "panduan-rust-pemula",
            "publish_date": "2026-10-10",
            "category": "Pemrograman",
            "tags": ["rust", "systems", "concurrency"]
        }
        res = ArticleExporter.to_zola_markdown(meta, "<p>Halo Dunia Rust</p>")
        self.assertTrue(res.startswith("+++"))
        self.assertIn('title = "Panduan Rust untuk Pemula"', res)
        self.assertIn('date = 2026-10-10', res)
        self.assertIn('slug = "panduan-rust-pemula"', res)
        self.assertIn('[taxonomies]', res)
        self.assertIn('categories = ["Pemrograman"]', res)
        self.assertIn('"rust", "systems", "concurrency"', res)
        self.assertIn("<p>Halo Dunia Rust</p>", res)

    def test_generate_tech_article_json_ld(self):
        schema = ArticleExporter.generate_tech_article_json_ld(
            title="Setup Lab Jaringan SDN Menggunakan Mininet",
            dependencies=["Ubuntu 24.04", "OpenFlow 1.3", "Python 3.12"],
            proficiency_level="Intermediate / Mahasiswa Semester 5",
            content="Langkah instalasi dan konfigurasi kontroler SDN Ryu dengan Mininet.",
            date_published="2026-10-11",
            publisher="Telkom University Purwokerto"
        )
        self.assertEqual(schema["@type"], "TechArticle")
        self.assertEqual(schema["headline"], "Setup Lab Jaringan SDN Menggunakan Mininet")
        self.assertIn("Ubuntu 24.04, OpenFlow 1.3, Python 3.12", schema["dependencies"])
        self.assertEqual(schema["proficiencyLevel"], "Intermediate / Mahasiswa Semester 5")
        self.assertEqual(schema["datePublished"], "2026-10-11")
        self.assertEqual(schema["publisher"]["name"], "Telkom University Purwokerto")

    def test_to_pelican_markdown(self):
        meta = {
            "seo_title": "Tutorial Pemrograman Python 3.12",
            "publish_date": "2026-10-11",
            "category": "Tutorial",
            "tags": ["python", "pemrograman", "pelican"],
            "slug": "tutorial-python-3-12",
            "meta_description": "Panduan dasar sintaks Python 3.12 modern."
        }
        res = ArticleExporter.to_pelican_markdown(meta, "<p>Halo Dunia Python</p>")
        self.assertIn("Title: Tutorial Pemrograman Python 3.12", res)
        self.assertIn("Date: 2026-10-11", res)
        self.assertIn("Category: Tutorial", res)
        self.assertIn("Tags: python, pemrograman, pelican", res)
        self.assertIn("Slug: tutorial-python-3-12", res)
        self.assertIn("Summary: Panduan dasar sintaks Python 3.12 modern.", res)
        self.assertIn("<p>Halo Dunia Python</p>", res)

    def test_generate_dataset_json_ld(self):
        schema = ArticleExporter.generate_dataset_json_ld(
            dataset_name="Banyumas 5G Channel Propagation Trace",
            description="RF channel impulse response and path loss dataset recorded in Banyumas urban area.",
            creator_name="Dr. Aris Triwiyatno",
            license_url="https://creativecommons.org/licenses/by/4.0/",
            keywords=["5G", "path loss", "channel sounding", "telecommunications"],
            download_url="https://repository.telkomuniversity.ac.id/datasets/5g-banyumas.zip",
            publisher_name="Telkom University Purwokerto"
        )
        self.assertEqual(schema["@type"], "Dataset")
        self.assertEqual(schema["name"], "Banyumas 5G Channel Propagation Trace")
        self.assertEqual(schema["creator"]["name"], "Dr. Aris Triwiyatno")
        self.assertEqual(schema["license"], "https://creativecommons.org/licenses/by/4.0/")
        self.assertIn("5G", schema["keywords"])
        self.assertEqual(schema["distribution"][0]["contentUrl"], "https://repository.telkomuniversity.ac.id/datasets/5g-banyumas.zip")
        self.assertEqual(schema["publisher"]["name"], "Telkom University Purwokerto")

    def test_to_docusaurus_markdown(self):
        meta = {
            "seo_title": "Panduan Instalasi LoRa Gateway",
            "topic": "LoRa Gateway",
            "slug": "panduan-lora-gateway",
            "sidebar_label": "Instalasi Gateway",
            "sidebar_position": 3,
            "meta_description": "Langkah setup gateway LoRaWAN The Things Network.",
            "tags": ["lora", "iot", "ttn"]
        }
        res = ArticleExporter.to_docusaurus_markdown(meta, "<p>Hubungkan antena dan power supply.</p>")
        self.assertTrue(res.startswith("---"))
        self.assertIn("id: panduan-lora-gateway", res)
        self.assertIn('title: "Panduan Instalasi LoRa Gateway"', res)
        self.assertIn('sidebar_label: "Instalasi Gateway"', res)
        self.assertIn("sidebar_position: 3", res)
        self.assertIn('description: "Langkah setup gateway LoRaWAN The Things Network."', res)
        self.assertIn('"lora", "iot", "ttn"', res)
        self.assertIn("<p>Hubungkan antena dan power supply.</p>", res)

    def test_generate_special_announcement_json_ld(self):
        schema = ArticleExporter.generate_special_announcement_json_ld(
            title="Pemberitahuan Darurat Pemeliharaan Server Lab",
            text="Server komputasi cloud lab akan offline untuk upgrade switch 10Gbps.",
            date_posted="2026-10-14T08:00:00+07:00",
            expires_date="2026-10-15T18:00:00+07:00",
            category="Academic Advisory",
            publisher="Telkom University Purwokerto"
        )
        self.assertEqual(schema["@type"], "SpecialAnnouncement")
        self.assertEqual(schema["name"], "Pemberitahuan Darurat Pemeliharaan Server Lab")
        self.assertEqual(schema["text"], "Server komputasi cloud lab akan offline untuk upgrade switch 10Gbps.")
        self.assertEqual(schema["datePosted"], "2026-10-14T08:00:00+07:00")
        self.assertEqual(schema["expires"], "2026-10-15T18:00:00+07:00")
        self.assertEqual(schema["category"], "Academic Advisory")
        self.assertEqual(schema["publisher"]["name"], "Telkom University Purwokerto")

    def test_to_mkdocs_markdown(self):
        meta = {
            "seo_title": "Konfigurasi Protokol Routing OSPF di Cisco Packet Tracer",
            "topic": "Routing OSPF",
            "meta_description": "Modul praktikum perutean dinamik OSPF multi-area untuk mahasiswa.",
            "tags": ["jaringan", "cisco", "ospf", "praktikum"]
        }
        res = ArticleExporter.to_mkdocs_markdown(meta, "<p>Buka CLI router dan masukkan perintah router ospf 1.</p>")
        self.assertTrue(res.startswith("---"))
        self.assertIn('title: "Konfigurasi Protokol Routing OSPF di Cisco Packet Tracer"', res)
        self.assertIn('description: "Modul praktikum perutean dinamik OSPF multi-area untuk mahasiswa."', res)
        self.assertIn('"jaringan", "cisco", "ospf", "praktikum"', res)
        self.assertIn("# Konfigurasi Protokol Routing OSPF di Cisco Packet Tracer", res)
        self.assertIn("<p>Buka CLI router dan masukkan perintah router ospf 1.</p>", res)

    def test_generate_credential_json_ld(self):
        schema = ArticleExporter.generate_credential_json_ld(
            credential_name="Sarjana Teknik Telekomunikasi (S.T.)",
            description="Program sarjana teknik telekomunikasi terakreditasi Unggul LAM INFOKOM.",
            credential_category="degree",
            recognized_by="Telkom University Purwokerto",
            educational_level="Bachelor's Degree / Level 6 KKNI"
        )
        self.assertEqual(schema["@type"], "EducationalOccupationalCredential")
        self.assertEqual(schema["name"], "Sarjana Teknik Telekomunikasi (S.T.)")
        self.assertEqual(schema["description"], "Program sarjana teknik telekomunikasi terakreditasi Unggul LAM INFOKOM.")
        self.assertEqual(schema["credentialCategory"], "degree")
        self.assertEqual(schema["educationalLevel"], "Bachelor's Degree / Level 6 KKNI")
        self.assertEqual(schema["recognizedBy"]["name"], "Telkom University Purwokerto")

    def test_to_starlight_markdown(self):
        meta = {
            "seo_title": "Panduan Praktikum Fiber Optik",
            "topic": "Praktikum Fiber Optik",
            "meta_description": "Dokumentasi prosedur splicing kabel fiber optik core tunggal.",
            "sidebar_label": "Modul Fiber Optik",
            "sidebar_order": 2
        }
        res = ArticleExporter.to_starlight_markdown(meta, "<p>Persiapkan alat fusion splicer dan cleaver.</p>")
        self.assertTrue(res.startswith("---"))
        self.assertIn('title: "Panduan Praktikum Fiber Optik"', res)
        self.assertIn('description: "Dokumentasi prosedur splicing kabel fiber optik core tunggal."', res)
        self.assertIn("sidebar:", res)
        self.assertIn('  label: "Modul Fiber Optik"', res)
        self.assertIn("  order: 2", res)
        self.assertIn("<p>Persiapkan alat fusion splicer dan cleaver.</p>", res)

    def test_generate_academic_event_json_ld(self):
        res = ArticleExporter.generate_academic_event_json_ld(
            event_name="IEEE International Conference on Communications 2026",
            description="Konferensi internasional unggulan IEEE bidang teknik komunikasi nirkabel dan telekomunikasi.",
            start_date="2026-06-14",
            end_date="2026-06-18",
            location_name="Palais des congrès de Montréal, Canada",
            core_rank="A",
            organizer="IEEE Communications Society",
            url="https://icc2026.ieee-icc.org"
        )
        self.assertEqual(res["@context"], "https://schema.org")
        self.assertEqual(res["@type"], "Event")
        self.assertEqual(res["name"], "IEEE International Conference on Communications 2026")
        self.assertEqual(res["startDate"], "2026-06-14")
        self.assertEqual(res["endDate"], "2026-06-18")
        self.assertEqual(res["location"]["name"], "Palais des congrès de Montréal, Canada")
        self.assertEqual(res["organizer"]["name"], "IEEE Communications Society")
        self.assertEqual(res["url"], "https://icc2026.ieee-icc.org")
        props = res.get("additionalProperty", [])
        self.assertEqual(len(props), 1)
        self.assertEqual(props[0]["name"], "CORE Rank")
        self.assertEqual(props[0]["value"], "A")

    def test_to_hexo_markdown(self):
        meta = {
            "seo_title": "Panduan Instalasi Antena Parabola",
            "publish_date": "2026-10-15 10:00:00",
            "category": "Tutorial Telekomunikasi",
            "tags": ["Antena", "RF", "Parabola"]
        }
        res = ArticleExporter.to_hexo_markdown(meta, "<p>Langkah kalibrasi azimut dan elevasi antena.</p>")
        self.assertTrue(res.startswith("---"))
        self.assertIn('title: "Panduan Instalasi Antena Parabola"', res)
        self.assertIn("date: 2026-10-15 10:00:00", res)
        self.assertIn("categories:", res)
        self.assertIn('  - "Tutorial Telekomunikasi"', res)
        self.assertIn("tags:", res)
        self.assertIn('  - "Antena"', res)
        self.assertIn('  - "RF"', res)
        self.assertIn('  - "Parabola"', res)
        self.assertIn("<p>Langkah kalibrasi azimut dan elevasi antena.</p>", res)

    def test_generate_government_grant_json_ld(self):
        res = ArticleExporter.generate_government_grant_json_ld(
            grant_name="BIMA Kemdikbud Riset Terapan 2026",
            description="Hibah penelitian dosen berbasis prototipe komunikasi maritim.",
            agency_name="Direktorat Riset, Teknologi, dan Pengabdian kepada Masyarakat",
            recipient_name="Dr. Ir. Budi Santoso, M.T.",
            amount=150000000.0,
            year=2026,
            url="https://bima.kemdikbud.go.id/award/2026-001"
        )
        self.assertEqual(res["@context"], "https://schema.org")
        self.assertEqual(res["@type"], "GovernmentService")
        self.assertEqual(res["name"], "BIMA Kemdikbud Riset Terapan 2026")
        self.assertEqual(res["provider"]["name"], "Direktorat Riset, Teknologi, dan Pengabdian kepada Masyarakat")
        self.assertEqual(res["serviceAudience"]["audienceType"], "Academic Researchers")
        self.assertEqual(res["offers"]["price"], 150000000.0)
        self.assertEqual(res["offers"]["priceCurrency"], "IDR")
        self.assertEqual(res["offers"]["recipient"]["name"], "Dr. Ir. Budi Santoso, M.T.")
        self.assertEqual(res["url"], "https://bima.kemdikbud.go.id/award/2026-001")
        self.assertEqual(res["additionalProperty"][0]["name"], "Fiscal Year")
        self.assertEqual(res["additionalProperty"][0]["value"], "2026")

    def test_to_vitepress_markdown(self):
        meta = {
            "seo_title": "Panduan Konfigurasi BGP Router",
            "meta_description": "Dokumentasi teknis peering BGP dan manipulasi AS-Path.",
            "publish_date": "2026-10-15",
            "outline": [2, 4]
        }
        res = ArticleExporter.to_vitepress_markdown(meta, "## Langkah 1: Konfigurasi ASN")
        self.assertTrue(res.startswith("---"))
        self.assertIn('title: "Panduan Konfigurasi BGP Router"', res)
        self.assertIn('description: "Dokumentasi teknis peering BGP dan manipulasi AS-Path."', res)
        self.assertIn('date: "2026-10-15"', res)
        self.assertIn('outline: [2, 4]', res)
        self.assertIn("## Langkah 1: Konfigurasi ASN", res)

    def test_generate_financial_assistance_json_ld(self):
        res = ArticleExporter.generate_financial_assistance_json_ld(
            scholarship_name="Beasiswa KIP Kuliah Merdeka",
            sponsor_name="Kemdikbudristek RI",
            recipient_name="Ahmad Hidayat",
            amount=6000000.0,
            semester="Ganjil",
            academic_year="2026/2027",
            url="https://kip-kuliah.kemdikbud.go.id"
        )
        self.assertEqual(res["@context"], "https://schema.org")
        self.assertEqual(res["@type"], "FinancialAssistance")
        self.assertEqual(res["name"], "Beasiswa KIP Kuliah Merdeka")
        self.assertEqual(res["provider"]["name"], "Kemdikbudristek RI")
        self.assertEqual(res["recipient"]["name"], "Ahmad Hidayat")
        self.assertEqual(res["amount"]["value"], 6000000.0)
        self.assertEqual(res["amount"]["currency"], "IDR")
        self.assertEqual(res["url"], "https://kip-kuliah.kemdikbud.go.id")

    def test_to_jekyll_markdown(self):
        meta = {
            "seo_title": "Tutorial Pemrograman Python 3.12",
            "publish_date": "2026-10-16 12:00:00",
            "layout": "post",
            "category": "Tutorial",
            "tags": ["python", "jekyll", "telematika"]
        }
        res = ArticleExporter.to_jekyll_markdown(meta, "<p>Pengantar Python modern.</p>")
        self.assertTrue(res.startswith("---"))
        self.assertIn("layout: post", res)
        self.assertIn('title: "Tutorial Pemrograman Python 3.12"', res)
        self.assertIn("date: 2026-10-16 12:00:00", res)
        self.assertIn('category: "Tutorial"', res)
        self.assertIn("tags:", res)
        self.assertIn('  - "python"', res)
        self.assertIn('  - "jekyll"', res)
        self.assertIn("<p>Pengantar Python modern.</p>", res)

    def test_generate_thesis_json_ld(self):
        res = ArticleExporter.generate_thesis_json_ld(
            title="Optimasi MIMO Beamforming 5G mmWave",
            student_name="Dewi Sartika",
            advisor_name="Dr. Ir. Budi Santoso, M.T.",
            graduation_year=2026,
            abstract="Penelitian ini menganalisis efisiensi energi hybrid beamforming.",
            in_support_of="Sarjana Teknik (S.T.)",
            university_name="Telkom University Purwokerto",
            url="https://openlibrary.telkomuniversity.ac.id/thesis/120120005"
        )
        self.assertEqual(res["@context"], "https://schema.org")
        self.assertEqual(res["@type"], "Thesis")
        self.assertEqual(res["name"], "Optimasi MIMO Beamforming 5G mmWave")
        self.assertEqual(res["author"]["name"], "Dewi Sartika")
        self.assertEqual(res["contributor"][0]["name"], "Dr. Ir. Budi Santoso, M.T.")
        self.assertEqual(res["sourceOrganization"]["name"], "Telkom University Purwokerto")
        self.assertEqual(res["datePublished"], "2026")
        self.assertEqual(res["url"], "https://openlibrary.telkomuniversity.ac.id/thesis/120120005")

    def test_to_quartz_markdown(self):
        meta = {
            "seo_title": "Catatan Riset Jaringan Seluler",
            "publish_date": "2026-10-18",
            "category": "Riset",
            "tags": ["telekomunikasi", "seluler", "5g"]
        }
        res = ArticleExporter.to_quartz_markdown(meta, "<p>Catatan catatan riset.</p>")
        self.assertTrue(res.startswith("---"))
        self.assertIn('title: "Catatan Riset Jaringan Seluler"', res)
        self.assertIn("date: 2026-10-18", res)
        self.assertIn('description: "Riset note"', res)
        self.assertIn("tags:", res)
        self.assertIn('  - "telekomunikasi"', res)
        self.assertIn('  - "5g"', res)
        self.assertIn("<p>Catatan catatan riset.</p>", res)

    def test_generate_educational_credential_json_ld(self):
        res = ArticleExporter.generate_educational_credential_json_ld(
            credential_name="Sertifikasi Kompetensi Perekayasa Jaringan Seluler 5G",
            recipient_name="Ahmad Zaki",
            issuer_name="Badan Nasional Sertifikasi Profesi (BNSP)",
            valid_from="2026-10-15",
            credential_category="Professional License",
            cert_id="BNSP-TEL-2026-0912",
            url="https://bnsp.go.id/cert/BNSP-TEL-2026-0912"
        )
        self.assertEqual(res["@context"], "https://schema.org")
        self.assertEqual(res["@type"], "EducationalOccupationalCredential")
        self.assertEqual(res["name"], "Sertifikasi Kompetensi Perekayasa Jaringan Seluler 5G")
        self.assertEqual(res["credentialCategory"], "Professional License")
        self.assertEqual(res["recognizedBy"]["name"], "Badan Nasional Sertifikasi Profesi (BNSP)")
        self.assertEqual(res["about"]["name"], "Ahmad Zaki")
        self.assertEqual(res["validFrom"], "2026-10-15")
        self.assertEqual(res["identifier"], "BNSP-TEL-2026-0912")
        self.assertEqual(res["url"], "https://bnsp.go.id/cert/BNSP-TEL-2026-0912")

    def test_to_astro_starlight_markdown(self):
        meta = {
            "seo_title": "Panduan Instalasi Lab Antena",
            "meta_description": "Dokumentasi setup pengujian antena horn lab RF.",
            "category": "Panduan Lab",
            "sidebar_order": 3
        }
        res = ArticleExporter.to_astro_starlight_markdown(meta, "<p>Langkah 1: Pasang tripod dudukan antena.</p>")
        self.assertTrue(res.startswith("---"))
        self.assertIn('title: "Panduan Instalasi Lab Antena"', res)
        self.assertIn('description: "Dokumentasi setup pengujian antena horn lab RF."', res)
        self.assertIn("sidebar:", res)
        self.assertIn("order: 3", res)
        self.assertIn('badge: "Panduan Lab"', res)
        self.assertIn("<p>Langkah 1: Pasang tripod dudukan antena.</p>", res)

    def test_generate_community_action_project_json_ld(self):
        res = ArticleExporter.generate_community_action_project_json_ld(
            project_title="Pemberdayaan UMKM Sentra Kerajinan Logam Berbasis IoT",
            description="Pelatihan dan implementasi monitoring inventaris IoT di Desa Tumiyang.",
            leader_name="Dr. Hendra Gunawan, S.T., M.T.",
            location="Desa Tumiyang, Kebasen, Banyumas",
            funder_name="Telkom University Purwokerto",
            fiscal_year=2026,
            url="https://pkm.telkomuniversity.ac.id/2026/umkm-logam"
        )
        self.assertEqual(res["@context"], "https://schema.org")
        self.assertEqual(res["@type"], "Project")
        self.assertEqual(res["name"], "Pemberdayaan UMKM Sentra Kerajinan Logam Berbasis IoT")
        self.assertEqual(res["description"], "Pelatihan dan implementasi monitoring inventaris IoT di Desa Tumiyang.")
        self.assertEqual(res["founder"]["name"], "Dr. Hendra Gunawan, S.T., M.T.")
        self.assertEqual(res["locationCreated"]["name"], "Desa Tumiyang, Kebasen, Banyumas")
        self.assertEqual(res["funder"]["name"], "Telkom University Purwokerto")
        self.assertEqual(res["temporalCoverage"], "2026")
        self.assertEqual(res["url"], "https://pkm.telkomuniversity.ac.id/2026/umkm-logam")

    def test_to_docusaurus_v3_tabs_markdown(self):
        meta = {
            "seo_title": "Implementasi Link Budget FSO Python",
            "meta_description": "Dokumentasi dan simulasi Free Space Optics.",
            "slug": "fso-link-budget-guide",
            "sidebar_position": 4
        }
        tabs = [
            {"label": "Python", "value": "python", "content": "```python\ncalc_fso_link()\n```"},
            {"label": "MATLAB", "value": "matlab", "content": "```matlab\nfso_sim();\n```"}
        ]
        res = ArticleExporter.to_docusaurus_v3_tabs_markdown(
            meta,
            "<p>Berikut implementasi kalkulasi optical margin.</p>",
            tabs=tabs
        )
        self.assertTrue(res.startswith("---"))
        self.assertIn('title: "Implementasi Link Budget FSO Python"', res)
        self.assertIn('slug: /fso-link-budget-guide', res)
        self.assertIn("sidebar_position: 4", res)
        self.assertIn("import Tabs from '@theme/Tabs';", res)
        self.assertIn("<Tabs>", res)
        self.assertIn('<TabItem value="python" label="Python">', res)
        self.assertIn('calc_fso_link()', res)
        self.assertIn('</Tabs>', res)
        self.assertIn("<p>Berikut implementasi kalkulasi optical margin.</p>", res)

    def test_generate_educational_organization_json_ld(self):
        res = ArticleExporter.generate_educational_organization_json_ld(
            name="S1 Teknik Telekomunikasi Telkom University Purwokerto",
            alternate_name="Telecommunication Engineering TUP",
            url="https://tele.telkomuniversity.ac.id",
            logo_url="https://tele.telkomuniversity.ac.id/logo.png",
            description="Program Studi S1 Teknik Telekomunikasi terakreditasi Unggul.",
            address={
                "street": "Jl. DI Panjaitan No. 128",
                "locality": "Purwokerto",
                "region": "Jawa Tengah",
                "postal_code": "53147",
                "country": "ID"
            },
            accreditation="Unggul (LAM INFOKOM)"
        )
        self.assertEqual(res["@context"], "https://schema.org")
        self.assertEqual(res["@type"], "EducationalOrganization")
        self.assertEqual(res["name"], "S1 Teknik Telekomunikasi Telkom University Purwokerto")
        self.assertEqual(res["alternateName"], "Telecommunication Engineering TUP")
        self.assertEqual(res["address"]["postalCode"], "53147")
        self.assertEqual(res["hasCredential"]["name"], "Unggul (LAM INFOKOM)")

    def test_to_nextjs_contentlayer_mdx(self):
        meta = {
            "seo_title": "Optimasi Jaringan Nirkabel 5G",
            "meta_description": "Studi kasus propagasi mmWave 28 GHz di area urban.",
            "publish_date": "2026-10-21",
            "category": "Riset Nirkabel",
            "tags": ["5g", "mmwave", "propagation"]
        }
        res = ArticleExporter.to_nextjs_contentlayer_mdx(meta, "<p>Analisis coverage dan path loss.</p>")
        self.assertTrue(res.startswith("---"))
        self.assertIn('title: "Optimasi Jaringan Nirkabel 5G"', res)
        self.assertIn('date: "2026-10-21"', res)
        self.assertIn('category: "Riset Nirkabel"', res)
        self.assertIn('"5g", "mmwave", "propagation"', res)
        self.assertIn("published: true", res)
        self.assertIn("<p>Analisis coverage dan path loss.</p>", res)

    def test_generate_startup_incubation_project_json_ld(self):
        meta = {
            "startup_name": "IoT AgroSense",
            "founder": "Budi Santoso",
            "sector": "Smart Agriculture",
            "url": "https://agrosense.telkomuniversity.ac.id",
            "description": "Inkubasi sensor IoT pertanian mandiri."
        }
        res = ArticleExporter.generate_startup_incubation_project_json_ld(meta)
        self.assertEqual(res["@type"], "Project")
        self.assertEqual(res["name"], "IoT AgroSense")
        self.assertEqual(res["founder"]["name"], "Budi Santoso")
        self.assertEqual(res["category"], "Smart Agriculture")
        self.assertEqual(res["funder"]["name"], "Program Wirausaha Merdeka Telkom University Purwokerto")

    def test_to_remix_route_mdx(self):
        meta = {
            "seo_title": "Desain Antena Mikrostrip 5G",
            "meta_description": "Simulasi CST Studio Suite untuk patch antenna.",
            "slug": "antena-mikrostrip-5g",
            "publish_date": "2026-10-22"
        }
        res = ArticleExporter.to_remix_route_mdx(meta, "<p>Hasil simulasi S-parameter.</p>")
        self.assertTrue(res.startswith("---"))
        self.assertIn('breadcrumb: "Desain Antena Mikrostrip 5G"', res)
        self.assertIn('slug: "antena-mikrostrip-5g"', res)
        self.assertIn('meta:', res)
        self.assertIn('og:title', res)
        self.assertIn("<p>Hasil simulasi S-parameter.</p>", res)

    def test_generate_academic_exchange_program_json_ld(self):
        meta = {
            "program_name": "IISMA 2026 NUS Cohort",
            "description": "Program pertukaran sarjana teknik telekomunikasi di NUS.",
            "host_university": "National University of Singapore",
            "country": "Singapore",
            "category": "S1 Teknik Telekomunikasi",
            "url": "https://iisma.kemdikbud.go.id"
        }
        res = ArticleExporter.generate_academic_exchange_program_json_ld(meta)
        self.assertEqual(res["@context"], "https://schema.org")
        self.assertEqual(res["@type"], "EducationalOccupationalProgram")
        self.assertEqual(res["name"], "IISMA 2026 NUS Cohort")
        self.assertEqual(res["hasCourse"]["provider"]["name"], "National University of Singapore")
        self.assertEqual(res["hasCourse"]["provider"]["address"]["addressCountry"], "Singapore")

    def test_to_vitepress_markdown(self):
        meta = {
            "seo_title": "Tutorial Simulasi Antena CST",
            "meta_description": "Langkah demi langkah merancang antena mikrostrip.",
            "publish_date": "2026-10-23",
            "tags": ["antena", "cst", "microwave"]
        }
        res = ArticleExporter.to_vitepress_markdown(meta, "<p>Tutorial lengkap simulasi.</p>")
        self.assertTrue(res.startswith("---"))
        self.assertIn('title: "Tutorial Simulasi Antena CST"', res)
        self.assertIn('outline: [2, 3]', res)
        self.assertIn('editLink: false', res)
        self.assertIn('"antena", "cst", "microwave"', res)
        self.assertIn("<p>Tutorial lengkap simulasi.</p>", res)

    def test_generate_humanitarian_action_json_ld(self):
        res = ArticleExporter.generate_humanitarian_action_json_ld(
            action_title="Relawan Komunikasi Tanggap Darurat Bencana Merapi",
            description="Penyediaan jaringan komunikasi radio ad-hoc darurat di posko pengungsian.",
            student_name="Reza Kurniawan",
            partner_org="BPBD Provinsi Jawa Tengah",
            location="Magelang, Jawa Tengah",
            start_date="2026-08-15",
            url="https://kemanusiaan.telkomuniversity.ac.id/merapi"
        )
        self.assertEqual(res["@context"], "https://schema.org")
        self.assertEqual(res["@type"], "Project")
        self.assertEqual(res["name"], "Relawan Komunikasi Tanggap Darurat Bencana Merapi")
        self.assertEqual(res["founder"]["name"], "Reza Kurniawan")
        self.assertEqual(res["funder"]["name"], "BPBD Provinsi Jawa Tengah")
        self.assertEqual(res["location"]["name"], "Magelang, Jawa Tengah")
        self.assertEqual(res["url"], "https://kemanusiaan.telkomuniversity.ac.id/merapi")

    def test_to_hugo_academic_markdown(self):
        meta = {
            "seo_title": "Simulasi Propagasi Kanal Terahertz",
            "meta_description": "Analisis redaman atmosfer pada pita frekuensi 300 GHz.",
            "publish_date": "2026-10-24",
            "category": "Wireless Communications",
            "tags": ["6G", "THz", "Propagasi"]
        }
        res = ArticleExporter.to_hugo_academic_markdown(meta, "<p>Model kanal transmisi terahertz.</p>")
        self.assertTrue(res.startswith("---"))
        self.assertIn('title: "Simulasi Propagasi Kanal Terahertz"', res)
        self.assertIn('summary: "Analisis redaman atmosfer pada pita frekuensi 300 GHz."', res)
        self.assertIn('categories: ["Wireless Communications"]', res)
        self.assertIn('authors: ["admin"]', res)
        self.assertIn("math: true", res)
        self.assertIn("<p>Model kanal transmisi terahertz.</p>", res)

    def test_generate_faq_page_json_ld(self):
        faq_items = [
            {"question": "Berapa SKS syarat lulus Teknik Telekomunikasi?", "answer": "Mahasiswa wajib menyelesaikan minimal 144 SKS."},
            {"question": "Apakah tersedia peminatan Cyber Security?", "answer": "Ya, terdapat peminatan Jaringan dan Keamanan Siber."}
        ]
        res = ArticleExporter.generate_faq_page_json_ld(faq_items, title="FAQ Prodi S1 Teknik Telekomunikasi")
        self.assertEqual(res["@context"], "https://schema.org")
        self.assertEqual(res["@type"], "FAQPage")
        self.assertEqual(res["name"], "FAQ Prodi S1 Teknik Telekomunikasi")
        self.assertEqual(len(res["mainEntity"]), 2)
        self.assertEqual(res["mainEntity"][0]["@type"], "Question")
        self.assertEqual(res["mainEntity"][0]["name"], "Berapa SKS syarat lulus Teknik Telekomunikasi?")
        self.assertEqual(res["mainEntity"][0]["acceptedAnswer"]["@type"], "Answer")
        self.assertEqual(res["mainEntity"][0]["acceptedAnswer"]["text"], "Mahasiswa wajib menyelesaikan minimal 144 SKS.")

    def test_to_mkdocs_material_markdown(self):
        meta = {
            "seo_title": "Panduan Praktikum Fiber Optik",
            "meta_description": "Dokumentasi prosedur splicing kabel fiber optik core tunggal.",
            "icon": "material/lan",
            "tags": ["fiber-optics", "splicing", "praktikum"]
        }
        res = ArticleExporter.to_mkdocs_material_markdown(meta, "<p>Persiapkan alat fusion splicer dan cleaver.</p>")
        self.assertTrue(res.startswith("---"))
        self.assertIn('title: "Panduan Praktikum Fiber Optik"', res)
        self.assertIn('description: "Dokumentasi prosedur splicing kabel fiber optik core tunggal."', res)
        self.assertIn('icon: "material/lan"', res)
        self.assertIn('"fiber-optics", "splicing", "praktikum"', res)
        self.assertIn("<p>Persiapkan alat fusion splicer dan cleaver.</p>", res)

    def test_generate_how_to_json_ld(self):
        steps = [
            {"name": "Kupas Kabel", "text": "Gunakan stripper untuk mengupas jaket luar kabel."},
            {"name": "Potong Fiber", "text": "Gunakan precision cleaver untuk memotong flat 90 derajat."}
        ]
        res = ArticleExporter.generate_how_to_json_ld(
            name="Prosedur Fusion Splicing Serat Optik",
            steps=steps,
            description="Panduan standar penyambungan serat optik.",
            total_time="PT15M",
            tools=["Fusion Splicer", "Fiber Cleaver"]
        )
        self.assertEqual(res["@context"], "https://schema.org")
        self.assertEqual(res["@type"], "HowTo")
        self.assertEqual(res["name"], "Prosedur Fusion Splicing Serat Optik")
        self.assertEqual(len(res["step"]), 2)
        self.assertEqual(res["totalTime"], "PT15M")
        self.assertEqual(res["tool"][0]["name"], "Fusion Splicer")

    def test_to_docusaurus_mdx(self):
        meta = {
            "slug": "docusaurus-dwdm",
            "seo_title": "Panduan Sistem DWDM",
            "meta_description": "Dokumentasi teknis multiplexing optik rapat.",
            "sidebar_position": 3,
            "tags": ["dwdm", "optik", "telekomunikasi"]
        }
        res = ArticleExporter.to_docusaurus_mdx(meta, "<p>Penjelasan multiplexing kanal optik.</p>")
        self.assertTrue(res.startswith("---"))
        self.assertIn("id: docusaurus-dwdm", res)
        self.assertIn('title: "Panduan Sistem DWDM"', res)
        self.assertIn("slug: /docusaurus-dwdm", res)
        self.assertIn("sidebar_position: 3", res)
        self.assertIn('"dwdm", "optik", "telekomunikasi"', res)
        self.assertIn("<p>Penjelasan multiplexing kanal optik.</p>", res)


if __name__ == "__main__":
    unittest.main()






