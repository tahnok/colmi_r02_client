serve_docs:
	echo "Serving documentation at http://localhost:8080"
	echo "Press Ctrl+C to stop the server."
	poetry run python -m http.server -d docs/ 8080

update:
	poetry lock --no-sync
	poetry install

install:
	poetry install

test: check

check: install
	poetry run ruff format
	poetry run ruff check --fix
	poetry run mypy colmi_r02_client
	poetry run pytest
	poetry check --lock

run: install
	poetry run colmi_r02_util scan

.PHONY: serve_docs test check run update install