#!/usr/bin/env python3
import os
import sys
import sqlite3
import argparse
from pathlib import Path
from typing import Dict, Any, List

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from config import settings

def check_environment() -> Dict[str, Any]:
    issues: List[str] = []
    checks: Dict[str, Any] = {}

    # 1. Python version check
    py_version = sys.version_info
    py_ok = py_version >= (3, 9)
    checks["python_version"] = {
        "value": f"{py_version.major}.{py_version.minor}.{py_version.micro}",
        "passed": py_ok
    }
    if not py_ok:
        issues.append(f"Python version {checks['python_version']['value']} is lower than 3.9")

    # 2. Required directories
    dirs_to_check = [settings.prompts_dir, settings.articles_dir]
    dir_status = {}
    for d in dirs_to_check:
        exists = d.exists()
        writable = os.access(d, os.W_OK) if exists else False
        dir_status[d.name] = {"exists": exists, "writable": writable}
        if not exists:
            issues.append(f"Directory {d.name} does not exist")
    checks["directories"] = dir_status

    # 3. Environment Variables
    env_status = {
        "GEMINI_API_KEY": bool(settings.llm.api_key),
        "TELEGRAM_BOT_TOKEN": bool(settings.telegram.bot_token),
        "WP_CONFIGURED": bool(settings.wp.username and settings.wp.application_password),
    }
    checks["env_vars"] = env_status

    # 4. Database Check
    db_ok = False
    if settings.db_path.exists():
        try:
            conn = sqlite3.connect(str(settings.db_path))
            cur = conn.cursor()
            cur.execute("SELECT COUNT(1) FROM sqlite_master WHERE type='table' AND name='articles';")
            table_exists = cur.fetchone()[0] == 1
            conn.close()
            db_ok = table_exists
        except Exception:
            db_ok = False
    checks["database"] = {"exists": settings.db_path.exists(), "schema_ready": db_ok}

    is_healthy = len(issues) == 0 and checks["database"]["schema_ready"]
    return {
        "healthy": is_healthy,
        "checks": checks,
        "issues": issues
    }

def main():
    parser = argparse.ArgumentParser(description="Telkom Editorial Environment Doctor")
    parser.add_argument("--json", action="store_true", help="Output results in JSON format")
    args = parser.parse_args()

    result = check_environment()

    if args.json:
        import json
        print(json.dumps(result, indent=2))
    else:
        status_icon = "✅ HEALTHY" if result["healthy"] else "⚠️ ATTENTION NEEDED"
        print(f"=== System Doctor Report: {status_icon} ===")
        print(f"Python: {result['checks']['python_version']['value']} (Passed: {result['checks']['python_version']['passed']})")
        print(f"Database Ready: {result['checks']['database']['schema_ready']}")
        print("Env variables:")
        for k, v in result["checks"]["env_vars"].items():
            print(f"  - {k}: {'CONFIGURED' if v else 'NOT SET'}")

        if result["issues"]:
            print("\nIssues found:")
            for issue in result["issues"]:
                print(f"  [!] {issue}")

    sys.exit(0 if result["healthy"] else 1)

if __name__ == "__main__":
    main()
