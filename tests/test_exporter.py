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

if __name__ == "__main__":
    unittest.main()


