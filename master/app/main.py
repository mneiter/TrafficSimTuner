from fastapi import FastAPI, BackgroundTasks, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

from .models import SimulationInput, SimulationResult
from .runner import launch_simulations

from pathlib import Path
from fastapi.templating import Jinja2Templates

app = FastAPI(title="TrafficSimTuner")

# Allow frontend requests
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Jinja2 templates directory
BASE_DIR = Path(__file__).resolve().parent.parent
templates = Jinja2Templates(directory=BASE_DIR / "templates")

# In-memory result storage (simple prototype)
results_store: list[SimulationResult] = []

# Serve UI
@app.get("/", response_class=HTMLResponse)
def index(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

# Start simulation batch with permutations
@app.post("/submit_permutations")
async def submit(input_data: SimulationInput, background_tasks: BackgroundTasks):
    results_store.clear()  # Clear old results
    background_tasks.add_task(launch_simulations, input_data)
    total = (
        len(input_data.accel_values) *
        len(input_data.tau_values) *
        len(input_data.startup_delay_values)
    )
    return {"status": "processing_started", "total_combinations": total}

# Receive a result from a simulation worker
@app.post("/report_result")
async def receive_result(result: SimulationResult):
    results_store.append(result)
    return {"status": "result_received"}

# Return the best result so far
@app.get("/results")
def get_best_result():
    if not results_store:
        return {"status": "no_results_yet"}

    best = min(results_store, key=lambda r: r.total_error)
    return {
        "winner": best,
        "total_results": len(results_store)
    }
