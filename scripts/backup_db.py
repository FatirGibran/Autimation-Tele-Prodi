#!/usr/bin/env python3
import sys
import shutil
import sqlite3
import argparse
from datetime import datetime
from pathlib import Path

# Add project root to sys.path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from config import settings

def perform_backup(db_path: Path, backup_dir: Path, max_backups: int = 10, verify: bool = True) -> Path:
    if not db_path.exists():
        raise FileNotFoundError(f"Database file not found at: {db_path}")

    backup_dir.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
    target_path = backup_dir / f"editorial_backup_{timestamp}.db"

    # Use SQLite online backup API to ensure ACID consistency without locking issues
    src_conn = sqlite3.connect(str(db_path))
    dst_conn = sqlite3.connect(str(target_path))
    try:
        with dst_conn:
            src_conn.backup(dst_conn)
    finally:
        src_conn.close()
        dst_conn.close()

    if verify:
        verify_conn = sqlite3.connect(str(target_path))
        try:
            cursor = verify_conn.execute("PRAGMA integrity_check;")
            result = cursor.fetchone()[0]
            if result != "ok":
                target_path.unlink(missing_ok=True)
                raise RuntimeError(f"Backup integrity check failed: {result}")
        finally:
            verify_conn.close()

    # Retention policy: remove older backups exceeding max_backups
    existing_backups = sorted(backup_dir.glob("editorial_backup_*.db"), key=lambda p: p.stat().st_mtime)
    while len(existing_backups) > max_backups:
        oldest = existing_backups.pop(0)
        oldest.unlink(missing_ok=True)

    return target_path

def main():
    parser = argparse.ArgumentParser(description="Automated SQLite Database Backup Utility")
    parser.add_argument("--db", type=str, default=str(settings.db_path), help="Path to source SQLite database")
    parser.add_argument("--dest", type=str, default=str(PROJECT_ROOT / "backups"), help="Destination directory for backups")
    parser.add_argument("--max-backups", type=int, default=10, help="Maximum number of backups to retain")
    parser.add_argument("--no-verify", action="store_true", help="Skip PRAGMA integrity check")

    args = parser.parse_args()
    db_path = Path(args.db)
    dest_dir = Path(args.dest)

    try:
        backup_file = perform_backup(db_path, dest_dir, max_backups=args.max_backups, verify=not args.no_verify)
        print(f"Successfully created backup: {backup_file}")
    except Exception as e:
        print(f"Backup failed: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()
