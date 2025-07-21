from fastapi import FastAPI, BackgroundTasks, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

from .models import SimulationInput, SimulationResult
from .runner import launch_simulations

from pathlib import Path

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

# In-memory result storage
results_store: list[SimulationResult] = []

# Serve UI
@app.get("/", response_class=HTMLResponse)
def index(request: Request):
    try:
        print("[INFO] Serving index.html")
        return templates.TemplateResponse("index.html", {"request": request})
    except Exception as e:
        print(f"[ERROR] Failed to render index.html: {e}")
        return HTMLResponse(content="Internal Server Error", status_code=500)

# Start simulation batch with permutations
@app.post("/submit_permutations")
async def submit(input_data: SimulationInput, background_tasks: BackgroundTasks):
    try:
        results_store.clear()
        background_tasks.add_task(launch_simulations, input_data)
        total = (
            len(input_data.accel_values) *
            len(input_data.tau_values) *
            len(input_data.startup_delay_values)
        )
        print(f"[INFO] Submitted simulation job with {total} combinations.")
        return {"status": "processing_started", "total_combinations": total}
    except Exception as e:
        print(f"[ERROR] Failed to submit simulation: {e}")
        return {"status": "error", "message": str(e)}

# Receive a result from a simulation worker
@app.post("/report_result")
async def receive_result(result: SimulationResult):
    try:
        results_store.append(result)
        print(f"[INFO] Received result: accel={result.accel}, tau={result.tau}, startup_delay={result.startup_delay}, error={result.total_error}")
        return {"status": "result_received"}
    except Exception as e:
        print(f"[ERROR] Failed to process result: {e}")
        return {"status": "error", "message": str(e)}

# Return the best result so far
@app.get("/results")
def get_best_result():
    try:
        if not results_store:
            print("[INFO] No results yet.")
            return {"status": "no_results_yet"}

        best = min(results_store, key=lambda r: r.total_error)
        print(f"[INFO] Returning best result with error {best.total_error}")
        return {
            "winner": best,
            "total_results": len(results_store)
        }
    except Exception as e:
        print(f"[ERROR] Failed to fetch results: {e}")
        return {"status": "error", "message": str(e)}
