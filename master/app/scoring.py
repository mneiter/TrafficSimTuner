from .models import SimulationInput, SimulationResult
from typing import List, Tuple

def find_best_result(results: List[SimulationResult], input_data: SimulationInput) -> Tuple[SimulationResult, float]:
    expected_delays = input_data.expected_delays

    def score(r: SimulationResult) -> float:
        value = (
            (r.intersection_avg_delays.get("I2", 0.0) - expected_delays["I2"]) ** 2 +
            (r.intersection_avg_delays.get("I3", 0.0) - expected_delays["I3"]) ** 2
        )
        print(f"[DEBUG] Score for {r}: {value:.4f}")
        return value

    best_result = min(results, key=score)
    best_score = score(best_result)
    return best_result, best_score
