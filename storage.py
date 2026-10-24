import json
import sqlite3
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional, Dict, Any, List, Tuple

class StorageManager:
    def __init__(self, db_path: Path):
        self.db_path = db_path
        self._init_db()

    def _get_connection(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def _init_db(self) -> None:
        with self._get_connection() as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS articles (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    topic TEXT NOT NULL,
                    category TEXT NOT NULL,
                    publish_date TEXT NOT NULL,
                    image_url TEXT,
                    focus_keyphrase TEXT NOT NULL,
                    seo_title TEXT NOT NULL,
                    slug TEXT NOT NULL UNIQUE,
                    meta_description TEXT NOT NULL,
                    html_content TEXT,
                    status TEXT DEFAULT 'draft',
                    wp_post_id INTEGER,
                    is_deleted INTEGER DEFAULT 0,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
            """)
            cursor = conn.execute("PRAGMA table_info(articles);")
            columns = [row["name"] for row in cursor.fetchall()]
            if "is_deleted" not in columns and len(columns) > 0:
                conn.execute("ALTER TABLE articles ADD COLUMN is_deleted INTEGER DEFAULT 0;")

            conn.execute("CREATE INDEX IF NOT EXISTS idx_keyphrase ON articles(focus_keyphrase);")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_slug ON articles(slug);")
            conn.execute("""
                CREATE TABLE IF NOT EXISTS article_tags (
                    article_id INTEGER NOT NULL,
                    tag TEXT NOT NULL,
                    PRIMARY KEY (article_id, tag),
                    FOREIGN KEY (article_id) REFERENCES articles(id) ON DELETE CASCADE
                );
            """)
            conn.execute("CREATE INDEX IF NOT EXISTS idx_tag ON article_tags(tag);")
            conn.execute("""
                CREATE TABLE IF NOT EXISTS article_audit_logs (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    article_id INTEGER NOT NULL,
                    old_status TEXT NOT NULL,
                    new_status TEXT NOT NULL,
                    note TEXT,
                    changed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (article_id) REFERENCES articles(id) ON DELETE CASCADE
                );
            """)
            conn.execute("CREATE INDEX IF NOT EXISTS idx_audit_article ON article_audit_logs(article_id);")
            conn.execute("""
                CREATE TABLE IF NOT EXISTS article_revisions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    article_id INTEGER NOT NULL,
                    revision_num INTEGER NOT NULL,
                    html_content TEXT,
                    meta_description TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (article_id) REFERENCES articles(id) ON DELETE CASCADE
                );
            """)
            conn.execute("CREATE INDEX IF NOT EXISTS idx_rev_article ON article_revisions(article_id);")
            conn.execute("""
                CREATE TABLE IF NOT EXISTS article_meta (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    article_id INTEGER NOT NULL,
                    meta_key TEXT NOT NULL,
                    meta_value TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    UNIQUE(article_id, meta_key),
                    FOREIGN KEY (article_id) REFERENCES articles(id) ON DELETE CASCADE
                );
            """)
            conn.execute("CREATE INDEX IF NOT EXISTS idx_meta_article ON article_meta(article_id);")
            conn.execute("""
                CREATE TABLE IF NOT EXISTS article_exports (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    article_id INTEGER NOT NULL,
                    export_type TEXT NOT NULL,
                    destination_path TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (article_id) REFERENCES articles(id) ON DELETE CASCADE
                );
            """)
            conn.execute("CREATE INDEX IF NOT EXISTS idx_exports_article ON article_exports(article_id);")
            conn.execute("""
                CREATE TABLE IF NOT EXISTS article_schedules (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    article_id INTEGER NOT NULL UNIQUE,
                    scheduled_at TEXT NOT NULL,
                    status TEXT DEFAULT 'pending',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (article_id) REFERENCES articles(id) ON DELETE CASCADE
                );
            """)
            conn.execute("CREATE INDEX IF NOT EXISTS idx_sched_time ON article_schedules(scheduled_at);")
            conn.execute("""
                CREATE TABLE IF NOT EXISTS article_engagement (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    article_id INTEGER NOT NULL UNIQUE,
                    view_count INTEGER DEFAULT 0,
                    share_count INTEGER DEFAULT 0,
                    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (article_id) REFERENCES articles(id) ON DELETE CASCADE
                );
            """)
            conn.execute("CREATE INDEX IF NOT EXISTS idx_eng_article ON article_engagement(article_id);")
            conn.execute("""
                CREATE TABLE IF NOT EXISTS article_categories (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL UNIQUE,
                    slug TEXT NOT NULL UNIQUE,
                    parent_id INTEGER,
                    description TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (parent_id) REFERENCES article_categories(id) ON DELETE SET NULL
                );
            """)
            conn.execute("CREATE INDEX IF NOT EXISTS idx_cat_parent ON article_categories(parent_id);")
            conn.execute("""
                CREATE TABLE IF NOT EXISTS article_locks (
                    article_id INTEGER PRIMARY KEY,
                    locked_by TEXT NOT NULL,
                    expires_at TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (article_id) REFERENCES articles(id) ON DELETE CASCADE
                );
            """)
            conn.execute("""
                CREATE TABLE IF NOT EXISTS article_bookmarks (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    article_id INTEGER NOT NULL,
                    user_identifier TEXT NOT NULL,
                    notes TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    UNIQUE(article_id, user_identifier),
                    FOREIGN KEY (article_id) REFERENCES articles(id) ON DELETE CASCADE
                );
            """)
            conn.execute("CREATE INDEX IF NOT EXISTS idx_bm_user ON article_bookmarks(user_identifier);")
            conn.execute("""
                CREATE TABLE IF NOT EXISTS schema_migrations (
                    version TEXT PRIMARY KEY,
                    applied_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
            """)
            conn.execute("""
                CREATE TABLE IF NOT EXISTS article_reading_metrics (
                    article_id INTEGER PRIMARY KEY,
                    word_count INTEGER NOT NULL,
                    reading_time_min INTEGER NOT NULL,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (article_id) REFERENCES articles(id) ON DELETE CASCADE
                );
            """)
            conn.execute("""
                CREATE TABLE IF NOT EXISTS editorial_subscribers (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id TEXT NOT NULL,
                    channel TEXT NOT NULL,
                    category TEXT NOT NULL DEFAULT 'all',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    UNIQUE(user_id, channel, category)
                );
            """)
            conn.execute("CREATE INDEX IF NOT EXISTS idx_sub_category ON editorial_subscribers(category);")
            conn.execute("""
                CREATE TABLE IF NOT EXISTS article_view_logs (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    article_id INTEGER NOT NULL,
                    referrer TEXT,
                    user_agent_hash TEXT,
                    viewed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (article_id) REFERENCES articles(id) ON DELETE CASCADE
                );
            """)
            conn.execute("CREATE INDEX IF NOT EXISTS idx_view_article ON article_view_logs(article_id);")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_view_time ON article_view_logs(viewed_at);")
            conn.execute("""
                CREATE TABLE IF NOT EXISTS editorial_tasks (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    article_id INTEGER NOT NULL,
                    assignee TEXT NOT NULL,
                    task_type TEXT NOT NULL,
                    due_date TEXT NOT NULL,
                    status TEXT DEFAULT 'pending',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (article_id) REFERENCES articles(id) ON DELETE CASCADE
                );
            """)
            conn.execute("CREATE INDEX IF NOT EXISTS idx_task_assignee ON editorial_tasks(assignee);")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_task_status ON editorial_tasks(status);")
            conn.execute("""
                CREATE TABLE IF NOT EXISTS taxonomy_meta (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    taxonomy TEXT NOT NULL,
                    term_slug TEXT NOT NULL,
                    meta_key TEXT NOT NULL,
                    meta_value TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    UNIQUE(taxonomy, term_slug, meta_key)
                );
            """)
            conn.execute("CREATE INDEX IF NOT EXISTS idx_tax_slug ON taxonomy_meta(taxonomy, term_slug);")
            conn.execute("""
                CREATE TABLE IF NOT EXISTS article_notes (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    article_id INTEGER NOT NULL,
                    author TEXT NOT NULL,
                    note_text TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (article_id) REFERENCES articles(id) ON DELETE CASCADE
                );
            """)
            conn.execute("CREATE INDEX IF NOT EXISTS idx_note_article ON article_notes(article_id);")
            conn.execute("""
                CREATE TABLE IF NOT EXISTS publishing_webhook_logs (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    event TEXT NOT NULL,
                    target_url TEXT NOT NULL,
                    status_code INTEGER NOT NULL,
                    payload_snippet TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
            """)
            conn.execute("CREATE INDEX IF NOT EXISTS idx_webhook_event ON publishing_webhook_logs(event);")
            conn.execute("""
                CREATE TABLE IF NOT EXISTS taxonomy_synonyms (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    canonical_term TEXT NOT NULL,
                    alias_term TEXT NOT NULL UNIQUE,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
            """)
            conn.execute("CREATE INDEX IF NOT EXISTS idx_tax_synonym ON taxonomy_synonyms(alias_term);")
            conn.execute("""
                CREATE TABLE IF NOT EXISTS article_reviewers (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    article_id INTEGER NOT NULL,
                    reviewer_name TEXT NOT NULL,
                    reviewer_email TEXT NOT NULL,
                    status TEXT DEFAULT 'assigned',
                    assigned_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (article_id) REFERENCES articles(id) ON DELETE CASCADE
                );
            """)
            conn.execute("CREATE INDEX IF NOT EXISTS idx_rev_article ON article_reviewers(article_id);")
            conn.execute("""
                CREATE TABLE IF NOT EXISTS syndication_logs (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    article_id INTEGER NOT NULL,
                    platform TEXT NOT NULL,
                    external_url TEXT NOT NULL,
                    syndicated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (article_id) REFERENCES articles(id) ON DELETE CASCADE
                );
            """)
            conn.execute("CREATE INDEX IF NOT EXISTS idx_synd_article ON syndication_logs(article_id);")
            conn.execute("""
                CREATE TABLE IF NOT EXISTS editorial_checklists (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    article_id INTEGER NOT NULL,
                    item_key TEXT NOT NULL,
                    item_label TEXT NOT NULL,
                    is_checked INTEGER DEFAULT 0,
                    checked_by TEXT,
                    checked_at TIMESTAMP,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    UNIQUE(article_id, item_key),
                    FOREIGN KEY (article_id) REFERENCES articles(id) ON DELETE CASCADE
                );
            """)
            conn.execute("CREATE INDEX IF NOT EXISTS idx_chk_article ON editorial_checklists(article_id);")
            conn.execute("""
                CREATE TABLE IF NOT EXISTS article_citations (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    article_id INTEGER NOT NULL,
                    citing_paper_title TEXT NOT NULL,
                    citing_authors TEXT NOT NULL,
                    journal_name TEXT NOT NULL,
                    citation_year INTEGER NOT NULL,
                    doi TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (article_id) REFERENCES articles(id) ON DELETE CASCADE
                );
            """)
            conn.execute("CREATE INDEX IF NOT EXISTS idx_cite_article ON article_citations(article_id);")
            conn.execute("""
                CREATE TABLE IF NOT EXISTS editorial_comments (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    article_id INTEGER NOT NULL,
                    author TEXT NOT NULL,
                    comment_text TEXT NOT NULL,
                    paragraph_index INTEGER,
                    is_resolved INTEGER DEFAULT 0,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    resolved_at TIMESTAMP,
                    FOREIGN KEY (article_id) REFERENCES articles(id) ON DELETE CASCADE
                );
            """)
            conn.execute("CREATE INDEX IF NOT EXISTS idx_comment_article ON editorial_comments(article_id);")
            conn.execute("""
                CREATE TABLE IF NOT EXISTS content_snippets (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    snippet_key TEXT UNIQUE NOT NULL,
                    snippet_title TEXT NOT NULL,
                    snippet_html TEXT NOT NULL,
                    category TEXT DEFAULT 'general',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
            """)
            conn.execute("CREATE INDEX IF NOT EXISTS idx_snippet_cat ON content_snippets(category);")
            conn.execute("""
                CREATE TABLE IF NOT EXISTS competition_achievements (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    competition_name TEXT NOT NULL,
                    award_rank TEXT NOT NULL,
                    team_name TEXT NOT NULL,
                    team_members TEXT NOT NULL,
                    supervisor TEXT NOT NULL,
                    year INTEGER NOT NULL,
                    organizer TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
            """)
            conn.execute("CREATE INDEX IF NOT EXISTS idx_comp_year ON competition_achievements(year);")
            conn.execute("""
                CREATE TABLE IF NOT EXISTS journal_indexings (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    journal_name TEXT NOT NULL,
                    sinta_rank INTEGER NOT NULL,
                    issn TEXT NOT NULL,
                    publisher TEXT NOT NULL,
                    focus_scope TEXT NOT NULL,
                    archive_url TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
            """)
            conn.execute("CREATE INDEX IF NOT EXISTS idx_journal_sinta ON journal_indexings(sinta_rank);")
            conn.execute("""
                CREATE TABLE IF NOT EXISTS lab_safety_inspections (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    lab_name TEXT NOT NULL,
                    inspector TEXT NOT NULL,
                    inspection_date TEXT NOT NULL,
                    compliance_score REAL NOT NULL,
                    is_passed INTEGER NOT NULL,
                    notes TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
            """)
            conn.execute("CREATE INDEX IF NOT EXISTS idx_safety_lab ON lab_safety_inspections(lab_name);")
            conn.execute("""
                CREATE TABLE IF NOT EXISTS mbkm_credit_transfers (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    program_name TEXT NOT NULL,
                    partner_institution TEXT NOT NULL,
                    student_name TEXT NOT NULL,
                    nim TEXT NOT NULL,
                    semester INTEGER NOT NULL,
                    total_sks INTEGER NOT NULL,
                    converted_gpa REAL NOT NULL,
                    courses_json TEXT NOT NULL,
                    sk_number TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
            """)
            conn.execute("CREATE INDEX IF NOT EXISTS idx_mbkm_nim ON mbkm_credit_transfers(nim);")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_mbkm_prog ON mbkm_credit_transfers(program_name);")
            conn.execute("""
                CREATE TABLE IF NOT EXISTS yudisium_clearances (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    student_name TEXT NOT NULL,
                    nim TEXT NOT NULL UNIQUE,
                    thesis_title TEXT NOT NULL,
                    ipk REAL NOT NULL,
                    earned_sks INTEGER NOT NULL,
                    graduation_predicate TEXT NOT NULL,
                    yudisium_date TEXT NOT NULL,
                    verification_code TEXT NOT NULL,
                    is_cleared INTEGER DEFAULT 1,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
            """)
            conn.execute("CREATE INDEX IF NOT EXISTS idx_yudisium_nim ON yudisium_clearances(nim);")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_yudisium_pred ON yudisium_clearances(graduation_predicate);")
            conn.execute("""
                CREATE TABLE IF NOT EXISTS lab_equipment_calibrations (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    asset_id TEXT NOT NULL,
                    equipment_name TEXT NOT NULL,
                    lab_name TEXT NOT NULL,
                    calibration_date TEXT NOT NULL,
                    due_date TEXT NOT NULL,
                    calibration_status TEXT NOT NULL,
                    operating_condition TEXT NOT NULL,
                    technician_name TEXT NOT NULL,
                    notes TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
            """)
            conn.execute("CREATE INDEX IF NOT EXISTS idx_equip_asset ON lab_equipment_calibrations(asset_id);")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_equip_lab ON lab_equipment_calibrations(lab_name);")
            conn.execute("""
                CREATE TABLE IF NOT EXISTS kkn_village_projects (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    group_code TEXT NOT NULL UNIQUE,
                    village_name TEXT NOT NULL,
                    district_name TEXT NOT NULL,
                    regency_name TEXT NOT NULL,
                    supervisor_dpl TEXT NOT NULL,
                    student_count INTEGER NOT NULL,
                    thematic_focus TEXT NOT NULL,
                    flagship_program TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
            """)
            conn.execute("CREATE INDEX IF NOT EXISTS idx_kkn_group ON kkn_village_projects(group_code);")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_kkn_regency ON kkn_village_projects(regency_name);")
            conn.execute("""
                CREATE TABLE IF NOT EXISTS faculty_bkd_records (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    lecturer_name TEXT NOT NULL,
                    nidn TEXT NOT NULL,
                    academic_rank TEXT NOT NULL,
                    semester TEXT NOT NULL,
                    teaching_credits REAL NOT NULL,
                    research_credits REAL NOT NULL,
                    service_credits REAL NOT NULL,
                    supporting_credits REAL NOT NULL,
                    total_sks REAL NOT NULL,
                    is_compliant INTEGER NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
            """)
            conn.execute("CREATE INDEX IF NOT EXISTS idx_bkd_nidn ON faculty_bkd_records(nidn);")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_bkd_semester ON faculty_bkd_records(semester);")
            conn.execute("""
                CREATE TABLE IF NOT EXISTS conference_presentations (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    paper_title TEXT NOT NULL,
                    authors TEXT NOT NULL,
                    conference_name TEXT NOT NULL,
                    acronym TEXT NOT NULL,
                    core_tier TEXT NOT NULL,
                    publisher TEXT NOT NULL,
                    year INTEGER NOT NULL,
                    city TEXT NOT NULL,
                    paper_url TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
            """)
            conn.execute("CREATE INDEX IF NOT EXISTS idx_conf_tier ON conference_presentations(core_tier);")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_conf_year ON conference_presentations(year);")
            conn.execute("""
                CREATE TABLE IF NOT EXISTS bima_grant_proposals (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    project_title TEXT NOT NULL,
                    lead_researcher TEXT NOT NULL,
                    lead_nidn TEXT NOT NULL,
                    scheme_name TEXT NOT NULL,
                    requested_budget REAL NOT NULL,
                    approved_budget REAL NOT NULL,
                    fiscal_year INTEGER NOT NULL,
                    proposal_status TEXT NOT NULL DEFAULT 'submitted',
                    contract_number TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
            """)
            conn.execute("CREATE INDEX IF NOT EXISTS idx_bima_nidn ON bima_grant_proposals(lead_nidn);")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_bima_year ON bima_grant_proposals(fiscal_year);")
            conn.execute("""
                CREATE TABLE IF NOT EXISTS kerja_praktik_placements (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    student_name TEXT NOT NULL,
                    nim TEXT NOT NULL,
                    company_name TEXT NOT NULL,
                    industry_sector TEXT NOT NULL,
                    duration_weeks INTEGER NOT NULL,
                    project_title TEXT NOT NULL,
                    company_mentor TEXT,
                    placement_status TEXT NOT NULL DEFAULT 'approved',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
            """)
            conn.execute("CREATE INDEX IF NOT EXISTS idx_kp_nim ON kerja_praktik_placements(nim);")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_kp_company ON kerja_praktik_placements(company_name);")
            conn.execute("""
                CREATE TABLE IF NOT EXISTS lab_spectrum_allocations (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    lab_name TEXT NOT NULL,
                    center_frequency_mhz REAL NOT NULL,
                    bandwidth_mhz REAL NOT NULL,
                    transmit_power_dbm REAL NOT NULL,
                    band_designation TEXT NOT NULL,
                    license_number TEXT,
                    valid_until TEXT,
                    is_active INTEGER NOT NULL DEFAULT 1,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
            """)
            conn.execute("CREATE INDEX IF NOT EXISTS idx_spectrum_lab ON lab_spectrum_allocations(lab_name);")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_spectrum_band ON lab_spectrum_allocations(band_designation);")
            conn.execute("""
                CREATE TABLE IF NOT EXISTS study_program_accreditations (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    program_name TEXT NOT NULL,
                    agency TEXT NOT NULL,
                    rating TEXT NOT NULL,
                    sk_number TEXT NOT NULL,
                    issued_date TEXT,
                    expiry_date TEXT NOT NULL,
                    is_active INTEGER NOT NULL DEFAULT 1,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
            """)
            conn.execute("CREATE INDEX IF NOT EXISTS idx_accred_agency ON study_program_accreditations(agency);")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_accred_rating ON study_program_accreditations(rating);")
            conn.execute("""
                CREATE TABLE IF NOT EXISTS student_scholarships (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    student_name TEXT NOT NULL,
                    nim TEXT NOT NULL,
                    scholarship_type TEXT NOT NULL,
                    sponsor_name TEXT NOT NULL,
                    amount REAL NOT NULL,
                    semester TEXT NOT NULL,
                    academic_year TEXT NOT NULL,
                    status TEXT NOT NULL DEFAULT 'active',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
            """)
            conn.execute("CREATE INDEX IF NOT EXISTS idx_scholarship_nim ON student_scholarships(nim);")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_scholarship_type ON student_scholarships(scholarship_type);")
            conn.execute("""
                CREATE TABLE IF NOT EXISTS bnsp_certifications (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    student_name TEXT NOT NULL,
                    nim TEXT NOT NULL,
                    scheme_name TEXT NOT NULL,
                    assessor_name TEXT NOT NULL,
                    cert_number TEXT NOT NULL,
                    issue_date TEXT NOT NULL,
                    valid_until TEXT NOT NULL,
                    is_competent INTEGER NOT NULL DEFAULT 1,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
            """)
            conn.execute("CREATE INDEX IF NOT EXISTS idx_bnsp_nim ON bnsp_certifications(nim);")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_bnsp_scheme ON bnsp_certifications(scheme_name);")
            conn.execute("""
                CREATE TABLE IF NOT EXISTS student_graduation_honors (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    student_name TEXT NOT NULL,
                    nim TEXT NOT NULL,
                    ipk REAL NOT NULL,
                    honor_predicate TEXT NOT NULL,
                    thesis_title TEXT NOT NULL,
                    study_duration_semesters INTEGER NOT NULL DEFAULT 8,
                    graduation_year INTEGER NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
            """)
            conn.execute("CREATE INDEX IF NOT EXISTS idx_honors_nim ON student_graduation_honors(nim);")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_honors_year ON student_graduation_honors(graduation_year);")
            conn.execute("""
                CREATE TABLE IF NOT EXISTS tridharma_research_grants (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    lecturer_name TEXT NOT NULL,
                    nidn TEXT NOT NULL,
                    project_title TEXT NOT NULL,
                    grant_amount REAL NOT NULL,
                    fiscal_year INTEGER NOT NULL,
                    publication_target TEXT NOT NULL,
                    status TEXT NOT NULL DEFAULT 'active',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
            """)
            conn.execute("CREATE INDEX IF NOT EXISTS idx_tridharma_nidn ON tridharma_research_grants(nidn);")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_tridharma_year ON tridharma_research_grants(fiscal_year);")
            conn.execute("""
                CREATE TABLE IF NOT EXISTS iot_sensor_telemetry_feeds (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    node_id TEXT NOT NULL,
                    sensor_type TEXT NOT NULL,
                    reading_value REAL NOT NULL,
                    unit TEXT NOT NULL,
                    battery_level REAL NOT NULL DEFAULT 100.0,
                    recorded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
            """)
            conn.execute("CREATE INDEX IF NOT EXISTS idx_iot_node ON iot_sensor_telemetry_feeds(node_id);")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_iot_type ON iot_sensor_telemetry_feeds(sensor_type);")
            conn.execute("""
                CREATE TABLE IF NOT EXISTS fast_track_students (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    student_name TEXT NOT NULL,
                    nim TEXT NOT NULL UNIQUE,
                    ipk REAL NOT NULL,
                    completed_sks INTEGER NOT NULL,
                    toefl_score INTEGER NOT NULL,
                    masters_specialization TEXT NOT NULL,
                    status TEXT DEFAULT 'Eligible',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
            """)
            conn.execute("CREATE INDEX IF NOT EXISTS idx_fasttrack_nim ON fast_track_students(nim);")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_fasttrack_status ON fast_track_students(status);")
            conn.execute("""
                CREATE TABLE IF NOT EXISTS lab_calibration_compliance (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    equipment_name TEXT NOT NULL,
                    serial_number TEXT NOT NULL UNIQUE,
                    lab_room TEXT NOT NULL,
                    last_calibration_date TEXT NOT NULL,
                    next_due_date TEXT NOT NULL,
                    calibration_status TEXT NOT NULL,
                    cert_number TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
            """)
            conn.execute("CREATE INDEX IF NOT EXISTS idx_calib_compliance_sn ON lab_calibration_compliance(serial_number);")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_calib_compliance_status ON lab_calibration_compliance(calibration_status);")
            conn.execute("""
                CREATE TABLE IF NOT EXISTS lecturer_hki_records (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    work_title TEXT NOT NULL,
                    creators_json TEXT NOT NULL,
                    creation_type TEXT NOT NULL,
                    application_number TEXT NOT NULL,
                    registration_number TEXT NOT NULL UNIQUE,
                    registration_date TEXT NOT NULL,
                    rubric_points REAL DEFAULT 0.0,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
            """)
            conn.execute("CREATE INDEX IF NOT EXISTS idx_hki_reg ON lecturer_hki_records(registration_number);")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_hki_type ON lecturer_hki_records(creation_type);")
            conn.execute("""
                CREATE TABLE IF NOT EXISTS student_msib_internships (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    student_name TEXT NOT NULL,
                    nim TEXT NOT NULL UNIQUE,
                    industry_partner TEXT NOT NULL,
                    internship_role TEXT NOT NULL,
                    mentor_grade REAL NOT NULL,
                    letter_grade TEXT NOT NULL,
                    converted_sks INTEGER NOT NULL,
                    duration_months INTEGER NOT NULL DEFAULT 5,
                    status TEXT DEFAULT 'Approved',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
            """)
            conn.execute("CREATE INDEX IF NOT EXISTS idx_msib_nim ON student_msib_internships(nim);")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_msib_partner ON student_msib_internships(industry_partner);")
            conn.execute("""
                CREATE TABLE IF NOT EXISTS lecturer_pkm_grants (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    project_title TEXT NOT NULL,
                    team_leader TEXT NOT NULL,
                    nidn TEXT NOT NULL,
                    partner_name TEXT NOT NULL,
                    target_location TEXT NOT NULL,
                    proposed_budget REAL NOT NULL,
                    approved_budget REAL NOT NULL,
                    fiscal_year INTEGER NOT NULL,
                    focus_area TEXT NOT NULL,
                    status TEXT DEFAULT 'Approved',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
            """)
            conn.execute("CREATE INDEX IF NOT EXISTS idx_pkm_nidn ON lecturer_pkm_grants(nidn);")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_pkm_year ON lecturer_pkm_grants(fiscal_year);")
            conn.execute("""
                CREATE TABLE IF NOT EXISTS fso_link_budget_records (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    link_name TEXT NOT NULL,
                    link_distance_km REAL NOT NULL,
                    tx_power_dbm REAL NOT NULL,
                    rx_power_dbm REAL NOT NULL,
                    geometric_loss_db REAL NOT NULL,
                    atmospheric_loss_db REAL NOT NULL,
                    link_margin_db REAL NOT NULL,
                    status TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
            """)
            conn.execute("CREATE INDEX IF NOT EXISTS idx_fso_link ON fso_link_budget_records(link_name);")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_fso_status ON fso_link_budget_records(status);")
            conn.execute("""
                CREATE TABLE IF NOT EXISTS satellite_link_budgets (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    satellite_name TEXT NOT NULL,
                    downlink_freq_ghz REAL NOT NULL,
                    slant_range_km REAL NOT NULL,
                    tx_eirp_dbw REAL NOT NULL,
                    rx_g_over_t_db_k REAL NOT NULL,
                    bandwidth_mhz REAL NOT NULL,
                    cnr_db REAL NOT NULL,
                    link_margin_db REAL NOT NULL,
                    is_viable INTEGER NOT NULL DEFAULT 1,
                    status TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
            """)
            conn.execute("CREATE INDEX IF NOT EXISTS idx_sat_name ON satellite_link_budgets(satellite_name);")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_sat_viable ON satellite_link_budgets(is_viable);")
            conn.execute("""
                CREATE TABLE IF NOT EXISTS student_kampus_mengajar (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    student_name TEXT NOT NULL,
                    nim TEXT NOT NULL UNIQUE,
                    target_school TEXT NOT NULL,
                    school_level TEXT NOT NULL,
                    teaching_hours INTEGER NOT NULL,
                    composite_score REAL NOT NULL,
                    letter_grade TEXT NOT NULL,
                    converted_sks INTEGER NOT NULL,
                    status TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
            """)
            conn.execute("CREATE INDEX IF NOT EXISTS idx_km_nim ON student_kampus_mengajar(nim);")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_km_school ON student_kampus_mengajar(target_school);")
            conn.execute("""
                CREATE TABLE IF NOT EXISTS rf_intermod_records (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    component_name TEXT NOT NULL,
                    input_power_dbm REAL NOT NULL,
                    gain_db REAL NOT NULL,
                    iip3_dbm REAL NOT NULL,
                    fundamental_pout_dbm REAL NOT NULL,
                    imd3_suppression_dbc REAL NOT NULL,
                    linearity_status TEXT NOT NULL,
                    is_linear INTEGER NOT NULL DEFAULT 1,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
            """)
            conn.execute("CREATE INDEX IF NOT EXISTS idx_rf_comp ON rf_intermod_records(component_name);")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_rf_linear ON rf_intermod_records(is_linear);")
            conn.execute("""
                CREATE TABLE IF NOT EXISTS radar_detection_records (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    radar_name TEXT NOT NULL,
                    peak_power_kw REAL NOT NULL,
                    antenna_gain_dbi REAL NOT NULL,
                    rcs_m2 REAL NOT NULL,
                    freq_ghz REAL NOT NULL,
                    min_detectable_signal_dbm REAL NOT NULL,
                    max_range_km REAL NOT NULL,
                    round_trip_delay_us REAL NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
            """)
            conn.execute("CREATE INDEX IF NOT EXISTS idx_radar_name ON radar_detection_records(radar_name);")
            conn.execute("""
                CREATE TABLE IF NOT EXISTS student_wirausaha_merdeka (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    student_name TEXT NOT NULL,
                    nim TEXT NOT NULL UNIQUE,
                    startup_name TEXT NOT NULL,
                    business_sector TEXT NOT NULL,
                    mentor_score REAL NOT NULL,
                    pitch_score REAL NOT NULL,
                    composite_score REAL NOT NULL,
                    converted_sks INTEGER NOT NULL,
                    letter_grade TEXT NOT NULL,
                    status TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
            """)
            conn.execute("CREATE INDEX IF NOT EXISTS idx_wmk_nim ON student_wirausaha_merdeka(nim);")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_wmk_startup ON student_wirausaha_merdeka(startup_name);")
            conn.execute("""
                CREATE TABLE IF NOT EXISTS edfa_amplifier_records (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    device_name TEXT NOT NULL,
                    input_power_dbm REAL NOT NULL,
                    pump_power_mw REAL NOT NULL,
                    small_signal_gain_db REAL NOT NULL,
                    actual_gain_db REAL NOT NULL,
                    output_power_dbm REAL NOT NULL,
                    noise_figure_db REAL NOT NULL,
                    operating_regime TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
            """)
            conn.execute("CREATE INDEX IF NOT EXISTS idx_edfa_name ON edfa_amplifier_records(device_name);")
            conn.execute("""
                CREATE TABLE IF NOT EXISTS otdr_fiber_records (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    link_name TEXT NOT NULL,
                    fiber_length_km REAL NOT NULL,
                    wavelength_nm INTEGER NOT NULL,
                    total_loss_db REAL NOT NULL,
                    event_loss_db REAL NOT NULL,
                    attenuation_db_km REAL NOT NULL,
                    quality_status TEXT NOT NULL,
                    is_compliant INTEGER NOT NULL DEFAULT 1,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
            """)
            conn.execute("CREATE INDEX IF NOT EXISTS idx_otdr_link ON otdr_fiber_records(link_name);")
            conn.execute("""
                CREATE TABLE IF NOT EXISTS mimo_capacity_records (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    channel_name TEXT NOT NULL,
                    bandwidth_mhz REAL NOT NULL,
                    snr_db REAL NOT NULL,
                    num_tx INTEGER NOT NULL,
                    num_rx INTEGER NOT NULL,
                    spectral_eff_bps_hz REAL NOT NULL,
                    capacity_gbps REAL NOT NULL,
                    gain_factor REAL NOT NULL,
                    status TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
            """)
            conn.execute("CREATE INDEX IF NOT EXISTS idx_mimo_channel ON mimo_capacity_records(channel_name);")
            conn.execute("""
                CREATE TABLE IF NOT EXISTS student_iisma_exchange (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    student_name TEXT NOT NULL,
                    nim TEXT NOT NULL UNIQUE,
                    host_university TEXT NOT NULL,
                    country TEXT NOT NULL,
                    gpa_host REAL NOT NULL,
                    credits_taken INTEGER NOT NULL,
                    converted_sks INTEGER NOT NULL,
                    letter_grade TEXT NOT NULL,
                    status TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
            """)
            conn.execute("CREATE INDEX IF NOT EXISTS idx_iisma_nim ON student_iisma_exchange(nim);")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_iisma_host ON student_iisma_exchange(host_university);")
            conn.execute("""
                CREATE TABLE IF NOT EXISTS fspl_link_budget_records (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    link_name TEXT NOT NULL,
                    freq_mhz REAL NOT NULL,
                    distance_km REAL NOT NULL,
                    fspl_db REAL NOT NULL,
                    rx_power_dbm REAL NOT NULL,
                    fade_margin_db REAL NOT NULL,
                    is_viable INTEGER NOT NULL DEFAULT 1,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
            """)
            conn.execute("CREATE INDEX IF NOT EXISTS idx_fspl_link ON fspl_link_budget_records(link_name);")
            conn.execute("""
                CREATE TABLE IF NOT EXISTS optical_dispersion_records (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    fiber_name TEXT NOT NULL,
                    length_km REAL NOT NULL,
                    dispersion_param REAL NOT NULL,
                    pulse_broadening_ps REAL NOT NULL,
                    max_bit_rate_gbps REAL NOT NULL,
                    severity TEXT NOT NULL,
                    requires_compensation INTEGER NOT NULL DEFAULT 0,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
            """)
            conn.execute("CREATE INDEX IF NOT EXISTS idx_disp_fiber ON optical_dispersion_records(fiber_name);")
            conn.execute("""
                CREATE TABLE IF NOT EXISTS student_proyek_kemanusiaan (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    student_name TEXT NOT NULL,
                    nim TEXT NOT NULL UNIQUE,
                    partner_org TEXT NOT NULL,
                    location TEXT NOT NULL,
                    field_hours INTEGER NOT NULL,
                    composite_score REAL NOT NULL,
                    converted_sks INTEGER NOT NULL,
                    letter_grade TEXT NOT NULL,
                    status TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
            """)
            conn.execute("CREATE INDEX IF NOT EXISTS idx_kemanusiaan_nim ON student_proyek_kemanusiaan(nim);")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_kemanusiaan_org ON student_proyek_kemanusiaan(partner_org);")
            conn.execute("""
                CREATE TABLE IF NOT EXISTS optical_pmd_records (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    fiber_name TEXT NOT NULL,
                    length_km REAL NOT NULL,
                    pmd_coeff REAL NOT NULL,
                    mean_dgd_ps REAL NOT NULL,
                    max_bit_rate_gbps REAL NOT NULL,
                    outage_risk TEXT NOT NULL,
                    is_safe INTEGER NOT NULL DEFAULT 1,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
            """)
            conn.execute("CREATE INDEX IF NOT EXISTS idx_pmd_fiber ON optical_pmd_records(fiber_name);")
            conn.execute("""
                CREATE TABLE IF NOT EXISTS cost231_propagation_records (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    area_name TEXT NOT NULL,
                    freq_mhz REAL NOT NULL,
                    distance_km REAL NOT NULL,
                    base_station_height_m REAL NOT NULL,
                    mobile_height_m REAL NOT NULL,
                    path_loss_db REAL NOT NULL,
                    coverage_quality TEXT NOT NULL,
                    is_metro INTEGER NOT NULL DEFAULT 0,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
            """)
            conn.execute("CREATE INDEX IF NOT EXISTS idx_cost231_area ON cost231_propagation_records(area_name);")


























    def is_keyphrase_used(self, keyphrase: str) -> bool:
        normalized = keyphrase.strip().lower()
        with self._get_connection() as conn:
            cursor = conn.execute(
                "SELECT COUNT(1) FROM articles WHERE LOWER(TRIM(focus_keyphrase)) = ?",
                (normalized,)
            )
            count = cursor.fetchone()[0]
            return count > 0

    def is_slug_used(self, slug: str) -> bool:
        normalized = slug.strip().lower()
        with self._get_connection() as conn:
            cursor = conn.execute(
                "SELECT COUNT(1) FROM articles WHERE LOWER(TRIM(slug)) = ?",
                (normalized,)
            )
            count = cursor.fetchone()[0]
            return count > 0

    def save_article(self, data: Dict[str, Any]) -> int:
        with self._get_connection() as conn:
            cursor = conn.execute("""
                INSERT INTO articles (
                    topic, category, publish_date, image_url, focus_keyphrase,
                    seo_title, slug, meta_description, html_content, status, wp_post_id
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                data["topic"],
                data["category"],
                data["publish_date"],
                data.get("image_url", ""),
                data["focus_keyphrase"],
                data["seo_title"],
                data["slug"],
                data["meta_description"],
                data.get("html_content", ""),
                data.get("status", "draft"),
                data.get("wp_post_id")
            ))
            return cursor.lastrowid

    def list_articles(self, limit: int = 50, include_deleted: bool = False) -> List[Dict[str, Any]]:
        with self._get_connection() as conn:
            query = "SELECT * FROM articles" if include_deleted else "SELECT * FROM articles WHERE is_deleted = 0"
            cursor = conn.execute(f"{query} ORDER BY id DESC LIMIT ?", (limit,))
            return [dict(row) for row in cursor.fetchall()]

    def soft_delete_article(self, article_id: int) -> bool:
        with self._get_connection() as conn:
            cursor = conn.execute("UPDATE articles SET is_deleted = 1 WHERE id = ?", (article_id,))
            if cursor.rowcount > 0:
                conn.execute(
                    "INSERT INTO article_audit_logs (article_id, old_status, new_status, note) VALUES (?, ?, ?, ?)",
                    (article_id, "active", "trashed", "Soft-deleted to trash")
                )
                return True
            return False

    def restore_article(self, article_id: int) -> bool:
        with self._get_connection() as conn:
            cursor = conn.execute("UPDATE articles SET is_deleted = 0 WHERE id = ?", (article_id,))
            if cursor.rowcount > 0:
                conn.execute(
                    "INSERT INTO article_audit_logs (article_id, old_status, new_status, note) VALUES (?, ?, ?, ?)",
                    (article_id, "trashed", "restored", "Restored from trash")
                )
                return True
            return False

    def list_trash(self, limit: int = 50) -> List[Dict[str, Any]]:
        with self._get_connection() as conn:
            cursor = conn.execute(
                "SELECT * FROM articles WHERE is_deleted = 1 ORDER BY id DESC LIMIT ?",
                (limit,)
            )
            return [dict(row) for row in cursor.fetchall()]

    def update_wp_post_id(self, article_id: int, wp_post_id: int, status: str = "published") -> None:
        with self._get_connection() as conn:
            conn.execute(
                "UPDATE articles SET wp_post_id = ?, status = ? WHERE id = ?",
                (wp_post_id, status, article_id)
            )

    def get_article_by_slug(self, slug: str) -> Optional[Dict[str, Any]]:
        with self._get_connection() as conn:
            cursor = conn.execute("SELECT * FROM articles WHERE slug = ?", (slug.strip().lower(),))
            row = cursor.fetchone()
            return dict(row) if row else None

    def get_article_by_id(self, article_id: int) -> Optional[Dict[str, Any]]:
        with self._get_connection() as conn:
            cursor = conn.execute("SELECT * FROM articles WHERE id = ?", (article_id,))
            row = cursor.fetchone()
            return dict(row) if row else None

    def search_articles(self, query: str, limit: int = 20) -> List[Dict[str, Any]]:
        pattern = f"%{query.strip().lower()}%"
        with self._get_connection() as conn:
            cursor = conn.execute(
                """
                SELECT * FROM articles
                WHERE LOWER(topic) LIKE ?
                   OR LOWER(focus_keyphrase) LIKE ?
                   OR LOWER(seo_title) LIKE ?
                ORDER BY id DESC LIMIT ?
                """,
                (pattern, pattern, pattern, limit)
            )
            return [dict(row) for row in cursor.fetchall()]

    def delete_article(self, article_id: int) -> bool:
        with self._get_connection() as conn:
            cursor = conn.execute("DELETE FROM articles WHERE id = ?", (article_id,))
            return cursor.rowcount > 0

    def get_statistics(self) -> Dict[str, Any]:
        with self._get_connection() as conn:
            total = conn.execute("SELECT COUNT(1) FROM articles").fetchone()[0]
            published = conn.execute("SELECT COUNT(1) FROM articles WHERE status IN ('published', 'draft_in_wp')").fetchone()[0]
            ready = conn.execute("SELECT COUNT(1) FROM articles WHERE status = 'ready'").fetchone()[0]
            needs_review = conn.execute("SELECT COUNT(1) FROM articles WHERE status = 'needs_review'").fetchone()[0]
            return {
                "total_articles": total,
                "published_count": published,
                "ready_count": ready,
                "needs_review_count": needs_review,
            }

    def add_tags(self, article_id: int, tags: List[str]) -> None:
        with self._get_connection() as conn:
            for tag in tags:
                normalized = tag.strip().lower()
                if normalized:
                    conn.execute(
                        "INSERT OR IGNORE INTO article_tags (article_id, tag) VALUES (?, ?)",
                        (article_id, normalized)
                    )

    def get_article_tags(self, article_id: int) -> List[str]:
        with self._get_connection() as conn:
            cursor = conn.execute(
                "SELECT tag FROM article_tags WHERE article_id = ? ORDER BY tag ASC",
                (article_id,)
            )
            return [row["tag"] for row in cursor.fetchall()]

    def get_articles_by_tag(self, tag: str, limit: int = 50) -> List[Dict[str, Any]]:
        normalized = tag.strip().lower()
        with self._get_connection() as conn:
            cursor = conn.execute(
                """
                SELECT a.* FROM articles a
                JOIN article_tags t ON a.id = t.article_id
                WHERE t.tag = ?
                ORDER BY a.id DESC LIMIT ?
                """,
                (normalized, limit)
            )
            return [dict(row) for row in cursor.fetchall()]

    def update_status(self, article_id: int, new_status: str, note: str = "") -> bool:
        with self._get_connection() as conn:
            cursor = conn.execute("SELECT status FROM articles WHERE id = ?", (article_id,))
            row = cursor.fetchone()
            if not row:
                return False
            old_status = row["status"]
            conn.execute("UPDATE articles SET status = ? WHERE id = ?", (new_status, article_id))
            conn.execute(
                "INSERT INTO article_audit_logs (article_id, old_status, new_status, note) VALUES (?, ?, ?, ?)",
                (article_id, old_status, new_status, note)
            )
            return True

    def get_audit_logs(self, article_id: int) -> List[Dict[str, Any]]:
        with self._get_connection() as conn:
            cursor = conn.execute(
                "SELECT * FROM article_audit_logs WHERE article_id = ? ORDER BY id ASC",
                (article_id,)
            )
            return [dict(row) for row in cursor.fetchall()]

    def bulk_update_status(self, article_ids: List[int], status: str) -> int:
        if not article_ids:
            return 0
        placeholders = ",".join("?" for _ in article_ids)
        with self._get_connection() as conn:
            cursor = conn.execute(
                f"UPDATE articles SET status = ? WHERE id IN ({placeholders})",
                [status] + article_ids
            )
            return cursor.rowcount

    def filter_by_date_range(self, start_date: str, end_date: str) -> List[Dict[str, Any]]:
        with self._get_connection() as conn:
            cursor = conn.execute(
                """
                SELECT * FROM articles
                WHERE publish_date >= ? AND publish_date <= ?
                ORDER BY publish_date DESC, id DESC
                """,
                (start_date, end_date)
            )
            return [dict(row) for row in cursor.fetchall()]

    def search_articles(self, query: str, limit: int = 20) -> List[Dict[str, Any]]:
        """
        Performs multi-column keyword search with matching context highlighting.
        """
        cleaned_query = query.strip()
        if not cleaned_query:
            return []
        pattern = f"%{cleaned_query}%"
        with self._get_connection() as conn:
            cursor = conn.execute(
                """
                SELECT * FROM articles
                WHERE topic LIKE ? OR focus_keyphrase LIKE ? OR meta_description LIKE ? OR html_content LIKE ?
                ORDER BY id DESC LIMIT ?
                """,
                (pattern, pattern, pattern, pattern, limit)
            )
            rows = [dict(row) for row in cursor.fetchall()]

        for item in rows:
            desc = item.get("meta_description", "")
            item["matched_snippet"] = desc if cleaned_query.lower() in desc.lower() else item.get("topic", "")

        return rows

    def optimize_and_check_integrity(self) -> Dict[str, Any]:
        """
        Executes database integrity check and compacts SQLite database with VACUUM.
        """
        with self._get_connection() as conn:
            cursor = conn.execute("PRAGMA integrity_check;")
            integrity_result = cursor.fetchone()[0]
            is_ok = integrity_result == "ok"
            if is_ok:
                conn.execute("VACUUM;")
            return {
                "status": "ok" if is_ok else "corrupted",
                "integrity_check": integrity_result,
                "vacuumed": is_ok
            }

    def create_revision(self, article_id: int) -> Optional[int]:
        """
        Creates a timestamped snapshot revision of the current article content.
        """
        with self._get_connection() as conn:
            cursor = conn.execute("SELECT html_content, meta_description FROM articles WHERE id = ?", (article_id,))
            row = cursor.fetchone()
            if not row:
                return None
            rev_count_cur = conn.execute("SELECT COUNT(*) FROM article_revisions WHERE article_id = ?", (article_id,))
            next_rev = rev_count_cur.fetchone()[0] + 1
            rev_cur = conn.execute(
                "INSERT INTO article_revisions (article_id, revision_num, html_content, meta_description) VALUES (?, ?, ?, ?)",
                (article_id, next_rev, row["html_content"], row["meta_description"])
            )
            return rev_cur.lastrowid

    def get_revisions(self, article_id: int) -> List[Dict[str, Any]]:
        with self._get_connection() as conn:
            cursor = conn.execute(
                "SELECT * FROM article_revisions WHERE article_id = ? ORDER BY revision_num DESC",
                (article_id,)
            )
            return [dict(row) for row in cursor.fetchall()]

    def set_article_meta(self, article_id: int, key: str, value: str) -> None:
        """
        Stores or updates arbitrary key-value metadata for an article.
        """
        with self._get_connection() as conn:
            conn.execute("""
                INSERT INTO article_meta (article_id, meta_key, meta_value)
                VALUES (?, ?, ?)
                ON CONFLICT(article_id, meta_key) DO UPDATE SET meta_value = excluded.meta_value;
            """, (article_id, key.strip(), value.strip()))

    def get_article_meta(self, article_id: int, key: Optional[str] = None) -> Any:
        """
        Retrieves custom metadata for an article (single key string value, or dict of all keys).
        """
        with self._get_connection() as conn:
            if key:
                cursor = conn.execute(
                    "SELECT meta_value FROM article_meta WHERE article_id = ? AND meta_key = ?",
                    (article_id, key.strip())
                )
                row = cursor.fetchone()
                return row["meta_value"] if row else None
            else:
                cursor = conn.execute(
                    "SELECT meta_key, meta_value FROM article_meta WHERE article_id = ?",
                    (article_id,)
                )
                return {row["meta_key"]: row["meta_value"] for row in cursor.fetchall()}

    def delete_article_meta(self, article_id: int, key: str) -> bool:
        """
        Deletes a specific metadata key for an article.
        """
        with self._get_connection() as conn:
            cursor = conn.execute(
                "DELETE FROM article_meta WHERE article_id = ? AND meta_key = ?",
                (article_id, key.strip())
            )
            return cursor.rowcount > 0

    def log_export_event(self, article_id: int, export_type: str, destination_path: str) -> int:
        """
        Records an export audit event for tracking generated deliverables.
        """
        with self._get_connection() as conn:
            cursor = conn.execute("""
                INSERT INTO article_exports (article_id, export_type, destination_path)
                VALUES (?, ?, ?)
            """, (article_id, export_type.strip(), destination_path.strip()))
            return cursor.lastrowid

    def get_export_history(self, article_id: int) -> List[Dict[str, Any]]:
        """
        Fetches all recorded export events for an article.
        """
        with self._get_connection() as conn:
            cursor = conn.execute(
                "SELECT * FROM article_exports WHERE article_id = ? ORDER BY id DESC",
                (article_id,)
            )
            return [dict(row) for row in cursor.fetchall()]

    def enable_wal_mode(self) -> str:
        """
        Enables SQLite Write-Ahead Logging (WAL) mode for high-concurrency access.
        Returns the active journal mode string.
        """
        with self._get_connection() as conn:
            cursor = conn.execute("PRAGMA journal_mode=WAL;")
            row = cursor.fetchone()
            return row[0].upper() if row else "UNKNOWN"

    def list_categories(self) -> List[Dict[str, Any]]:
        """
        Retrieves distinct categories across active articles with counts.
        """
        with self._get_connection() as conn:
            cursor = conn.execute("""
                SELECT category, COUNT(1) as article_count
                FROM articles
                WHERE is_deleted = 0
                GROUP BY category
                ORDER BY article_count DESC, category ASC
            """)
            return [dict(row) for row in cursor.fetchall()]

    def get_articles_by_category(self, category: str, limit: int = 50) -> List[Dict[str, Any]]:
        """
        Retrieves non-deleted articles filtered by a specific category.
        """
        with self._get_connection() as conn:
            cursor = conn.execute("""
                SELECT * FROM articles
                WHERE LOWER(TRIM(category)) = LOWER(TRIM(?)) AND is_deleted = 0
                ORDER BY id DESC
                LIMIT ?
            """, (category, limit))
            return [dict(row) for row in cursor.fetchall()]

    def get_editorial_analytics(self, days: int = 30) -> Dict[str, Any]:
        """
        Aggregates editorial analytics and publishing velocity within the specified rolling window.
        """
        with self._get_connection() as conn:
            cursor = conn.execute("""
                SELECT status, COUNT(1) as cnt
                FROM articles
                WHERE is_deleted = 0
                  AND created_at >= datetime('now', ?)
                GROUP BY status
            """, (f"-{days} days",))
            status_counts = {row["status"]: row["cnt"] for row in cursor.fetchall()}

            cursor = conn.execute("""
                SELECT COUNT(1) as total, COUNT(DISTINCT category) as categories_active
                FROM articles
                WHERE is_deleted = 0
                  AND created_at >= datetime('now', ?)
            """, (f"-{days} days",))
            meta_row = cursor.fetchone()
            total = meta_row["total"] if meta_row else 0
            cat_count = meta_row["categories_active"] if meta_row else 0

            published = status_counts.get("published", 0)
            velocity_per_day = round(published / max(1, days), 2)

            return {
                "window_days": days,
                "total_articles": total,
                "status_breakdown": status_counts,
                "published_count": published,
                "active_categories": cat_count,
                "publishing_velocity_per_day": velocity_per_day,
            }

    def prune_revisions(self, retention_days: int = 30, keep_minimum: int = 2) -> int:
        """
        Prunes historical revisions older than retention_days while retaining
        at least keep_minimum recent revisions per article.
        If retention_days is 0 or negative, prunes all revisions exceeding keep_minimum.
        Returns the number of deleted revisions.
        """
        with self._get_connection() as conn:
            if retention_days > 0:
                time_filter = "AND created_at < datetime('now', ?)"
                params = (keep_minimum, f"-{retention_days} days")
            else:
                time_filter = ""
                params = (keep_minimum,)

            cursor = conn.execute(f"""
                DELETE FROM article_revisions
                WHERE id NOT IN (
                    SELECT id FROM (
                        SELECT id,
                               ROW_NUMBER() OVER (PARTITION BY article_id ORDER BY revision_num DESC) as rn
                        FROM article_revisions
                    ) WHERE rn <= ?
                )
                {time_filter}
            """, params)
            return cursor.rowcount

    def schedule_publication(self, article_id: int, scheduled_at: str) -> int:
        """
        Schedules an article for automated publishing at a specific ISO timestamp.
        """
        with self._get_connection() as conn:
            cursor = conn.execute("""
                INSERT INTO article_schedules (article_id, scheduled_at, status)
                VALUES (?, ?, 'pending')
                ON CONFLICT(article_id) DO UPDATE SET
                    scheduled_at = excluded.scheduled_at,
                    status = 'pending';
            """, (article_id, scheduled_at.strip()))
            return cursor.lastrowid

    def get_pending_schedules(self, before_time: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Retrieves articles queued for scheduled publication, optionally filtered up to before_time.
        """
        with self._get_connection() as conn:
            if before_time:
                cursor = conn.execute("""
                    SELECT s.*, a.seo_title, a.slug, a.category, a.status as article_status
                    FROM article_schedules s
                    JOIN articles a ON s.article_id = a.id
                    WHERE s.status = 'pending' AND s.scheduled_at <= ? AND a.is_deleted = 0
                    ORDER BY s.scheduled_at ASC;
                """, (before_time.strip(),))
            else:
                cursor = conn.execute("""
                    SELECT s.*, a.seo_title, a.slug, a.category, a.status as article_status
                    FROM article_schedules s
                    JOIN articles a ON s.article_id = a.id
                    WHERE s.status = 'pending' AND a.is_deleted = 0
                    ORDER BY s.scheduled_at ASC;
                """)
            return [dict(row) for row in cursor.fetchall()]

    def cancel_schedule(self, article_id: int) -> bool:
        """
        Cancels an active scheduled publication entry.
        """
        with self._get_connection() as conn:
            cursor = conn.execute(
                "UPDATE article_schedules SET status = 'cancelled' WHERE article_id = ? AND status = 'pending';",
                (article_id,)
            )
            return cursor.rowcount > 0

    def export_database_dump(self) -> Dict[str, Any]:
        """
        Exports all articles, tags, revisions, metadata, and schedules into a serializable dump dict.
        """
        with self._get_connection() as conn:
            articles = [dict(r) for r in conn.execute("SELECT * FROM articles;").fetchall()]
            tags = [dict(r) for r in conn.execute("SELECT * FROM article_tags;").fetchall()]
            meta = [dict(r) for r in conn.execute("SELECT * FROM article_meta;").fetchall()]
            revisions = [dict(r) for r in conn.execute("SELECT * FROM article_revisions;").fetchall()]
            schedules = [dict(r) for r in conn.execute("SELECT * FROM article_schedules;").fetchall()]

            return {
                "schema_version": "2.3.0",
                "dump_created_at": datetime.utcnow().isoformat(),
                "articles": articles,
                "article_tags": tags,
                "article_meta": meta,
                "article_revisions": revisions,
                "article_schedules": schedules,
            }

    def import_database_dump(self, dump_data: Dict[str, Any]) -> Dict[str, int]:
        """
        Imports articles and tags from a dump dictionary into the database,
        skipping existing records that share the same slug.
        Returns counts of imported items.
        """
        imported_articles = 0
        imported_tags = 0
        with self._get_connection() as conn:
            for art in dump_data.get("articles", []):
                slug = art.get("slug", "").strip()
                if not slug:
                    continue
                existing = conn.execute("SELECT id FROM articles WHERE slug = ?", (slug,)).fetchone()
                if existing:
                    continue

                cursor = conn.execute("""
                    INSERT INTO articles (
                        topic, category, publish_date, image_url, focus_keyphrase,
                        seo_title, slug, meta_description, html_content, status, wp_post_id
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    art.get("topic", "N/A"),
                    art.get("category", "Umum"),
                    art.get("publish_date", "2026-10-01"),
                    art.get("image_url", ""),
                    art.get("focus_keyphrase", ""),
                    art.get("seo_title", ""),
                    slug,
                    art.get("meta_description", ""),
                    art.get("html_content", ""),
                    art.get("status", "draft"),
                    art.get("wp_post_id")
                ))
                new_id = cursor.lastrowid
                imported_articles += 1

                old_id = art.get("id")
                for tag_row in dump_data.get("article_tags", []):
                    if tag_row.get("article_id") == old_id:
                        conn.execute(
                            "INSERT OR IGNORE INTO article_tags (article_id, tag) VALUES (?, ?)",
                            (new_id, tag_row.get("tag", "").strip())
                        )
                        imported_tags += 1

        return {
            "articles_imported": imported_articles,
            "tags_imported": imported_tags,
        }

    def record_engagement(self, article_id: int, views_increment: int = 1, shares_increment: int = 0) -> Dict[str, Any]:
        """
        Increments view and share counts for an article and returns updated stats.
        """
        with self._get_connection() as conn:
            conn.execute("""
                INSERT INTO article_engagement (article_id, view_count, share_count, last_updated)
                VALUES (?, ?, ?, CURRENT_TIMESTAMP)
                ON CONFLICT(article_id) DO UPDATE SET
                    view_count = view_count + excluded.view_count,
                    share_count = share_count + excluded.share_count,
                    last_updated = CURRENT_TIMESTAMP;
            """, (article_id, max(0, views_increment), max(0, shares_increment)))

            cursor = conn.execute(
                "SELECT * FROM article_engagement WHERE article_id = ?;",
                (article_id,)
            )
            return dict(cursor.fetchone())

    def get_top_engaged_articles(self, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Retrieves top performing articles ranked by total views and shares.
        """
        with self._get_connection() as conn:
            cursor = conn.execute("""
                SELECT e.*, a.seo_title, a.slug, a.category
                FROM article_engagement e
                JOIN articles a ON e.article_id = a.id
                WHERE a.is_deleted = 0
                ORDER BY e.view_count DESC, e.share_count DESC
                LIMIT ?;
            """, (limit,))
            return [dict(row) for row in cursor.fetchall()]

    def add_category(self, name: str, slug: str, parent_id: Optional[int] = None, description: Optional[str] = None) -> int:
        """
        Adds a new hierarchical category for editorial taxonomy.
        """
        with self._get_connection() as conn:
            cursor = conn.execute("""
                INSERT INTO article_categories (name, slug, parent_id, description)
                VALUES (?, ?, ?, ?);
            """, (name.strip(), slug.strip().lower(), parent_id, description))
            return cursor.lastrowid

    def get_category_tree(self) -> List[Dict[str, Any]]:
        """
        Retrieves all categories organized into a parent-children tree structure.
        """
        with self._get_connection() as conn:
            cursor = conn.execute("SELECT * FROM article_categories ORDER BY parent_id ASC, name ASC;")
            all_cats = [dict(r) for r in cursor.fetchall()]

        by_id = {c["id"]: {**c, "children": []} for c in all_cats}
        roots = []
        for c in by_id.values():
            p_id = c.get("parent_id")
            if p_id and p_id in by_id:
                by_id[p_id]["children"].append(c)
            else:
                roots.append(c)
        return roots

    def get_category_by_slug(self, slug: str) -> Optional[Dict[str, Any]]:
        """
        Retrieves category data by its URL slug.
        """
        with self._get_connection() as conn:
            cursor = conn.execute("SELECT * FROM article_categories WHERE slug = ?;", (slug.strip().lower(),))
            row = cursor.fetchone()
            return dict(row) if row else None

    def acquire_article_lock(self, article_id: int, user_id: str, ttl_seconds: int = 300) -> Tuple[bool, Optional[str]]:
        """
        Acquires or refreshes an editing lease lock for an article.
        Returns (True, None) on success, or (False, locked_by_user) if locked by someone else.
        """
        now = datetime.utcnow()
        now_iso = now.isoformat()
        expires_iso = (now + timedelta(seconds=ttl_seconds)).isoformat()

        with self._get_connection() as conn:
            cursor = conn.execute("SELECT locked_by, expires_at FROM article_locks WHERE article_id = ?;", (article_id,))
            row = cursor.fetchone()

            if row:
                locked_by = row["locked_by"]
                expires_at = row["expires_at"]
                if locked_by != user_id and expires_at > now_iso:
                    return False, locked_by

            conn.execute("""
                INSERT INTO article_locks (article_id, locked_by, expires_at)
                VALUES (?, ?, ?)
                ON CONFLICT(article_id) DO UPDATE SET
                    locked_by = excluded.locked_by,
                    expires_at = excluded.expires_at,
                    created_at = CURRENT_TIMESTAMP;
            """, (article_id, user_id, expires_iso))
            return True, None

    def release_article_lock(self, article_id: int, user_id: str) -> bool:
        """
        Releases an active editing lease if held by the given user.
        """
        with self._get_connection() as conn:
            cursor = conn.execute(
                "DELETE FROM article_locks WHERE article_id = ? AND locked_by = ?;",
                (article_id, user_id)
            )
            return cursor.rowcount > 0

    def get_article_lock_status(self, article_id: int) -> Optional[Dict[str, Any]]:
        """
        Retrieves active lock status for an article if still valid.
        """
        now_iso = datetime.utcnow().isoformat()
        with self._get_connection() as conn:
            cursor = conn.execute(
                "SELECT * FROM article_locks WHERE article_id = ? AND expires_at > ?;",
                (article_id, now_iso)
            )
            row = cursor.fetchone()
            return dict(row) if row else None

    def batch_replace_content(
        self,
        target_str: str,
        replace_str: str,
        status_filter: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Executes a transactional search-and-replace across article drafts
        for seo_title, meta_description, and html_content.
        """
        if not target_str:
            return {"articles_updated": 0, "total_replacements": 0}

        updated_count = 0
        total_replacements = 0

        with self._get_connection() as conn:
            query = "SELECT id, seo_title, meta_description, html_content FROM articles WHERE is_deleted = 0"
            params = []
            if status_filter:
                query += " AND status = ?"
                params.append(status_filter)

            cursor = conn.execute(query, params)
            rows = cursor.fetchall()

            for row in rows:
                art_id = row["id"]
                title = row["seo_title"] or ""
                desc = row["meta_description"] or ""
                html = row["html_content"] or ""

                matches = title.count(target_str) + desc.count(target_str) + html.count(target_str)
                if matches > 0:
                    new_title = title.replace(target_str, replace_str)
                    new_desc = desc.replace(target_str, replace_str)
                    new_html = html.replace(target_str, replace_str)

                    conn.execute("""
                        UPDATE articles SET
                            seo_title = ?,
                            meta_description = ?,
                            html_content = ?
                        WHERE id = ?;
                    """, (new_title, new_desc, new_html, art_id))
                    updated_count += 1
                    total_replacements += matches

        return {
            "articles_updated": updated_count,
            "total_replacements": total_replacements
        }

    def get_category_analytics(self) -> List[Dict[str, Any]]:
        """
        Aggregates article count, total views, and average views grouped by category.
        """
        with self._get_connection() as conn:
            cursor = conn.execute("""
                SELECT
                    a.category,
                    COUNT(a.id) AS total_articles,
                    COALESCE(SUM(e.view_count), 0) AS total_views,
                    COALESCE(AVG(e.view_count), 0.0) AS avg_views
                FROM articles a
                LEFT JOIN article_engagement e ON a.id = e.article_id
                WHERE a.is_deleted = 0
                GROUP BY a.category
                ORDER BY total_views DESC, total_articles DESC;
            """)
            return [dict(row) for row in cursor.fetchall()]

    def add_bookmark(self, article_id: int, user_identifier: str, notes: Optional[str] = None) -> int:
        """
        Adds an article to the user's reading list or bookmarks.
        """
        with self._get_connection() as conn:
            cursor = conn.execute("""
                INSERT INTO article_bookmarks (article_id, user_identifier, notes)
                VALUES (?, ?, ?)
                ON CONFLICT(article_id, user_identifier) DO UPDATE SET notes = excluded.notes;
            """, (article_id, user_identifier.strip(), notes.strip() if notes else None))
            return cursor.lastrowid

    def list_bookmarks(self, user_identifier: str) -> List[Dict[str, Any]]:
        """
        Lists all bookmarked articles for a specific user.
        """
        with self._get_connection() as conn:
            cursor = conn.execute("""
                SELECT b.id AS bookmark_id, b.article_id, b.notes, b.created_at AS bookmarked_at,
                       a.seo_title, a.slug, a.category, a.status
                FROM article_bookmarks b
                JOIN articles a ON b.article_id = a.id
                WHERE b.user_identifier = ? AND a.is_deleted = 0
                ORDER BY b.created_at DESC;
            """, (user_identifier.strip(),))
            return [dict(row) for row in cursor.fetchall()]

    def remove_bookmark(self, article_id: int, user_identifier: str) -> bool:
        """
        Removes an article from the user's reading list.
        """
        with self._get_connection() as conn:
            cursor = conn.execute("""
                DELETE FROM article_bookmarks
                WHERE article_id = ? AND user_identifier = ?;
            """, (article_id, user_identifier.strip()))
            return cursor.rowcount > 0

    def get_applied_migrations(self) -> List[str]:
        """
        Retrieves all applied migration versions ordered chronologically.
        """
        with self._get_connection() as conn:
            cursor = conn.execute("SELECT version FROM schema_migrations ORDER BY applied_at ASC;")
            return [row["version"] for row in cursor.fetchall()]

    def record_migration(self, version: str) -> None:
        """
        Records an applied migration version into the tracking table.
        """
        with self._get_connection() as conn:
            conn.execute("INSERT OR IGNORE INTO schema_migrations (version) VALUES (?);", (version.strip(),))

    def update_reading_metrics(self, article_id: int, word_count: int, reading_time_min: int) -> None:
        """
        Records or updates word count and calculated reading time metrics for an article.
        """
        with self._get_connection() as conn:
            conn.execute("""
                INSERT INTO article_reading_metrics (article_id, word_count, reading_time_min, updated_at)
                VALUES (?, ?, ?, CURRENT_TIMESTAMP)
                ON CONFLICT(article_id) DO UPDATE SET
                    word_count = excluded.word_count,
                    reading_time_min = excluded.reading_time_min,
                    updated_at = CURRENT_TIMESTAMP;
            """, (article_id, word_count, reading_time_min))

    def get_reading_metrics(self, article_id: int) -> Optional[Dict[str, Any]]:
        """
        Retrieves reading time and word count statistics for an article.
        """
        with self._get_connection() as conn:
            cursor = conn.execute("""
                SELECT article_id, word_count, reading_time_min, updated_at
                FROM article_reading_metrics
                WHERE article_id = ?;
            """, (article_id,))
            row = cursor.fetchone()
            return dict(row) if row else None

    def subscribe_user(self, user_id: str, channel: str, category: str = "all") -> bool:
        """
        Subscribes a user to editorial publication notifications for a given category.
        """
        with self._get_connection() as conn:
            cursor = conn.execute("""
                INSERT OR IGNORE INTO editorial_subscribers (user_id, channel, category)
                VALUES (?, ?, ?);
            """, (user_id.strip(), channel.strip().lower(), category.strip().lower()))
            return cursor.rowcount > 0

    def get_subscribers(self, category: str = "all") -> List[Dict[str, Any]]:
        """
        Retrieves active subscribers matching the category or subscribed to 'all'.
        """
        cat = category.strip().lower()
        with self._get_connection() as conn:
            if cat == "all":
                cursor = conn.execute("""
                    SELECT id, user_id, channel, category, created_at
                    FROM editorial_subscribers;
                """)
            else:
                cursor = conn.execute("""
                    SELECT id, user_id, channel, category, created_at
                    FROM editorial_subscribers
                    WHERE category = ? OR category = 'all';
                """, (cat,))
            return [dict(row) for row in cursor.fetchall()]

    def unsubscribe_user(self, user_id: str, category: str = "all") -> bool:
        """
        Unsubscribes a user from notifications for a specific category or all categories.
        """
        cat = category.strip().lower()
        with self._get_connection() as conn:
            if cat == "all":
                cursor = conn.execute("""
                    DELETE FROM editorial_subscribers
                    WHERE user_id = ?;
                """, (user_id.strip(),))
            else:
                cursor = conn.execute("""
                    DELETE FROM editorial_subscribers
                    WHERE user_id = ? AND category = ?;
                """, (user_id.strip(), cat))
            return cursor.rowcount > 0

    def compare_revisions(self, article_id: int, rev_a: int, rev_b: int) -> Dict[str, Any]:
        """
        Compares two stored revisions of an article, computing character and word count deltas.
        """
        with self._get_connection() as conn:
            cur_a = conn.execute(
                "SELECT revision_num, html_content, meta_description, created_at FROM article_revisions WHERE article_id = ? AND revision_num = ?",
                (article_id, rev_a)
            )
            row_a = cur_a.fetchone()
            cur_b = conn.execute(
                "SELECT revision_num, html_content, meta_description, created_at FROM article_revisions WHERE article_id = ? AND revision_num = ?",
                (article_id, rev_b)
            )
            row_b = cur_b.fetchone()

            if not row_a or not row_b:
                return {
                    "article_id": article_id,
                    "found": False,
                    "error": "One or both revisions not found"
                }

            content_a = row_a["html_content"] or ""
            content_b = row_b["html_content"] or ""
            words_a = len(content_a.split())
            words_b = len(content_b.split())
            chars_a = len(content_a)
            chars_b = len(content_b)

            return {
                "article_id": article_id,
                "found": True,
                "rev_a": {
                    "revision_num": rev_a,
                    "word_count": words_a,
                    "char_count": chars_a,
                    "meta_description": row_a["meta_description"],
                    "created_at": row_a["created_at"]
                },
                "rev_b": {
                    "revision_num": rev_b,
                    "word_count": words_b,
                    "char_count": chars_b,
                    "meta_description": row_b["meta_description"],
                    "created_at": row_b["created_at"]
                },
                "deltas": {
                    "word_diff": words_b - words_a,
                    "char_diff": chars_b - chars_a,
                    "meta_changed": row_a["meta_description"] != row_b["meta_description"]
                }
            }

    def record_article_view(self, article_id: int, referrer: str = "", user_agent_hash: str = "") -> int:
        """
        Records an individual timestamped article view event for analytics.
        """
        with self._get_connection() as conn:
            cursor = conn.execute("""
                INSERT INTO article_view_logs (article_id, referrer, user_agent_hash)
                VALUES (?, ?, ?)
            """, (article_id, referrer.strip(), user_agent_hash.strip()))
            conn.execute("""
                INSERT INTO article_engagement (article_id, view_count, share_count)
                VALUES (?, 1, 0)
                ON CONFLICT(article_id) DO UPDATE SET
                    view_count = view_count + 1,
                    last_updated = CURRENT_TIMESTAMP;
            """, (article_id,))
            return cursor.lastrowid

    def get_article_views_by_date(self, article_id: int, days: int = 7) -> List[Dict[str, Any]]:
        """
        Returns time-series daily view count aggregates for the specified article over recent days.
        """
        with self._get_connection() as conn:
            cursor = conn.execute("""
                SELECT DATE(viewed_at) as view_date, COUNT(1) as views
                FROM article_view_logs
                WHERE article_id = ? AND viewed_at >= DATETIME('now', ? || ' days')
                GROUP BY DATE(viewed_at)
                ORDER BY view_date ASC;
            """, (article_id, f"-{days}"))
            return [{"date": row["view_date"], "views": row["views"]} for row in cursor.fetchall()]

    def create_editorial_task(self, article_id: int, assignee: str, task_type: str, due_date: str) -> int:
        """
        Creates an editorial review, proofreading, or fact-checking task assignment.
        """
        with self._get_connection() as conn:
            cursor = conn.execute("""
                INSERT INTO editorial_tasks (article_id, assignee, task_type, due_date, status)
                VALUES (?, ?, ?, ?, 'pending')
            """, (article_id, assignee.strip(), task_type.strip(), due_date.strip()))
            return cursor.lastrowid

    def list_editorial_tasks(self, status: str = "pending") -> List[Dict[str, Any]]:
        """
        Lists editorial tasks optionally filtered by status ('pending', 'in_progress', 'completed', 'all').
        """
        with self._get_connection() as conn:
            if status.lower() == "all":
                cursor = conn.execute("""
                    SELECT id, article_id, assignee, task_type, due_date, status, created_at
                    FROM editorial_tasks
                    ORDER BY id DESC;
                """)
            else:
                cursor = conn.execute("""
                    SELECT id, article_id, assignee, task_type, due_date, status, created_at
                    FROM editorial_tasks
                    WHERE status = ?
                    ORDER BY id DESC;
                """, (status.strip().lower(),))
            return [dict(row) for row in cursor.fetchall()]

    def update_task_status(self, task_id: int, status: str) -> bool:
        """
        Updates the completion status of an editorial task.
        """
        with self._get_connection() as conn:
            cursor = conn.execute("""
                UPDATE editorial_tasks
                SET status = ?
                WHERE id = ?;
            """, (status.strip().lower(), task_id))
            return cursor.rowcount > 0

    def set_taxonomy_meta(self, taxonomy: str, term_slug: str, meta_key: str, meta_value: str) -> None:
        """
        Sets a key-value metadata attribute for a taxonomy term (category, tag, series).
        """
        with self._get_connection() as conn:
            conn.execute("""
                INSERT INTO taxonomy_meta (taxonomy, term_slug, meta_key, meta_value)
                VALUES (?, ?, ?, ?)
                ON CONFLICT(taxonomy, term_slug, meta_key) DO UPDATE SET
                    meta_value = excluded.meta_value,
                    created_at = CURRENT_TIMESTAMP;
            """, (taxonomy.strip().lower(), term_slug.strip().lower(), meta_key.strip(), meta_value.strip()))

    def get_taxonomy_meta(self, taxonomy: str, term_slug: str) -> Dict[str, str]:
        """
        Retrieves all metadata key-value pairs associated with a taxonomy term.
        """
        with self._get_connection() as conn:
            cursor = conn.execute("""
                SELECT meta_key, meta_value
                FROM taxonomy_meta
                WHERE taxonomy = ? AND term_slug = ?;
            """, (taxonomy.strip().lower(), term_slug.strip().lower()))
            return {row["meta_key"]: row["meta_value"] for row in cursor.fetchall()}

    def delete_taxonomy_meta(self, taxonomy: str, term_slug: str, meta_key: str) -> bool:
        """
        Removes a specific metadata entry from a taxonomy term.
        """
        with self._get_connection() as conn:
            cursor = conn.execute("""
                DELETE FROM taxonomy_meta
                WHERE taxonomy = ? AND term_slug = ? AND meta_key = ?;
            """, (taxonomy.strip().lower(), term_slug.strip().lower(), meta_key.strip()))
            return cursor.rowcount > 0

    def add_editorial_note(self, article_id: int, author: str, note_text: str) -> int:
        """
        Creates a new editorial collaboration note or feedback item on an article.
        """
        with self._get_connection() as conn:
            cursor = conn.execute("""
                INSERT INTO article_notes (article_id, author, note_text)
                VALUES (?, ?, ?);
            """, (article_id, author.strip(), note_text.strip()))
            return cursor.lastrowid

    def list_editorial_notes(self, article_id: int) -> List[Dict[str, Any]]:
        """
        Retrieves all editorial notes attached to an article ordered chronologically.
        """
        with self._get_connection() as conn:
            cursor = conn.execute("""
                SELECT id, article_id, author, note_text, created_at
                FROM article_notes
                WHERE article_id = ?
                ORDER BY id ASC;
            """, (article_id,))
            return [dict(row) for row in cursor.fetchall()]

    def delete_editorial_note(self, note_id: int) -> bool:
        """
        Removes an editorial note by its primary ID.
        """
        with self._get_connection() as conn:
            cursor = conn.execute("DELETE FROM article_notes WHERE id = ?;", (note_id,))
            return cursor.rowcount > 0

    def log_webhook_dispatch(
        self,
        event: str,
        target_url: str,
        status_code: int,
        payload_snippet: str = ""
    ) -> int:
        """
        Records an outbound publishing webhook notification attempt and HTTP status code.
        """
        with self._get_connection() as conn:
            cursor = conn.execute("""
                INSERT INTO publishing_webhook_logs (event, target_url, status_code, payload_snippet)
                VALUES (?, ?, ?, ?);
            """, (event.strip(), target_url.strip(), int(status_code), payload_snippet.strip()))
            return cursor.lastrowid

    def get_recent_webhook_logs(self, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Retrieves recent webhook dispatch logs ordered by latest creation timestamp.
        """
        with self._get_connection() as conn:
            cursor = conn.execute("""
                SELECT id, event, target_url, status_code, payload_snippet, created_at
                FROM publishing_webhook_logs
                ORDER BY id DESC
                LIMIT ?;
            """, (int(limit),))
            return [dict(row) for row in cursor.fetchall()]

    def add_taxonomy_synonym(self, canonical_term: str, alias_term: str) -> bool:
        """
        Registers an alias term mapping to a canonical academic taxonomy term.
        """
        can = canonical_term.strip().lower()
        alias = alias_term.strip().lower()
        if not can or not alias or can == alias:
            return False
        with self._get_connection() as conn:
            cursor = conn.execute("""
                INSERT OR REPLACE INTO taxonomy_synonyms (canonical_term, alias_term)
                VALUES (?, ?);
            """, (can, alias))
            return cursor.rowcount > 0

    def resolve_canonical_term(self, alias_term: str) -> str:
        """
        Resolves an alias term to its canonical academic taxonomy term, or returns the term itself if none found.
        """
        cleaned = alias_term.strip().lower()
        with self._get_connection() as conn:
            cursor = conn.execute("""
                SELECT canonical_term
                FROM taxonomy_synonyms
                WHERE alias_term = ?;
            """, (cleaned,))
            row = cursor.fetchone()
            return row["canonical_term"] if row else cleaned

    def list_taxonomy_synonyms(self) -> List[Dict[str, str]]:
        """
        Lists all registered taxonomy alias-to-canonical term mappings.
        """
        with self._get_connection() as conn:
            cursor = conn.execute("""
                SELECT canonical_term, alias_term
                FROM taxonomy_synonyms
                ORDER BY canonical_term ASC, alias_term ASC;
            """)
            return [dict(row) for row in cursor.fetchall()]

    def assign_article_reviewer(self, article_id: int, reviewer_name: str, reviewer_email: str) -> int:
        """
        Assigns an academic peer reviewer to an article.
        """
        with self._get_connection() as conn:
            cursor = conn.execute("""
                INSERT INTO article_reviewers (article_id, reviewer_name, reviewer_email, status)
                VALUES (?, ?, ?, 'assigned')
            """, (article_id, reviewer_name.strip(), reviewer_email.strip()))
            return cursor.lastrowid

    def list_article_reviewers(self, article_id: int) -> List[Dict[str, Any]]:
        """
        Lists all peer reviewers assigned to an article.
        """
        with self._get_connection() as conn:
            cursor = conn.execute("""
                SELECT id, article_id, reviewer_name, reviewer_email, status, assigned_at, updated_at
                FROM article_reviewers
                WHERE article_id = ?
                ORDER BY id ASC
            """, (article_id,))
            return [dict(row) for row in cursor.fetchall()]

    def update_reviewer_status(self, review_id: int, status: str) -> bool:
        """
        Updates the peer review status (e.g., 'in_review', 'accepted', 'rejected', 'changes_requested').
        """
        with self._get_connection() as conn:
            cursor = conn.execute("""
                UPDATE article_reviewers
                SET status = ?, updated_at = CURRENT_TIMESTAMP
                WHERE id = ?
            """, (status.strip(), review_id))
            return cursor.rowcount > 0

    def record_syndication_log(self, article_id: int, platform: str, external_url: str) -> int:
        """
        Records an external syndication or republication of an article (e.g. Medium, LinkedIn, ResearchGate).
        """
        with self._get_connection() as conn:
            cursor = conn.execute("""
                INSERT INTO syndication_logs (article_id, platform, external_url)
                VALUES (?, ?, ?)
            """, (article_id, platform.strip(), external_url.strip()))
            return cursor.lastrowid

    def get_syndication_logs(self, article_id: int) -> List[Dict[str, Any]]:
        """
        Retrieves all external syndication logs recorded for an article.
        """
        with self._get_connection() as conn:
            cursor = conn.execute("""
                SELECT id, article_id, platform, external_url, syndicated_at
                FROM syndication_logs
                WHERE article_id = ?
                ORDER BY id ASC
            """, (article_id,))
            return [dict(row) for row in cursor.fetchall()]

    def set_checklist_item(
        self,
        article_id: int,
        item_key: str,
        item_label: str,
        is_checked: bool,
        checked_by: str = ""
    ) -> bool:
        """
        Sets or updates an editorial workflow checklist verification item for an article.
        """
        val = 1 if is_checked else 0
        with self._get_connection() as conn:
            conn.execute("""
                INSERT INTO editorial_checklists (article_id, item_key, item_label, is_checked, checked_by, checked_at)
                VALUES (?, ?, ?, ?, ?, CASE WHEN ? = 1 THEN CURRENT_TIMESTAMP ELSE NULL END)
                ON CONFLICT(article_id, item_key) DO UPDATE SET
                    item_label = excluded.item_label,
                    is_checked = excluded.is_checked,
                    checked_by = excluded.checked_by,
                    checked_at = CASE WHEN excluded.is_checked = 1 THEN CURRENT_TIMESTAMP ELSE NULL END
            """, (article_id, item_key.strip(), item_label.strip(), val, checked_by.strip(), val))
            return True

    def get_checklist_status(self, article_id: int) -> List[Dict[str, Any]]:
        """
        Retrieves all checklist verification items for an article.
        """
        with self._get_connection() as conn:
            cursor = conn.execute("""
                SELECT id, article_id, item_key, item_label, is_checked, checked_by, checked_at, created_at
                FROM editorial_checklists
                WHERE article_id = ?
                ORDER BY id ASC
            """, (article_id,))
            rows = []
            for r in cursor.fetchall():
                d = dict(r)
                d["is_checked"] = bool(d["is_checked"])
                rows.append(d)
            return rows

    def record_article_citation(
        self,
        article_id: int,
        citing_paper_title: str,
        citing_authors: str,
        journal_name: str,
        citation_year: int,
        doi: str = ""
    ) -> int:
        """
        Records an academic citation of an article by external papers or journals.
        """
        with self._get_connection() as conn:
            cursor = conn.execute("""
                INSERT INTO article_citations (article_id, citing_paper_title, citing_authors, journal_name, citation_year, doi)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (article_id, citing_paper_title.strip(), citing_authors.strip(), journal_name.strip(), int(citation_year), doi.strip()))
            return cursor.lastrowid

    def get_article_citations(self, article_id: int) -> List[Dict[str, Any]]:
        """
        Retrieves all academic citations recorded for an article.
        """
        with self._get_connection() as conn:
            cursor = conn.execute("""
                SELECT id, article_id, citing_paper_title, citing_authors, journal_name, citation_year, doi, created_at
                FROM article_citations
                WHERE article_id = ?
                ORDER BY citation_year DESC, id DESC
            """, (article_id,))
            return [dict(row) for row in cursor.fetchall()]

    def add_editorial_comment(
        self,
        article_id: int,
        author: str,
        comment_text: str,
        paragraph_index: Optional[int] = None
    ) -> int:
        """
        Adds an inline editorial review comment on an article draft or paragraph.
        """
        with self._get_connection() as conn:
            cursor = conn.execute("""
                INSERT INTO editorial_comments (article_id, author, comment_text, paragraph_index)
                VALUES (?, ?, ?, ?)
            """, (article_id, author.strip(), comment_text.strip(), paragraph_index))
            return cursor.lastrowid

    def list_editorial_comments(
        self,
        article_id: int,
        include_resolved: bool = True
    ) -> List[Dict[str, Any]]:
        """
        Lists editorial review comments for an article, optionally filtering out resolved comments.
        """
        with self._get_connection() as conn:
            if include_resolved:
                cursor = conn.execute("""
                    SELECT id, article_id, author, comment_text, paragraph_index, is_resolved, created_at, resolved_at
                    FROM editorial_comments
                    WHERE article_id = ?
                    ORDER BY id ASC
                """, (article_id,))
            else:
                cursor = conn.execute("""
                    SELECT id, article_id, author, comment_text, paragraph_index, is_resolved, created_at, resolved_at
                    FROM editorial_comments
                    WHERE article_id = ? AND is_resolved = 0
                    ORDER BY id ASC
                """, (article_id,))
            return [dict(row) for row in cursor.fetchall()]

    def resolve_editorial_comment(self, comment_id: int) -> bool:
        """
        Marks an editorial review comment as resolved with current timestamp.
        """
        with self._get_connection() as conn:
            now_iso = datetime.now().isoformat()
            cursor = conn.execute("""
                UPDATE editorial_comments
                SET is_resolved = 1, resolved_at = ?
                WHERE id = ?
            """, (now_iso, comment_id))
            return cursor.rowcount > 0

    def save_content_snippet(
        self,
        snippet_key: str,
        snippet_title: str,
        snippet_html: str,
        category: str = "general"
    ) -> int:
        """
        Saves or updates a reusable content snippet by key.
        """
        with self._get_connection() as conn:
            now_iso = datetime.now().isoformat()
            cursor = conn.execute("""
                INSERT INTO content_snippets (snippet_key, snippet_title, snippet_html, category, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?, ?)
                ON CONFLICT(snippet_key) DO UPDATE SET
                    snippet_title = excluded.snippet_title,
                    snippet_html = excluded.snippet_html,
                    category = excluded.category,
                    updated_at = excluded.updated_at
            """, (snippet_key.strip(), snippet_title.strip(), snippet_html.strip(), category.strip(), now_iso, now_iso))
            return cursor.lastrowid

    def get_content_snippet(self, snippet_key: str) -> Optional[Dict[str, Any]]:
        """
        Retrieves a reusable content snippet by key.
        """
        with self._get_connection() as conn:
            cursor = conn.execute("""
                SELECT id, snippet_key, snippet_title, snippet_html, category, created_at, updated_at
                FROM content_snippets
                WHERE snippet_key = ?
            """, (snippet_key.strip(),))
            row = cursor.fetchone()
            return dict(row) if row else None

    def list_content_snippets(self, category: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Lists reusable content snippets, optionally filtered by category.
        """
        with self._get_connection() as conn:
            if category:
                cursor = conn.execute("""
                    SELECT id, snippet_key, snippet_title, snippet_html, category, created_at, updated_at
                    FROM content_snippets
                    WHERE category = ?
                    ORDER BY snippet_key ASC
                """, (category.strip(),))
            else:
                cursor = conn.execute("""
                    SELECT id, snippet_key, snippet_title, snippet_html, category, created_at, updated_at
                    FROM content_snippets
                    ORDER BY category ASC, snippet_key ASC
                """)
            return [dict(row) for row in cursor.fetchall()]

    def record_competition_achievement(
        self,
        competition_name: str,
        award_rank: str,
        team_name: str,
        team_members: List[str],
        supervisor: str,
        year: int,
        organizer: str
    ) -> int:
        """
        Records a student innovation/competition award achievement.
        """
        members_str = ", ".join(m.strip() for m in team_members if m.strip())
        with self._get_connection() as conn:
            cursor = conn.execute("""
                INSERT INTO competition_achievements (
                    competition_name, award_rank, team_name, team_members, supervisor, year, organizer
                ) VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (
                competition_name.strip(),
                award_rank.strip(),
                team_name.strip(),
                members_str,
                supervisor.strip(),
                int(year),
                organizer.strip()
            ))
            return cursor.lastrowid

    def list_competition_achievements(self, year: Optional[int] = None) -> List[Dict[str, Any]]:
        """
        Lists competition achievements, optionally filtered by year.
        """
        with self._get_connection() as conn:
            if year:
                cursor = conn.execute("""
                    SELECT id, competition_name, award_rank, team_name, team_members, supervisor, year, organizer, created_at
                    FROM competition_achievements
                    WHERE year = ?
                    ORDER BY id DESC
                """, (int(year),))
            else:
                cursor = conn.execute("""
                    SELECT id, competition_name, award_rank, team_name, team_members, supervisor, year, organizer, created_at
                    FROM competition_achievements
                    ORDER BY year DESC, id DESC
                """)
            return [dict(row) for row in cursor.fetchall()]

    def record_journal_indexing(
        self,
        journal_name: str,
        sinta_rank: int,
        issn: str,
        publisher: str,
        focus_scope: str,
        archive_url: str = ""
    ) -> int:
        """
        Records an accredited scientific journal into the department index directory.
        """
        with self._get_connection() as conn:
            cursor = conn.execute("""
                INSERT INTO journal_indexings (
                    journal_name, sinta_rank, issn, publisher, focus_scope, archive_url
                ) VALUES (?, ?, ?, ?, ?, ?)
            """, (
                journal_name.strip(),
                int(sinta_rank),
                issn.strip(),
                publisher.strip(),
                focus_scope.strip(),
                archive_url.strip()
            ))
            return cursor.lastrowid

    def list_journal_indexings(self, min_sinta: Optional[int] = None) -> List[Dict[str, Any]]:
        """
        Lists registered scientific journals, optionally filtering by maximum SINTA rank (1 being highest).
        """
        with self._get_connection() as conn:
            if min_sinta is not None:
                cursor = conn.execute("""
                    SELECT id, journal_name, sinta_rank, issn, publisher, focus_scope, archive_url, created_at
                    FROM journal_indexings
                    WHERE sinta_rank <= ?
                    ORDER BY sinta_rank ASC, journal_name ASC
                """, (int(min_sinta),))
            else:
                cursor = conn.execute("""
                    SELECT id, journal_name, sinta_rank, issn, publisher, focus_scope, archive_url, created_at
                    FROM journal_indexings
                    ORDER BY sinta_rank ASC, journal_name ASC
                """)
            return [dict(row) for row in cursor.fetchall()]

    def record_safety_inspection(
        self,
        lab_name: str,
        inspector: str,
        inspection_date: str,
        compliance_score: float,
        is_passed: bool,
        notes: str = ""
    ) -> int:
        """
        Records a laboratory safety and K3 compliance inspection report.
        """
        with self._get_connection() as conn:
            cursor = conn.execute("""
                INSERT INTO lab_safety_inspections (
                    lab_name, inspector, inspection_date, compliance_score, is_passed, notes
                ) VALUES (?, ?, ?, ?, ?, ?)
            """, (
                lab_name.strip(),
                inspector.strip(),
                inspection_date.strip(),
                float(compliance_score),
                1 if is_passed else 0,
                notes.strip()
            ))
            return cursor.lastrowid

    def list_safety_inspections(self, lab_name: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Lists laboratory safety inspection records, optionally filtered by lab name.
        """
        with self._get_connection() as conn:
            if lab_name:
                cursor = conn.execute("""
                    SELECT id, lab_name, inspector, inspection_date, compliance_score, is_passed, notes, created_at
                    FROM lab_safety_inspections
                    WHERE lab_name = ?
                    ORDER BY id DESC
                """, (lab_name.strip(),))
            else:
                cursor = conn.execute("""
                    SELECT id, lab_name, inspector, inspection_date, compliance_score, is_passed, notes, created_at
                    FROM lab_safety_inspections
                    ORDER BY id DESC
                """)
            return [dict(row) for row in cursor.fetchall()]

    def record_mbkm_credit_transfer(
        self,
        program_name: str,
        partner_institution: str,
        student_name: str,
        nim: str,
        semester: int,
        total_sks: int,
        converted_gpa: float,
        courses: List[Dict[str, Any]],
        sk_number: str = ""
    ) -> int:
        """
        Records an MBKM course credit transfer equivalence entry for a student.
        """
        import json
        with self._get_connection() as conn:
            cursor = conn.execute("""
                INSERT INTO mbkm_credit_transfers (
                    program_name, partner_institution, student_name, nim, semester,
                    total_sks, converted_gpa, courses_json, sk_number
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                program_name.strip(),
                partner_institution.strip(),
                student_name.strip(),
                nim.strip(),
                int(semester),
                int(total_sks),
                float(converted_gpa),
                json.dumps(courses),
                sk_number.strip()
            ))
            return cursor.lastrowid

    def list_mbkm_credit_transfers(self, nim: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Lists MBKM credit transfer equivalence entries, optionally filtered by student NIM.
        """
        import json
        with self._get_connection() as conn:
            if nim:
                cursor = conn.execute("""
                    SELECT id, program_name, partner_institution, student_name, nim,
                           semester, total_sks, converted_gpa, courses_json, sk_number, created_at
                    FROM mbkm_credit_transfers
                    WHERE nim = ?
                    ORDER BY id DESC
                """, (nim.strip(),))
            else:
                cursor = conn.execute("""
                    SELECT id, program_name, partner_institution, student_name, nim,
                           semester, total_sks, converted_gpa, courses_json, sk_number, created_at
                    FROM mbkm_credit_transfers
                    ORDER BY id DESC
                """)
            results = []
            for row in cursor.fetchall():
                d = dict(row)
                try:
                    d["courses"] = json.loads(d["courses_json"])
                except Exception:
                    d["courses"] = []
                results.append(d)
            return results

    def record_yudisium_clearance(
        self,
        student_name: str,
        nim: str,
        thesis_title: str,
        ipk: float,
        earned_sks: int,
        graduation_predicate: str,
        yudisium_date: str,
        verification_code: str,
        is_cleared: bool = True
    ) -> int:
        """
        Records a graduation (Yudisium) clearance and degree conferral credential.
        """
        with self._get_connection() as conn:
            cursor = conn.execute("""
                INSERT OR REPLACE INTO yudisium_clearances (
                    student_name, nim, thesis_title, ipk, earned_sks,
                    graduation_predicate, yudisium_date, verification_code, is_cleared
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                student_name.strip(),
                nim.strip(),
                thesis_title.strip(),
                float(ipk),
                int(earned_sks),
                graduation_predicate.strip(),
                yudisium_date.strip(),
                verification_code.strip(),
                1 if is_cleared else 0
            ))
            return cursor.lastrowid

    def list_yudisium_clearances(self, predicate: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Lists graduation yudisium clearances, optionally filtered by graduation predicate.
        """
        with self._get_connection() as conn:
            if predicate:
                cursor = conn.execute("""
                    SELECT id, student_name, nim, thesis_title, ipk, earned_sks,
                           graduation_predicate, yudisium_date, verification_code, is_cleared, created_at
                    FROM yudisium_clearances
                    WHERE graduation_predicate = ?
                    ORDER BY id DESC
                """, (predicate.strip(),))
            else:
                cursor = conn.execute("""
                    SELECT id, student_name, nim, thesis_title, ipk, earned_sks,
                           graduation_predicate, yudisium_date, verification_code, is_cleared, created_at
                    FROM yudisium_clearances
                    ORDER BY id DESC
                """)
            return [dict(row) for row in cursor.fetchall()]

    def get_yudisium_clearance_by_nim(self, nim: str) -> Optional[Dict[str, Any]]:
        """
        Retrieves a student's graduation yudisium clearance by NIM.
        """
        with self._get_connection() as conn:
            cursor = conn.execute("""
                SELECT id, student_name, nim, thesis_title, ipk, earned_sks,
                       graduation_predicate, yudisium_date, verification_code, is_cleared, created_at
                FROM yudisium_clearances
                WHERE nim = ?
            """, (nim.strip(),))
            row = cursor.fetchone()
            return dict(row) if row else None

    def record_equipment_calibration(
        self,
        asset_id: str,
        equipment_name: str,
        lab_name: str,
        calibration_date: str,
        due_date: str,
        calibration_status: str,
        operating_condition: str,
        technician_name: str,
        notes: str = ""
    ) -> int:
        """
        Records a laboratory equipment calibration audit and operating condition log.
        """
        with self._get_connection() as conn:
            cursor = conn.execute("""
                INSERT INTO lab_equipment_calibrations (
                    asset_id, equipment_name, lab_name, calibration_date, due_date,
                    calibration_status, operating_condition, technician_name, notes
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                asset_id.strip(),
                equipment_name.strip(),
                lab_name.strip(),
                calibration_date.strip(),
                due_date.strip(),
                calibration_status.strip(),
                operating_condition.strip(),
                technician_name.strip(),
                notes.strip()
            ))
            return cursor.lastrowid

    def list_equipment_calibrations(
        self,
        lab_name: Optional[str] = None,
        status: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Lists laboratory equipment calibration records with optional filtering by lab name or calibration status.
        """
        with self._get_connection() as conn:
            query = """
                SELECT id, asset_id, equipment_name, lab_name, calibration_date, due_date,
                       calibration_status, operating_condition, technician_name, notes, created_at
                FROM lab_equipment_calibrations
            """
            params = []
            conditions = []
            if lab_name:
                conditions.append("lab_name = ?")
                params.append(lab_name.strip())
            if status:
                conditions.append("calibration_status = ?")
                params.append(status.strip())

            if conditions:
                query += " WHERE " + " AND ".join(conditions)

            query += " ORDER BY id DESC"
            cursor = conn.execute(query, tuple(params))
            return [dict(row) for row in cursor.fetchall()]

    def record_kkn_project(
        self,
        group_code: str,
        village_name: str,
        district_name: str,
        regency_name: str,
        supervisor_dpl: str,
        student_count: int,
        thematic_focus: str,
        flagship_program: str
    ) -> int:
        with self._get_connection() as conn:
            cursor = conn.execute("""
                INSERT INTO kkn_village_projects (
                    group_code, village_name, district_name, regency_name,
                    supervisor_dpl, student_count, thematic_focus, flagship_program
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                group_code.strip(),
                village_name.strip(),
                district_name.strip(),
                regency_name.strip(),
                supervisor_dpl.strip(),
                int(student_count),
                thematic_focus.strip(),
                flagship_program.strip()
            ))
            return cursor.lastrowid

    def list_kkn_projects(self, regency_name: Optional[str] = None) -> List[Dict[str, Any]]:
        with self._get_connection() as conn:
            query = "SELECT * FROM kkn_village_projects"
            params = []
            if regency_name:
                query += " WHERE regency_name = ?"
                params.append(regency_name.strip())
            query += " ORDER BY id DESC"
            cursor = conn.execute(query, tuple(params))
            return [dict(row) for row in cursor.fetchall()]

    def get_kkn_project_by_id(self, project_id: int) -> Optional[Dict[str, Any]]:
        with self._get_connection() as conn:
            cursor = conn.execute("SELECT * FROM kkn_village_projects WHERE id = ?", (int(project_id),))
            row = cursor.fetchone()
            return dict(row) if row else None

    def record_faculty_bkd(
        self,
        lecturer_name: str,
        nidn: str,
        academic_rank: str,
        semester: str,
        teaching_credits: float,
        research_credits: float,
        service_credits: float,
        supporting_credits: float,
        total_sks: float,
        is_compliant: bool
    ) -> int:
        with self._get_connection() as conn:
            cursor = conn.execute("""
                INSERT INTO faculty_bkd_records (
                    lecturer_name, nidn, academic_rank, semester,
                    teaching_credits, research_credits, service_credits,
                    supporting_credits, total_sks, is_compliant
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                lecturer_name.strip(),
                nidn.strip(),
                academic_rank.strip(),
                semester.strip(),
                float(teaching_credits),
                float(research_credits),
                float(service_credits),
                float(supporting_credits),
                float(total_sks),
                1 if is_compliant else 0
            ))
            return cursor.lastrowid

    def list_faculty_bkd_records(self, semester: Optional[str] = None) -> List[Dict[str, Any]]:
        with self._get_connection() as conn:
            query = "SELECT * FROM faculty_bkd_records"
            params = []
            if semester:
                query += " WHERE semester = ?"
                params.append(semester.strip())
            query += " ORDER BY id DESC"
            cursor = conn.execute(query, tuple(params))
            return [dict(row) for row in cursor.fetchall()]

    def get_faculty_bkd_by_nidn(self, nidn: str) -> List[Dict[str, Any]]:
        with self._get_connection() as conn:
            cursor = conn.execute(
                "SELECT * FROM faculty_bkd_records WHERE nidn = ? ORDER BY semester DESC, id DESC",
                (nidn.strip(),)
            )
            return [dict(row) for row in cursor.fetchall()]

    def record_conference_presentation(
        self,
        paper_title: str,
        authors: str,
        conference_name: str,
        acronym: str,
        core_tier: str,
        publisher: str,
        year: int,
        city: str,
        paper_url: str = ""
    ) -> int:
        with self._get_connection() as conn:
            cursor = conn.execute("""
                INSERT INTO conference_presentations (
                    paper_title, authors, conference_name, acronym,
                    core_tier, publisher, year, city, paper_url
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                paper_title.strip(),
                authors.strip(),
                conference_name.strip(),
                acronym.strip(),
                core_tier.strip().upper(),
                publisher.strip(),
                int(year),
                city.strip(),
                paper_url.strip() if paper_url else None
            ))
            return cursor.lastrowid

    def list_conference_presentations(
        self,
        core_tier: Optional[str] = None,
        year: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        with self._get_connection() as conn:
            query = "SELECT * FROM conference_presentations"
            params = []
            conditions = []
            if core_tier:
                conditions.append("core_tier = ?")
                params.append(core_tier.strip().upper())
            if year:
                conditions.append("year = ?")
                params.append(int(year))

            if conditions:
                query += " WHERE " + " AND ".join(conditions)

            query += " ORDER BY year DESC, id DESC"
            cursor = conn.execute(query, tuple(params))
            return [dict(row) for row in cursor.fetchall()]

    def record_bima_grant(
        self,
        project_title: str,
        lead_researcher: str,
        lead_nidn: str,
        scheme_name: str,
        requested_budget: float,
        approved_budget: float,
        fiscal_year: int,
        proposal_status: str = "submitted",
        contract_number: Optional[str] = None
    ) -> int:
        with self._get_connection() as conn:
            cursor = conn.execute("""
                INSERT INTO bima_grant_proposals (
                    project_title, lead_researcher, lead_nidn, scheme_name,
                    requested_budget, approved_budget, fiscal_year, proposal_status, contract_number
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                project_title.strip(),
                lead_researcher.strip(),
                lead_nidn.strip(),
                scheme_name.strip(),
                float(requested_budget),
                float(approved_budget),
                int(fiscal_year),
                proposal_status.strip(),
                contract_number.strip() if contract_number else None
            ))
            return cursor.lastrowid

    def list_bima_grants(
        self,
        fiscal_year: Optional[int] = None,
        status: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        with self._get_connection() as conn:
            query = "SELECT * FROM bima_grant_proposals"
            params = []
            conditions = []
            if fiscal_year is not None:
                conditions.append("fiscal_year = ?")
                params.append(int(fiscal_year))
            if status:
                conditions.append("proposal_status = ?")
                params.append(status.strip())

            if conditions:
                query += " WHERE " + " AND ".join(conditions)

            query += " ORDER BY fiscal_year DESC, id DESC"
            cursor = conn.execute(query, tuple(params))
            return [dict(row) for row in cursor.fetchall()]

    def get_bima_grant_by_id(self, grant_id: int) -> Optional[Dict[str, Any]]:
        with self._get_connection() as conn:
            cursor = conn.execute(
                "SELECT * FROM bima_grant_proposals WHERE id = ?",
                (int(grant_id),)
            )
            row = cursor.fetchone()
            return dict(row) if row else None

    def record_kp_placement(
        self,
        student_name: str,
        nim: str,
        company_name: str,
        industry_sector: str,
        duration_weeks: int,
        project_title: str,
        company_mentor: Optional[str] = None,
        placement_status: str = "approved"
    ) -> int:
        with self._get_connection() as conn:
            cursor = conn.execute("""
                INSERT INTO kerja_praktik_placements (
                    student_name, nim, company_name, industry_sector,
                    duration_weeks, project_title, company_mentor, placement_status
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                student_name.strip(),
                nim.strip(),
                company_name.strip(),
                industry_sector.strip(),
                int(duration_weeks),
                project_title.strip(),
                company_mentor.strip() if company_mentor else None,
                placement_status.strip()
            ))
            return cursor.lastrowid

    def list_kp_placements(
        self,
        placement_status: Optional[str] = None,
        company_name: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        with self._get_connection() as conn:
            query = "SELECT * FROM kerja_praktik_placements"
            params = []
            conditions = []
            if placement_status:
                conditions.append("placement_status = ?")
                params.append(placement_status.strip())
            if company_name:
                conditions.append("company_name = ?")
                params.append(company_name.strip())

            if conditions:
                query += " WHERE " + " AND ".join(conditions)

            query += " ORDER BY id DESC"
            cursor = conn.execute(query, tuple(params))
            return [dict(row) for row in cursor.fetchall()]

    def get_kp_placement_by_nim(self, nim: str) -> List[Dict[str, Any]]:
        with self._get_connection() as conn:
            cursor = conn.execute(
                "SELECT * FROM kerja_praktik_placements WHERE nim = ? ORDER BY id DESC",
                (nim.strip(),)
            )
            return [dict(row) for row in cursor.fetchall()]

    def record_spectrum_allocation(
        self,
        lab_name: str,
        center_frequency_mhz: float,
        bandwidth_mhz: float,
        transmit_power_dbm: float,
        band_designation: str,
        license_number: Optional[str] = None,
        valid_until: Optional[str] = None,
        is_active: bool = True
    ) -> int:
        with self._get_connection() as conn:
            cursor = conn.execute("""
                INSERT INTO lab_spectrum_allocations (
                    lab_name, center_frequency_mhz, bandwidth_mhz,
                    transmit_power_dbm, band_designation, license_number, valid_until, is_active
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                lab_name.strip(),
                float(center_frequency_mhz),
                float(bandwidth_mhz),
                float(transmit_power_dbm),
                band_designation.strip(),
                license_number.strip() if license_number else None,
                valid_until.strip() if valid_until else None,
                1 if is_active else 0
            ))
            return cursor.lastrowid

    def list_spectrum_allocations(
        self,
        is_active: Optional[bool] = None,
        lab_name: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        with self._get_connection() as conn:
            query = "SELECT * FROM lab_spectrum_allocations"
            params = []
            conditions = []
            if is_active is not None:
                conditions.append("is_active = ?")
                params.append(1 if is_active else 0)
            if lab_name:
                conditions.append("lab_name = ?")
                params.append(lab_name.strip())

            if conditions:
                query += " WHERE " + " AND ".join(conditions)

            query += " ORDER BY id DESC"
            cursor = conn.execute(query, tuple(params))
            return [dict(row) for row in cursor.fetchall()]

    def get_spectrum_allocation_by_id(self, allocation_id: int) -> Optional[Dict[str, Any]]:
        with self._get_connection() as conn:
            cursor = conn.execute(
                "SELECT * FROM lab_spectrum_allocations WHERE id = ?",
                (int(allocation_id),)
            )
            row = cursor.fetchone()
            return dict(row) if row else None

    def record_accreditation(
        self,
        program_name: str,
        agency: str,
        rating: str,
        sk_number: str,
        expiry_date: str,
        issued_date: Optional[str] = None,
        is_active: bool = True
    ) -> int:
        with self._get_connection() as conn:
            cursor = conn.execute("""
                INSERT INTO study_program_accreditations (
                    program_name, agency, rating, sk_number,
                    issued_date, expiry_date, is_active
                ) VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (
                program_name.strip(),
                agency.strip(),
                rating.strip(),
                sk_number.strip(),
                issued_date.strip() if issued_date else None,
                expiry_date.strip(),
                1 if is_active else 0
            ))
            return cursor.lastrowid

    def list_accreditations(
        self,
        agency: Optional[str] = None,
        is_active: Optional[bool] = None
    ) -> List[Dict[str, Any]]:
        with self._get_connection() as conn:
            query = "SELECT * FROM study_program_accreditations"
            params = []
            conditions = []
            if agency:
                conditions.append("agency = ?")
                params.append(agency.strip())
            if is_active is not None:
                conditions.append("is_active = ?")
                params.append(1 if is_active else 0)

            if conditions:
                query += " WHERE " + " AND ".join(conditions)

            query += " ORDER BY id DESC"
            cursor = conn.execute(query, tuple(params))
            return [dict(row) for row in cursor.fetchall()]

    def get_accreditation_by_id(self, accreditation_id: int) -> Optional[Dict[str, Any]]:
        with self._get_connection() as conn:
            cursor = conn.execute(
                "SELECT * FROM study_program_accreditations WHERE id = ?",
                (int(accreditation_id),)
            )
            row = cursor.fetchone()
            return dict(row) if row else None

    def record_scholarship(
        self,
        student_name: str,
        nim: str,
        scholarship_type: str,
        sponsor_name: str,
        amount: float,
        semester: str,
        academic_year: str,
        status: str = "active"
    ) -> int:
        with self._get_connection() as conn:
            cursor = conn.execute("""
                INSERT INTO student_scholarships (
                    student_name, nim, scholarship_type, sponsor_name,
                    amount, semester, academic_year, status
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                student_name.strip(),
                nim.strip(),
                scholarship_type.strip(),
                sponsor_name.strip(),
                float(amount),
                semester.strip(),
                academic_year.strip(),
                status.strip()
            ))
            return cursor.lastrowid

    def list_scholarships(
        self,
        scholarship_type: Optional[str] = None,
        status: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        with self._get_connection() as conn:
            query = "SELECT * FROM student_scholarships"
            params = []
            conditions = []
            if scholarship_type:
                conditions.append("scholarship_type = ?")
                params.append(scholarship_type.strip())
            if status:
                conditions.append("status = ?")
                params.append(status.strip())

            if conditions:
                query += " WHERE " + " AND ".join(conditions)

            query += " ORDER BY id DESC"
            cursor = conn.execute(query, tuple(params))
            return [dict(row) for row in cursor.fetchall()]

    def get_scholarships_by_nim(self, nim: str) -> List[Dict[str, Any]]:
        with self._get_connection() as conn:
            cursor = conn.execute(
                "SELECT * FROM student_scholarships WHERE nim = ? ORDER BY id DESC",
                (nim.strip(),)
            )
            return [dict(row) for row in cursor.fetchall()]

    def record_bnsp_certification(
        self,
        student_name: str,
        nim: str,
        scheme_name: str,
        assessor_name: str,
        cert_number: str,
        issue_date: str,
        valid_until: str,
        is_competent: bool = True
    ) -> int:
        with self._get_connection() as conn:
            cursor = conn.execute("""
                INSERT INTO bnsp_certifications (
                    student_name, nim, scheme_name, assessor_name,
                    cert_number, issue_date, valid_until, is_competent
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                student_name.strip(),
                nim.strip(),
                scheme_name.strip(),
                assessor_name.strip(),
                cert_number.strip(),
                issue_date.strip(),
                valid_until.strip(),
                1 if is_competent else 0
            ))
            return cursor.lastrowid

    def list_bnsp_certifications(
        self,
        scheme_name: Optional[str] = None,
        is_competent: Optional[bool] = None
    ) -> List[Dict[str, Any]]:
        with self._get_connection() as conn:
            query = "SELECT * FROM bnsp_certifications"
            params = []
            conditions = []
            if scheme_name:
                conditions.append("scheme_name = ?")
                params.append(scheme_name.strip())
            if is_competent is not None:
                conditions.append("is_competent = ?")
                params.append(1 if is_competent else 0)

            if conditions:
                query += " WHERE " + " AND ".join(conditions)

            query += " ORDER BY id DESC"
            cursor = conn.execute(query, tuple(params))
            return [dict(row) for row in cursor.fetchall()]

    def get_bnsp_certification_by_nim(self, nim: str) -> List[Dict[str, Any]]:
        with self._get_connection() as conn:
            cursor = conn.execute(
                "SELECT * FROM bnsp_certifications WHERE nim = ? ORDER BY id DESC",
                (nim.strip(),)
            )
            return [dict(row) for row in cursor.fetchall()]

    def record_graduation_honor(self, data: Dict[str, Any]) -> int:
        with self._get_connection() as conn:
            cursor = conn.execute("""
                INSERT INTO student_graduation_honors (
                    student_name, nim, ipk, honor_predicate, thesis_title,
                    study_duration_semesters, graduation_year
                ) VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (
                data["student_name"].strip(),
                data["nim"].strip(),
                float(data["ipk"]),
                data["honor_predicate"].strip(),
                data["thesis_title"].strip(),
                int(data.get("study_duration_semesters", 8)),
                int(data["graduation_year"])
            ))
            return cursor.lastrowid

    def list_graduation_honors(
        self,
        graduation_year: Optional[int] = None,
        predicate_keyword: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        with self._get_connection() as conn:
            query = "SELECT * FROM student_graduation_honors"
            conditions = []
            params = []

            if graduation_year is not None:
                conditions.append("graduation_year = ?")
                params.append(int(graduation_year))

            if predicate_keyword:
                conditions.append("LOWER(honor_predicate) LIKE ?")
                params.append(f"%{predicate_keyword.strip().lower()}%")

            if conditions:
                query += " WHERE " + " AND ".join(conditions)

            query += " ORDER BY id DESC"
            cursor = conn.execute(query, tuple(params))
            return [dict(row) for row in cursor.fetchall()]

    def get_graduation_honor_by_nim(self, nim: str) -> Optional[Dict[str, Any]]:
        with self._get_connection() as conn:
            cursor = conn.execute(
                "SELECT * FROM student_graduation_honors WHERE nim = ? ORDER BY id DESC LIMIT 1",
                (nim.strip(),)
            )
            row = cursor.fetchone()
            return dict(row) if row else None

    def record_tridharma_grant(self, data: Dict[str, Any]) -> int:
        with self._get_connection() as conn:
            cursor = conn.execute("""
                INSERT INTO tridharma_research_grants (
                    lecturer_name, nidn, project_title, grant_amount,
                    fiscal_year, publication_target, status
                ) VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (
                data["lecturer_name"].strip(),
                data["nidn"].strip(),
                data["project_title"].strip(),
                float(data["grant_amount"]),
                int(data["fiscal_year"]),
                data["publication_target"].strip(),
                data.get("status", "active").strip()
            ))
            return cursor.lastrowid

    def list_tridharma_grants(
        self,
        fiscal_year: Optional[int] = None,
        status: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        with self._get_connection() as conn:
            query = "SELECT * FROM tridharma_research_grants"
            conditions = []
            params = []

            if fiscal_year is not None:
                conditions.append("fiscal_year = ?")
                params.append(int(fiscal_year))

            if status:
                conditions.append("status = ?")
                params.append(status.strip())

            if conditions:
                query += " WHERE " + " AND ".join(conditions)

            query += " ORDER BY id DESC"
            cursor = conn.execute(query, tuple(params))
            return [dict(row) for row in cursor.fetchall()]

    def get_tridharma_grants_by_nidn(self, nidn: str) -> List[Dict[str, Any]]:
        with self._get_connection() as conn:
            cursor = conn.execute(
                "SELECT * FROM tridharma_research_grants WHERE nidn = ? ORDER BY id DESC",
                (nidn.strip(),)
            )
            return [dict(row) for row in cursor.fetchall()]

    def record_sensor_telemetry(self, data: Dict[str, Any]) -> int:
        with self._get_connection() as conn:
            cursor = conn.execute("""
                INSERT INTO iot_sensor_telemetry_feeds (
                    node_id, sensor_type, reading_value, unit, battery_level
                ) VALUES (?, ?, ?, ?, ?)
            """, (
                data["node_id"].strip(),
                data["sensor_type"].strip(),
                float(data["reading_value"]),
                data["unit"].strip(),
                float(data.get("battery_level", 100.0))
            ))
            return cursor.lastrowid

    def list_latest_sensor_telemetry(self, limit: int = 50) -> List[Dict[str, Any]]:
        with self._get_connection() as conn:
            cursor = conn.execute(
                "SELECT * FROM iot_sensor_telemetry_feeds ORDER BY id DESC LIMIT ?",
                (max(1, int(limit)),)
            )
            return [dict(row) for row in cursor.fetchall()]

    def get_sensor_telemetry_by_node(self, node_id: str, limit: int = 20) -> List[Dict[str, Any]]:
        with self._get_connection() as conn:
            cursor = conn.execute(
                "SELECT * FROM iot_sensor_telemetry_feeds WHERE node_id = ? ORDER BY id DESC LIMIT ?",
                (node_id.strip(), max(1, int(limit)))
            )
            return [dict(row) for row in cursor.fetchall()]

    def record_fast_track_student(
        self,
        student_name: str,
        nim: str,
        ipk: float,
        completed_sks: int,
        toefl_score: int,
        masters_specialization: str,
        status: str = "Eligible"
    ) -> int:
        """
        Records a student eligible for the fast-track accelerated master's program.
        """
        with self._get_connection() as conn:
            cursor = conn.execute("""
                INSERT INTO fast_track_students (
                    student_name, nim, ipk, completed_sks, toefl_score, masters_specialization, status
                ) VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (
                student_name.strip(),
                nim.strip(),
                float(ipk),
                int(completed_sks),
                int(toefl_score),
                masters_specialization.strip(),
                status.strip()
            ))
            return cursor.lastrowid

    def list_fast_track_students(self, status: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Lists fast-track master's student candidates with optional status filtering.
        """
        with self._get_connection() as conn:
            query = "SELECT * FROM fast_track_students"
            params = []
            if status:
                query += " WHERE status = ?"
                params.append(status.strip())
            query += " ORDER BY ipk DESC, id DESC"
            cursor = conn.execute(query, params)
            return [dict(row) for row in cursor.fetchall()]

    def get_fast_track_student_by_nim(self, nim: str) -> Optional[Dict[str, Any]]:
        """
        Retrieves a fast-track student profile by student identification number (NIM).
        """
        with self._get_connection() as conn:
            cursor = conn.execute("SELECT * FROM fast_track_students WHERE nim = ?", (nim.strip(),))
            row = cursor.fetchone()
            return dict(row) if row else None

    def record_lab_calibration_compliance(
        self,
        equipment_name: str,
        serial_number: str,
        lab_room: str,
        last_calibration_date: str,
        next_due_date: str,
        calibration_status: str,
        cert_number: str
    ) -> int:
        """
        Records laboratory telecommunications equipment calibration compliance under ISO/IEC 17025.
        """
        with self._get_connection() as conn:
            cursor = conn.execute("""
                INSERT INTO lab_calibration_compliance (
                    equipment_name, serial_number, lab_room, last_calibration_date,
                    next_due_date, calibration_status, cert_number
                ) VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (
                equipment_name.strip(),
                serial_number.strip(),
                lab_room.strip(),
                last_calibration_date.strip(),
                next_due_date.strip(),
                calibration_status.strip(),
                cert_number.strip()
            ))
            return cursor.lastrowid

    def list_lab_calibration_compliance(self, status: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Lists equipment calibration compliance records with optional status filtering.
        """
        with self._get_connection() as conn:
            query = "SELECT * FROM lab_calibration_compliance"
            params = []
            if status:
                query += " WHERE calibration_status = ?"
                params.append(status.strip())
            query += " ORDER BY next_due_date ASC, id DESC"
            cursor = conn.execute(query, params)
            return [dict(row) for row in cursor.fetchall()]

    def get_lab_calibration_by_serial(self, serial_number: str) -> Optional[Dict[str, Any]]:
        """
        Retrieves an equipment calibration record by serial number.
        """
        with self._get_connection() as conn:
            cursor = conn.execute("SELECT * FROM lab_calibration_compliance WHERE serial_number = ?", (serial_number.strip(),))
            row = cursor.fetchone()
            return dict(row) if row else None

    def record_lecturer_hki(
        self,
        work_title: str,
        creators: List[str],
        creation_type: str,
        application_number: str,
        registration_number: str,
        registration_date: str,
        rubric_points: float = 0.0
    ) -> int:
        """
        Records a DJKI Kemenkumham Intellectual Property / HKI copyright registration for BKD and SINTA tracking.
        """
        clean_creators = [c.strip() for c in creators if c.strip()]
        with self._get_connection() as conn:
            cursor = conn.execute("""
                INSERT INTO lecturer_hki_records (
                    work_title, creators_json, creation_type, application_number,
                    registration_number, registration_date, rubric_points
                ) VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (
                work_title.strip(),
                json.dumps(clean_creators, ensure_ascii=False),
                creation_type.strip(),
                application_number.strip(),
                registration_number.strip(),
                registration_date.strip(),
                float(rubric_points)
            ))
            return cursor.lastrowid

    def list_lecturer_hki_records(self, creation_type: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Lists lecturer HKI copyright registrations with decoded creators list and optional creation type filtering.
        """
        with self._get_connection() as conn:
            query = "SELECT * FROM lecturer_hki_records"
            params = []
            if creation_type:
                query += " WHERE creation_type = ?"
                params.append(creation_type.strip())
            query += " ORDER BY id DESC"
            cursor = conn.execute(query, params)
            results = []
            for row in cursor.fetchall():
                data = dict(row)
                try:
                    data["creators"] = json.loads(data.get("creators_json") or "[]")
                except Exception:
                    data["creators"] = []
                results.append(data)
            return results

    def get_lecturer_hki_by_reg_number(self, registration_number: str) -> Optional[Dict[str, Any]]:
        """
        Retrieves an HKI copyright record by official registration number.
        """
        with self._get_connection() as conn:
            cursor = conn.execute(
                "SELECT * FROM lecturer_hki_records WHERE registration_number = ?",
                (registration_number.strip(),)
            )
            row = cursor.fetchone()
            if not row:
                return None
            data = dict(row)
            try:
                data["creators"] = json.loads(data.get("creators_json") or "[]")
            except Exception:
                data["creators"] = []
            return data

    def record_msib_internship(
        self,
        student_name: str,
        nim: str,
        industry_partner: str,
        internship_role: str,
        mentor_grade: float,
        letter_grade: str,
        converted_sks: int,
        duration_months: int = 5,
        status: str = "Approved"
    ) -> int:
        """
        Records a certified MSIB Kampus Merdeka internship and credit conversion record.
        """
        with self._get_connection() as conn:
            cursor = conn.execute("""
                INSERT INTO student_msib_internships (
                    student_name, nim, industry_partner, internship_role, mentor_grade,
                    letter_grade, converted_sks, duration_months, status
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                student_name.strip(),
                nim.strip(),
                industry_partner.strip(),
                internship_role.strip(),
                float(mentor_grade),
                letter_grade.strip(),
                int(converted_sks),
                int(duration_months),
                status.strip()
            ))
            return cursor.lastrowid

    def list_msib_internships(self, partner: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Lists MSIB internship student records with optional industry partner filtering.
        """
        with self._get_connection() as conn:
            query = "SELECT * FROM student_msib_internships"
            params = []
            if partner:
                query += " WHERE industry_partner LIKE ?"
                params.append(f"%{partner.strip()}%")
            query += " ORDER BY id DESC"
            cursor = conn.execute(query, params)
            return [dict(row) for row in cursor.fetchall()]

    def get_msib_by_nim(self, nim: str) -> Optional[Dict[str, Any]]:
        """
        Retrieves a student MSIB internship record by student ID (NIM).
        """
        with self._get_connection() as conn:
            cursor = conn.execute("SELECT * FROM student_msib_internships WHERE nim = ?", (nim.strip(),))
            row = cursor.fetchone()
            return dict(row) if row else None

    def record_pkm_grant(
        self,
        project_title: str,
        team_leader: str,
        nidn: str,
        partner_name: str,
        target_location: str,
        proposed_budget: float,
        approved_budget: float,
        fiscal_year: int,
        focus_area: str,
        status: str = "Approved"
    ) -> int:
        """
        Records a lecturer Tridharma Community Service (PKM) grant award and budget allocation.
        """
        with self._get_connection() as conn:
            cursor = conn.execute("""
                INSERT INTO lecturer_pkm_grants (
                    project_title, team_leader, nidn, partner_name, target_location,
                    proposed_budget, approved_budget, fiscal_year, focus_area, status
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                project_title.strip(),
                team_leader.strip(),
                nidn.strip(),
                partner_name.strip(),
                target_location.strip(),
                float(proposed_budget),
                float(approved_budget),
                int(fiscal_year),
                focus_area.strip(),
                status.strip()
            ))
            return cursor.lastrowid

    def list_pkm_grants(
        self,
        fiscal_year: Optional[int] = None,
        status: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Lists lecturer PKM grants with optional fiscal year and status filters.
        """
        with self._get_connection() as conn:
            query = "SELECT * FROM lecturer_pkm_grants"
            params = []
            conditions = []
            if fiscal_year:
                conditions.append("fiscal_year = ?")
                params.append(int(fiscal_year))
            if status:
                conditions.append("status = ?")
                params.append(status.strip())

            if conditions:
                query += " WHERE " + " AND ".join(conditions)

            query += " ORDER BY fiscal_year DESC, id DESC"
            cursor = conn.execute(query, params)
            return [dict(row) for row in cursor.fetchall()]

    def get_pkm_grant_by_id(self, grant_id: int) -> Optional[Dict[str, Any]]:
        """
        Retrieves a PKM grant record by primary key ID.
        """
        with self._get_connection() as conn:
            cursor = conn.execute("SELECT * FROM lecturer_pkm_grants WHERE id = ?", (int(grant_id),))
            row = cursor.fetchone()
            return dict(row) if row else None

    def record_fso_link_budget(
        self,
        link_name: str,
        link_distance_km: float,
        tx_power_dbm: float,
        rx_power_dbm: float,
        geometric_loss_db: float,
        atmospheric_loss_db: float,
        link_margin_db: float,
        status: str
    ) -> int:
        """
        Records an FSO laser telecommunications link budget computation audit.
        """
        with self._get_connection() as conn:
            cursor = conn.execute("""
                INSERT INTO fso_link_budget_records (
                    link_name, link_distance_km, tx_power_dbm, rx_power_dbm,
                    geometric_loss_db, atmospheric_loss_db, link_margin_db, status
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                link_name.strip(),
                float(link_distance_km),
                float(tx_power_dbm),
                float(rx_power_dbm),
                float(geometric_loss_db),
                float(atmospheric_loss_db),
                float(link_margin_db),
                status.strip()
            ))
            return cursor.lastrowid

    def list_fso_link_budgets(self, status: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Lists FSO optical link budget calculation records.
        """
        with self._get_connection() as conn:
            query = "SELECT * FROM fso_link_budget_records"
            params = []
            if status:
                query += " WHERE status = ?"
                params.append(status.strip())
            query += " ORDER BY id DESC"
            cursor = conn.execute(query, params)
            return [dict(row) for row in cursor.fetchall()]

    def get_fso_link_budget_by_id(self, record_id: int) -> Optional[Dict[str, Any]]:
        """
        Retrieves an FSO link budget computation record by primary key ID.
        """
        with self._get_connection() as conn:
            cursor = conn.execute("SELECT * FROM fso_link_budget_records WHERE id = ?", (int(record_id),))
            row = cursor.fetchone()
            return dict(row) if row else None

    def record_satellite_link_budget(
        self,
        satellite_name: str,
        downlink_freq_ghz: float,
        slant_range_km: float,
        tx_eirp_dbw: float,
        rx_g_over_t_db_k: float,
        bandwidth_mhz: float,
        cnr_db: float,
        link_margin_db: float,
        is_viable: bool,
        status: str
    ) -> int:
        """
        Records a satellite downlink link budget and ground station G/T calculation audit.
        """
        with self._get_connection() as conn:
            cursor = conn.execute("""
                INSERT INTO satellite_link_budgets (
                    satellite_name, downlink_freq_ghz, slant_range_km, tx_eirp_dbw,
                    rx_g_over_t_db_k, bandwidth_mhz, cnr_db, link_margin_db,
                    is_viable, status
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                satellite_name.strip(),
                float(downlink_freq_ghz),
                float(slant_range_km),
                float(tx_eirp_dbw),
                float(rx_g_over_t_db_k),
                float(bandwidth_mhz),
                float(cnr_db),
                float(link_margin_db),
                1 if is_viable else 0,
                status.strip()
            ))
            return cursor.lastrowid

    def list_satellite_link_budgets(self, is_viable: Optional[bool] = None) -> List[Dict[str, Any]]:
        """
        Lists satellite link budget computation audit records with optional feasibility filter.
        """
        with self._get_connection() as conn:
            query = "SELECT * FROM satellite_link_budgets"
            params = []
            if is_viable is not None:
                query += " WHERE is_viable = ?"
                params.append(1 if is_viable else 0)
            query += " ORDER BY id DESC"
            cursor = conn.execute(query, params)
            return [dict(row) for row in cursor.fetchall()]

    def get_satellite_link_budget_by_id(self, budget_id: int) -> Optional[Dict[str, Any]]:
        """
        Retrieves a satellite link budget computation record by primary key ID.
        """
        with self._get_connection() as conn:
            cursor = conn.execute("SELECT * FROM satellite_link_budgets WHERE id = ?", (int(budget_id),))
            row = cursor.fetchone()
            return dict(row) if row else None

    def record_kampus_mengajar_student(
        self,
        student_name: str,
        nim: str,
        target_school: str,
        school_level: str,
        teaching_hours: int,
        composite_score: float,
        letter_grade: str,
        converted_sks: int,
        status: str
    ) -> int:
        """
        Records an MBKM Kampus Mengajar teaching assistantship student evaluation.
        """
        with self._get_connection() as conn:
            cursor = conn.execute("""
                INSERT INTO student_kampus_mengajar (
                    student_name, nim, target_school, school_level, teaching_hours,
                    composite_score, letter_grade, converted_sks, status
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                student_name.strip(),
                nim.strip(),
                target_school.strip(),
                school_level.strip(),
                int(teaching_hours),
                float(composite_score),
                letter_grade.strip(),
                int(converted_sks),
                status.strip()
            ))
            return cursor.lastrowid

    def list_kampus_mengajar_students(self, status: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Lists student Kampus Mengajar records with optional status filter.
        """
        with self._get_connection() as conn:
            query = "SELECT * FROM student_kampus_mengajar"
            params = []
            if status:
                query += " WHERE status LIKE ?"
                params.append(f"%{status.strip()}%")
            query += " ORDER BY id DESC"
            cursor = conn.execute(query, params)
            return [dict(row) for row in cursor.fetchall()]

    def get_kampus_mengajar_by_nim(self, nim: str) -> Optional[Dict[str, Any]]:
        """
        Retrieves a student Kampus Mengajar record by student NIM.
        """
        with self._get_connection() as conn:
            cursor = conn.execute("SELECT * FROM student_kampus_mengajar WHERE nim = ?", (nim.strip(),))
            row = cursor.fetchone()
            return dict(row) if row else None

    def record_rf_intermod_distortion(
        self,
        component_name: str,
        input_power_dbm: float,
        gain_db: float,
        iip3_dbm: float,
        fundamental_pout_dbm: float,
        imd3_suppression_dbc: float,
        linearity_status: str,
        is_linear: bool
    ) -> int:
        """
        Records an RF front-end intermodulation distortion (IMD3) calculation audit.
        """
        with self._get_connection() as conn:
            cursor = conn.execute("""
                INSERT INTO rf_intermod_records (
                    component_name, input_power_dbm, gain_db, iip3_dbm,
                    fundamental_pout_dbm, imd3_suppression_dbc, linearity_status, is_linear
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                component_name.strip(),
                float(input_power_dbm),
                float(gain_db),
                float(iip3_dbm),
                float(fundamental_pout_dbm),
                float(imd3_suppression_dbc),
                linearity_status.strip(),
                1 if is_linear else 0
            ))
            return cursor.lastrowid

    def list_rf_intermod_records(self, is_linear: Optional[bool] = None) -> List[Dict[str, Any]]:
        """
        Lists RF intermodulation distortion audit records with optional linearity filter.
        """
        with self._get_connection() as conn:
            query = "SELECT * FROM rf_intermod_records"
            params = []
            if is_linear is not None:
                query += " WHERE is_linear = ?"
                params.append(1 if is_linear else 0)
            query += " ORDER BY id DESC"
            cursor = conn.execute(query, params)
            return [dict(row) for row in cursor.fetchall()]

    def get_rf_intermod_by_id(self, record_id: int) -> Optional[Dict[str, Any]]:
        """
        Retrieves an RF intermodulation distortion calculation record by primary key ID.
        """
        with self._get_connection() as conn:
            cursor = conn.execute("SELECT * FROM rf_intermod_records WHERE id = ?", (int(record_id),))
            row = cursor.fetchone()
            return dict(row) if row else None

    def record_radar_detection(self, data: Dict[str, Any]) -> int:
        """
        Stores a calculated radar range equation and target cross section record.
        """
        with self._get_connection() as conn:
            cursor = conn.execute("""
                INSERT INTO radar_detection_records (
                    radar_name, peak_power_kw, antenna_gain_dbi, rcs_m2,
                    freq_ghz, min_detectable_signal_dbm, max_range_km, round_trip_delay_us
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                data.get("radar_name", "Primary Surveillance Radar"),
                float(data.get("peak_power_kw", 0.0)),
                float(data.get("antenna_gain_dbi", 0.0)),
                float(data.get("rcs_m2", 1.0)),
                float(data.get("freq_ghz", 0.0)),
                float(data.get("min_detectable_signal_dbm", -100.0)),
                float(data.get("max_range_km", 0.0)),
                float(data.get("round_trip_delay_us", 0.0))
            ))
            return cursor.lastrowid

    def list_radar_detections(self, limit: int = 50) -> List[Dict[str, Any]]:
        """
        Lists stored radar detection calculation records ordered by most recent.
        """
        with self._get_connection() as conn:
            cursor = conn.execute(
                "SELECT * FROM radar_detection_records ORDER BY id DESC LIMIT ?",
                (max(1, int(limit)),)
            )
            return [dict(row) for row in cursor.fetchall()]

    def get_radar_detection_by_id(self, record_id: int) -> Optional[Dict[str, Any]]:
        """
        Retrieves a radar detection record by ID.
        """
        with self._get_connection() as conn:
            cursor = conn.execute("SELECT * FROM radar_detection_records WHERE id = ?", (int(record_id),))
            row = cursor.fetchone()
            return dict(row) if row else None

    def record_wmk_startup(self, data: Dict[str, Any]) -> int:
        """
        Inserts or replaces a student Wirausaha Merdeka (WMK) startup record.
        """
        with self._get_connection() as conn:
            cursor = conn.execute("""
                INSERT INTO student_wirausaha_merdeka (
                    student_name, nim, startup_name, business_sector,
                    mentor_score, pitch_score, composite_score,
                    converted_sks, letter_grade, status
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(nim) DO UPDATE SET
                    student_name = excluded.student_name,
                    startup_name = excluded.startup_name,
                    business_sector = excluded.business_sector,
                    mentor_score = excluded.mentor_score,
                    pitch_score = excluded.pitch_score,
                    composite_score = excluded.composite_score,
                    converted_sks = excluded.converted_sks,
                    letter_grade = excluded.letter_grade,
                    status = excluded.status
            """, (
                data.get("student_name", "").strip(),
                data.get("nim", "").strip(),
                data.get("startup_name", "").strip(),
                data.get("business_sector", "").strip(),
                float(data.get("mentor_score", 0.0)),
                float(data.get("pitch_score", 0.0)),
                float(data.get("composite_score", 0.0)),
                int(data.get("converted_sks", 0)),
                data.get("letter_grade", "C").strip(),
                data.get("status", "").strip()
            ))
            return cursor.lastrowid

    def list_wmk_startups(self, limit: int = 50) -> List[Dict[str, Any]]:
        """
        Lists stored student Wirausaha Merdeka startup records ordered by id descending.
        """
        with self._get_connection() as conn:
            cursor = conn.execute(
                "SELECT * FROM student_wirausaha_merdeka ORDER BY id DESC LIMIT ?",
                (max(1, int(limit)),)
            )
            return [dict(row) for row in cursor.fetchall()]

    def get_wmk_by_nim(self, nim: str) -> Optional[Dict[str, Any]]:
        """
        Retrieves a student Wirausaha Merdeka startup record by NIM.
        """
        with self._get_connection() as conn:
            cursor = conn.execute(
                "SELECT * FROM student_wirausaha_merdeka WHERE nim = ?",
                (nim.strip(),)
            )
            row = cursor.fetchone()
            return dict(row) if row else None

    def record_edfa_amplifier(self, data: Dict[str, Any]) -> int:
        """
        Stores an optical EDFA amplifier gain and noise figure calculation record.
        """
        with self._get_connection() as conn:
            cursor = conn.execute("""
                INSERT INTO edfa_amplifier_records (
                    device_name, input_power_dbm, pump_power_mw, small_signal_gain_db,
                    actual_gain_db, output_power_dbm, noise_figure_db, operating_regime
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                data.get("device_name", "EDFA Pre-Amplifier C-Band"),
                float(data.get("input_power_dbm", -20.0)),
                float(data.get("pump_power_mw", 100.0)),
                float(data.get("small_signal_gain_db", 25.0)),
                float(data.get("actual_gain_db", 20.0)),
                float(data.get("output_power_dbm", 0.0)),
                float(data.get("noise_figure_db", 4.0)),
                data.get("operating_regime", "Small-Signal Linear")
            ))
            return cursor.lastrowid

    def list_edfa_amplifiers(self, limit: int = 50) -> List[Dict[str, Any]]:
        """
        Lists stored optical EDFA amplifier records ordered by most recent.
        """
        with self._get_connection() as conn:
            cursor = conn.execute(
                "SELECT * FROM edfa_amplifier_records ORDER BY id DESC LIMIT ?",
                (max(1, int(limit)),)
            )
            return [dict(row) for row in cursor.fetchall()]

    def get_edfa_by_id(self, record_id: int) -> Optional[Dict[str, Any]]:
        """
        Retrieves an optical EDFA amplifier calculation record by ID.
        """
        with self._get_connection() as conn:
            cursor = conn.execute("SELECT * FROM edfa_amplifier_records WHERE id = ?", (int(record_id),))
            row = cursor.fetchone()
            return dict(row) if row else None

    def record_otdr_measurement(self, data: Dict[str, Any]) -> int:
        """
        Stores an OTDR fiber reflectometry trace and intrinsic attenuation audit record.
        """
        with self._get_connection() as conn:
            cursor = conn.execute("""
                INSERT INTO otdr_fiber_records (
                    link_name, fiber_length_km, wavelength_nm, total_loss_db,
                    event_loss_db, attenuation_db_km, quality_status, is_compliant
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                data.get("link_name", "Ruas Serat Optik").strip(),
                float(data.get("fiber_length_km", 0.0)),
                int(data.get("wavelength_nm", 1550)),
                float(data.get("total_loss_db", 0.0)),
                float(data.get("event_loss_db", 0.0)),
                float(data.get("attenuation_db_km", 0.0)),
                data.get("quality_status", "Optimal").strip(),
                1 if data.get("is_compliant", True) else 0
            ))
            return cursor.lastrowid

    def list_otdr_measurements(self, limit: int = 50) -> List[Dict[str, Any]]:
        """
        Lists stored OTDR optical fiber records ordered by most recent.
        """
        with self._get_connection() as conn:
            cursor = conn.execute(
                "SELECT * FROM otdr_fiber_records ORDER BY id DESC LIMIT ?",
                (max(1, int(limit)),)
            )
            return [dict(row) for row in cursor.fetchall()]

    def get_otdr_by_id(self, record_id: int) -> Optional[Dict[str, Any]]:
        """
        Retrieves an OTDR optical fiber trace record by ID.
        """
        with self._get_connection() as conn:
            cursor = conn.execute("SELECT * FROM otdr_fiber_records WHERE id = ?", (int(record_id),))
            row = cursor.fetchone()
            return dict(row) if row else None

    def record_mimo_capacity(self, data: Dict[str, Any]) -> int:
        """
        Stores a MIMO antenna channel capacity and spatial multiplexing calculation record.
        """
        with self._get_connection() as conn:
            cursor = conn.execute("""
                INSERT INTO mimo_capacity_records (
                    channel_name, bandwidth_mhz, snr_db, num_tx, num_rx,
                    spectral_eff_bps_hz, capacity_gbps, gain_factor, status
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                data.get("channel_name", "5G NR MIMO Channel").strip(),
                float(data.get("bandwidth_mhz", 100.0)),
                float(data.get("snr_db", 20.0)),
                int(data.get("num_tx", 4)),
                int(data.get("num_rx", 4)),
                float(data.get("spectral_eff_bps_hz", 0.0)),
                float(data.get("capacity_gbps", 0.0)),
                float(data.get("gain_factor", 1.0)),
                data.get("status", "High-Rank MIMO").strip()
            ))
            return cursor.lastrowid

    def list_mimo_capacities(self, limit: int = 50) -> List[Dict[str, Any]]:
        """
        Lists stored MIMO capacity records ordered by most recent.
        """
        with self._get_connection() as conn:
            cursor = conn.execute(
                "SELECT * FROM mimo_capacity_records ORDER BY id DESC LIMIT ?",
                (max(1, int(limit)),)
            )
            return [dict(row) for row in cursor.fetchall()]

    def get_mimo_by_id(self, record_id: int) -> Optional[Dict[str, Any]]:
        """
        Retrieves a MIMO capacity record by ID.
        """
        with self._get_connection() as conn:
            cursor = conn.execute("SELECT * FROM mimo_capacity_records WHERE id = ?", (int(record_id),))
            row = cursor.fetchone()
            return dict(row) if row else None

    def record_iisma_student(self, data: Dict[str, Any]) -> int:
        """
        Inserts or updates an IISMA international student exchange awardee record.
        """
        with self._get_connection() as conn:
            cursor = conn.execute("""
                INSERT INTO student_iisma_exchange (
                    student_name, nim, host_university, country,
                    gpa_host, credits_taken, converted_sks, letter_grade, status
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(nim) DO UPDATE SET
                    student_name = excluded.student_name,
                    host_university = excluded.host_university,
                    country = excluded.country,
                    gpa_host = excluded.gpa_host,
                    credits_taken = excluded.credits_taken,
                    converted_sks = excluded.converted_sks,
                    letter_grade = excluded.letter_grade,
                    status = excluded.status
            """, (
                data.get("student_name", "").strip(),
                data.get("nim", "").strip(),
                data.get("host_university", "").strip(),
                data.get("country", "").strip(),
                float(data.get("gpa_host", 0.0)),
                int(data.get("credits_taken", 0)),
                int(data.get("converted_sks", 0)),
                data.get("letter_grade", "C").strip(),
                data.get("status", "").strip()
            ))
            return cursor.lastrowid

    def list_iisma_students(self, limit: int = 50) -> List[Dict[str, Any]]:
        """
        Lists stored IISMA exchange student records ordered by id descending.
        """
        with self._get_connection() as conn:
            cursor = conn.execute(
                "SELECT * FROM student_iisma_exchange ORDER BY id DESC LIMIT ?",
                (max(1, int(limit)),)
            )
            return [dict(row) for row in cursor.fetchall()]

    def get_iisma_by_nim(self, nim: str) -> Optional[Dict[str, Any]]:
        """
        Retrieves an IISMA exchange student record by NIM.
        """
        with self._get_connection() as conn:
            cursor = conn.execute(
                "SELECT * FROM student_iisma_exchange WHERE nim = ?",
                (nim.strip(),)
            )
            row = cursor.fetchone()
            return dict(row) if row else None

    def record_fspl_link_budget(self, data: Dict[str, Any]) -> int:
        """
        Stores an RF FSPL and wireless link budget audit record into the database.
        """
        with self._get_connection() as conn:
            cursor = conn.execute("""
                INSERT INTO fspl_link_budget_records (
                    link_name, freq_mhz, distance_km, fspl_db, rx_power_dbm, fade_margin_db, is_viable
                ) VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (
                data.get("link_name", "Wireless Link").strip(),
                float(data.get("freq_mhz", 2400.0)),
                float(data.get("distance_km", 1.0)),
                float(data.get("fspl_db", 0.0)),
                float(data.get("rx_power_dbm", -70.0)),
                float(data.get("fade_margin_db", 15.0)),
                1 if data.get("is_viable", True) else 0
            ))
            return cursor.lastrowid

    def list_fspl_link_budgets(self, limit: int = 50) -> List[Dict[str, Any]]:
        """
        Lists stored RF link budget audit records ordered by id descending.
        """
        with self._get_connection() as conn:
            cursor = conn.execute(
                "SELECT * FROM fspl_link_budget_records ORDER BY id DESC LIMIT ?",
                (max(1, int(limit)),)
            )
            return [dict(row) for row in cursor.fetchall()]

    def get_fspl_link_budget_by_id(self, record_id: int) -> Optional[Dict[str, Any]]:
        """
        Retrieves an RF link budget audit record by primary key ID.
        """
        with self._get_connection() as conn:
            cursor = conn.execute(
                "SELECT * FROM fspl_link_budget_records WHERE id = ?",
                (int(record_id),)
            )
            row = cursor.fetchone()
            return dict(row) if row else None

    def record_optical_dispersion(self, data: Dict[str, Any]) -> int:
        """
        Stores an optical fiber dispersion and pulse broadening record into the database.
        """
        with self._get_connection() as conn:
            cursor = conn.execute("""
                INSERT INTO optical_dispersion_records (
                    fiber_name, length_km, dispersion_param, pulse_broadening_ps, max_bit_rate_gbps, severity, requires_compensation
                ) VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (
                data.get("fiber_name", "Fiber Link").strip(),
                float(data.get("length_km", 10.0)),
                float(data.get("dispersion_param", 17.0)),
                float(data.get("pulse_broadening_ps", 0.0)),
                float(data.get("max_bit_rate_gbps", 10.0)),
                data.get("severity", "Rendah").strip(),
                1 if data.get("requires_compensation", False) else 0
            ))
            return cursor.lastrowid

    def list_optical_dispersions(self, limit: int = 50) -> List[Dict[str, Any]]:
        """
        Lists stored optical fiber dispersion records ordered by id descending.
        """
        with self._get_connection() as conn:
            cursor = conn.execute(
                "SELECT * FROM optical_dispersion_records ORDER BY id DESC LIMIT ?",
                (max(1, int(limit)),)
            )
            return [dict(row) for row in cursor.fetchall()]

    def get_optical_dispersion_by_id(self, record_id: int) -> Optional[Dict[str, Any]]:
        """
        Retrieves an optical fiber dispersion record by primary key ID.
        """
        with self._get_connection() as conn:
            cursor = conn.execute(
                "SELECT * FROM optical_dispersion_records WHERE id = ?",
                (int(record_id),)
            )
            row = cursor.fetchone()
            return dict(row) if row else None

    def record_proyek_kemanusiaan(self, data: Dict[str, Any]) -> int:
        """
        Stores an MBKM Proyek Kemanusiaan student completion record into the database.
        """
        with self._get_connection() as conn:
            cursor = conn.execute("""
                INSERT INTO student_proyek_kemanusiaan (
                    student_name, nim, partner_org, location, field_hours, composite_score, converted_sks, letter_grade, status
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(nim) DO UPDATE SET
                    partner_org = excluded.partner_org,
                    location = excluded.location,
                    field_hours = excluded.field_hours,
                    composite_score = excluded.composite_score,
                    converted_sks = excluded.converted_sks,
                    letter_grade = excluded.letter_grade,
                    status = excluded.status;
            """, (
                data.get("student_name", "Mahasiswa").strip(),
                data.get("nim", "1201200000").strip(),
                data.get("partner_org", "BPBD").strip(),
                data.get("location", "Banyumas").strip(),
                int(data.get("field_hours", 400)),
                float(data.get("composite_score", 0.0)),
                int(data.get("converted_sks", 0)),
                data.get("letter_grade", "C").strip(),
                data.get("status", "").strip()
            ))
            return cursor.lastrowid

    def list_proyek_kemanusiaan(self, limit: int = 50) -> List[Dict[str, Any]]:
        """
        Lists stored Proyek Kemanusiaan student records ordered by id descending.
        """
        with self._get_connection() as conn:
            cursor = conn.execute(
                "SELECT * FROM student_proyek_kemanusiaan ORDER BY id DESC LIMIT ?",
                (max(1, int(limit)),)
            )
            return [dict(row) for row in cursor.fetchall()]

    def get_proyek_kemanusiaan_by_nim(self, nim: str) -> Optional[Dict[str, Any]]:
        """
        Retrieves a Proyek Kemanusiaan student record by NIM.
        """
        with self._get_connection() as conn:
            cursor = conn.execute(
                "SELECT * FROM student_proyek_kemanusiaan WHERE nim = ?",
                (nim.strip(),)
            )
            row = cursor.fetchone()
            return dict(row) if row else None

    def record_optical_pmd(self, data: Dict[str, Any]) -> int:
        """
        Stores an optical fiber PMD (Polarization Mode Dispersion) audit telemetry record.
        """
        with self._get_connection() as conn:
            cursor = conn.execute("""
                INSERT INTO optical_pmd_records (
                    fiber_name, length_km, pmd_coeff, mean_dgd_ps, max_bit_rate_gbps, outage_risk, is_safe
                ) VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (
                data.get("fiber_name", "Ruas Serat Optik").strip(),
                float(data.get("length_km", 0.0)),
                float(data.get("pmd_coeff", 0.0)),
                float(data.get("mean_dgd_ps", 0.0)),
                float(data.get("max_bit_rate_gbps", 0.0)),
                data.get("outage_risk", "Sangat Rendah").strip(),
                1 if data.get("is_safe", True) else 0
            ))
            return cursor.lastrowid

    def list_optical_pmd(self, limit: int = 50) -> List[Dict[str, Any]]:
        """
        Lists stored optical fiber PMD audit records ordered by id descending.
        """
        with self._get_connection() as conn:
            cursor = conn.execute(
                "SELECT * FROM optical_pmd_records ORDER BY id DESC LIMIT ?",
                (max(1, int(limit)),)
            )
            return [dict(row) for row in cursor.fetchall()]

    def get_optical_pmd_by_id(self, record_id: int) -> Optional[Dict[str, Any]]:
        """
        Retrieves an optical fiber PMD audit record by primary key ID.
        """
        with self._get_connection() as conn:
            cursor = conn.execute(
                "SELECT * FROM optical_pmd_records WHERE id = ?",
                (int(record_id),)
            )
            row = cursor.fetchone()
            return dict(row) if row else None

    def record_cost231_propagation(self, data: Dict[str, Any]) -> int:
        """
        Stores a cellular radio COST 231 Hata propagation loss telemetry record.
        """
        with self._get_connection() as conn:
            cursor = conn.execute("""
                INSERT INTO cost231_propagation_records (
                    area_name, freq_mhz, distance_km, base_station_height_m, mobile_height_m,
                    path_loss_db, coverage_quality, is_metro
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                data.get("area_name", "Area Urban").strip(),
                float(data.get("freq_mhz", 1800.0)),
                float(data.get("distance_km", 1.0)),
                float(data.get("base_station_height_m", 30.0)),
                float(data.get("mobile_height_m", 1.5)),
                float(data.get("path_loss_db", 0.0)),
                data.get("coverage_quality", "Baik").strip(),
                1 if data.get("is_metro", False) else 0
            ))
            return cursor.lastrowid

    def list_cost231_propagations(self, limit: int = 50) -> List[Dict[str, Any]]:
        """
        Lists stored COST 231 Hata propagation records ordered by id descending.
        """
        with self._get_connection() as conn:
            cursor = conn.execute(
                "SELECT * FROM cost231_propagation_records ORDER BY id DESC LIMIT ?",
                (max(1, int(limit)),)
            )
            return [dict(row) for row in cursor.fetchall()]

    def get_cost231_propagation_by_id(self, record_id: int) -> Optional[Dict[str, Any]]:
        """
        Retrieves a COST 231 Hata propagation record by primary key ID.
        """
        with self._get_connection() as conn:
            cursor = conn.execute(
                "SELECT * FROM cost231_propagation_records WHERE id = ?",
                (int(record_id),)
            )
            row = cursor.fetchone()
            return dict(row) if row else None



















































