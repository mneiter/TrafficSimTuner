from fastapi import FastAPI, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from .models import SimulationInput, SimulationResult
from .runner import launch_simulations

app = FastAPI(title="TrafficSimTuner")

# Enable CORS for frontend access
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# In-memory results store (for simplicity)
results_store: list[SimulationResult] = []

@app.post("/submit_permutations")
async def submit(input_data: SimulationInput, background_tasks: BackgroundTasks):
    background_tasks.add_task(launch_simulations, input_data)
    total = (
        len(input_data.accel_values) *
        len(input_data.tau_values) *
        len(input_data.startup_delay_values)
    )
    return {"status": "processing_started", "total_combinations": total}


@app.post("/report_result")
async def receive_result(result: SimulationResult):
    results_store.append(result)
    return {"status": "result_received"}


@app.get("/results")
def get_best_result():
    if not results_store:
        return {"status": "no_results_yet"}

    best = min(results_store, key=lambda r: r.total_error)
    return {
        "winner": best,
        "total_results": len(results_store)
    }
