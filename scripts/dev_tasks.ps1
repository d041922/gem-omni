param(
  [Parameter(Mandatory=$true)]
  [ValidateSet('bootstrap','check','test','smoke','docs-verify','healthcheck')]
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
    & $python -m ruff check $root --select E9,F63,F7,F82 --exclude external_ref,.venv,venv
    & $python -m compileall -q $root
    & $python (Join-Path $root 'tools\verify_docs.py')
  }
  'test' {
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
