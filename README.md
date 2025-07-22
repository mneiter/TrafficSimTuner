# 🚦 TrafficSimTuner

**TrafficSimTuner** is a simulation and optimization tool for traffic intersections. It uses SUMO (Simulation of Urban Mobility) and a Python backend (FastAPI) to launch vehicle flow simulations with various configurations, collect delay results, and determine the optimal parameters.

---

## 📦 Tech Stack

- **Python 3.10+**
- **FastAPI** + HTML (Jinja2)
- **Docker / Docker Compose**
- **SUMO** (microscopic traffic simulator)
- **Makefile** for easy CLI usage

---

## 🚀 Getting Started

### 1. Prerequisites

- [Docker](https://docs.docker.com/get-docker/)
- [Git](https://git-scm.com/)
- (Optional) [Make](https://www.gnu.org/software/make/) – for convenient commands

### 2. Clone the repository

```bash
git clone https://github.com/mneiter/TrafficSimTuner.git
cd TrafficSimTuner
```

---

## ⚙️ Run the App

### 🔧 Option A: Using Makefile (Recommended)

Run FastAPI server:

```bash
make master-run
```

Build Docker images:

```bash
make master-build     # Backend (FastAPI)
make worker-build     # Worker (SUMO simulation)
```

Run a test simulation manually:

```bash
make worker-run-test
```

Clean Docker resources:

```bash
make clean
```

### 🔧 Option B: Using Docker Compose

Only run the FastAPI server:

```bash
docker compose up --build master
```

> App will be available at: [http://localhost:8000](http://localhost:8000)

> By default, the `worker` container is not auto-started.

---

## 📊 Running a Worker Simulation

To run a single simulation manually:

```bash
docker run --rm \
  -e ACCEL=2.5 \
  -e TAU=1.0 \
  -e STARTUP_DELAY=0.5 \
  -e MASTER_URL=http://host.docker.internal:8000/report_result \
  traffic-sim-worker
```

---

## 🗂 Project Structure

```
TrafficSimTuner/
├── master/
│   ├── app/
│   │   ├── main.py         # FastAPI application
│   │   ├── models.py       # Data schemas
│   │   └── runner.py       # Launches simulation permutations
│   ├── templates/          # index.html (frontend UI)
│   └── requirements.txt
├── worker/
│   ├── entrypoint.py       # Updates vehicle params, runs simulation
│   ├── run_simulation.py   # Connects to SUMO via TraCI
│   ├── hw_model.*.xml      # SUMO model files (routes, config, etc.)
├── docker-compose.yml
├── Makefile
└── README.md
```

---

## 🏁 How it works

1. User submits parameter ranges (accel, tau, startupDelay) via UI.
2. Backend generates permutations and spawns workers.
3. Each worker runs SUMO with updated vtypes, reports average delays.
4. Backend selects the best result based on squared error.

---

## 📮 Endpoints (FastAPI)

- `POST /submit_permutations` — trigger batch of simulations
- `POST /report_result` — worker sends one result
- `GET /results` — return the best result (once all simulations finish)
- `GET /` — main UI page (HTML)

---

## 🙋 Support

Open an issue or contact [Michael](mailto:michael@example.com) for help.

---

## 📝 License

MIT License. See [LICENSE](LICENSE) for more information.
