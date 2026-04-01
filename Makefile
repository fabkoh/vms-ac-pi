# ──────────────────────────────────────────────
# Etlas development helpers
# Usage: make <target>
# Run from the vms-ac-pi directory
# ──────────────────────────────────────────────

# Pi SSH config — override with: make deploy PI_HOST=etlas@192.168.1.250
PI_HOST ?= etlas@192.168.1.250
PI_JAR_PATH ?= /home/etlas/vms-ac-backend-0.0.1-SNAPSHOT.jar
PI_UI_PATH ?= /home/etlas/vms-ac-ui-next

# ── Backend (Spring Boot) ─────────────────────

## Run backend with H2 in-memory DB
backend-dev:
	cd ../vms-ac-server && ./mvnw spring-boot:run -Dspring-boot.run.profiles=dev

## Run backend with local PostgreSQL (staging)
backend-staging:
	cd ../vms-ac-server && DB_PORT=5432 DB_HOST=localhost DB_PASSWORD=postgres SECRET_ENCRYPTION_KEY=ISSSecretkey ./mvnw spring-boot:run -Dspring-boot.run.profiles=production

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

## Lint frontend
frontend-lint:
	cd ../vms-ac-ui-next && npm run lint

## Check frontend builds cleanly without running it (catches compile-time errors)
build-check:
	cd ../vms-ac-ui-next && npm run build
	@echo "✓ Frontend build OK"

# ── Pi (Python) ──────────────────────────────

## Install Pi dependencies
pi-install:
	pip3 install -r requirements.txt

# ── Deploy to Pi ─────────────────────────────

## Build + copy backend JAR to Pi
deploy-backend: backend-build
	scp ../vms-ac-server/target/vms-ac-backend-0.0.1-SNAPSHOT.jar $(PI_HOST):$(PI_JAR_PATH)
	@echo "✓ Backend deployed to $(PI_HOST)"

## Build + copy frontend to Pi
deploy-frontend:
	cd ../vms-ac-ui-next && npm run build
	rsync -avz --delete ../vms-ac-ui-next/.next $(PI_HOST):$(PI_UI_PATH)/
	rsync -avz ../vms-ac-ui-next/public $(PI_HOST):$(PI_UI_PATH)/
	rsync -avz ../vms-ac-ui-next/package.json $(PI_HOST):$(PI_UI_PATH)/
	@echo "✓ Frontend deployed to $(PI_HOST)"

## Build + deploy both backend and frontend to Pi
deploy: deploy-backend deploy-frontend
	@echo "✓ Full deploy complete"

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

## Run backend + frontend in staging (local PostgreSQL)
staging:
	@trap 'kill 0' EXIT; \
	(cd ../vms-ac-server && DB_PORT=5432 DB_HOST=localhost DB_PASSWORD=postgres SECRET_ENCRYPTION_KEY=ISSSecretkey ./mvnw spring-boot:run -Dspring-boot.run.profiles=production) & \
	(cd ../vms-ac-ui-next && npm run build && npm run start) & \
	wait

.PHONY: backend-dev backend-staging backend-build backend-test \
        frontend-install frontend-dev frontend-lint build-check \
        pi-install setup dev staging \
        deploy-backend deploy-frontend deploy
