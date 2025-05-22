# Makefile
.PHONY: help setup dev-up dev-down backend-dev frontend-dev test clean

help: ## Show this help message
	@echo 'Usage: make [target]'
	@echo ''
	@echo 'Targets:'
	@awk 'BEGIN {FS = ":.*?## "} /^[a-zA-Z_-]+:.*?## / {printf "  %-15s %s\n", $$1, $$2}' $(MAKEFILE_LIST)

setup: ## Initial project setup
	@echo "Setting up Brand Intelligence Platform..."
	@cp backend/.env.example backend/.env
	@echo "Please edit backend/.env with your API keys"

dev-up: ## Start development environment
	docker-compose -f docker-compose.dev.yml up -d
	@echo "Development environment started!"
	@echo "Backend API: http://localhost:8000"
	@echo "PostgreSQL: localhost:5432"
	@echo "Redis: localhost:6379"
	@echo "Elasticsearch: http://localhost:9200"

dev-down: ## Stop development environment
	docker-compose -f docker-compose.dev.yml down

backend-dev: ## Run backend in development mode
	cd backend && python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

frontend-dev: ## Run frontend in development mode
	cd frontend && npm run dev

test: ## Run tests
	cd backend && python -m pytest tests/
	cd frontend && npm test

clean: ## Clean up docker containers and volumes
	docker-compose -f docker-compose.dev.yml down -v
	docker system prune -f

db-migrate: ## Run database migrations
	cd backend && alembic upgrade head

db-reset: ## Reset database
	cd backend && alembic downgrade base && alembic upgrade head

logs: ## Show application logs
	docker-compose -f docker-compose.dev.yml logs -f backend