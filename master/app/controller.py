import logging
from .logging_config import setup_logger
setup_logger()
logger = logging.getLogger(__name__)

from fastapi import BackgroundTasks, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from pathlib import Path

from .models import SimulationInput, SimulationResult
from .store import InMemoryStore
from .runner import SimulationRunner
from .scoring import Scoring


class TrafficSimController:
    def __init__(self):
        base_dir = Path(__file__).resolve().parent.parent
        self.templates = Jinja2Templates(directory=base_dir / "templates")
        self.runner = SimulationRunner()

    def ping(self):
        logger.info("Ping endpoint called")
        return {"status": "ok"}

    def index(self, request: Request):
        try:
            logger.info("Serving index.html")
            return self.templates.TemplateResponse("index.html", {"request": request})
        except Exception as e:
            logger.error(f"Failed to render index.html: {e}")
            return HTMLResponse(content="Internal Server Error", status_code=500)

    async def submit(self, input_data: SimulationInput, background_tasks: BackgroundTasks, store: InMemoryStore):
        try:
            store.clear()
            logger.info(f"Store values before submit: input_data={store.get_input_data()}, results={store.get_results()}, worker_count={store.get_worker_count()}")

            logger.info(f"Received input data: {input_data}")
            store.save_input_data(input_data)

            background_tasks.add_task(self.runner.launch, input_data)
            num_workers = (
                len(input_data.accel_values) *
                len(input_data.tau_values) *
                len(input_data.startup_delay_values)
            )
            store.set_worker_count(num_workers)
            logger.info(f"Submitted simulation job with {num_workers} combinations.")
            return {"status": "processing_started", "total_combinations": num_workers}
        except Exception as e:
            logger.error(f"Failed to submit simulation: {e}")
            return {"status": "error", "message": str(e)}

    async def receive_result(self, result: SimulationResult, store: InMemoryStore):
        try:
            logger.info(f"Received result: {result}")
            store.save_result(result)

            logger.info(f"Total results stored: {len(store.get_results())}")
            return {"status": "result_received"}
        except Exception as e:
            logger.error(f"Failed to process result: {e}")
            return {"status": "error", "message": str(e)}

    def get_best_result(self, store: InMemoryStore):
        try:
            results = store.get_results()
            input_data = store.get_input_data()
            expected_total = store.get_worker_count()

            logger.info(f"Restored input data: {input_data}")
            logger.debug(f"Stored {len(results)} of {expected_total} expected results.")

            if not results:
                return {"status": "no_results_yet"}

            if len(results) < expected_total:
                return {
                    "status": "in_progress",
                    "received": len(results),
                    "expected": expected_total
                }

            scorer = Scoring(input_data)
            best_result, best_score = scorer.best_result(results)

            logger.info(f"Best result found: {best_result}")
            logger.info(f"Minimum score: {best_score:.4f}")

            return best_result
        except Exception as e:
            logger.error(f"Failed to fetch results: {e}")
            return {"status": "error", "message": str(e)}
