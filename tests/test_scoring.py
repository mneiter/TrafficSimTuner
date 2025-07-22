import pytest
from master.app.scoring import find_best_result 
from master.app.models import SimulationInput, SimulationResult

def test_find_best_result_simple_case():
    input_data = SimulationInput(
        accel_values=[],
        tau_values=[],
        startup_delay_values=[],
        expected_delays={"I2": 50.0, "I3": 20.0}
    )

    results = [
        SimulationResult(accel=1.0, tau=1.0, startup_delay=0.0, intersection_avg_delays={"I2": 48.0, "I3": 18.0}),
        SimulationResult(accel=2.0, tau=1.5, startup_delay=0.5, intersection_avg_delays={"I2": 51.0, "I3": 21.0}),
        SimulationResult(accel=3.0, tau=2.0, startup_delay=1.0, intersection_avg_delays={"I2": 60.0, "I3": 25.0}),
    ]

    best_result, best_score = find_best_result(results, input_data)

    assert best_result.accel == 1.0
    assert best_result.tau == 1.0
    assert best_result.startup_delay == 0.0
    assert best_score == pytest.approx(8.0)  # (48-50)^2 + (18-20)^2 = 4 + 4 = 8

def test_find_best_result_exact_match():
    input_data = SimulationInput(
        accel_values=[],
        tau_values=[],
        startup_delay_values=[],
        expected_delays={"I2": 45.0, "I3": 15.0}
    )

    results = [
        SimulationResult(accel=1.0, tau=1.0, startup_delay=0.0, intersection_avg_delays={"I2": 45.0, "I3": 15.0}),
        SimulationResult(accel=2.0, tau=1.5, startup_delay=0.5, intersection_avg_delays={"I2": 46.0, "I3": 16.0}),
    ]

    best_result, best_score = find_best_result(results, input_data)

    assert best_score == 0.0
    assert best_result.intersection_avg_delays == {"I2": 45.0, "I3": 15.0}

def test_find_best_result_missing_key():
    input_data = SimulationInput(
        accel_values=[],
        tau_values=[],
        startup_delay_values=[],
        expected_delays={"I2": 10.0, "I3": 5.0}
    )

    results = [
        SimulationResult(accel=1.0, tau=1.0, startup_delay=0.0, intersection_avg_delays={"I2": 10.0}),  # I3 missing
        SimulationResult(accel=2.0, tau=1.5, startup_delay=0.5, intersection_avg_delays={"I2": 11.0, "I3": 6.0}),
    ]

    best_result, best_score = find_best_result(results, input_data)

    assert best_result.accel == 2.0
    assert best_score == pytest.approx(2.0)  # (11-10)^2 + (6-5)^2 = 1 + 1

