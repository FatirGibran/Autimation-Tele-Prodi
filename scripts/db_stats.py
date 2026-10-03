#!/usr/bin/env python3
"""
Inspects SQLite editorial database health, disk footprint, and table metrics.
"""

import sys
import sqlite3
from pathlib import Path

# Add project root to sys.path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from config import settings


def inspect_database(db_path: Path) -> None:
    if not db_path.exists():
        print(f"Database tidak ditemukan di path: {db_path}")
        sys.exit(1)

    file_size_bytes = db_path.stat().st_size
    file_size_kb = file_size_bytes / 1024

    wal_path = db_path.with_name(f"{db_path.name}-wal")
    wal_size_kb = (wal_path.stat().st_size / 1024) if wal_path.exists() else 0.0

    print("=" * 60)
    print(" 📊 Telkom Editorial Database Health & Footprint Inspector")
    print("=" * 60)
    print(f" Database Path : {db_path}")
    print(f" DB File Size  : {file_size_kb:.2f} KB ({file_size_bytes} bytes)")
    print(f" WAL File Size : {wal_size_kb:.2f} KB ({'Aktif' if wal_path.exists() else 'Nonaktif'})")

    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row

    try:
        # PRAGMA checks
        page_size = conn.execute("PRAGMA page_size;").fetchone()[0]
        page_count = conn.execute("PRAGMA page_count;").fetchone()[0]
        freelist = conn.execute("PRAGMA freelist_count;").fetchone()[0]
        journal_mode = conn.execute("PRAGMA journal_mode;").fetchone()[0]

        print(f" Journal Mode  : {journal_mode.upper()}")
        print(f" Page Size     : {page_size} bytes")
        print(f" Page Count    : {page_count} pages")
        print(f" Free Pages    : {freelist} pages ({(freelist * page_size) / 1024:.2f} KB unallocated)")
        print("-" * 60)

        # Table row counts
        tables_cursor = conn.execute("""
            SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%' ORDER BY name;
        """)
        tables = [row["name"] for row in tables_cursor.fetchall()]

        print(f" {'Tabel':<25} | {'Baris':<10} | {'Status'}")
        print("-" * 60)
        for tbl in tables:
            cnt = conn.execute(f"SELECT COUNT(1) FROM {tbl};").fetchone()[0]
            status = "Siap" if cnt >= 0 else "Error"
            print(f" {tbl:<25} | {cnt:<10} | {status}")

        # Index count
        idx_cursor = conn.execute("SELECT COUNT(1) FROM sqlite_master WHERE type='index';")
        total_indexes = idx_cursor.fetchone()[0]
        print("-" * 60)
        print(f" Total Indeks : {total_indexes} indeks terdaftar")

        # Integrity check
        integrity = conn.execute("PRAGMA integrity_check;").fetchone()[0]
        print(f" Integritas   : {'OK (Sehat)' if integrity == 'ok' else f'FAIL ({integrity})'}")
        print("=" * 60)
    finally:
        conn.close()


if __name__ == "__main__":
    db_file = Path(sys.argv[1]) if len(sys.argv) > 1 else settings.db_path
    inspect_database(db_file)
