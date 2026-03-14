# ──────────────────────────────────────────────
# Etlas development helpers
# Usage: make <target>
# Run from the vms-ac-pi directory
# ──────────────────────────────────────────────

# ── Backend (Spring Boot) ─────────────────────

## Run backend with H2 in-memory DB
backend-dev:
	cd ../vms-ac-server && ./mvnw spring-boot:run -Dspring-boot.run.profiles=dev

## Run backend with local PostgreSQL
backend-dev-pg:
	cd ../vms-ac-server && ./mvnw spring-boot:run -Dspring-boot.run.profiles=devpostgres

## Build backend JAR (skip tests)
backend-build:
	cd ../vms-ac-server && ./mvnw clean package -DskipTests

## Run backend tests
backend-test:
	cd ../vms-ac-server && ./mvnw test

# ── Frontend (Next.js) ───────────────────────

## Install frontend dependencies
frontend-install:
	cd ../vms-ac-ui-next && npm install

## Run frontend dev server
frontend-dev:
	cd ../vms-ac-ui-next && npm run dev

## Build frontend for production
frontend-build:
	cd ../vms-ac-ui-next && npm run build

## Lint frontend
frontend-lint:
	cd ../vms-ac-ui-next && npm run lint

# ── Pi (Python) ──────────────────────────────

## Install Pi dependencies
pi-install:
	pip3 install -r requirements.txt

## Run Pi API locally (no GPIO — will fail on non-Pi)
pi-api:
	cd src && python3 api.py

# ── Combined ─────────────────────────────────

## First-time setup: install all dependencies
setup: frontend-install pi-install
	@echo "Dependencies installed. Copy config templates:"
	@echo "  cp ../vms-ac-ui-next/.env.development.example ../vms-ac-ui-next/.env.development.local"
	@echo "  cp src/var.example.py src/var.py"

## Run backend + frontend together in one terminal (Ctrl+C kills both)
dev:
	@trap 'kill 0' EXIT; \
	(cd ../vms-ac-server && ./mvnw spring-boot:run -Dspring-boot.run.profiles=dev) & \
	(cd ../vms-ac-ui-next && npm run dev) & \
	wait

.PHONY: backend-dev backend-dev-pg backend-build backend-test \
        frontend-install frontend-dev frontend-build frontend-lint \
        pi-install pi-api setup dev
