# Makefile for TrafficSimTuner

# ─────────────── Master (FastAPI) ───────────────

.PHONY: master-run
master-run:
	@echo "Running FastAPI server locally..."
	cd master && uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

.PHONY: master-install
master-install:
	@echo "Installing Python dependencies for master..."
	cd master && pip install -r requirements.txt

.PHONY: master-build
master-build:
	@echo "Building Docker image for master..."
	docker build -t traffic-sim-master ./master

.PHONY: master-up
master-up:
	@echo "Running master server via docker-compose..."
	docker-compose up --build

# ─────────────── Worker (Simulation) ───────────────

.PHONY: worker-build
worker-build:
	@echo "Building Docker image for worker..."
	docker build -t traffic-sim-worker ./worker

.PHONY: worker-run-test
worker-run-test:
	@echo "Running simulation worker locally with .env..."
	docker run --rm --network=simnet \
		--env-file .env \
		traffic-sim-worker

.PHONY: worker-run-test-with-env
worker-run-test-with-env:
	@echo "Running simulation worker with specific environment variables..."
	docker run \
		--name test-worker \
		-e ACCEL=2.5 -e TAU=1.0 -e STARTUP_DELAY=0.5 \
		-e MASTER_URL=http://host.docker.internal:8000/report_result \
		traffic-sim-worker

# ─────────────── Utilities ───────────────

.PHONY: clean
clean:
	@echo "Cleaning up dangling containers/images..."
	docker system prune -f

.PHONY: help
help:
	@echo ""
	@echo "Available Make targets:"
	@echo "  make master-run         - Run FastAPI server (reload mode, local)"
	@echo "  make master-install     - Install dependencies for master"
	@echo "  make master-build       - Build master Docker image"
	@echo "  make master-up          - Run master using docker-compose"
	@echo "  make worker-build       - Build worker Docker image"
	@echo "  make worker-run-test    - Run one test simulation worker"
	@echo "  make clean              - Clean up unused Docker resources"
