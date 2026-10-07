import unittest
from components import EditorialComponents

class TestEditorialComponents(unittest.TestCase):
    def test_css_scoping(self):
        css = EditorialComponents.get_scoped_css()
        self.assertIn(".tu-editorial-container", css)
        self.assertIn("#c53030", css)
        self.assertIn("#0f172a", css)

    def test_render_hero(self):
        hero = EditorialComponents.render_hero(
            category="IoT",
            date_str="28 September 2026",
            read_time="4 Menit Baca",
            title="Judul Artikel",
            lead_html="Lead paragraf contoh."
        )
        self.assertIn('<header class="tu-hero-header">', hero)
        self.assertIn("Judul Artikel", hero)
        self.assertIn("28 September 2026", hero)

    def test_render_figure(self):
        fig = EditorialComponents.render_figure(
            img_url="https://example.com/img.jpg",
            alt_text="Alt test",
            caption="Caption test"
        )
        self.assertIn('loading="lazy"', fig)
        self.assertIn('alt="Alt test"', fig)

    def test_render_comparison_grid(self):
        grid = EditorialComponents.render_comparison_grid(
            legacy_title="Docker",
            legacy_items=["Berat", "Lambat"],
            modern_title="Wasm",
            modern_items=["Ringan", "Cepat"]
        )
        self.assertIn('<div class="tu-comparison-grid">', grid)
        self.assertIn("Docker", grid)
        self.assertIn("Wasm", grid)

    def test_render_key_takeaways(self):
        card = EditorialComponents.render_key_takeaways(
            items=["Kinerja tinggi", "Sandbox aman", "Hemat energi"],
            heading="Poin Inti Wasm"
        )
        self.assertIn("tu-takeaways-card", card)
        self.assertIn("Poin Inti Wasm", card)
        self.assertIn("Sandbox aman", card)

    def test_render_author_card(self):
        author = EditorialComponents.render_author_card(
            author_name="Dr. Budi Santoso",
            author_role="Dosen Riset IoT",
            bio_text="Fokus riset smart sensor."
        )
        self.assertIn("tu-author-card", author)
        self.assertIn("Dr. Budi Santoso", author)
        self.assertIn("Dosen Riset IoT", author)
        self.assertIn("Fokus riset smart sensor.", author)

    def test_render_faq_accordion(self):
        items = [
            ("Apa itu WebAssembly?", "WebAssembly adalah format instruksi biner."),
            ("Apakah aman?", "Sangat aman berkat model memori terisolasi.")
        ]
        faq = EditorialComponents.render_faq_accordion(items, section_title="Pertanyaan Populer")
        self.assertIn("tu-faq-wrap", faq)
        self.assertIn("Pertanyaan Populer", faq)
        self.assertIn("<summary class=\"tu-faq-question\">Apa itu WebAssembly?</summary>", faq)
        self.assertIn("<div class=\"tu-faq-answer\">WebAssembly adalah format instruksi biner.</div>", faq)
        self.assertIn("<details class=\"tu-faq-item\">", faq)

    def test_render_stat_grid(self):
        stats = [
            {"value": "95%", "label": "Efisiensi Memori"},
            {"value": "10x", "label": "Kecepatan Cold Start"}
        ]
        grid = EditorialComponents.render_stat_grid(stats)
        self.assertIn("tu-stat-grid", grid)
        self.assertIn("tu-stat-card", grid)
        self.assertIn("95%", grid)
        self.assertIn("Efisiensi Memori", grid)
        self.assertIn("10x", grid)
        self.assertIn("Kecepatan Cold Start", grid)

    def test_render_references_block(self):
        refs = [
            "Haas, A. et al. (2017). Bringing the Web up to Speed with WebAssembly. ACM SIGPLAN.",
            "World Wide Web Consortium (W3C). WebAssembly Core Specification."
        ]
        block = EditorialComponents.render_references_block(refs, heading="Daftar Pustaka")
        self.assertIn("tu-references-box", block)
        self.assertIn("Daftar Pustaka", block)
        self.assertIn("Bringing the Web up to Speed", block)
        self.assertIn("tu-references-list", block)

    def test_render_code_block(self):
        sample_code = "fn main() {\n    println!(\"Hello <Wasm>\");\n}"
        block = EditorialComponents.render_code_block(sample_code, language="rust", filename="main.rs")
        self.assertIn("tu-code-container", block)
        self.assertIn("main.rs", block)
        self.assertIn("tu-code-badge", block)
        self.assertIn("rust", block)
        self.assertIn("&lt;Wasm&gt;", block)

    def test_render_timeline_component(self):
        events = [
            {"date": "Q1 2026", "title": "Inisiasi Riset", "description": "Eksplorasi modul WebAssembly."},
            {"date": "Q2 2026", "title": "Implementasi Edge", "description": "Uji coba runtime di gateway IoT."}
        ]
        timeline = EditorialComponents.render_timeline_component(events)
        self.assertIn("tu-timeline", timeline)
        self.assertIn("tu-timeline-item", timeline)
        self.assertIn("Inisiasi Riset", timeline)
        self.assertIn("Q1 2026", timeline)

    def test_render_alumni_quote_card(self):
        card = EditorialComponents.render_alumni_quote_card(
            name="Ahmad Fauzan",
            batch="Angkatan 2022",
            role="AI Engineer",
            company="Tech Corp",
            quote="Kurikulum prodi sangat aplikatif!",
            avatar_url="https://example.com/avatar.jpg"
        )
        self.assertIn("tu-alumni-card", card)
        self.assertIn("Ahmad Fauzan", card)
        self.assertIn("Angkatan 2022", card)
        self.assertIn("Tech Corp", card)
        self.assertIn("Kurikulum prodi sangat aplikatif!", card)
        self.assertIn("tu-alumni-avatar", card)

    def test_render_feature_matrix(self):
        cols = ["Materi", "S1 Sains Data", "Sertifikasi Singkat"]
        rows = [
            {"feature": "Fondasi Teori Matematika", "values": [True, False]},
            {"feature": "Portofolio Industri Terverifikasi", "values": [True, True]},
            {"feature": "Durasi Studi", "values": ["8 Semester", "3 Bulan"]}
        ]
        matrix = EditorialComponents.render_feature_matrix(cols, rows)
        self.assertIn("tu-feature-matrix", matrix)
        self.assertIn("<th>S1 Sains Data</th>", matrix)
        self.assertIn("tu-matrix-check", matrix)
        self.assertIn("tu-matrix-cross", matrix)
        self.assertIn("8 Semester", matrix)

    def test_render_table_of_contents(self):
        headings = [
            {"tag": "h2", "text": "Pengantar WebAssembly"},
            {"tag": "h3", "text": "Keunggulan Kinerja"}
        ]
        toc = EditorialComponents.render_table_of_contents(headings)
        self.assertIn("tu-toc-card", toc)
        self.assertIn("#pengantar-webassembly", toc)
        self.assertIn("tu-toc-sub", toc)

    def test_render_author_team(self):
        members = [
            {"name": "Dr. Ir. Budi", "role": "Dosen Pembina", "lab": "Lab IoT & Edge", "avatar_url": "https://example.com/budi.jpg"}
        ]
        grid = EditorialComponents.render_author_team(members)
        self.assertIn("tu-team-section", grid)
        self.assertIn("Dr. Ir. Budi", grid)
        self.assertIn("Lab IoT &amp; Edge", grid)

    def test_render_download_card(self):
        card = EditorialComponents.render_download_card(
            title="Silabus Mata Kuliah Edge Computing",
            description="Panduan kurikulum dan RPS semester genap.",
            file_type="PDF",
            file_size="2.4 MB",
            download_url="https://bif-pwt.telkomuniversity.ac.id/rps.pdf"
        )
        self.assertIn("tu-download-card", card)
        self.assertIn("PDF", card)
        self.assertIn("2.4 MB", card)

    def test_render_video_embed(self):
        video = EditorialComponents.render_video_embed(
            embed_url="https://www.youtube-nocookie.com/embed/demo123",
            title="Kuliah Umum Edge Computing",
            caption="Rekaman sesi kuliah umum semester genap 2026."
        )
        self.assertIn("tu-video-figure", video)
        self.assertIn("Kuliah Umum Edge Computing", video)

    def test_render_admission_cta(self):
        cta = EditorialComponents.render_admission_cta()
        self.assertIn("tu-cta-banner", cta)
        self.assertIn("Telkom University Purwokerto", cta)

    def test_render_metric_callout(self):
        metric = EditorialComponents.render_metric_callout("98%", "Tingkat Kelulusan Tepat Waktu", "Berdasarkan audit akademik 2026")
        self.assertIn("tu-metric-card", metric)
        self.assertIn("98%", metric)
        self.assertIn("Tingkat Kelulusan Tepat Waktu", metric)

    def test_render_pull_quote(self):
        quote = EditorialComponents.render_pull_quote(
            quote="Komputasi awan dan edge computing adalah masa depan industri telekomunikasi.",
            author="Prof. Adiwijaya",
            source="IEEE Journal",
            citation_url="https://ieee.org/paper123"
        )
        self.assertIn("tu-pull-quote", quote)
        self.assertIn("Prof. Adiwijaya", quote)
        self.assertIn("IEEE Journal", quote)

    def test_render_lab_affiliation_banner(self):
        banner = EditorialComponents.render_lab_affiliation_banner(
            lab_name="Laboratorium Jaringan & Keamanan Siber",
            focus_area="Kriptografi Post-Quantum",
            coordinator="Dr. Hendra",
            lab_url="https://bif-pwt.telkomuniversity.ac.id/lab/cyber"
        )
        self.assertIn("tu-lab-banner", banner)
        self.assertIn("Kriptografi Post-Quantum", banner)
        self.assertIn("Dr. Hendra", banner)

    def test_render_prerequisite_tree(self):
        tree = EditorialComponents.render_prerequisite_tree(
            course_code="CS304",
            course_name="Komputasi Bergerak Lanjut",
            prerequisites=["Struktur Data", "Jaringan Komputer"],
            semester="Semester 5"
        )
        self.assertIn("tu-prereq-card", tree)
        self.assertIn("CS304", tree)
        self.assertIn("Jaringan Komputer", tree)

    def test_render_event_box(self):
        box = EditorialComponents.render_event_box(
            event_name="Workshop Edge AI & Microcontrollers",
            date_time="10 Oktober 2026, 09:00 WIB",
            speaker="Alumni Ahli IoT",
            location="Auditorium Gedung IoT Telkom Purwokerto",
            rsvp_url="https://bif-pwt.telkomuniversity.ac.id/event/rsvp"
        )
        self.assertIn("tu-event-box", box)
        self.assertIn("Workshop Edge AI", box)
        self.assertIn("Daftar Seminar", box)

    def test_render_code_repo_card(self):
        repo = EditorialComponents.render_code_repo_card(
            repo_name="telkom-edge-inference",
            github_url="https://github.com/prodi/telkom-edge-inference",
            stars="142",
            language="Rust",
            description="Runtime inferensi model kuantisasi untuk MCU."
        )
        self.assertIn("tu-repo-card", repo)
        self.assertIn("telkom-edge-inference", repo)
        self.assertIn("142", repo)
        self.assertIn("Rust", repo)

    def test_render_faculty_profile_card(self):
        card = EditorialComponents.render_faculty_profile_card(
            name="Dr. Aris Tri Jaka, M.Kom.",
            academic_title="Lektor Kepala / Dosen Peneliti AI",
            nidn="0612038501",
            expertise="Computer Vision & Deep Learning",
            scholar_url="https://scholar.google.com/citations?user=xyz",
            email="aris@telkomuniversity.ac.id"
        )
        self.assertIn("tu-faculty-card", card)
        self.assertIn("Dr. Aris Tri Jaka", card)
        self.assertIn("0612038501", card)
        self.assertIn("Google Scholar", card)

    def test_render_capstone_showcase_card(self):
        showcase = EditorialComponents.render_capstone_showcase_card(
            project_title="Sistem Deteksi Anomali Jaringan IoT",
            student_names=["Fajar Nugraha", "Rina Wulandari"],
            supervisor="Dr. Budi Santoso",
            abstract="Implementasi algoritma Isolation Forest pada mikrokontroler ESP32.",
            demo_url="https://demo.prodi.ac.id",
            github_url="https://github.com/prodi/capstone-iot"
        )
        self.assertIn("tu-capstone-card", showcase)
        self.assertIn("Sistem Deteksi Anomali", showcase)
        self.assertIn("Fajar Nugraha, Rina Wulandari", showcase)
        self.assertIn("Live Demo", showcase)

    def test_render_certification_grid(self):
        certs = [
            {"name": "AWS Certified Solutions Architect", "issuer": "Amazon Web Services", "level": "Associate", "icon": "☁️"},
            {"name": "Cisco Certified Network Associate (CCNA)", "issuer": "Cisco Systems", "level": "Professional", "icon": "🌐"}
        ]
        grid = EditorialComponents.render_certification_grid(certs)
        self.assertIn("tu-cert-section", grid)
        self.assertIn("AWS Certified", grid)
        self.assertIn("Cisco Systems", grid)

    def test_render_academic_calendar_card(self):
        events = [
            {"date": "1 - 5 September 2026", "activity": "Pengisian KRS Semester Ganjil", "status": "Selesai"},
            {"date": "26 - 31 Oktober 2026", "activity": "Ujian Tengah Semester (UTS)", "status": "Mendatang"}
        ]
        cal = EditorialComponents.render_academic_calendar_card("Semester Ganjil 2026/2027", events)
        self.assertIn("tu-calendar-card", cal)
        self.assertIn("Semester Ganjil 2026/2027", cal)
        self.assertIn("Pengisian KRS", cal)

    def test_render_industry_partner_banner(self):
        partners = [
            {"name": "Telkom Indonesia", "category": "Telekomunikasi"},
            {"name": "Google Cloud", "category": "Cloud Computing"}
        ]
        banner = EditorialComponents.render_industry_partner_banner("Mitra Magang & Kerjasama Industri", partners)
        self.assertIn("tu-partner-banner", banner)
        self.assertIn("Telkom Indonesia", banner)
        self.assertIn("Google Cloud", banner)

    def test_render_accreditation_badge(self):
        badge = EditorialComponents.render_accreditation_badge(
            agency="LAM INFOKOM",
            grade="Unggul",
            decree_no="045/SK/LAM-INFOKOM/Akred/S/VIII/2026",
            valid_until="31 Agustus 2031"
        )
        self.assertIn("tu-accreditation-card", badge)
        self.assertIn("LAM INFOKOM", badge)
        self.assertIn("Unggul", badge)
        self.assertIn("045/SK/LAM-INFOKOM", badge)

    def test_render_lab_equipment_card(self):
        equipment = [
            {"name": "NVIDIA DGX A100 Server", "specs": "8x A100 80GB GPU, 1TB RAM", "quantity": "2"},
            {"name": "Oculus Quest Pro VR Headset", "specs": "Spatial computing dev kit", "quantity": "10"}
        ]
        card = EditorialComponents.render_lab_equipment_card("Lab Kecerdasan Buatan & Robotika", equipment)
        self.assertIn("tu-lab-equipment-card", card)
        self.assertIn("NVIDIA DGX A100 Server", card)
        self.assertIn("8x A100 80GB GPU", card)
        self.assertIn("2 unit", card)

    def test_render_award_podium_card(self):
        awards = [
            {"medal": "Juara 1 (Emas)", "team": "Tim CyberBIF", "project": "Sistem Pertahanan IoT Post-Quantum"},
            {"medal": "Juara 2 (Perak)", "team": "Tim TeleAlgo", "project": "Optimasi Rute Jaringan 6G"}
        ]
        podium = EditorialComponents.render_award_podium_card("Gemastik Divisi Keamanan Siber 2026", awards)
        self.assertIn("tu-award-podium-card", podium)
        self.assertIn("Gemastik Divisi Keamanan Siber 2026", podium)
        self.assertIn("Tim CyberBIF", podium)
        self.assertIn("Juara 1 (Emas)", podium)

    def test_render_exchange_program_showcase(self):
        univs = [
            {"name": "Kumamoto University", "country": "Jepang", "quota": "4 Mahasiswa"},
            {"name": "Universiti Teknologi Malaysia", "country": "Malaysia", "quota": "6 Mahasiswa"}
        ]
        showcase = EditorialComponents.render_exchange_program_showcase("Program Pertukaran Mahasiswa Internasional", univs)
        self.assertIn("tu-exchange-showcase", showcase)
        self.assertIn("Kumamoto University", showcase)
        self.assertIn("Jepang", showcase)
        self.assertIn("4 Mahasiswa", showcase)

    def test_render_career_placement_card(self):
        metrics = [
            {"label": "Masa Tunggu Kerja", "value": "2.1 Bulan", "detail": "Rata-rata lulusan 2025/2026"},
            {"label": "Gaji Pertama Rata-rata", "value": "Rp 9.500.000", "detail": "Di atas standar UMR Jabodetabek"}
        ]
        card = EditorialComponents.render_career_placement_card("Statistik Keterserapan Alumni Informatika", metrics)
        self.assertIn("tu-career-placement-card", card)
        self.assertIn("2.1 Bulan", card)
        self.assertIn("Masa Tunggu Kerja", card)
        self.assertIn("Rp 9.500.000", card)

    def test_render_journal_publication_card(self):
        card = EditorialComponents.render_journal_publication_card(
            title="Optimasi Deep Learning pada Edge IoT",
            authors=["Budi Santoso", "Siti Rahma"],
            journal_name="IEEE Internet of Things Journal",
            doi_url="https://doi.org/10.1109/JIOT.2026.123456",
            quartile="Q1"
        )
        self.assertIn("tu-journal-card", card)
        self.assertIn("Q1", card)
        self.assertIn("IEEE Internet of Things Journal", card)
        self.assertIn("Budi Santoso, Siti Rahma", card)
        self.assertIn("https://doi.org/10.1109/JIOT.2026.123456", card)

    def test_render_student_club_card(self):
        card = EditorialComponents.render_student_club_card(
            club_name="Cyber Security Club Purwokerto",
            focus_area="Ethical Hacking & CTF",
            leader="Rian Pratama",
            meet_schedule="Setiap Kamis 16:00 WIB",
            member_count=35
        )
        self.assertIn("tu-club-card", card)
        self.assertIn("Cyber Security Club Purwokerto", card)
        self.assertIn("Ethical Hacking &amp; CTF", card)
        self.assertIn("Rian Pratama", card)
        self.assertIn("35 Mahasiswa", card)

    def test_render_research_grant_banner(self):
        banner = EditorialComponents.render_research_grant_banner(
            grant_name="Pengembangan Smart Campus Digital Twin Berbasis IoT",
            scheme="Hibah Penelitian Fundamental",
            funding_agency="Kemendikbudristek",
            amount="Rp 150.000.000",
            lead_researcher="Dr. Ir. Hendra"
        )
        self.assertIn("tu-grant-banner", banner)
        self.assertIn("Smart Campus Digital Twin", banner)
        self.assertIn("Kemendikbudristek", banner)
        self.assertIn("Rp 150.000.000", banner)

    def test_render_specialization_track_card(self):
        card = EditorialComponents.render_specialization_track_card(
            track_name="Keminatan Artificial Intelligence",
            description="Fokus mendalam pada machine learning, vision, dan NLP.",
            core_courses=["Deep Learning", "Pengolahan Citra Digital", "NLP"],
            career_roles=["AI Engineer", "Data Scientist", "MLOps Engineer"]
        )
        self.assertIn("tu-track-card", card)
        self.assertIn("Keminatan Artificial Intelligence", card)
        self.assertIn("Deep Learning", card)
        self.assertIn("AI Engineer", card)

    def test_render_data_center_facility_card(self):
        specs = [
            {"key": "Kapasitas Server", "value": "4 Rak Blade Server 42U"},
            {"key": "Konektivitas", "value": "Redundant 10 Gbps Fiber Optic"},
            {"key": "Sistem Pendingin", "value": "Precision In-Row Cooling"}
        ]
        card = EditorialComponents.render_data_center_facility_card("Data Center Laboratorium Informatika", specs)
        self.assertIn("tu-facility-card", card)
        self.assertIn("Data Center Laboratorium Informatika", card)
        self.assertIn("4 Rak Blade Server 42U", card)
        self.assertIn("Redundant 10 Gbps Fiber Optic", card)

if __name__ == "__main__":
    unittest.main()


