$ErrorActionPreference = "Stop"
Set-Location (Split-Path (Split-Path $PSScriptRoot -Parent) -Parent)
python -m pytest
if ($LASTEXITCODE -ne 0) { throw "Échec des tests Python." }
python commun/scripts/smoke.py
if ($LASTEXITCODE -ne 0) { throw "Échec des tests HTTP." }
npm --prefix partie-4-frontend run test:e2e
if ($LASTEXITCODE -ne 0) { throw "Échec des tests navigateur." }
