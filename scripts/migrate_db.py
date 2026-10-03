import sys
from pathlib import Path

# Add project root to path
PROJECT_ROOT = Path(__file__).parent.parent.resolve()
sys.path.insert(0, str(PROJECT_ROOT))

from config import settings
from storage import StorageManager

def run_migration() -> dict:
    """
    Executes automated schema verification, index creation, and migration synchronization.
    """
    print(f"Running database migration check on: {settings.db_path}")
    storage = StorageManager(settings.db_path)

    # Enable WAL mode for high concurrency
    active_mode = storage.enable_wal_mode()
    print(f"Active SQLite journal mode: {active_mode}")

    # Check integrity & vacuum
    maintenance = storage.optimize_and_check_integrity()
    print(f"Integrity check status    : {maintenance['integrity_check']}")
    print(f"VACUUM status             : {'SUCCESS' if maintenance['vacuumed'] else 'FAILED'}")

    # Verify tables
    with storage._get_connection() as conn:
        cursor = conn.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name;")
        tables = [row["name"] for row in cursor.fetchall()]

    expected_tables = ["articles", "article_tags", "article_audit_logs", "article_revisions", "article_meta", "article_exports"]
    missing = [t for t in expected_tables if t not in tables]

    result = {
        "active_mode": active_mode,
        "integrity": maintenance["integrity_check"],
        "tables_found": tables,
        "missing_tables": missing,
        "is_synced": len(missing) == 0 and maintenance["integrity_check"] == "ok"
    }

    if result["is_synced"]:
        print(f"All {len(tables)} tables synchronized and verified successfully.")
    else:
        print(f"Migration error! Missing tables: {missing}")

    return result

if __name__ == "__main__":
    report = run_migration()
    if not report["is_synced"]:
        sys.exit(1)
