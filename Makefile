.PHONY: test audit run cli-list clean help

help:
	@echo "Available commands:"
	@echo "  make test      - Run all unit test suites"
	@echo "  make audit     - Run Yoast SEO audit on sample article"
	@echo "  make run       - Run Telegram Bot locally"
	@echo "  make cli-list  - List all recorded articles in database"
	@echo "  make clean     - Clean python cache files"

test:
	python3 -m unittest discover -s tests

audit:
	python3 cli.py audit --html articles/2026-09-28-webassembly-edge-computing-iot.html --meta articles/2026-09-28-webassembly-edge-computing-iot-metadata.json

run:
	python3 bot.py

cli-list:
	python3 cli.py list

clean:
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
