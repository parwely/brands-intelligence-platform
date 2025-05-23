# Brand Intelligence Platform - PowerShell Development Script

param(
    [Parameter(Mandatory=$true)]
    [ValidateSet("setup", "dev", "stop", "clean", "logs", "help")]
    [string]$Command
)

function Show-Help {
    Write-Host "Brand Intelligence Platform - Development Commands" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "Usage: .\dev.ps1 [command]" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "Commands:" -ForegroundColor Green
    Write-Host "  setup   - Initial project setup"
    Write-Host "  dev     - Start development environment"
    Write-Host "  stop    - Stop all services"
    Write-Host "  clean   - Clean up containers and volumes"
    Write-Host "  logs    - Show logs for all services"
    Write-Host "  help    - Show this help"
}

function Setup-Project {
    Write-Host "🚀 Setting up Brand Intelligence Platform..." -ForegroundColor Green
    
    if (!(Test-Path "backend\.env")) {
        Copy-Item "backend\.env.example" "backend\.env"
        Write-Host "✅ Created backend\.env - Edit with your settings" -ForegroundColor Green
    } else {
        Write-Host "ℹ️ backend\.env already exists" -ForegroundColor Yellow
    }
    
    Write-Host "Building Docker images..." -ForegroundColor Blue
    docker-compose -f docker-compose.dev.yml build
    Write-Host "✅ Setup complete! Run '.\dev.ps1 dev' to start" -ForegroundColor Green
}

function Start-Dev {
    Write-Host "🔄 Starting development environment..." -ForegroundColor Blue
    docker-compose -f docker-compose.dev.yml up -d postgres redis
    Write-Host "⏳ Waiting for databases to be ready..." -ForegroundColor Yellow
    Start-Sleep -Seconds 10
    docker-compose -f docker-compose.dev.yml up backend frontend
}

function Stop-Services {
    Write-Host "🛑 Stopping all services..." -ForegroundColor Red
    docker-compose -f docker-compose.dev.yml down
}

function Clean-All {
    Write-Host "🧹 Cleaning up..." -ForegroundColor Yellow
    docker-compose -f docker-compose.dev.yml down -v
    docker system prune -f
}

function Show-Logs {
    docker-compose -f docker-compose.dev.yml logs -f
}

# Execute command
switch ($Command) {
    "setup" { Setup-Project }
    "dev" { Start-Dev }
    "stop" { Stop-Services }
    "clean" { Clean-All }
    "logs" { Show-Logs }
    "help" { Show-Help }
}