PYTHON ?= python

.PHONY: bootstrap check test smoke docs-verify healthcheck

bootstrap:
	$(PYTHON) -m pip install -r requirements.txt
	$(PYTHON) -m pip install pytest pytest-cov ruff

check:
	$(PYTHON) -m ruff check . --select E9,F63,F7,F82 --exclude external_ref,.venv,venv
	$(PYTHON) -m compileall -q .
	$(PYTHON) tools/verify_docs.py

test:
	$(PYTHON) -m pytest -q tests

smoke:
	$(PYTHON) tools/healthcheck.py --mode stub

docs-verify:
	$(PYTHON) tools/verify_docs.py

healthcheck:
	$(PYTHON) tools/healthcheck.py --mode live
