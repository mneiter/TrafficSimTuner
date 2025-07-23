import logging
from .logging_config import setup_logger
setup_logger()
logger = logging.getLogger(__name__)

from typing import List, Tuple
from .models import SimulationInput, SimulationResult

class Scoring:
    def __init__(self, input_data: SimulationInput):
        self.expected_delays = input_data.expected_delays

    def _calculate_score(self, result: SimulationResult) -> float:
        """
        Calculate the total squared error between actual and expected delays.
        """
        i2_error = (result.intersection_avg_delays.get("I2", 0.0) - self.expected_delays["I2"]) ** 2
        i3_error = (result.intersection_avg_delays.get("I3", 0.0) - self.expected_delays["I3"]) ** 2
        total_error = i2_error + i3_error
        logger.debug(f"Score for {result}: {total_error:.4f}")
        return total_error

    def best_result(self, results: List[SimulationResult]) -> Tuple[SimulationResult, float]:
        """
        Find the result with the lowest score.
        """
        best_result = min(results, key=self._calculate_score)
        best_score = self._calculate_score(best_result)
        return best_result, best_score
