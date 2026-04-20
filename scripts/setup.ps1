# BanShield Windows Setup Script
# Requires PowerShell 5.1 or later

$ErrorActionPreference = "Stop"

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  BanShield Setup for Windows" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan

# Check if uv is installed
if (-not (Get-Command uv -ErrorAction SilentlyContinue)) {
    Write-Host "uv not found. Installing uv..." -ForegroundColor Yellow
    powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
    $env:Path = [System.Environment]::GetEnvironmentVariable("Path", "Machine") + ";" + [System.Environment]::GetEnvironmentVariable("Path", "User")
}

Write-Host "Creating virtual environment with uv..." -ForegroundColor Green
uv venv

Write-Host "Installing dependencies..." -ForegroundColor Green
uv pip install -e ".[dev]"

Write-Host "Installing Playwright browsers..." -ForegroundColor Green
playwright install

if (-not (Test-Path ".env")) {
    Write-Host "Creating .env from example..." -ForegroundColor Green
    Copy-Item ".env.example" ".env"
    Write-Host "Please edit .env with your Azure and Qdrant credentials." -ForegroundColor Yellow
}

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  Setup complete!" -ForegroundColor Cyan
Write-Host "  Run 'uv run banshield' to start." -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
