@echo off
REM Brand Intelligence Platform - Windows Development Scripts

if "%1"=="setup" goto setup
if "%1"=="dev" goto dev  
if "%1"=="stop" goto stop
if "%1"=="clean" goto clean
if "%1"=="logs" goto logs
if "%1"=="help" goto help

:help
echo Brand Intelligence Platform - Development Commands
echo.
echo Usage: dev.bat [command]
echo.
echo Commands:
echo   setup   - Initial project setup
echo   dev     - Start development environment
echo   stop    - Stop all services
echo   clean   - Clean up containers and volumes
echo   logs    - Show logs for all services
echo   help    - Show this help
goto end

:setup
echo 🚀 Setting up Brand Intelligence Platform...
echo Creating environment files...
if not exist backend\.env (
    copy backend\.env.example backend\.env
    echo ✅ Created backend\.env - Edit with your settings
) else (
    echo ℹ️ backend\.env already exists
)
echo Building Docker images...
docker-compose -f docker-compose.dev.yml build
echo ✅ Setup complete! Run 'dev.bat dev' to start
goto end

:dev
echo 🔄 Starting development environment...
docker-compose -f docker-compose.dev.yml up -d postgres redis
echo ⏳ Waiting for databases to be ready...
timeout /t 10 /nobreak > nul
docker-compose -f docker-compose.dev.yml up backend frontend
goto end

:stop
echo 🛑 Stopping all services...
docker-compose -f docker-compose.dev.yml down
goto end

:clean
echo 🧹 Cleaning up...
docker-compose -f docker-compose.dev.yml down -v
docker system prune -f
goto end

:logs
docker-compose -f docker-compose.dev.yml logs -f
goto end

:end