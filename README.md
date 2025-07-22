# 🚦 TrafficSimTuner

**TrafficSimTuner** is a simulation and optimization tool for traffic intersections. It uses SUMO (Simulation of Urban Mobility) to simulate vehicle flows and FastAPI to manage simulation tasks, aggregate results, and identify the optimal configuration.

---

## 🧰 Tech Stack

- **Python 3.11+**
- **FastAPI** with Jinja2 HTML templates
- **SUMO** (microscopic traffic simulator)
- **Docker & Docker Compose**
- **Makefile** for developer convenience
- **Pydantic** for data validation

---

## 🚀 Getting Started

### 1. Prerequisites

- [Docker](https://docs.docker.com/get-docker/)
- [Git](https://git-scm.com/)
- (Optional) [Make](https://www.gnu.org/software/make/)

### 2. Clone the Repository

```bash
git clone https://github.com/mneiter/TrafficSimTuner.git
cd TrafficSimTuner
```

### 3. (Optional) Create Virtual Environment

> This step is for local development outside Docker.

```bash
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
pip install -r master/requirements.txt
```

---

## ⚙️ Running the Application

### 🔁 With Docker Compose

```bash
make restart
```

This will:

- Shut down previous containers
- Build the images (Master, Worker, Redis)
- Launch the backend and infrastructure

The app will be available at [http://localhost:8000](http://localhost:8000)

> Worker containers are launched dynamically based on your simulation request.

---

### 🧪 Run a Single Worker Manually

```bash
docker run --rm \
  --network=simnet \
  -e ACCEL=2.5 \
  -e TAU=1.0 \
  -e STARTUP_DELAY=0.5 \
  -e MASTER_URL=http://master:8000/report_result \
  traffic-sim-worker
```

---

## 🗂 Project Structure

```
TrafficSimTuner/
├── master/
│   ├── Dockerfile
│   ├── requirements.txt
│   ├── templates/
│   │   ├── index.html         # Frontend UI
│   ├── app/
│   │   ├── main.py
│   │   ├── endpoints.py
│   │   ├── InMemoryStore.py
│   │   ├── runner.py
│   │   └── ...
├── worker/
│   ├── Dockerfile
│   ├── entrypoint.py
│   ├── run_simulation.py
│   ├── hw_model.*.xml     # SUMO network/config files
├── docker-compose.yml
├── Makefile
└── README.md
```

---

## 📬 API Endpoints (FastAPI)

- `GET /` – UI HTML page
- `GET /ping` – health check
- `POST /submit_permutations` – submit range of parameters
- `POST /report_result` – worker reports simulation result
- `GET /results` – fetch best result or status

---

## 📈 How It Works

1. User submits ranges for `accel`, `tau`, and `startup_delay`
2. The master backend spawns one Docker worker per permutation
3. Each worker runs SUMO with adjusted parameters
4. Each worker reports its average delays to the master
5. The master selects the best result using score minimization

---

## 🧹 Common Commands (Makefile)

```bash
make master-run         # Run FastAPI server locally
make master-install     # Install Python packages for master
make master-build       # Build Docker image for master
make worker-build       # Build Docker image for worker
make worker-run-test    # Run one worker manually
make clean              # Remove dangling Docker resources
make restart            # Rebuild and restart the whole stack
```

---

## 📝 License

MIT License — see `LICENSE`.

Project Repository: [https://github.com/mneiter/TrafficSimTuner](https://github.com/mneiter/TrafficSimTuner)
