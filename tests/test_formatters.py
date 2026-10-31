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

    def test_format_satellite_link_announcement_telegram(self):
        msg = TelegramFormatter.format_satellite_link_announcement_telegram(
            satellite_name="Telkom-4 (Merah Putih)",
            downlink_freq_ghz=12.2,
            station_name="Stasiun Bumi Banyumas",
            cnr_db=11.25,
            link_margin_db=4.25,
            modulation="DVB-S2 8PSK",
            portal_url="https://telemetry.telkomuniversity.ac.id/sat"
        )
        self.assertIn("Hasil Audit Link Budget Komunikasi Satelit", msg)
        self.assertIn("Telkom-4 (Merah Putih)", msg)
        self.assertIn("12.20 GHz", msg)
        self.assertIn("Stasiun Bumi Banyumas", msg)
        self.assertIn("11.25 dB", msg)
        self.assertIn("+4.25 dB", msg)
        self.assertIn("DVB-S2 8PSK", msg)
        self.assertIn("https://telemetry.telkomuniversity.ac.id/sat", msg)

    def test_format_kampus_mengajar_announcement_telegram(self):
        msg = TelegramFormatter.format_kampus_mengajar_announcement_telegram(
            student_name="Annisa Rahma",
            nim="1201200045",
            target_school="SMP Negeri 2 Kedungbanteng",
            converted_sks=20,
            letter_grade="A",
            portal_url="https://kampusmerdeka.kemdikbud.go.id"
        )
        self.assertIn("Apresiasi Kelulusan Program Kampus Mengajar MBKM", msg)
        self.assertIn("Annisa Rahma", msg)
        self.assertIn("1201200045", msg)
        self.assertIn("SMP Negeri 2 Kedungbanteng", msg)
        self.assertIn("20 SKS Diakui", msg)
        self.assertIn("A", msg)
        self.assertIn("https://kampusmerdeka.kemdikbud.go.id", msg)

    def test_format_radar_telemetry_announcement_telegram(self):
        msg = TelegramFormatter.format_radar_telemetry_announcement_telegram(
            radar_name="Surveillance Radar X-Band",
            freq_ghz=9.45,
            peak_power_kw=60.0,
            antenna_gain_dbi=36.0,
            rcs_m2=2.0,
            max_range_km=48.25,
            portal_url="https://telemetry.telkomuniversity.ac.id/radar"
        )
        self.assertIn("Hasil Audit Telemetri Jangkauan Radar Monostatik", msg)
        self.assertIn("Surveillance Radar X-Band", msg)
        self.assertIn("9.45 GHz", msg)
        self.assertIn("60.0 kW", msg)
        self.assertIn("36.0 dBi", msg)
        self.assertIn("48.25 km", msg)
        self.assertIn("https://telemetry.telkomuniversity.ac.id/radar", msg)

    def test_format_wirausaha_merdeka_telegram(self):
        msg = TelegramFormatter.format_wirausaha_merdeka_telegram(
            student_name="Budi Santoso",
            nim="1201201050",
            startup_name="IoT AgroSense",
            business_sector="Smart Agriculture",
            composite_score=89.6,
            converted_sks=20,
            letter_grade="A",
            portal_url="https://wmk.telkomuniversity.ac.id/showcase"
        )
        self.assertIn("Apresiasi Kelulusan MBKM Wirausaha Merdeka (WMK)", msg)
        self.assertIn("Budi Santoso", msg)
        self.assertIn("1201201050", msg)
        self.assertIn("IoT AgroSense", msg)
        self.assertIn("Smart Agriculture", msg)
        self.assertIn("89.6 / 100", msg)
        self.assertIn("20 SKS Diakui", msg)
        self.assertIn("https://wmk.telkomuniversity.ac.id/showcase", msg)

    def test_format_otdr_telemetry_telegram(self):
        msg = TelegramFormatter.format_otdr_telemetry_telegram(
            link_name="Backbone Purwokerto - Banyumas",
            fiber_length_km=42.5,
            wavelength_nm=1550,
            total_loss_db=8.85,
            attenuation_db_km=0.1980,
            quality_status="Optimal / Sesuai Standar ITU-T G.652",
            portal_url="https://telemetry.telkomuniversity.ac.id/otdr"
        )
        self.assertIn("Hasil Audit Redaman Serat Optik OTDR", msg)
        self.assertIn("Backbone Purwokerto - Banyumas", msg)
        self.assertIn("42.50 km", msg)
        self.assertIn("1550 nm", msg)
        self.assertIn("8.85 dB", msg)
        self.assertIn("0.1980 dB/km", msg)
        self.assertIn("ITU-T G.652", msg)
        self.assertIn("https://telemetry.telkomuniversity.ac.id/otdr", msg)

    def test_format_iisma_exchange_telegram(self):
        msg = TelegramFormatter.format_iisma_exchange_telegram(
            student_name="Nadia Putri",
            nim="1201201088",
            host_university="National University of Singapore",
            country="Singapore",
            gpa_host=3.85,
            converted_sks=20,
            letter_grade="A",
            portal_url="https://iisma.kemdikbud.go.id"
        )
        self.assertIn("Apresiasi Prestasi IISMA MBKM Luar Negeri", msg)
        self.assertIn("Nadia Putri", msg)
        self.assertIn("1201201088", msg)
        self.assertIn("National University of Singapore", msg)
        self.assertIn("IPK 3.85 / 4.00", msg)
        self.assertIn("20 SKS Diakui", msg)
        self.assertIn("https://iisma.kemdikbud.go.id", msg)

    def test_format_fspl_link_budget_telegram(self):
        msg = TelegramFormatter.format_fspl_link_budget_telegram(
            link_name="Link Microwave Banyumas-Purbalingga",
            freq_mhz=5800.0,
            distance_km=14.2,
            fspl_db=130.75,
            rx_power_dbm=-66.75,
            fade_margin_db=18.25,
            is_viable=True,
            portal_url="https://rf.telkomuniversity.ac.id/link/banyumas"
        )
        self.assertIn("Laporan Audit Wireless Link Budget & FSPL", msg)
        self.assertIn("Link Microwave Banyumas-Purbalingga", msg)
        self.assertIn("5800.0 MHz", msg)
        self.assertIn("14.20 km", msg)
        self.assertIn("130.75 dB", msg)
        self.assertIn("-66.75 dBm", msg)
        self.assertIn("+18.25 dB", msg)
        self.assertIn("LAYAK / STABIL (Viable)", msg)
        self.assertIn("https://rf.telkomuniversity.ac.id/link/banyumas", msg)

    def test_format_proyek_kemanusiaan_telegram(self):
        msg = TelegramFormatter.format_proyek_kemanusiaan_telegram(
            student_name="Reza Kurniawan",
            nim="1201201099",
            partner_org="BPBD Banyumas",
            location="Banyumas",
            converted_sks=20,
            letter_grade="A",
            portal_url="https://kemanusiaan.telkomuniversity.ac.id"
        )
        self.assertIn("Apresiasi Mahasiswa MBKM Proyek Kemanusiaan", msg)
        self.assertIn("Reza Kurniawan", msg)
        self.assertIn("1201201099", msg)
        self.assertIn("BPBD Banyumas", msg)
        self.assertIn("Banyumas", msg)
        self.assertIn("20 SKS Diakui", msg)
        self.assertIn("A", msg)
        self.assertIn("https://kemanusiaan.telkomuniversity.ac.id", msg)

    def test_format_rain_attenuation_telegram(self):
        msg = TelegramFormatter.format_rain_attenuation_telegram(
            link_name="MW Link Kampus - Gunung Slamet",
            freq_ghz=15.0,
            distance_km=14.5,
            rain_rate_mm_hr=95.0,
            rain_attenuation_db=18.42,
            excess_margin_db=11.58,
            status="Margin Mencukupi (Toleran Hujan)",
            portal_url="https://rf.telkomuniversity.ac.id/microwave/slamet"
        )
        self.assertIn("Laporan Redaman Hujan Microwave Terestrial (ITU-R P.838)", msg)
        self.assertIn("MW Link Kampus - Gunung Slamet", msg)
        self.assertIn("15.00 GHz", msg)
        self.assertIn("14.50 km", msg)
        self.assertIn("95.0 mm/jam", msg)
        self.assertIn("18.42 dB", msg)
        self.assertIn("+11.58 dB", msg)
        self.assertIn("Margin Mencukupi (Toleran Hujan)", msg)
        self.assertIn("https://rf.telkomuniversity.ac.id/microwave/slamet", msg)

    def test_format_studi_independen_telegram(self):
        msg = TelegramFormatter.format_studi_independen_telegram(
            student_name="Dimas Pratama",
            nim="1201201111",
            partner_name="PT Telkom Indonesia",
            track_name="Cloud & Network Architect",
            converted_sks=20,
            letter_grade="A",
            portal_url="https://kampusmerdeka.kemdikbud.go.id/studi/1201201111"
        )
        self.assertIn("Apresiasi Kelulusan Studi Independen Bersertifikat (SIB)", msg)
        self.assertIn("Dimas Pratama", msg)
        self.assertIn("1201201111", msg)
        self.assertIn("PT Telkom Indonesia", msg)
        self.assertIn("Cloud & Network Architect", msg)
        self.assertIn("20 SKS Diakui", msg)
        self.assertIn("A", msg)
        self.assertIn("https://kampusmerdeka.kemdikbud.go.id/studi/1201201111", msg)

    def test_format_satellite_gas_attenuation_telegram(self):
        msg = TelegramFormatter.format_satellite_gas_attenuation_telegram(
            frequency_ghz=14.25,
            elevation_angle_deg=28.5,
            slant_attenuation_db=0.35,
            oxygen_att_db_km=0.0152,
            water_vapor_att_db_km=0.0210,
            status="Sangat Rendah (Transmisi Satelit Sangat Jernih)",
            portal_url="https://sat.telkomuniversity.ac.id/link/earth-station"
        )
        self.assertIn("Laporan Redaman Gas Atmosfer Tautan Satelit (ITU-R P.676)", msg)
        self.assertIn("14.25 GHz", msg)
        self.assertIn("28.5°", msg)
        self.assertIn("0.35 dB", msg)
        self.assertIn("Sangat Rendah (Transmisi Satelit Sangat Jernih)", msg)
        self.assertIn("https://sat.telkomuniversity.ac.id/link/earth-station", msg)

    def test_format_pkm_pimnas_telegram(self):
        msg = TelegramFormatter.format_pkm_pimnas_telegram(
            student_name="Arif Rahman",
            nim="1201201044",
            scheme="PKM-KC (Karsa Cipta)",
            proposal_title="Drone Pemantau Sinyal Maritim 4G/5G",
            converted_sks=20,
            status="Lolos PIMNAS (Medali Emas)",
            medal="Medali Emas PIMNAS",
            portal_url="https://kemahasiswaan.telkomuniversity.ac.id/pkm/2026-001"
        )
        self.assertIn("Prestasi Gemilang Mahasiswa PKM & PIMNAS Belmawa", msg)
        self.assertIn("Arif Rahman", msg)
        self.assertIn("1201201044", msg)
        self.assertIn("PKM-KC (Karsa Cipta)", msg)
        self.assertIn("Medali Emas PIMNAS", msg)
        self.assertIn("Drone Pemantau Sinyal Maritim 4G/5G", msg)
        self.assertIn("20 SKS Diakui", msg)
        self.assertIn("https://kemahasiswaan.telkomuniversity.ac.id/pkm/2026-001", msg)

    def test_format_satellite_scintillation_telegram(self):
        msg = TelegramFormatter.format_satellite_scintillation_telegram(
            satellite_name="Telkom-4 (Merah Putih)",
            frequency_ghz=12.25,
            elevation_angle_deg=35.0,
            antenna_diameter_m=1.8,
            fade_depth_db=0.85,
            fading_risk="Sangat Rendah (Scintillation Margin Aman)",
            portal_url="https://sat.telkomuniversity.ac.id/scintillation"
        )
        self.assertIn("Laporan Audit Sintilasi Troposfer Satelit (ITU-R P.618)", msg)
        self.assertIn("Telkom-4 (Merah Putih)", msg)
        self.assertIn("12.25 GHz", msg)
        self.assertIn("35.0°", msg)
        self.assertIn("1.80 meter", msg)
        self.assertIn("0.85 dB", msg)
        self.assertIn("https://sat.telkomuniversity.ac.id/scintillation", msg)

    def test_format_pmm_mbkm_telegram(self):
        msg = TelegramFormatter.format_pmm_mbkm_telegram(
            student_name="Nabila Putri",
            nim="1201201088",
            host_university="Universitas Gadjah Mada",
            composite_score=89.5,
            letter_grade="A",
            converted_sks=20,
            status="Lulus Penuh Program PMM - Rekognisi 20 SKS",
            portal_url="https://mbkm.telkomuniversity.ac.id/pmm/2026-088"
        )
        self.assertIn("Apresiasi Penuntasan Pertukaran Mahasiswa Merdeka (PMM)", msg)
        self.assertIn("Nabila Putri", msg)
        self.assertIn("1201201088", msg)
        self.assertIn("Universitas Gadjah Mada", msg)
        self.assertIn("89.50", msg)
        self.assertIn("Nilai Mutu:** `A`", msg)
        self.assertIn("20 SKS Diakui", msg)
        self.assertIn("https://mbkm.telkomuniversity.ac.id/pmm/2026-088", msg)

    def test_format_satellite_faraday_telegram(self):
        msg = TelegramFormatter.format_satellite_faraday_telegram(
            satellite_name="Nusantara Satu (L-Band)",
            frequency_ghz=1.5,
            tec_tecu=45.0,
            rotation_angle_deg=8.4,
            polarization_loss_db=0.095,
            rotation_risk="Sedang",
            is_linear_viable=True,
            portal_url="https://sat.telkomuniversity.ac.id/faraday"
        )
        self.assertIn("Telemetri Faraday Rotation Satelit (ITU-R P.531)", msg)
        self.assertIn("Nusantara Satu (L-Band)", msg)
        self.assertIn("1.50 GHz", msg)
        self.assertIn("45.0 TECU", msg)
        self.assertIn("8.40°", msg)
        self.assertIn("0.095 dB", msg)
        self.assertIn("Polarisasi Linier Aman", msg)
        self.assertIn("https://sat.telkomuniversity.ac.id/faraday", msg)

    def test_format_praktisi_mengajar_telegram(self):
        msg = TelegramFormatter.format_praktisi_mengajar_telegram(
            course_name="Jaringan Akses Nirkabel 5G & Beyond",
            practitioner_name="Ir. Hendra Wijaya, M.Sc.",
            industry_company="PT Telkomsel",
            lecturer_name="Dr. Ir. Budi Santoso, M.T.",
            teaching_hours=14,
            composite_score=88.5,
            letter_grade="A",
            converted_sks=3,
            status="Lulus Rekognisi Praktisi Industri",
            portal_url="https://mbkm.telkomuniversity.ac.id/praktisi/2026"
        )
        self.assertIn("Kolaborasi MBKM Praktisi Mengajar Industri", msg)
        self.assertIn("Jaringan Akses Nirkabel 5G & Beyond", msg)
        self.assertIn("Ir. Hendra Wijaya, M.Sc.", msg)
        self.assertIn("PT Telkomsel", msg)
        self.assertIn("14 Jam Pertemuan", msg)
        self.assertIn("88.5", msg)
        self.assertIn("3 SKS Diakui", msg)
        self.assertIn("https://mbkm.telkomuniversity.ac.id/praktisi/2026", msg)

    def test_format_satellite_rain_attenuation_telegram(self):
        msg = TelegramFormatter.format_satellite_rain_attenuation_telegram(
            satellite_name="Telkom-4 (Ku-Band)",
            frequency_ghz=12.25,
            elevation_angle_deg=52.0,
            rain_rate_mm_h=95.0,
            predicted_attenuation_db=7.85,
            attenuation_risk="Sedang",
            is_link_viable=True,
            portal_url="https://sat.telkomuniversity.ac.id/rain"
        )
        self.assertIn("Telemetri Redaman Hujan Satelit (ITU-R P.618)", msg)
        self.assertIn("Telkom-4 (Ku-Band)", msg)
        self.assertIn("12.25 GHz", msg)
        self.assertIn("52.0°", msg)
        self.assertIn("95.0 mm/jam", msg)
        self.assertIn("7.85 dB", msg)
        self.assertIn("Tautan Andal & Stabil", msg)
        self.assertIn("https://sat.telkomuniversity.ac.id/rain", msg)

    def test_format_p2mw_startup_telegram(self):
        msg = TelegramFormatter.format_p2mw_startup_telegram(
            student_name="Dimas Pratama",
            nim="1201202050",
            business_name="AgroTele-IoT",
            business_stage="Tahap Bertumbuh",
            category="Teknologi Terapan & IoT",
            composite_score=88.5,
            letter_grade="A",
            converted_sks=6,
            status="Lolos Pendanaan & Inkubasi P2MW Tahap Bertumbuh",
            portal_url="https://mbkm.telkomuniversity.ac.id/p2mw/2026-050"
        )
        self.assertIn("Apresiasi Inkubasi Startup Mahasiswa P2MW Kemendikbudristek", msg)
        self.assertIn("AgroTele-IoT", msg)
        self.assertIn("Dimas Pratama", msg)
        self.assertIn("1201202050", msg)
        self.assertIn("Tahap Bertumbuh", msg)
        self.assertIn("88.5", msg)
        self.assertIn("6 SKS Diakui", msg)
        self.assertIn("https://mbkm.telkomuniversity.ac.id/p2mw/2026-050", msg)

    def test_format_satellite_gaseous_attenuation_telegram(self):
        msg = TelegramFormatter.format_satellite_gaseous_attenuation_telegram(
            satellite_name="Nusantara-2",
            frequency_ghz=28.5,
            elevation_angle_deg=45.0,
            gamma_oxygen=0.0352,
            gamma_vapor=0.1245,
            slant_attenuation_db=0.648,
            risk_level="Rendah",
            portal_url="https://telemetry.telkomuniversity.ac.id/satellite/nusantara-2"
        )
        self.assertIn("Laporan Audit Redaman Gas Atmosfer Satelit (ITU-R P.676)", msg)
        self.assertIn("Nusantara-2", msg)
        self.assertIn("28.5 GHz", msg)
        self.assertIn("45.0°", msg)
        self.assertIn("0.0352 dB/km", msg)
        self.assertIn("0.648 dB", msg)
        self.assertIn("https://telemetry.telkomuniversity.ac.id/satellite/nusantara-2", msg)

    def test_format_pkm_proposal_telegram(self):
        msg = TelegramFormatter.format_pkm_proposal_telegram(
            student_name="Rizky Firmansyah",
            nim="1201210034",
            proposal_title="Sistem Radar Cuaca Maritim Terdistribusi",
            scheme="PKM-KC",
            composite_score=88.5,
            letter_grade="A",
            funding_status="Didanai Belmawa & Lolos PIMNAS",
            converted_sks=4,
            portal_url="https://simbelmawa.kemdikbud.go.id/pkm/2026-034"
        )
        self.assertIn("Apresiasi Kelulusan Proposal PKM Simbelmawa Kemendikbudristek", msg)
        self.assertIn("Sistem Radar Cuaca Maritim Terdistribusi", msg)
        self.assertIn("Rizky Firmansyah", msg)
        self.assertIn("1201210034", msg)
        self.assertIn("PKM-KC", msg)
        self.assertIn("4 SKS Diakui", msg)
        self.assertIn("https://simbelmawa.kemdikbud.go.id/pkm/2026-034", msg)

    def test_format_optical_fwm_telegram(self):
        msg = TelegramFormatter.format_optical_fwm_telegram(
            fiber_title="Span Jawa-Bali SMF-28",
            fiber_length_km=75.0,
            channel_spacing_ghz=100.0,
            chromatic_dispersion=17.0,
            phase_mismatch=8.56,
            coherence_length_km=0.734,
            fwm_efficiency_percent=0.012,
            fwm_power_dbm=-52.4,
            fwm_risk="Sangat Rendah (Dispersi Terkendali)",
            portal_url="https://telemetry.telkomuniversity.ac.id/fwm/jb-1"
        )
        self.assertIn("DWDM Four-Wave Mixing (FWM) Phase-Matching", msg)
        self.assertIn("Span Jawa-Bali SMF-28", msg)
        self.assertIn("75.0 km", msg)
        self.assertIn("100.0 GHz", msg)
        self.assertIn("0.734 km", msg)
        self.assertIn("-52.40 dBm", msg)
        self.assertIn("https://telemetry.telkomuniversity.ac.id/fwm/jb-1", msg)

    def test_format_ppk_ormawa_telegram(self):
        msg = TelegramFormatter.format_ppk_ormawa_telegram(
            proposal_title="Pemberdayaan Desa Cerdas Berbasis LoRaWAN",
            ormawa_name="HMTT Telkom University",
            topic="Smart Agriculture & Monitoring Lingkungan",
            village_location="Desa Cibeusi",
            composite_score=89.0,
            letter_grade="A",
            allocated_budget_idr=38000000,
            funding_status="Lolos Pendanaan Belmawa Dikti 2026",
            portal_url="https://belmawa.kemdikbud.go.id/ppk-ormawa/2026-089"
        )
        self.assertIn("Pengumuman Pendanaan PPK Ormawa Belmawa Kemendikbudristek", msg)
        self.assertIn("Pemberdayaan Desa Cerdas Berbasis LoRaWAN", msg)
        self.assertIn("HMTT Telkom University", msg)
        self.assertIn("Desa Cibeusi", msg)
        self.assertIn("Rp 38,000,000", msg)
        self.assertIn("https://belmawa.kemdikbud.go.id/ppk-ormawa/2026-089", msg)


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

