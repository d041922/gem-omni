param(
  [Parameter(Mandatory=$true)]
  [ValidateSet('bootstrap','check','test','test-full','smoke','docs-verify','healthcheck')]
  [string]$Task
)

$ErrorActionPreference = 'Stop'
$root = Split-Path -Parent $PSScriptRoot
$pythonCandidates = @(
  (Join-Path $root '.venv\Scripts\python.exe'),
  (Join-Path $root 'venv\Scripts\python.exe'),
  'python'
)
$python = $pythonCandidates | Where-Object {
  if ($_ -eq 'python') { $true } else { Test-Path $_ }
} | Select-Object -First 1

function Invoke-Checked {
  param([scriptblock]$Command)
  & $Command
  if ($LASTEXITCODE -ne 0) {
    exit $LASTEXITCODE
  }
}

switch ($Task) {
  'bootstrap' {
    Invoke-Checked { & $python -m pip install -r (Join-Path $root 'requirements.txt') }
    Invoke-Checked { & $python -m pip install pytest pytest-cov ruff }
  }
  'check' {
    Invoke-Checked { & $python -m ruff check (Join-Path $root 'app.py') (Join-Path $root 'core') (Join-Path $root 'skills') (Join-Path $root 'agents') (Join-Path $root 'pages') (Join-Path $root 'scripts') (Join-Path $root 'tools') (Join-Path $root 'tests') --select E9,F63,F7,F82 --exclude external_ref,.venv,venv }
    Invoke-Checked { & $python -m compileall -q (Join-Path $root 'app.py') (Join-Path $root 'core') (Join-Path $root 'skills') (Join-Path $root 'agents') (Join-Path $root 'pages') (Join-Path $root 'scripts') (Join-Path $root 'tools') }
    Invoke-Checked { & $python (Join-Path $root 'tools\verify_docs.py') }
  }
  'test' {
    Invoke-Checked { & $python -m pytest -q (Join-Path $root 'tests\\test_policy_init.py') (Join-Path $root 'tests\\test_news_intelligence.py') (Join-Path $root 'tests\\test_ui_empty_state.py') (Join-Path $root 'tests\\test_ui_binding_technicals.py') }
  }
  'test-full' {
    Invoke-Checked { & $python -m pytest -q (Join-Path $root 'tests') }
  }
  'smoke' {
    Invoke-Checked { & $python (Join-Path $root 'tools\healthcheck.py') --mode stub }
  }
  'docs-verify' {
    Invoke-Checked { & $python (Join-Path $root 'tools\verify_docs.py') }
  }
  'healthcheck' {
    Invoke-Checked { & $python (Join-Path $root 'tools\healthcheck.py') --mode live }
  }
}
