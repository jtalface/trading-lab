.PHONY: help build up down restart logs shell-backend shell-frontend test seed ingest demo clean

help:
	@echo "Volatility Edge Lab - Development Commands"
	@echo ""
	@echo "Setup:"
	@echo "  make build     - Build Docker images"
	@echo "  make up        - Start all services"
	@echo "  make down      - Stop all services"
	@echo "  make restart   - Restart all services"
	@echo ""
	@echo "Data:"
	@echo "  make check     - Check database status"
	@echo "  make seed      - Seed database with instruments"
	@echo "  make ingest    - Ingest sample data (ES & NQ)"
	@echo "  make demo      - Run demo backtest"
	@echo "  make setup     - Complete setup (all-in-one)"
	@echo ""
	@echo "Development:"
	@echo "  make logs      - View logs (all services)"
	@echo "  make shell-backend  - Open backend shell"
	@echo "  make shell-frontend - Open frontend shell"
	@echo "  make test      - Run backend tests"
	@echo ""
	@echo "Cleanup:"
	@echo "  make clean     - Stop and remove all containers/volumes"

build:
	docker-compose build

up:
	docker-compose up -d
	@echo "Services starting..."
	@echo "Frontend: http://localhost:3847"
	@echo "API Docs: http://localhost:8432/docs"

down:
	docker-compose down

restart:
	docker-compose restart

logs:
	docker-compose logs -f

shell-backend:
	docker-compose exec backend bash

shell-frontend:
	docker-compose exec frontend sh

test:
	docker-compose exec backend pytest -v

check:
	docker-compose exec backend python scripts/check_data.py

seed:
	docker-compose exec backend python scripts/seed_data.py

ingest:
	docker-compose exec backend python scripts/ingest_csv.py ES /app/data/sample_data/ES_sample.csv
	docker-compose exec backend python scripts/ingest_csv.py NQ /app/data/sample_data/NQ_sample.csv

demo:
	docker-compose exec backend python scripts/run_demo_backtest.py

setup-complete:
	docker-compose exec backend python scripts/setup_complete.py

setup: setup-complete
	@echo ""
	@echo "✅ Setup complete!"
	@echo "🌐 Open http://localhost:3847 to get started"

dates:
	@echo "Checking available backtest date ranges..."
	@docker-compose exec backend python scripts/check_available_dates.py

clean:
	docker-compose down -v
	@echo "All containers and volumes removed"

# Local development (without Docker)
dev-backend:
	cd backend && \
	export USE_SQLITE=true && \
	uvicorn app.main:app --reload

dev-frontend:
	cd frontend && npm run dev

dev-install:
	cd backend && pip install -r requirements.txt
	cd frontend && npm install

