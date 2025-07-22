from typing import List, Optional
from .models import SimulationResult, SimulationInput
import logging

class InMemoryStore:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(InMemoryStore, cls).__new__(cls)
            cls._instance._results: List[SimulationResult] = []
            cls._instance._worker_count: int = 0
            cls._instance._input_data: Optional[SimulationInput] = None
        return cls._instance

    # --- Simulation Results ---
    def save_result(self, result: SimulationResult):
        print(f"[INFO] Saving simulation result: {result}")
        self._results.append(result)

    def get_results(self) -> List[SimulationResult]:
        return self._results

    # --- Worker Count ---
    def set_worker_count(self, count: int):
        self._worker_count = count

    def get_worker_count(self) -> int:
        return self._worker_count

    # --- Simulation Input Data ---
    def save_input_data(self, input_data: SimulationInput):
        self._input_data = input_data

    def get_input_data(self) -> Optional[SimulationInput]:
        return self._input_data

    # --- Store Management ---
    def clear(self):
        self._results = []
        self._worker_count = 0
        self._input_data = None
