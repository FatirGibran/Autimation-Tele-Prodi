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

    def test_render_capstone_project_card(self):
        card = EditorialComponents.render_capstone_project_card(
            title="Sistem Deteksi Retinopati Diabetik Berbasis CNN",
            students=["Fajar Nugraha", "Dewi Lestari"],
            advisor="Dr. Budi Santoso",
            repo_url="https://github.com/prodi/retinopathy-cnn",
            demo_url="https://retino.prodi.ac.id",
            tags=["AI", "Healthcare", "PyTorch"]
        )
        self.assertIn("tu-capstone-card", card)
        self.assertIn("Sistem Deteksi Retinopati", card)
        self.assertIn("Fajar Nugraha, Dewi Lestari", card)
        self.assertIn("Dr. Budi Santoso", card)
        self.assertIn("Kode Sumber", card)

    def test_render_certification_badge_card(self):
        card = EditorialComponents.render_certification_badge_card(
            cert_name="AWS Certified Solutions Architect",
            issuer="Amazon Web Services",
            validity_period="3 Tahun",
            credential_url="https://aws.amazon.com/verify/123"
        )
        self.assertIn("tu-cert-card", card)
        self.assertIn("AWS Certified Solutions Architect", card)
        self.assertIn("Amazon Web Services", card)
        self.assertIn("3 Tahun", card)

    def test_render_academic_calendar_banner(self):
        milestones = [
            {"date": "1 September 2026", "event": "Awal Perkuliahan Semester Ganjil"},
            {"date": "20 - 31 Oktober 2026", "event": "Ujian Tengah Semester"}
        ]
        banner = EditorialComponents.render_academic_calendar_banner(
            semester_name="Semester Ganjil",
            academic_year="2026/2027",
            milestones=milestones
        )
        self.assertIn("tu-calendar-banner", banner)
        self.assertIn("Semester Ganjil", banner)
        self.assertIn("2026/2027", banner)
        self.assertIn("Awal Perkuliahan", banner)

    def test_render_lab_reservation_card(self):
        slots = ["08:00 - 10:00 WIB", "13:00 - 15:00 WIB"]
        card = EditorialComponents.render_lab_reservation_card(
            lab_name="Lab AI & Data Science",
            equipment_name="NVIDIA DGX Station A100",
            supervisor="Ir. Hendra",
            booking_status="Tersedia",
            schedule_slots=slots
        )
        self.assertIn("tu-reservation-card", card)
        self.assertIn("NVIDIA DGX Station A100", card)
        self.assertIn("Lab AI &amp; Data Science", card)
        self.assertIn("08:00 - 10:00 WIB", card)

    def test_render_exchange_testimonial_card(self):
        transfers = ["Artificial Intelligence (4 SKS)", "Computer Vision (3 SKS)"]
        card = EditorialComponents.render_exchange_testimonial_card(
            student_name="Anisa Rahma",
            host_university="Kumamoto University",
            country="Jepang",
            courses_transferred=transfers,
            testimonial="Pengalaman riset yang luar biasa di laboratorium robotika Jepang."
        )
        self.assertIn("tu-exchange-testi-card", card)
        self.assertIn("Anisa Rahma", card)
        self.assertIn("Kumamoto University", card)
        self.assertIn("Artificial Intelligence (4 SKS)", card)

    def test_render_cpl_curriculum_card(self):
        desc = ["Mampu merancang arsitektur sistem berbasis awan", "Mampu menerapkan etika profesi rekayasa perangkat lunak"]
        card = EditorialComponents.render_cpl_curriculum_card(
            cpl_code="CPL-03",
            title="Kemampuan Perancangan Rekayasa Perangkat Lunak",
            domain="Keterampilan Khusus",
            descriptions=desc
        )
        self.assertIn("tu-cpl-card", card)
        self.assertIn("CPL-03", card)
        self.assertIn("Kemampuan Perancangan", card)
        self.assertIn("Mampu merancang arsitektur sistem", card)

    def test_render_internship_partner_card(self):
        roles = ["Cloud Engineer Intern", "Backend Developer"]
        card = EditorialComponents.render_internship_partner_card(
            company_name="PT Telkom Indonesia Tbk",
            industry="Telekomunikasi & Digital",
            city="Bandung",
            quota=5,
            roles=roles,
            logo_url="https://example.com/logo.png"
        )
        self.assertIn("tu-intern-partner-card", card)
        self.assertIn("PT Telkom Indonesia Tbk", card)
        self.assertIn("Bandung", card)
        self.assertIn("Kuota: 5 Posisi", card)
        self.assertIn("Cloud Engineer Intern", card)

    def test_render_grant_expenditure_card(self):
        milestones = [
            {"milestone": "Survei Literatur & Dataset", "spent_idr": 25000000, "status": "Selesai"},
            {"milestone": "Pengembangan Model Prototype", "spent_idr": 45000000, "status": "Berjalan"}
        ]
        card = EditorialComponents.render_grant_expenditure_card(
            grant_title="Sistem Deteksi Anomali IoT Jaringan Kampus",
            scheme="Hibah Riset Terapan",
            budget_idr=100000000,
            progress_pct=70,
            milestones=milestones
        )
        self.assertIn("tu-grant-exp-card", card)
        self.assertIn("Sistem Deteksi Anomali IoT", card)
        self.assertIn("Rp 100.000.000", card)
        self.assertIn("70%", card)
        self.assertIn("Survei Literatur", card)

    def test_render_course_reserve_book_card(self):
        card = EditorialComponents.render_course_reserve_book_card(
            title="Clean Architecture: A Craftsman's Guide",
            author="Robert C. Martin",
            call_number="QA76.76.D47 M37 2018",
            course_code="IF2143 Rekayasa Perangkat Lunak",
            available_copies=3
        )
        self.assertIn("tu-reserve-card", card)
        self.assertIn("Clean Architecture", card)
        self.assertIn("Robert C. Martin", card)
        self.assertIn("QA76.76.D47 M37 2018", card)
        self.assertIn("3 Eksemplar Tersedia", card)

    def test_render_alumni_tracer_stat_card(self):
        industries = [
            {"industry": "Teknologi Finansial & Perbankan", "percentage": 42},
            {"industry": "Software House & Konsultan IT", "percentage": 35}
        ]
        card = EditorialComponents.render_alumni_tracer_stat_card(
            cohort_year=2024,
            response_rate=88.5,
            avg_wait_months=2.4,
            top_industries=industries
        )
        self.assertIn("tu-tracer-card", card)
        self.assertIn("Angkatan 2024", card)
        self.assertIn("88.5%", card)
        self.assertIn("2.4 Bulan", card)
        self.assertIn("Teknologi Finansial", card)

    def test_render_curriculum_prerequisite_flow(self):
        html = EditorialComponents.render_curriculum_prerequisite_flow(
            course_code="TT302",
            course_name="Komunikasi Nirkabel",
            direct_prereqs=["TT201 Sinyal & Sistem", "TT203 Probabilitas"],
            unlocks_courses=["TT401 Jaringan Seluler Lanjut", "TT405 Radar"],
            min_credits_required=72
        )
        self.assertIn("tu-prereq-flow-card", html)
        self.assertIn("TT302", html)
        self.assertIn("Komunikasi Nirkabel", html)
        self.assertIn("TT201 Sinyal &amp; Sistem", html)
        self.assertIn("72 SKS", html)

    def test_render_lab_safety_equipment_card(self):
        ppes = [
            {"item": "Jas Laboratorium Katun", "required": "Wajib", "standard": "SNI 0115"},
            {"item": "Kacamata Pelindung (Goggles)", "required": "Wajib saat solder", "standard": "ANSI Z87.1"}
        ]
        contacts = [
            {"name": "Kepala Lab", "phone": "0281-641555"},
            {"name": "Satpam Kampus", "phone": "0812-9999-8888"}
        ]
        html = EditorialComponents.render_lab_safety_equipment_card("Lab Antena & Propagasi", ppes, contacts)
        self.assertIn("tu-lab-safety-card", html)
        self.assertIn("Lab Antena &amp; Propagasi", html)
        self.assertIn("Jas Laboratorium Katun", html)
        self.assertIn("0281-641555", html)

    def test_render_exchange_quota_table(self):
        partners = [
            {"university": "Universiti Teknologi Malaysia", "country": "Malaysia", "quota": 4, "min_gpa": 3.25, "language_requirement": "TOEFL 500"},
            {"university": "Kumamoto University", "country": "Jepang", "quota": 2, "min_gpa": 3.50, "language_requirement": "IELTS 6.0"}
        ]
        html = EditorialComponents.render_exchange_quota_table("IISMA Mandiri 2026", partners, "2026/2027")
        self.assertIn("tu-exchange-quota-container", html)
        self.assertIn("IISMA Mandiri 2026", html)
        self.assertIn("Universiti Teknologi Malaysia", html)
        self.assertIn("4 Mahasiswa", html)
        self.assertIn("IPK &ge; 3.25", html)

    def test_render_grant_funding_milestone_card(self):
        milestones = [
            {"phase": "Desain Prototipe", "status": "Selesai", "description": "Skema sirkuit RF selesai dirancang.", "progress_pct": 100},
            {"phase": "Uji Lapangan", "status": "Sedang Berjalan", "description": "Pengukuran redaman gelombang milimeter.", "progress_pct": 60}
        ]
        html = EditorialComponents.render_grant_funding_milestone_card(
            project_title="Rancang Bangun Antena MIMO 5G Purwokerto",
            grant_agency="Kemendikbudristek BIMA",
            budget_idr=125000000,
            milestones=milestones
        )
        self.assertIn("tu-grant-card", html)
        self.assertIn("Kemendikbudristek BIMA", html)
        self.assertIn("Rp 125.000.000", html)
        self.assertIn("Desain Prototipe", html)
        self.assertIn("100%", html)

    def test_render_tracer_salary_histogram(self):
        brackets = [
            {"bracket": "< Rp 5 Juta", "percentage": 12.5, "count": 10},
            {"bracket": "Rp 5 - 10 Juta", "percentage": 55.0, "count": 44},
            {"bracket": "> Rp 10 Juta", "percentage": 32.5, "count": 26}
        ]
        html = EditorialComponents.render_tracer_salary_histogram(
            cohort_year=2024,
            salary_brackets=brackets,
            median_salary_idr=8500000
        )
        self.assertIn("tu-salary-histogram-card", html)
        self.assertIn("Angkatan 2024", html)
        self.assertIn("Rp 8.500.000", html)
        self.assertIn("55.0%", html)
        self.assertIn("44 orang", html)

    def test_render_bloom_taxonomy_level_card(self):
        bloom_levels = [
            {"level": "C3", "cpl_code": "CPL-02", "description": "Menerapkan modulasi digital.", "weight_pct": 30},
            {"level": "C5", "cpl_code": "CPL-04", "description": "Mengevaluasi performa link radio.", "weight_pct": 40}
        ]
        html = EditorialComponents.render_bloom_taxonomy_level_card("TT-2103", "Sistem Komunikasi Radio", bloom_levels)
        self.assertIn("tu-bloom-card", html)
        self.assertIn("TT-2103", html)
        self.assertIn("Sistem Komunikasi Radio", html)
        self.assertIn("C3", html)
        self.assertIn("CPL-02", html)
        self.assertIn("Bobot: 30%", html)
        self.assertIn("Menerapkan modulasi digital", html)

    def test_render_hazardous_waste_protocol_card(self):
        waste = [
            {"category": "Limbah Asam Kuat", "container_type": "HDPE Biru", "storage_location": "Lemari B3", "safety_notes": "Sarung tangan nitril"}
        ]
        html = EditorialComponents.render_hazardous_waste_protocol_card(
            "Lab Kimia Material Telekomunikasi",
            waste,
            "Tiap akhir semester gasal"
        )
        self.assertIn("tu-waste-protocol-card", html)
        self.assertIn("Lab Kimia Material Telekomunikasi", html)
        self.assertIn("Limbah Asam Kuat", html)
        self.assertIn("HDPE Biru", html)
        self.assertIn("Tiap akhir semester gasal", html)

    def test_render_credit_transfer_matrix(self):
        mappings = [
            {
                "host_course_code": "ECE-301",
                "host_course_name": "Digital Signal Processing",
                "host_credits": 3,
                "home_course_code": "TT-3101",
                "home_course_name": "Pengolahan Sinyal Digital",
                "home_sks": 3,
                "status": "Disetujui"
            }
        ]
        html = EditorialComponents.render_credit_transfer_matrix("Universiti Teknologi Malaysia", mappings)
        self.assertIn("tu-credit-transfer-card", html)
        self.assertIn("Universiti Teknologi Malaysia", html)
        self.assertIn("ECE-301", html)
        self.assertIn("Digital Signal Processing", html)
        self.assertIn("TT-3101", html)
        self.assertIn("3 SKS", html)

    def test_render_patent_grant_card(self):
        html = EditorialComponents.render_patent_grant_card(
            patent_title="Antena Mikrostrip MIMO Fraktal Multi-Pita",
            patent_number="IDP000088921",
            inventors=["Dr. Wahyu Sedikit", "Fajar Hidayat"],
            filing_date="12 Maret 2025",
            status="Granted / Terdaftar",
            abstract="Inovasi antena mikrostrip untuk transceiver 5G pita gelombang milimeter."
        )
        self.assertIn("tu-patent-card", html)
        self.assertIn("Antena Mikrostrip MIMO Fraktal Multi-Pita", html)
        self.assertIn("IDP000088921", html)
        self.assertIn("Dr. Wahyu Sedikit, Fajar Hidayat", html)
        self.assertIn("Granted / Terdaftar", html)
        self.assertIn("Inovasi antena mikrostrip", html)

    def test_render_industry_partner_testimonial(self):
        html = EditorialComponents.render_industry_partner_testimonial(
            company_name="PT Telkom Indonesia",
            representative_name="Eko Prasetyo",
            position="VP Network Infrastructure",
            quote="Lulusan prodi memiliki kompetensi jaringan yang sangat siap pakai.",
            partner_logo_url="https://example.com/telkom.png",
            hired_alumni_count=18
        )
        self.assertIn("tu-partner-testimonial-card", html)
        self.assertIn("PT Telkom Indonesia", html)
        self.assertIn("Eko Prasetyo, VP Network Infrastructure", html)
        self.assertIn("siap pakai", html)
        self.assertIn("18 alumni", html)
        self.assertIn("https://example.com/telkom.png", html)

    def test_render_capstone_milestone_stepper(self):
        milestones = [
            {"step_number": 1, "title": "Seminar Proposal", "due_date": "Oktober 2026", "status": "Selesai"},
            {"step_number": 2, "title": "Seminar Hasil Riset", "due_date": "Desember 2026", "status": "Sedang Berjalan"},
            {"step_number": 3, "title": "Sidang Skripsi", "due_date": "Januari 2027", "status": "Menunggu"}
        ]
        html = EditorialComponents.render_capstone_milestone_stepper(
            "Deteksi Dini Retinopati Diabetik",
            milestones,
            current_step_index=2
        )
        self.assertIn("tu-capstone-stepper-card", html)
        self.assertIn("Deteksi Dini Retinopati Diabetik", html)
        self.assertIn("Seminar Proposal", html)
        self.assertIn("tu-step-completed", html)
        self.assertIn("tu-step-active", html)
        self.assertIn("Sidang Skripsi", html)

    def test_render_lab_workshop_banner(self):
        html = EditorialComponents.render_lab_workshop_banner(
            workshop_title="Hands-on Perancangan Antena 5G dengan CST Studio",
            speaker_name="Dr. Ir. Wahyu Sedikit, M.T.",
            speaker_affiliation="Laboratorium RF & Microwave",
            date_time="15 November 2026, 09:00 WIB",
            venue="Lab Antena Lt. 3",
            registration_url="https://lab-rf.prodi.ac.id/workshop-5g",
            quota_left=12
        )
        self.assertIn("tu-workshop-card", html)
        self.assertIn("Hands-on Perancangan Antena 5G", html)
        self.assertIn("Dr. Ir. Wahyu Sedikit, M.T.", html)
        self.assertIn("12 Kursi", html)
        self.assertIn("https://lab-rf.prodi.ac.id/workshop-5g", html)

    def test_render_internship_experience_card(self):
        html = EditorialComponents.render_internship_experience_card(
            student_name="Naufal Ilham",
            company_name="PT Telkomsel",
            role="Radio Access Network Engineer Intern",
            period="Agustus - Desember 2026",
            project_summary="Optimasi parameter handover pada 45 base station 5G NR area Purwokerto.",
            mentor_name="Budi Hartono (Senior RAN Specialist)"
        )
        self.assertIn("tu-internship-card", html)
        self.assertIn("PT Telkomsel", html)
        self.assertIn("Radio Access Network Engineer Intern", html)
        self.assertIn("Naufal Ilham", html)
        self.assertIn("Budi Hartono", html)
        self.assertIn("Optimasi parameter handover", html)

    def test_render_monograph_showcase_card(self):
        html = EditorialComponents.render_monograph_showcase_card(
            book_title="Pengolahan Sinyal Biomedis Modern",
            authors=["Prof. Dr. Ir. Sri Wahyuni", "Fatir Gibran"],
            publisher="Telkom University Press",
            isbn="978-623-123-456-7",
            year=2026,
            synopsis="Buku ajar komprehensif analisis wavelet dan deep learning untuk sinyal ECG.",
            purchase_url="https://press.telkomuniversity.ac.id/buku-biomedis"
        )
        self.assertIn("tu-monograph-card", html)
        self.assertIn("Pengolahan Sinyal Biomedis Modern", html)
        self.assertIn("Prof. Dr. Ir. Sri Wahyuni, Fatir Gibran", html)
        self.assertIn("978-623-123-456-7", html)
        self.assertIn("https://press.telkomuniversity.ac.id/buku-biomedis", html)

    def test_render_partner_university_profile_card(self):
        html = EditorialComponents.render_partner_university_profile_card(
            univ_name="Universiti Teknologi Malaysia (UTM)",
            country="Malaysia",
            world_ranking="QS Top 200",
            agreement_type="Student Exchange & Dual Degree",
            logo_url="https://example.com/utm-logo.png",
            contact_person="International Office UTM"
        )
        self.assertIn("tu-partner-univ-card", html)
        self.assertIn("Universiti Teknologi Malaysia (UTM)", html)
        self.assertIn("Malaysia", html)
        self.assertIn("QS Top 200", html)
        self.assertIn("Student Exchange &amp; Dual Degree", html)
        self.assertIn("International Office UTM", html)

    def test_render_community_service_card(self):
        html = EditorialComponents.render_community_service_card(
            title="Pelatihan IoT & Smart Farming",
            partner="Kelompok Tani Desa Kembaran",
            location="Banyumas, Jawa Tengah",
            grant_source="Hibah Pengabdian Kemendikbud",
            beneficiaries=50,
            sdgs_label="SDG 9 - Industri, Inovasi, dan Infrastruktur"
        )
        self.assertIn("tu-pkm-card", html)
        self.assertIn("Pelatihan IoT &amp; Smart Farming", html)
        self.assertIn("Kelompok Tani Desa Kembaran", html)
        self.assertIn("50 Orang", html)
        self.assertIn("SDG 9", html)

    def test_render_competition_achievement_card(self):
        html = EditorialComponents.render_competition_achievement_card(
            competition_name="Gemastik XVII Bidang Kota Cerdas",
            award_rank="Juara 1 (Medali Emas)",
            team_name="Tim Telematics SmartPurwokerto",
            team_members=["Fatir Gibran", "Ahmad Fauzi", "Rina Safitri"],
            supervisor="Dr. Eng. Ir. Bambang, M.T.",
            year=2026
        )
        self.assertIn("tu-competition-card", html)
        self.assertIn("Juara 1 (Medali Emas)", html)
        self.assertIn("Gemastik XVII", html)
        self.assertIn("Tim Telematics SmartPurwokerto", html)
        self.assertIn("Fatir Gibran", html)
        self.assertIn("Dr. Eng. Ir. Bambang", html)

    def test_render_journal_badge_card(self):
        html = EditorialComponents.render_journal_badge_card(
            journal_name="Jurnal Telematika dan Rekayasa Jaringan",
            sinta_rank=2,
            issn="2798-1234",
            publisher="Telkom University Press",
            focus_scope="Telekomunikasi Nirkabel, IoT, dan Antena",
            archive_url="https://journal.telkomuniversity.ac.id/jtrj"
        )
        self.assertIn("tu-journal-card", html)
        self.assertIn("SINTA 2", html)
        self.assertIn("2798-1234", html)
        self.assertIn("Telkom University Press", html)
        self.assertIn("https://journal.telkomuniversity.ac.id/jtrj", html)

    def test_render_teaching_assistant_recruitment_card(self):
        html = EditorialComponents.render_teaching_assistant_recruitment_card(
            course_name="Jaringan Komputer & Komunikasi Data",
            lab_name="Laboratorium Jaringan & Keamanan Siber",
            semester="Ganjil 2026/2027",
            min_grade="AB (3.50)",
            deadline="31 Agustus 2026",
            registration_url="https://lab.telkomuniversity.ac.id/recruitment"
        )
        self.assertIn("tu-ta-recruitment-card", html)
        self.assertIn("Jaringan Komputer", html)
        self.assertIn("AB (3.50)", html)
        self.assertIn("31 Agustus 2026", html)
        self.assertIn("https://lab.telkomuniversity.ac.id/recruitment", html)

    def test_render_lab_safety_guideline_card(self):
        html = EditorialComponents.render_lab_safety_guideline_card(
            lab_name="Laboratorium Elektronika & Instrumentasi",
            pic_technician="Budi Santoso, A.Md.",
            safety_rules=["Wajib jas laboratorium", "Gunakan alas kaki karet isolator", "Dilarang makan & minum"],
            emergency_call="Ext. 112 / APAR Ruang 204"
        )
        self.assertIn("tu-lab-safety-card", html)
        self.assertIn("Laboratorium Elektronika &amp; Instrumentasi", html)
        self.assertIn("Budi Santoso", html)
        self.assertIn("Wajib jas laboratorium", html)
        self.assertIn("Ext. 112 / APAR Ruang 204", html)

    def test_render_mbkm_credit_transfer_card(self):
        courses = [
            {"course_code": "IF3101", "course_name": "Cloud Computing", "sks": 4, "score_letter": "A"},
            {"course_code": "IF3102", "course_name": "Microservices", "sks": 4, "score_letter": "A"}
        ]
        html = EditorialComponents.render_mbkm_credit_transfer_card(
            program_name="Bangkit Academy 2026",
            partner="Google Indonesia",
            student_name="Fatir Gibran",
            nim="120122001",
            courses=courses,
            total_sks=8,
            converted_gpa=4.00,
            sk_number="SK-DEK/FTTE/09/2026"
        )
        self.assertIn("tu-mbkm-transfer-card", html)
        self.assertIn("Bangkit Academy 2026", html)
        self.assertIn("Google Indonesia", html)
        self.assertIn("Fatir Gibran", html)
        self.assertIn("120122001", html)
        self.assertIn("Cloud Computing", html)
        self.assertIn("8 SKS", html)
        self.assertIn("4.00", html)
        self.assertIn("SK-DEK/FTTE/09/2026", html)

    def test_render_yudisium_clearance_card(self):
        html = EditorialComponents.render_yudisium_clearance_card(
            student_name="Fatir Gibran",
            nim="120122001",
            thesis_title="Sistem Otomasi Portal Editorial Akademik Berbasis Microservices",
            ipk=3.85,
            predicate="Dengan Pujian (Cum Laude)",
            yudisium_date="20 Oktober 2026",
            verification_code="YUD-2026-FTTE-044"
        )
        self.assertIn("tu-yudisium-card", html)
        self.assertIn("Fatir Gibran", html)
        self.assertIn("120122001", html)
        self.assertIn("Sistem Otomasi Portal Editorial", html)
        self.assertIn("3.85", html)
        self.assertIn("Dengan Pujian (Cum Laude)", html)
        self.assertIn("YUD-2026-FTTE-044", html)

    def test_render_scopus_paper_showcase_card(self):
        html = EditorialComponents.render_scopus_paper_showcase_card(
            title="Optimizing Edge AI Routing in 6G Heterogeneous Networks",
            authors=["Fatir Gibran", "Dr. Bambang", "Prof. Tanaka"],
            journal_name="IEEE Transactions on Network and Service Management",
            quartile="Q1",
            sjr_score=1.92,
            doi="10.1109/TNSM.2026.334455",
            citation_count=14
        )
        self.assertIn("tu-scopus-paper-card", html)
        self.assertIn("Scopus Q1", html)
        self.assertIn("1.92", html)
        self.assertIn("Optimizing Edge AI Routing", html)
        self.assertIn("Fatir Gibran", html)
        self.assertIn("IEEE Transactions on Network", html)
        self.assertIn("10.1109/TNSM.2026.334455", html)

    def test_render_lab_equipment_status_card(self):
        html = EditorialComponents.render_lab_equipment_status_card(
            asset_id="LAB-RF-2026-088",
            equipment_name="Digital Spectrum Analyzer 13.6 GHz",
            lab_name="Laboratorium RF & Microwave",
            condition="Baik",
            cal_status="Valid",
            next_due_date="2027-04-15",
            pic="Laboran Ahmad, S.T."
        )
        self.assertIn("tu-lab-equipment-card", html)
        self.assertIn("LAB-RF-2026-088", html)
        self.assertIn("Digital Spectrum Analyzer", html)
        self.assertIn("tu-cal-valid", html)
        self.assertIn("Valid", html)
        self.assertIn("2027-04-15", html)

    def test_render_visiting_professor_card(self):
        html = EditorialComponents.render_visiting_professor_card(
            name="Prof. Dr. Hiroshi Tanaka",
            title_role="Chair of Optical Communications",
            home_university="The University of Tokyo",
            country="Jepang",
            lecture_topic="Next-Generation Terabit Optical Transceivers for Datacenters",
            date_time="5 November 2026, 09:00 WIB",
            registration_url="https://event.telkomuniversity.ac.id/visiting-prof"
        )
        self.assertIn("tu-visiting-prof-card", html)
        self.assertIn("Prof. Dr. Hiroshi Tanaka", html)
        self.assertIn("The University of Tokyo", html)
        self.assertIn("Jepang", html)
        self.assertIn("Next-Generation Terabit Optical Transceivers", html)
        self.assertIn("https://event.telkomuniversity.ac.id/visiting-prof", html)

    def test_render_kkn_village_profile_card(self):
        html = EditorialComponents.render_kkn_village_profile_card(
            group_code="KKN-01",
            village_name="Beji",
            district="Kedungbanteng",
            regency="Banyumas",
            supervisor_dpl="Dr. Ir. Budi",
            student_count=12,
            thematic_focus="Smart Village & Pertanian Presisi",
            flagship_program="Instalasi Sensor Tanah LoRa & Website Desa"
        )
        self.assertIn("tu-kkn-village-card", html)
        self.assertIn("KKN-01", html)
        self.assertIn("Desa Beji", html)
        self.assertIn("Kedungbanteng", html)
        self.assertIn("Banyumas", html)
        self.assertIn("Dr. Ir. Budi", html)
        self.assertIn("12 Mahasiswa", html)
        self.assertIn("Smart Village &amp; Pertanian Presisi", html)

    def test_render_faculty_bkd_compliance_card(self):
        breakdown = {
            "pendidikan": 8.0,
            "penelitian": 3.0,
            "pengabdian": 1.5,
            "penunjang": 1.0
        }
        html = EditorialComponents.render_faculty_bkd_compliance_card(
            lecturer_name="Dr. Eng. Ir. Suryo",
            nidn="0612345601",
            academic_rank="Lektor Kepala",
            semester="Ganjil 2026/2027",
            total_sks=13.5,
            is_compliant=True,
            breakdown=breakdown
        )
        self.assertIn("tu-faculty-bkd-card", html)
        self.assertIn("Dr. Eng. Ir. Suryo", html)
        self.assertIn("0612345601", html)
        self.assertIn("Lektor Kepala", html)
        self.assertIn("MEMENUHI KETENTUAN", html)
        self.assertIn("tu-bkd-compliant", html)
        self.assertIn("13.50 SKS", html)

    def test_render_core_conference_showcase_card(self):
        html = EditorialComponents.render_core_conference_showcase_card(
            paper_title="Distributed Consensus in 6G UAV Swarms",
            authors=["Fatir Gibran", "Dr. Bambang"],
            conference_name="IEEE International Conference on Computer Communications",
            acronym="INFOCOM",
            core_tier="A*",
            publisher="IEEE Xplore",
            year=2026,
            presentation_city="San Francisco, USA"
        )
        self.assertIn("tu-core-conf-card", html)
        self.assertIn("CORE Rank A*", html)
        self.assertIn("tu-core-astar", html)
        self.assertIn("Distributed Consensus in 6G UAV Swarms", html)
        self.assertIn("INFOCOM 2026", html)
        self.assertIn("San Francisco, USA", html)
        self.assertIn("IEEE Xplore", html)

    def test_render_academic_warning_counseling_card(self):
        html = EditorialComponents.render_academic_warning_counseling_card(
            student_name="Budi Santoso",
            nim="120122011",
            warning_level="SP-1",
            cumulative_gpa=1.92,
            earned_credits=38,
            remedial_target_sks=10,
            advisor_name="Ir. Hendra, M.T.",
            counseling_deadline="30 Oktober 2026"
        )
        self.assertIn("tu-academic-warning-card", html)
        self.assertIn("Peringatan Akademik (SP-1)", html)
        self.assertIn("Budi Santoso", html)
        self.assertIn("120122011", html)
        self.assertIn("1.92", html)
        self.assertIn("38 SKS", html)
        self.assertIn("10 SKS", html)
        self.assertIn("Ir. Hendra, M.T.", html)
        self.assertIn("30 Oktober 2026", html)

    def test_render_biomedical_telemetry_showcase_card(self):
        html = EditorialComponents.render_biomedical_telemetry_showcase_card(
            innovation_title="Wearable ECG Telemetry Node for Rural Clinics",
            clinical_partner="RS Margono Soekarjo Purwokerto",
            telemetry_protocol="LoRaWAN 920 MHz & MQTT",
            sensor_nodes=["AD8232 ECG Sensor", "MAX30102 Pulse Oximeter"],
            impact_summary="Pemantauan aritmia jantung jarak jauh real-time untuk puskesmas daerah pelosok.",
            demo_video_url="https://youtube.com/watch?v=biomed-demo"
        )
        self.assertIn("tu-biomedical-telemetry-card", html)
        self.assertIn("Telemetri Biomedis &amp; e-Health", html)
        self.assertIn("Wearable ECG Telemetry Node", html)
        self.assertIn("RS Margono Soekarjo Purwokerto", html)
        self.assertIn("LoRaWAN 920 MHz &amp; MQTT", html)
        self.assertIn("AD8232 ECG Sensor", html)
        self.assertIn("https://youtube.com/watch?v=biomed-demo", html)

if __name__ == "__main__":
    unittest.main()





