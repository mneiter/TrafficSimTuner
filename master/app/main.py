from fastapi import FastAPI, BackgroundTasks, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.templating import Jinja2Templates

from .models import SimulationInput, SimulationResult
from .runner import launch_simulations

from pathlib import Path
from .redis_client import RedisClient

app = FastAPI(title="TrafficSimTuner")
app.state.redis = RedisClient()

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

@app.get("/ping")
def ping():
    print("[INFO] Ping endpoint called")
    return {"status": "ok"}

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
async def submit(input_data: SimulationInput, background_tasks: BackgroundTasks, request: Request):
    try:
        redis_client: RedisClient = request.app.state.redis
        redis_client.clear()

        print(f"[DEBUG] Redis values before submit: input_data={redis_client.get_input_data()}, results={redis_client.get_results()}, worker_count={redis_client.get_worker_count()}")

        print(f"[INFO] Received input data: {input_data}")
        redis_client.save_input_data(input_data)

        background_tasks.add_task(launch_simulations, input_data)
        num_workers = (
            len(input_data.accel_values) *
            len(input_data.tau_values) *
            len(input_data.startup_delay_values)
        )
        redis_client.set_worker_count(num_workers)
        print(f"[INFO] Submitted simulation job with {num_workers} combinations.")
        return {"status": "processing_started", "total_combinations": num_workers}
    except Exception as e:
        print(f"[ERROR] Failed to submit simulation: {e}")
        return {"status": "error", "message": str(e)}

# Receive a result from a simulation worker
@app.post("/report_result")
async def receive_result(result: SimulationResult, request: Request):
    try:
        redis_client: RedisClient = request.app.state.redis

        print(f"[INFO] Received result: {result}")

        results = redis_client.get_results()
        results.append(result)
        redis_client.save_results(results)
        
        print(f"[INFO] Total results stored: {len(results)}")
        
        return {"status": "result_received"}
    except Exception as e:
        print(f"[ERROR] Failed to process result: {e}")
        return {"status": "error", "message": str(e)}

# Return the best result so far
@app.get("/results")
def get_best_result(request: Request):
    try:
        redis_client: RedisClient = request.app.state.redis
        results = redis_client.get_results()
        input_data = redis_client.get_input_data()
        expected_total = redis_client.get_worker_count()

        print(f"[INFO] Restored input data: {input_data}")
        print(f"[DEBUG] Stored {len(results)} of {expected_total} expected results.")

        if not results:
            print("[INFO] No results yet.")
            return {"status": "no_results_yet"}

        if len(results) < expected_total:
            print("[INFO] Waiting for more results...")
            return {
                "status": "in_progress",
                "received": len(results),
                "expected": expected_total
            }

        best_result = find_best_result(results, input_data)
        print(f"[INFO] Best result found: {best_result}")

        return best_result

    except Exception as e:
        print(f"[ERROR] Failed to fetch results: {e}")
        return {"status": "error", "message": str(e)}

def find_best_result(results, input_data):
    expected_delays = input_data.expected_delays

    print("[INFO] All results:")
    for r in results:
        print("-" * 40)
        print(r)

    def calculating_minimum_value(r: SimulationResult):
        return (
                (r.intersection_avg_delays.get("I2", 0.0) - expected_delays["I2"]) ** 2 +
                (r.intersection_avg_delays.get("I3", 0.0) - expected_delays["I3"]) ** 2
            )
    
    for r in results:
        score = calculating_minimum_value(r)
        print("-" * 40)
        print(f"Result: {r}")
        print(f"Score: {score:.4f}")

    best_result = min(results, key=calculating_minimum_value)
    print("=" * 40)
    print(f"[INFO] Best result found: {best_result}")
    return best_result
