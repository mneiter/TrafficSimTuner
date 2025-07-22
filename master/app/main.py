from fastapi import FastAPI, BackgroundTasks, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse

from .models import SimulationInput, SimulationResult
from .store import InMemoryStore
from . import endpoints

app = FastAPI(title="TrafficSimTuner")
app.state.store = InMemoryStore()

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
    return endpoints.ping()

@app.get("/", response_class=HTMLResponse)
def index(request: Request):
    return endpoints.index(request)

@app.post("/submit_permutations")
async def submit(input_data: SimulationInput, background_tasks: BackgroundTasks, request: Request):
    return await endpoints.submit(input_data, background_tasks, app.state.store)

@app.post("/report_result")
async def receive_result(result: SimulationResult, request: Request):
    return await endpoints.receive_result(result, app.state.store)

@app.get("/results")
def get_best_result(request: Request):
    return endpoints.get_best_result(app.state.store)
