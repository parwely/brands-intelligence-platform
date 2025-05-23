# Makefile
.PHONY: help setup dev-up dev-down backend-dev frontend-dev test clean db-init dev-logs

help: ## Show this help message
    @echo 'Usage: make [target]'
    @echo ''
    @echo 'Targets:'
    @awk 'BEGIN {FS = ":.*?## "} /^[a-zA-Z_-]+:.*?## / {printf "  %-15s %s\n", $$1, $$2}' $(MAKEFILE_LIST)

setup: ## Initial project setup
    @echo "Setting up Brand Intelligence Platform..."
    @cp backend/.env.example backend/.env || echo "Note: .env.example not found, please create backend/.env manually"
    @echo "Please edit backend/.env with your configuration"

dev-up: ## Start development environment
    docker-compose -f infrastructure/docker/docker-compose.dev.yml up -d
    @echo "Development environment started!"
    @echo "Backend API: http://localhost:8000"
    @echo "Frontend: http://localhost:3000"
    @echo "PostgreSQL: localhost:5432"
    @echo "Redis: localhost:6379"

dev-down: ## Stop development environment
    docker-compose -f infrastructure/docker/docker-compose.dev.yml down

dev-logs: ## Show development logs
    docker-compose -f infrastructure/docker/docker-compose.dev.yml logs -f

db-init: ## Initialize database
    docker-compose -f infrastructure/docker/docker-compose.dev.yml exec backend python -c "from app.core.init_db import init_database; import asyncio; asyncio.run(init_database())"

backend-dev: ## Run backend in development mode (local)
    cd backend && python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

frontend-dev: ## Run frontend in development mode (local)
    cd frontend && npm run dev

test: ## Run tests
    cd backend && python -m pytest tests/
    cd frontend && npm test

clean: ## Clean up docker containers and volumes
    docker-compose -f infrastructure/docker/docker-compose.dev.yml down -v
    docker system prune -f