import threading
from fastapi import BackgroundTasks, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from pathlib import Path

from .models import SimulationInput, SimulationResult
from .InMemoryStore import InMemoryStore
from .runner import SimulationRunner
from .scoring import find_best_result

BASE_DIR = Path(__file__).resolve().parent.parent
templates = Jinja2Templates(directory=BASE_DIR / "templates")

runner = SimulationRunner()

def ping():
    print("[INFO] Ping endpoint called")
    return {"status": "ok"}

def index(request: Request):
    try:
        print("[INFO] Serving index.html")
        return templates.TemplateResponse("index.html", {"request": request})
    except Exception as e:
        print(f"[ERROR] Failed to render index.html: {e}")
        return HTMLResponse(content="Internal Server Error", status_code=500)

async def submit(input_data: SimulationInput, background_tasks: BackgroundTasks, store: InMemoryStore):
    try:
        store.clear()
        print(f"[DEBUG] Store values before submit: input_data={store.get_input_data()}, results={store.get_results()}, worker_count={store.get_worker_count()}")

        print(f"[INFO] Received input data: {input_data}")
        store.save_input_data(input_data)

        background_tasks.add_task(runner.launch, input_data)
        num_workers = (
            len(input_data.accel_values) *
            len(input_data.tau_values) *
            len(input_data.startup_delay_values)
        )
        store.set_worker_count(num_workers)
        print(f"[INFO] Submitted simulation job with {num_workers} combinations.")
        return {"status": "processing_started", "total_combinations": num_workers}
    except Exception as e:
        print(f"[ERROR] Failed to submit simulation: {e}")
        return {"status": "error", "message": str(e)}

async def receive_result(result: SimulationResult, store: InMemoryStore):
    try:
        print(f"[INFO] Received result: {result}")
        store.save_result(result)

        print(f"[INFO] Total results stored: {len(store.get_results())}")
        return {"status": "result_received"}
    except Exception as e:
        print(f"[ERROR] Failed to process result: {e}")
        return {"status": "error", "message": str(e)}

def get_best_result(store: InMemoryStore):
    try:
        results = store.get_results()
        input_data = store.get_input_data()
        expected_total = store.get_worker_count()

        print(f"[INFO] Restored input data: {input_data}")
        print(f"[DEBUG] Stored {len(results)} of {expected_total} expected results.")

        if not results:
            return {"status": "no_results_yet"}

        if len(results) < expected_total:
            return {
                "status": "in_progress",
                "received": len(results),
                "expected": expected_total
            }

        best_result, best_score = find_best_result(results, input_data)
        print(f"[INFO] Best result found: {best_result}")
        print(f"[INFO] Minimum score: {best_score:.4f}")

        return best_result
    except Exception as e:
        print(f"[ERROR] Failed to fetch results: {e}")
        return {"status": "error", "message": str(e)}