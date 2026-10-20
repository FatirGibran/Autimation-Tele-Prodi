import unittest
from formatters import TelegramFormatter

class TestTelegramFormatter(unittest.TestCase):
    def test_format_seo_report(self):
        meta = {
            "focus_keyphrase": "teknologi iot",
            "seo_title": "Teknologi IoT Terkini",
            "slug": "teknologi-iot-terkini",
            "meta_description": "Pelajari perkembangan teknologi iot terbaru di Telkom University Purwokerto."
        }
        res = {
            "is_all_green": True,
            "score": 100,
            "checks": {
                "word_count": {"passed": True, "value": 450},
                "keyphrase_in_meta": {"passed": True}
            },
            "warnings": ["Pastikan gambar di-upload."]
        }
        output = TelegramFormatter.format_seo_report(meta, res)
        self.assertIn("YOAST SEO METADATA", output)
        self.assertIn("teknologi-iot-terkini", output)
        self.assertIn("Word Count (450)", output)
        self.assertIn("Pastikan gambar di-upload.", output)

    def test_format_stats_report(self):
        stats = {
            "total_articles": 15,
            "published_count": 5,
            "ready_count": 7,
            "needs_review_count": 3
        }
        output = TelegramFormatter.format_stats_report(stats)
        self.assertIn("Ringkasan Statistik Editorial", output)
        self.assertIn("Total Artikel: `15`", output)
        self.assertIn("Terpublikasi / WP Draft: `5`", output)

    def test_format_article_summary_card(self):
        art = {
            "id": 42,
            "topic": "Sistem Terdistribusi",
            "seo_title": "Sistem Terdistribusi di Cloud",
            "category": "Jaringan & Cloud",
            "publish_date": "2026-09-29",
            "focus_keyphrase": "sistem terdistribusi",
            "slug": "sistem-terdistribusi-cloud",
            "status": "ready",
            "wp_post_id": 999
        }
        output = TelegramFormatter.format_article_summary_card(art)
        self.assertIn("Detail Artikel (ID: 42)", output)
        self.assertIn("**WP Post ID:** `999`", output)
        self.assertIn("sistem-terdistribusi-cloud", output)

    def test_format_score_progress_bar(self):
        bar_high = TelegramFormatter.format_score_progress_bar(95)
        self.assertIn("100/100" if 100 in [95] else "95/100", bar_high)
        self.assertIn("Sempurna", bar_high)
        self.assertIn("█", bar_high)

        bar_low = TelegramFormatter.format_score_progress_bar(40)
        self.assertIn("40/100", bar_low)
        self.assertIn("Kritis", bar_low)

    def test_format_readability_badge(self):
        badge_good = TelegramFormatter.format_readability_badge(72.5)
        self.assertIn("🟢", badge_good)
        self.assertIn("72.5", badge_good)

        badge_poor = TelegramFormatter.format_readability_badge(30.0, label="Sulit Dibaca")
        self.assertIn("🔴", badge_poor)
        self.assertIn("Sulit Dibaca", badge_poor)

    def test_build_review_management_keyboard(self):
        keyboard = TelegramFormatter.build_review_management_keyboard(123, "test-slug")
        self.assertIn("inline_keyboard", keyboard)
        buttons = [btn["text"] for row in keyboard["inline_keyboard"] for btn in row]
        self.assertTrue(any("Setujui" in t for t in buttons))
        self.assertTrue(any("Revisi" in t for t in buttons))
        self.assertTrue(any(btn["callback_data"] == "approve:123" for row in keyboard["inline_keyboard"] for btn in row))

    def test_format_editorial_diff_preview(self):
        old_data = {
            "id": 10,
            "seo_title": "Judul Lama",
            "focus_keyphrase": "keyphrase lama",
            "status": "draft",
            "html_content": "<p>Satu dua tiga empat lima.</p>"
        }
        new_data = {
            "id": 10,
            "seo_title": "Judul Baru yang Diperbarui",
            "focus_keyphrase": "keyphrase baru",
            "status": "ready",
            "html_content": "<p>Satu dua tiga empat lima enam tujuh delapan.</p>"
        }
        diff_text = TelegramFormatter.format_editorial_diff_preview(old_data, new_data)
        self.assertIn("Perbandingan Revisi Editorial", diff_text)
        self.assertIn("Judul Lama", diff_text)
        self.assertIn("Judul Baru yang Diperbarui", diff_text)
        self.assertIn("keyphrase baru", diff_text)
        self.assertIn("ready", diff_text)
        self.assertIn("kata", diff_text)

    def test_format_scheduled_reminder_card(self):
        article = {
            "seo_title": "Peluncuran Lab Baru",
            "category": "Infrastruktur",
            "slug": "peluncuran-lab-baru"
        }
        card = TelegramFormatter.format_scheduled_reminder_card(article, "2026-10-10 10:00 WIB")
        self.assertIn("Pengingat Jadwal Terbit Artikel", card)
        self.assertIn("Peluncuran Lab Baru", card)
        self.assertIn("Infrastruktur", card)
        self.assertIn("2026-10-10 10:00 WIB", card)
        self.assertIn("peluncuran-lab-baru", card)

    def test_format_bibtex_telegram_card(self):
        article = {
            "seo_title": "Riset Keamanan IoT",
            "slug": "riset-keamanan-iot",
            "publish_date": "2026-10-01"
        }
        card = TelegramFormatter.format_bibtex_telegram_card(article)
        self.assertIn("Sitasi Akademik BibTeX", card)
        self.assertIn("@article{telkom_bif_riset_keamanan_iot_2026", card)
        self.assertIn("title = {Riset Keamanan IoT}", card)
        self.assertIn("https://bif-pwt.telkomuniversity.ac.id/riset-keamanan-iot/", card)

    def test_format_plagiarism_alert_card(self):
        card_low = TelegramFormatter.format_plagiarism_alert_card("Judul Aman", 8.5, [])
        self.assertIn("AMAN", card_low)
        self.assertIn("8.5%", card_low)

        sources = [{"url": "https://journal.org/paper1", "percent": 28.4}]
        card_high = TelegramFormatter.format_plagiarism_alert_card("Judul Plagiat", 32.0, sources)
        self.assertIn("DITOLAK", card_high)
        self.assertIn("32.0%", card_high)
        self.assertIn("https://journal.org/paper1", card_high)
        self.assertIn("28.4%", card_high)

    def test_format_conference_call_card(self):
        tracks = ["Artificial Intelligence", "Cybersecurity", "IoT Systems"]
        card = TelegramFormatter.format_conference_call_card(
            conf_name="ICITACEE 2026",
            deadline_str="15 November 2026",
            tracks=tracks,
            submission_url="https://icess.org/submit"
        )
        self.assertIn("ICITACEE 2026", card)
        self.assertIn("15 November 2026", card)
        self.assertIn("Artificial Intelligence", card)
        self.assertIn("https://icess.org/submit", card)

    def test_format_compact_seo_summary(self):
        report = {
            "score": 88,
            "grade": "Bagus Sekali",
            "errors": [],
            "warnings": ["Heading structure needs improvement"]
        }
        card = TelegramFormatter.format_compact_seo_summary(report, "webassembly-edge-computing-iot")
        self.assertIn("Ringkasan Audit SEO Yoast", card)
        self.assertIn("webassembly-edge-computing-iot", card)
        self.assertIn("88/100", card)
        self.assertIn("**Errors:** `0`", card)
        self.assertIn("**Warnings:** `1`", card)

    def test_format_capstone_defense_card(self):
        card = TelegramFormatter.format_capstone_defense_card(
            candidate_name="Fatir Gibran",
            thesis_title="Sistem Automasi Editorial Publikasi Program Studi Berbasis NLP",
            room_or_link="Lab Jaringan Komputer Lt. 3",
            examiners=["Dr. Eng. Ir. Budi Raharjo, M.T.", "Prof. Dr. Ir. Sri Wahyuni, M.Sc."],
            schedule_time="Kamis, 15 Oktober 2026 09:00 WIB"
        )
        self.assertIn("Jadwal Sidang Tugas Akhir Mahasiswa", card)
        self.assertIn("Fatir Gibran", card)
        self.assertIn("Lab Jaringan Komputer Lt. 3", card)
        self.assertIn("Dr. Eng. Ir. Budi Raharjo, M.T.", card)
        self.assertIn("Prof. Dr. Ir. Sri Wahyuni, M.Sc.", card)

    def test_format_weekly_editorial_digest(self):
        digest = TelegramFormatter.format_weekly_editorial_digest(
            week_range="5 - 11 Oktober 2026",
            published_count=12,
            top_categories=[{"name": "Akademik", "count": 7}, {"name": "Riset & Pengabdian", "count": 5}],
            highlights=["Publikasi jurnal bereputasi Q1", "Pembukaan pendaftaran capstone batch 2"]
        )
        self.assertIn("Ringkasan Editorial Mingguan (5 - 11 Oktober 2026)", digest)
        self.assertIn("Total Diterbitkan: `12` artikel", digest)
        self.assertIn("Akademik: 7 artikel", digest)
        self.assertIn("Publikasi jurnal bereputasi Q1", digest)

    def test_format_conference_reminder_card(self):
        card = TelegramFormatter.format_conference_reminder_card(
            conf_name="IEEE CyberTech 2026",
            deadline="1 November 2026",
            venue="Bali Nusa Dua Convention Center",
            registration_fee="Rp 2.500.000 (Author)",
            submit_url="https://cybertech2026.org/cfp"
        )
        self.assertIn("Pemberitahuan Call for Papers", card)
        self.assertIn("IEEE CyberTech 2026", card)
        self.assertIn("1 November 2026", card)
        self.assertIn("Bali Nusa Dua Convention Center", card)
        self.assertIn("https://cybertech2026.org/cfp", card)

    def test_format_student_achievement_broadcast(self):
        card = TelegramFormatter.format_student_achievement_broadcast(
            event_name="National Hackathon AI Kemendikbud 2026",
            winner_names=["Aditya Pratama", "Nabila Putri"],
            award_title="Juara 1 Grand Winner",
            level="Tingkat Nasional",
            supervisor_name="Dr. Ir. Hendra, M.T."
        )
        self.assertIn("Prestasi Membanggakan Mahasiswa Informatika", card)
        self.assertIn("Juara 1 Grand Winner (Tingkat Nasional)", card)
        self.assertIn("National Hackathon AI Kemendikbud 2026", card)
        self.assertIn("Aditya Pratama", card)
        self.assertIn("Dr. Ir. Hendra, M.T.", card)

    def test_format_scholarship_announcement_card(self):
        card = TelegramFormatter.format_scholarship_announcement_card(
            scholarship_name="Beasiswa Unggulan Prestasi 2026",
            sponsor="Yayasan Pendidikan Telkom",
            coverage="Bebas BPP 100% + Uang Saku Bulanan",
            deadline="25 Oktober 2026",
            eligibility=["Mahasiswa aktif semester 3 - 5", "IPK minimal 3.50"],
            apply_url="https://beasiswa.telkomuniversity.ac.id/apply"
        )
        self.assertIn("Informasi Pembukaan Beasiswa Pendidikan", card)
        self.assertIn("Beasiswa Unggulan Prestasi 2026", card)
        self.assertIn("Yayasan Pendidikan Telkom", card)
        self.assertIn("Bebas BPP 100%", card)
        self.assertIn("25 Oktober 2026", card)
        self.assertIn("IPK minimal 3.50", card)

    def test_format_journal_publication_alert(self):
        card = TelegramFormatter.format_journal_publication_alert(
            paper_title="Reinforcement Learning for Edge Drone Trajectory",
            authors=["Fajar Nugraha", "Budi Santoso"],
            journal_name="IEEE Transactions on Communications",
            quartile="Q1 - Scopus Top 5%",
            doi_url="https://doi.org/10.1109/TCOMM.2026.12345"
        )
        self.assertIn("Publikasi Jurnal Ilmiah Internasional Baru", card)
        self.assertIn("Reinforcement Learning for Edge Drone Trajectory", card)
        self.assertIn("Fajar Nugraha, Budi Santoso", card)
        self.assertIn("IEEE Transactions on Communications", card)
        self.assertIn("Q1 - Scopus Top 5%", card)
        self.assertIn("https://doi.org/10.1109/TCOMM.2026.12345", card)

    def test_format_patent_registration_card(self):
        card = TelegramFormatter.format_patent_registration_card(
            patent_title="Metode Kompresi Sinyal Bio-Medis Berbasis Wavelet",
            patent_number="IDS000004512",
            inventors=["Dr. Wahyu Sedikit", "Fatir Gibran"],
            filing_date="10 Oktober 2026",
            official_url="https://pdki-indonesia.dgip.go.id/patent/IDS000004512"
        )
        self.assertIn("Paten & Hak Kekayaan Intelektual Resmi Terdaftar", card)
        self.assertIn("Metode Kompresi Sinyal Bio-Medis", card)
        self.assertIn("IDS000004512", card)
        self.assertIn("Dr. Wahyu Sedikit, Fatir Gibran", card)
        self.assertIn("10 Oktober 2026", card)
        self.assertIn("https://pdki-indonesia.dgip.go.id/patent/IDS000004512", card)

    def test_format_credit_transfer_approval_card(self):
        courses = [
            {"host_course": "ECE 302 Signals", "home_course": "Pengolahan Sinyal", "sks": "3"},
            {"host_course": "ECE 401 Antennas", "home_course": "Antena & Propagasi", "sks": "4"}
        ]
        card = TelegramFormatter.format_credit_transfer_approval_card(
            student_name="Ahmad Fauzi",
            host_univ="Universiti Malaya",
            approved_courses=courses,
            total_ects=12.0,
            total_sks=7
        )
        self.assertIn("Persetujuan Konversi & Transfer Kredit Akademik", card)
        self.assertIn("Ahmad Fauzi", card)
        self.assertIn("Universiti Malaya", card)
        self.assertIn("12.0 ECTS", card)
        self.assertIn("7 SKS", card)
        self.assertIn("ECE 302 Signals", card)

    def test_format_workshop_invitation_card(self):
        card = TelegramFormatter.format_workshop_invitation_card(
            workshop_title="Kupas Tuntas Antena MIMO 5G dan Pengukuran SAR",
            speaker_name="Dr. Ir. Wahyu Sedikit, M.T.",
            speaker_title="Kepala Lab RF & Gelombang Mikro",
            schedule_time="Sabtu, 21 November 2026, 09:00 WIB",
            platform_or_room="Lab Jaringan Nirkabel Lt. 2",
            registration_url="https://bif-pwt.telkomuniversity.ac.id/workshop-mimo",
            quota=30
        )
        self.assertIn("Undangan Workshop & Pelatihan Akademik", card)
        self.assertIn("Kupas Tuntas Antena MIMO 5G", card)
        self.assertIn("Dr. Ir. Wahyu Sedikit, M.T.", card)
        self.assertIn("30 kursi", card)
        self.assertIn("https://bif-pwt.telkomuniversity.ac.id/workshop-mimo", card)

    def test_format_thesis_defense_schedule_broadcast(self):
        card = TelegramFormatter.format_thesis_defense_schedule_broadcast(
            student_name="Fatir Gibran",
            nim="1201220011",
            thesis_title="Sistem Otomasi Pipeline Publikasi Berbasis Multi-Agent LLM",
            room="Ruang Sidang Utama Fakultas Informatika",
            schedule="Senin, 19 Oktober 2026 13:00 WIB",
            chief_examiner="Prof. Dr. Ir. Adiwijaya, M.Kom."
        )
        self.assertIn("Jadwal Sidang Terbuka Tugas Akhir Mahasiswa", card)
        self.assertIn("Fatir Gibran", card)
        self.assertIn("1201220011", card)
        self.assertIn("Sistem Otomasi Pipeline Publikasi", card)
        self.assertIn("Prof. Dr. Ir. Adiwijaya, M.Kom.", card)
        self.assertIn("Ruang Sidang Utama", card)

    def test_format_community_service_broadcast(self):
        card = TelegramFormatter.format_community_service_broadcast(
            activity_title="Pelatihan AI dan Literasi Digital Sekolah",
            partner_name="SMK Telkom Purwokerto",
            location="Banyumas, Jawa Tengah",
            leader_name="Dr. Ir. Wahyu, M.T.",
            sdgs_theme="SDG 4 - Pendidikan Berkualitas",
            beneficiaries=65
        )
        self.assertIn("Laporan Kegiatan Pengabdian kepada Masyarakat (PKM)", card)
        self.assertIn("Pelatihan AI dan Literasi Digital Sekolah", card)
        self.assertIn("SMK Telkom Purwokerto", card)
        self.assertIn("Dr. Ir. Wahyu, M.T.", card)
        self.assertIn("SDG 4 - Pendidikan Berkualitas", card)
        self.assertIn("65 Orang", card)

    def test_format_competition_award_broadcast(self):
        card = TelegramFormatter.format_competition_award_broadcast(
            competition_name="Imagine Cup Asia 2026",
            award_title="Juara 1 Regional Winner",
            team_name="Tim Garuda Telematics",
            member_names=["Fatir Gibran", "Bayu Pratama"],
            organizer="Microsoft Asia Pacific"
        )
        self.assertIn("Selamat & Sukses atas Prestasi Mahasiswa!", card)
        self.assertIn("Juara 1 Regional Winner", card)
        self.assertIn("Imagine Cup Asia 2026", card)
        self.assertIn("Microsoft Asia Pacific", card)
        self.assertIn("Tim Garuda Telematics", card)
        self.assertIn("Fatir Gibran, Bayu Pratama", card)

    def test_format_yudisium_congratulations_broadcast(self):
        msg = TelegramFormatter.format_yudisium_congratulations_broadcast(
            student_name="Fatir Gibran",
            nim="120122001",
            thesis_title="Sistem Otomasi Portal Editorial Akademik",
            ipk=3.85,
            predicate="Dengan Pujian (Cum Laude)",
            yudisium_date="20 Oktober 2026"
        )
        self.assertIn("Selamat & Sukses atas Kelulusan Yudisium Sarjana!", msg)
        self.assertIn("Fatir Gibran", msg)
        self.assertIn("120122001", msg)
        self.assertIn("Sistem Otomasi Portal Editorial Akademik", msg)
        self.assertIn("3.85", msg)
        self.assertIn("Dengan Pujian (Cum Laude)", msg)
        self.assertIn("20 Oktober 2026", msg)

    def test_format_visiting_lecture_broadcast(self):
        msg = TelegramFormatter.format_visiting_lecture_broadcast(
            speaker_name="Prof. Dr. Hiroshi Tanaka",
            speaker_origin="The University of Tokyo, Jepang",
            lecture_topic="Next-Gen Terabit Optical Transceivers",
            date_time="5 November 2026, 09:00 WIB",
            venue="Auditorium Gedung Rektorat Lt. 3 & Zoom Meeting",
            registration_url="https://event.telkomuniversity.ac.id/visiting-prof"
        )
        self.assertIn("Undangan Kuliah Umum Dosen Tamu Internasional (Visiting Professor)", msg)
        self.assertIn("Prof. Dr. Hiroshi Tanaka", msg)
        self.assertIn("The University of Tokyo, Jepang", msg)
        self.assertIn("Next-Gen Terabit Optical Transceivers", msg)
        self.assertIn("5 November 2026, 09:00 WIB", msg)
        self.assertIn("https://event.telkomuniversity.ac.id/visiting-prof", msg)

    def test_format_kkn_village_completion_broadcast(self):
        msg = TelegramFormatter.format_kkn_village_completion_broadcast(
            group_code="KKN-TM-04",
            village_name="Cibodas",
            district="Pasirjambu",
            regency="Bandung",
            supervisor_dpl="Dr. Eng. Ahmad Fauzi",
            student_count=12,
            theme="Digitalisasi Desa Wisata & Smart Agriculture",
            flagship_outcome="Implementasi IoT Sensor Kelembapan Tanah Kebun Stroberi",
            documentation_url="https://kkn.telkomuniversity.ac.id/cibodas-04"
        )
        self.assertIn("Diseminasi & Penutupan KKN Tematik Mahasiswa", msg)
        self.assertIn("KKN-TM-04", msg)
        self.assertIn("Desa Cibodas, Kec. Pasirjambu, Kab. Bandung", msg)
        self.assertIn("Dr. Eng. Ahmad Fauzi", msg)
        self.assertIn("12 Mahasiswa", msg)
        self.assertIn("Digitalisasi Desa Wisata", msg)
        self.assertIn("Implementasi IoT Sensor", msg)
        self.assertIn("https://kkn.telkomuniversity.ac.id/cibodas-04", msg)

    def test_format_core_conference_presentation_broadcast(self):
        msg = TelegramFormatter.format_core_conference_presentation_broadcast(
            paper_title="Deep Reinforcement Learning for 6G Satellite Telemetry",
            presenter_name="Fatir Gibran",
            conference_name="IEEE International Conference on Communications",
            acronym="ICC 2026",
            core_tier="A",
            city="Montreal, Canada",
            date_str="14-18 Juni 2026",
            paper_url="https://doi.org/10.1109/ICC.2026.9876543"
        )
        self.assertIn("Diseminasi Riset Konferensi Internasional (CORE Ranked)", msg)
        self.assertIn("Deep Reinforcement Learning for 6G Satellite Telemetry", msg)
        self.assertIn("Fatir Gibran", msg)
        self.assertIn("IEEE International Conference on Communications (ICC 2026)", msg)
        self.assertIn("Peringkat A", msg)
        self.assertIn("Montreal, Canada", msg)
        self.assertIn("14-18 Juni 2026", msg)
        self.assertIn("https://doi.org/10.1109/ICC.2026.9876543", msg)

    def test_format_bima_grant_award_broadcast(self):
        msg = TelegramFormatter.format_bima_grant_award_broadcast(
            project_title="Optimasi MIMO 5G Beamforming Menggunakan Deep Learning",
            lead_researcher="Dr. Ir. Suryo",
            scheme_name="Penelitian Terapan (PT)",
            funding_amount=145000000.0,
            fiscal_year=2026,
            contract_no="045/E1/KS/2026"
        )
        self.assertIn("Pengumuman Pemenang Hibah Riset Kemdikbud BIMA", msg)
        self.assertIn("Optimasi MIMO 5G Beamforming", msg)
        self.assertIn("Dr. Ir. Suryo", msg)
        self.assertIn("Penelitian Terapan (PT)", msg)
        self.assertIn("Rp 145,000,000", msg)
        self.assertIn("2026", msg)
        self.assertIn("045/E1/KS/2026", msg)

    def test_format_kerja_praktik_showcase_broadcast(self):
        msg = TelegramFormatter.format_kerja_praktik_showcase_broadcast(
            student_name="Fatir Gibran",
            nim="120122001",
            company_name="PT Telkom Indonesia",
            project_title="Automated Quality Monitoring for 5G Core Network",
            duration_weeks=10,
            report_url="https://repository.telkomuniversity.ac.id/kp/120122001"
        )
        self.assertIn("Diseminasi & Kelulusan Kerja Praktik (KP) Mahasiswa", msg)
        self.assertIn("Fatir Gibran", msg)
        self.assertIn("120122001", msg)
        self.assertIn("PT Telkom Indonesia", msg)
        self.assertIn("Automated Quality Monitoring for 5G Core Network", msg)
        self.assertIn("10 Minggu", msg)
        self.assertIn("https://repository.telkomuniversity.ac.id/kp/120122001", msg)

    def test_format_accreditation_announcement_telegram(self):
        msg = TelegramFormatter.format_accreditation_announcement_telegram(
            program_name="S1 Teknik Telekomunikasi",
            agency="LAM INFOKOM",
            rating="Unggul",
            sk_number="042/SK/LAM-INFOKOM/Ak/S/VIII/2024",
            valid_until="2029-08-31",
            portal_url="https://akreditasi.telkomuniversity.ac.id/tele"
        )
        self.assertIn("Pengumuman Resmi Akreditasi Program Studi", msg)
        self.assertIn("S1 Teknik Telekomunikasi", msg)
        self.assertIn("LAM INFOKOM", msg)
        self.assertIn("Unggul", msg)
        self.assertIn("042/SK/LAM-INFOKOM/Ak/S/VIII/2024", msg)
        self.assertIn("2029-08-31", msg)
        self.assertIn("https://akreditasi.telkomuniversity.ac.id/tele", msg)

    def test_format_scholarship_announcement_telegram(self):
        msg = TelegramFormatter.format_scholarship_announcement_telegram(
            student_name="Bayu Pratama",
            nim="120120001",
            scholarship_type="Beasiswa Prestasi Unggulan",
            sponsor_name="Yayasan Pendidikan Telkom",
            amount_idr=7500000.0,
            semester="Semester Ganjil 2026/2027",
            portal_url="https://beasiswa.telkomuniversity.ac.id/pengumuman-001"
        )
        self.assertIn("Pengumuman Penerima Beasiswa & Bantuan Pendidikan", msg)
        self.assertIn("Bayu Pratama", msg)
        self.assertIn("120120001", msg)
        self.assertIn("Beasiswa Prestasi Unggulan", msg)
        self.assertIn("Yayasan Pendidikan Telkom", msg)
        self.assertIn("Rp 7,500,000", msg)
        self.assertIn("Semester Ganjil 2026/2027", msg)
        self.assertIn("https://beasiswa.telkomuniversity.ac.id/pengumuman-001", msg)

    def test_format_cum_laude_announcement_telegram(self):
        msg = TelegramFormatter.format_cum_laude_announcement_telegram(
            student_name="Dewi Sartika",
            nim="120120005",
            ipk=3.92,
            honor_predicate="Dengan Pujian (Cum Laude)",
            thesis_title="Optimasi MIMO Beamforming 5G",
            portal_url="https://akademik.telkomuniversity.ac.id/yudisium/120120005"
        )
        self.assertIn("Apresiasi Kelulusan Dengan Pujian", msg)
        self.assertIn("Dewi Sartika", msg)
        self.assertIn("120120005", msg)
        self.assertIn("3.92", msg)
        self.assertIn("Dengan Pujian (Cum Laude)", msg)
        self.assertIn("Optimasi MIMO Beamforming 5G", msg)
        self.assertIn("https://akademik.telkomuniversity.ac.id/yudisium/120120005", msg)

    def test_format_tridharma_grant_announcement_telegram(self):
        msg = TelegramFormatter.format_tridharma_grant_announcement_telegram(
            lecturer_name="Dr. Ir. Budi Santoso, M.T.",
            nidn="0612058001",
            project_title="Rancang Bangun Sensor Akustik Kelautan",
            grant_amount=25000000.0,
            fiscal_year=2026,
            publication_target="Jurnal SINTA 2",
            portal_url="https://lppm.telkomuniversity.ac.id/hibah-2026"
        )
        self.assertIn("Pengumuman Pemenang Hibah Riset Internal LPPM", msg)
        self.assertIn("Dr. Ir. Budi Santoso, M.T.", msg)
        self.assertIn("0612058001", msg)
        self.assertIn("2026", msg)
        self.assertIn("Rp 25.000.000", msg)
        self.assertIn("Rancang Bangun Sensor Akustik Kelautan", msg)
        self.assertIn("Jurnal SINTA 2", msg)
        self.assertIn("https://lppm.telkomuniversity.ac.id/hibah-2026", msg)

    def test_format_fast_track_announcement_telegram(self):
        msg = TelegramFormatter.format_fast_track_announcement_telegram(
            student_name="Ahmad Zaki",
            nim="1101230045",
            ipk=3.75,
            masters_program="Magister Teknik Telekomunikasi",
            portal_url="https://akademik.telkomuniversity.ac.id/fast-track"
        )
        self.assertIn("Program Akselerasi S1 + S2 (Fast-Track)", msg)
        self.assertIn("Ahmad Zaki", msg)
        self.assertIn("1101230045", msg)
        self.assertIn("3.75", msg)
        self.assertIn("Magister Teknik Telekomunikasi", msg)
        self.assertIn("https://akademik.telkomuniversity.ac.id/fast-track", msg)

    def test_format_hki_copyright_announcement_telegram(self):
        msg = TelegramFormatter.format_hki_copyright_announcement_telegram(
            work_title="Perangkat Lunak Simulasi Propagasi Gelombang Mikro 5G",
            creators=["Dr. Ir. Budi Santoso, M.T.", "Ahmad Zaki"],
            reg_number="EC002026104829",
            creation_type="Program Komputer",
            portal_url="https://e-hakcipta.dgip.go.id/check/EC002026104829"
        )
        self.assertIn("Pengumuman Pencatatan Hak Cipta / HKI Kemenkumham", msg)
        self.assertIn("Perangkat Lunak Simulasi Propagasi Gelombang Mikro 5G", msg)
        self.assertIn("Dr. Ir. Budi Santoso, M.T.", msg)
        self.assertIn("Ahmad Zaki", msg)
        self.assertIn("EC002026104829", msg)
        self.assertIn("Program Komputer", msg)
        self.assertIn("https://e-hakcipta.dgip.go.id/check/EC002026104829", msg)

    def test_format_msib_internship_announcement_telegram(self):
        msg = TelegramFormatter.format_msib_internship_announcement_telegram(
            student_name="Ahmad Zaki",
            nim="1101230045",
            partner_name="PT Telkom Indonesia",
            internship_role="Cloud & Network Engineer",
            converted_sks=20,
            portal_url="https://kampusmerdeka.kemdikbud.go.id/msib"
        )
        self.assertIn("Magang Bersertifikat (MSIB Kampus Merdeka)", msg)
        self.assertIn("Ahmad Zaki", msg)
        self.assertIn("1101230045", msg)
        self.assertIn("PT Telkom Indonesia", msg)
        self.assertIn("Cloud & Network Engineer", msg)
        self.assertIn("20 SKS Disetujui", msg)
        self.assertIn("https://kampusmerdeka.kemdikbud.go.id/msib", msg)

    def test_format_pkm_grant_announcement_telegram(self):
        msg = TelegramFormatter.format_pkm_grant_announcement_telegram(
            project_title="Pemberdayaan Teknologi IoT Desa Karangmangu",
            team_leader="Dr. Ir. Budi Santoso, M.T.",
            nidn="0612058001",
            partner_name="Kelompok Tani Makmur",
            budget_amount=15000000.0,
            fiscal_year=2026,
            portal_url="https://lppm.telkomuniversity.ac.id/pkm-2026"
        )
        self.assertIn("Hibah Pengabdian Masyarakat (PKM)", msg)
        self.assertIn("Pemberdayaan Teknologi IoT Desa Karangmangu", msg)
        self.assertIn("Dr. Ir. Budi Santoso, M.T.", msg)
        self.assertIn("0612058001", msg)
        self.assertIn("Kelompok Tani Makmur", msg)
        self.assertIn("Rp 15.000.000", msg)
        self.assertIn("2026", msg)
        self.assertIn("https://lppm.telkomuniversity.ac.id/pkm-2026", msg)



class TestCommandRateLimiter(unittest.TestCase):




    def test_rate_limiter_allows_and_blocks(self):
        from formatters import CommandRateLimiter
        import time

        limiter = CommandRateLimiter(default_cooldown=0.2)
        allowed, remaining = limiter.is_allowed(1001)
        self.assertTrue(allowed)
        self.assertEqual(remaining, 0.0)

        # Immediate repeat should be blocked
        allowed2, remaining2 = limiter.is_allowed(1001)
        self.assertFalse(allowed2)
        self.assertGreater(remaining2, 0.0)

        # Different user is not blocked
        allowed_other, _ = limiter.is_allowed(1002)
        self.assertTrue(allowed_other)

        # Reset user
        limiter.reset(1001)
        allowed_reset, _ = limiter.is_allowed(1001)
        self.assertTrue(allowed_reset)


if __name__ == "__main__":
    unittest.main()

