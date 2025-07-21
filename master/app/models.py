from pydantic import BaseModel, Field
from typing import List, Dict


class SimulationInput(BaseModel):
    expected_delays: Dict[str, float]  # e.g. {"I2": 50.0, "I3": 20.0}
    accel_values: List[float]
    tau_values: List[float]
    startup_delay_values: List[float]


class SimulationResult(BaseModel):
    accel: float
    tau: float
    startup_delay: float
    intersection_avg_delays: Dict[str, float]
    total_error: float = Field(..., description="Squared error against expected delays")
