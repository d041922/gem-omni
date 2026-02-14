param(
  [Parameter(Mandatory=$true)]
  [ValidateSet('bootstrap','check','test','test-full','smoke','docs-verify','healthcheck')]
  [string]$Task
)

$ErrorActionPreference = 'Stop'
$root = Split-Path -Parent $PSScriptRoot
$python = 'python'

switch ($Task) {
  'bootstrap' {
    & $python -m pip install -r (Join-Path $root 'requirements.txt')
    & $python -m pip install pytest pytest-cov ruff
  }
  'check' {
    & $python -m ruff check (Join-Path $root 'app.py') (Join-Path $root 'core') (Join-Path $root 'skills') (Join-Path $root 'agents') (Join-Path $root 'pages') (Join-Path $root 'scripts') (Join-Path $root 'tools') (Join-Path $root 'tests') --select E9,F63,F7,F82 --exclude external_ref,.venv,venv
    & $python -m compileall -q (Join-Path $root 'app.py') (Join-Path $root 'core') (Join-Path $root 'skills') (Join-Path $root 'agents') (Join-Path $root 'pages') (Join-Path $root 'scripts') (Join-Path $root 'tools')
    & $python (Join-Path $root 'tools\verify_docs.py')
  }
  'test' {
    & $python -m pytest -q (Join-Path $root 'tests\\test_policy_init.py') (Join-Path $root 'tests\\test_news_intelligence.py') (Join-Path $root 'tests\\test_ui_empty_state.py') (Join-Path $root 'tests\\test_ui_binding_technicals.py')
  }
  'test-full' {
    & $python -m pytest -q (Join-Path $root 'tests')
  }
  'smoke' {
    & $python (Join-Path $root 'tools\healthcheck.py') --mode stub
  }
  'docs-verify' {
    & $python (Join-Path $root 'tools\verify_docs.py')
  }
  'healthcheck' {
    & $python (Join-Path $root 'tools\healthcheck.py') --mode live
  }
}
