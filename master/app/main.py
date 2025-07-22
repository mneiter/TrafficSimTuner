from fastapi import FastAPI, BackgroundTasks, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse

from .models import SimulationInput, SimulationResult

from .store import InMemoryStore
from .controller import TrafficSimController

store = InMemoryStore()
controller = TrafficSimController()

app = FastAPI(title="TrafficSimTuner")
app.state.store = store

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/ping")
def ping():
    return controller.ping()

@app.get("/", response_class=HTMLResponse)
def index(request: Request):
    return controller.index(request)

@app.post("/submit_permutations")
async def submit(input_data: SimulationInput, background_tasks: BackgroundTasks, request: Request):
    return await controller.submit(input_data, background_tasks, store)

@app.post("/report_result")
async def receive_result(result: SimulationResult, request: Request):
    return await controller.receive_result(result, store)

@app.get("/results")
def get_best_result(request: Request):
    return controller.get_best_result(store)
