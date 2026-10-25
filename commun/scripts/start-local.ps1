$ErrorActionPreference = "Stop"
Set-Location (Split-Path (Split-Path $PSScriptRoot -Parent) -Parent)
docker compose up --build --detach --wait
if ($LASTEXITCODE -ne 0) { throw "Échec du démarrage Docker." }
Write-Host "Citoyen : http://127.0.0.1:5175"
Write-Host "Dashboard : http://127.0.0.1:8012/dashboard"
