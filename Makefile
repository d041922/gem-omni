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

.PHONY: bootstrap check check-lint check-compile check-docs test test-full test-full-fast smoke docs-verify healthcheck
PYTEST_OPTS := -q -p no:cacheprovider --basetemp=.tmp/pytest_tmp -o cache_dir=.tmp/pytest_cache
CHECK_TARGETS := app.py core skills agents pages scripts tools tests
EXISTING_CHECK_TARGETS := $(strip $(foreach p,$(CHECK_TARGETS),$(if $(wildcard $(p)),$(p),)))
DOC_VERIFY_SCRIPT := $(firstword $(wildcard tools/verify_docs.py scripts/verify_docs.py))
HEALTHCHECK_SCRIPT := $(firstword $(wildcard tools/healthcheck.py scripts/healthcheck.py))
QUICK_TEST_CANDIDATES := tests/test_policy_init.py tests/test_news_intelligence.py tests/test_ui_empty_state.py tests/test_ui_binding_technicals.py
EXISTING_QUICK_TESTS := $(strip $(foreach p,$(QUICK_TEST_CANDIDATES),$(if $(wildcard $(p)),$(p),)))

bootstrap:
	$(PYTHON) -m pip install -r requirements.txt
	$(PYTHON) -m pip install pytest pytest-cov ruff

check:
	$(MAKE) check-lint
	$(MAKE) check-compile
	$(MAKE) check-docs

check-lint:
	$(PYTHON) -m ruff check $(EXISTING_CHECK_TARGETS) --select E9,F63,F7,F82 --exclude external_ref,.venv,venv

check-compile:
	$(PYTHON) -m compileall -q $(EXISTING_CHECK_TARGETS)

check-docs:
	@if [ -n "$(DOC_VERIFY_SCRIPT)" ]; then \
		$(PYTHON) "$(DOC_VERIFY_SCRIPT)"; \
	else \
		echo "Skipping docs verify: no verify_docs.py found"; \
	fi

test:
	$(PYTHON) -c "import os; os.makedirs('.tmp/pytest_tmp', exist_ok=True); os.makedirs('.tmp/pytest_cache', exist_ok=True)"
	@if [ -n "$(EXISTING_QUICK_TESTS)" ]; then \
		$(PYTHON) -m pytest $(PYTEST_OPTS) $(EXISTING_QUICK_TESTS); \
	else \
		$(PYTHON) -m pytest $(PYTEST_OPTS) tests; \
	fi

test-full:
	$(PYTHON) -c "import os; os.makedirs('.tmp/pytest_tmp', exist_ok=True); os.makedirs('.tmp/pytest_cache', exist_ok=True)"
	$(PYTHON) -m pytest $(PYTEST_OPTS) tests

test-full-fast:
	$(PYTHON) -c "import os; os.makedirs('.tmp/pytest_tmp', exist_ok=True); os.makedirs('.tmp/pytest_cache', exist_ok=True)"
	$(PYTHON) -m pytest $(PYTEST_OPTS) --maxfail=20 tests

smoke:
	@if [ -n "$(HEALTHCHECK_SCRIPT)" ]; then \
		$(PYTHON) "$(HEALTHCHECK_SCRIPT)" --mode stub; \
	else \
		echo "Skipping smoke: no healthcheck.py found"; \
	fi

docs-verify:
	@if [ -n "$(DOC_VERIFY_SCRIPT)" ]; then \
		$(PYTHON) "$(DOC_VERIFY_SCRIPT)"; \
	else \
		echo "Skipping docs verify: no verify_docs.py found"; \
	fi

healthcheck:
	@if [ -n "$(HEALTHCHECK_SCRIPT)" ]; then \
		$(PYTHON) "$(HEALTHCHECK_SCRIPT)" --mode live; \
	else \
		echo "Skipping healthcheck: no healthcheck.py found"; \
	fi
