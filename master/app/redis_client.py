import os
import redis
import json
from .models import SimulationResult, SimulationInput
from typing import List, Optional

class RedisClient:
    def __init__(self):
        host = os.getenv("REDIS_HOST", "localhost")
        port = int(os.getenv("REDIS_PORT", 6379))
        self.r = redis.Redis(host=host, port=port, db=0, decode_responses=True)

    def save_results(self, results: List[SimulationResult]):
        serialized = [r.model_dump_json() for r in results]
        self.r.set("results_store", json.dumps(serialized))

    def get_results(self) -> List[SimulationResult]:
        data = self.r.get("results_store")
        if data:
            return [SimulationResult.model_validate_json(r) for r in json.loads(data)]
        return []

    def set_worker_count(self, count: int):
        self.r.set("num_simulation_workers", count)

    def get_worker_count(self) -> int:
        val = self.r.get("num_simulation_workers")
        return int(val) if val else 0

    def save_input_data(self, input_data: SimulationInput):
        serialized = input_data.model_dump_json()
        self.r.set("simulation_input", serialized)

    def get_input_data(self) -> Optional[SimulationInput]:
        data = self.r.get("simulation_input")
        if data:
            return SimulationInput.model_validate_json(data)
        return None

    def clear(self):
        self.r.delete("results_store", "num_simulation_workers", "simulation_input")
