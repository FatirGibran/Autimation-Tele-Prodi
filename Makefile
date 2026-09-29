.PHONY: test audit run cli-list cli-stats doctor backup bulk-audit clean help

help:
	@echo "Available commands:"
	@echo "  make test        - Run all unit test suites"
	@echo "  make audit       - Run Yoast SEO audit on sample article"
	@echo "  make bulk-audit  - Run batch SEO audit on all articles"
	@echo "  make doctor      - Run environment and configuration diagnostics"
	@echo "  make backup      - Create timestamped backup of SQLite database"
	@echo "  make run         - Run Telegram Bot locally"
	@echo "  make cli-list    - List all recorded articles in database"
	@echo "  make cli-stats   - Show summary statistics of editorial database"
	@echo "  make clean       - Clean python cache files"

test:
	python3 -m unittest discover -s tests

audit:
	python3 cli.py audit --html articles/2026-09-28-webassembly-edge-computing-iot.html --meta articles/2026-09-28-webassembly-edge-computing-iot-metadata.json

bulk-audit:
	python3 scripts/bulk_audit.py

doctor:
	python3 scripts/env_doctor.py

backup:
	python3 scripts/backup_db.py

run:
	python3 bot.py

cli-list:
	python3 cli.py list

cli-stats:
	python3 cli.py stats

clean:
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
