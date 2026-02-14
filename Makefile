ifeq ($(OS),Windows_NT)
ifneq ("$(wildcard .venv/Scripts/python.exe)","")
PYTHON := .venv/Scripts/python.exe
else ifneq ("$(wildcard venv/Scripts/python.exe)","")
PYTHON := venv/Scripts/python.exe
else
PYTHON ?= python
endif
else
ifneq ("$(wildcard .venv/bin/python)","")
PYTHON := .venv/bin/python
else ifneq ("$(wildcard venv/bin/python)","")
PYTHON := venv/bin/python
else
PYTHON ?= python3
endif
endif

.PHONY: bootstrap check check-lint check-compile check-docs test test-full smoke docs-verify healthcheck

bootstrap:
	$(PYTHON) -m pip install -r requirements.txt
	$(PYTHON) -m pip install pytest pytest-cov ruff

check:
	$(MAKE) check-lint
	$(MAKE) check-compile
	$(MAKE) check-docs

check-lint:
	$(PYTHON) -m ruff check app.py core skills agents pages scripts tools tests --select E9,F63,F7,F82 --exclude external_ref,.venv,venv

check-compile:
	$(PYTHON) -m compileall -q app.py core skills agents pages scripts tools

check-docs:
	$(PYTHON) tools/verify_docs.py

test:
	$(PYTHON) -m pytest -q tests

test-full:
	$(PYTHON) -m pytest -q tests

smoke:
	$(PYTHON) tools/healthcheck.py --mode stub

docs-verify:
	$(PYTHON) tools/verify_docs.py

healthcheck:
	$(PYTHON) tools/healthcheck.py --mode live
