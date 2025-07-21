# Makefile for TrafficSimTuner

# ─────────────── Master (FastAPI) ───────────────

.PHONY: master-run
master-run:
	@echo "▶ Running FastAPI server locally..."
	cd master && uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

.PHONY: master-install
master-install:
	@echo "📦 Installing Python dependencies for master..."
	cd master && pip install -r requirements.txt

.PHONY: master-build
master-build:
	@echo "🐳 Building Docker image for master..."
	docker build -t traffic-sim-master ./master

# ─────────────── Worker (Simulation) ───────────────

.PHONY: worker-build
worker-build:
	@echo "🐳 Building Docker image for worker..."
	docker build -t traffic-sim-worker ./worker

.PHONY: worker-run-test
worker-run-test:
	@echo "▶ Running simulation worker locally..."
	docker run --rm \
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
	@echo "  master-run          - Run FastAPI server (with reload)"
	@echo "  master-install      - Install dependencies for master"
	@echo "  master-build        - Build master Docker image"
	@echo "  worker-build        - Build worker Docker image"
	@echo "  worker-run-test     - Run a test worker with sample parameters"
	@echo "  clean               - Clean up unused Docker resources"
