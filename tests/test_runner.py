
import pytest

from master.app.models import SimulationInput
from master.app.runner import SimulationRunner

def test_generate_permutations():
    input_data = SimulationInput(
        accel_values=[1.0, 2.0],
        tau_values=[0.5],
        startup_delay_values=[0.0, 1.0],
        expected_delays={"I2": 50.0, "I3": 20.0}
    )
    runner = SimulationRunner(input_data)
    permutations = runner.generate_permutations()

    expected = [
        (1.0, 0.5, 0.0),
        (1.0, 0.5, 1.0),
        (2.0, 0.5, 0.0),
        (2.0, 0.5, 1.0),
    ]
    assert permutations == expected
    assert len(permutations) == 4

def test_simulation_runner_count():
    input_data = SimulationInput(
        accel_values=[1.0],
        tau_values=[0.5, 1.0],
        startup_delay_values=[0.0],
        expected_delays={"I2": 30.0, "I3": 15.0}
    )
    runner = SimulationRunner(input_data)
    assert runner.total_combinations() == 2
