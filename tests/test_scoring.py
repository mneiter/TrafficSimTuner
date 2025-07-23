import pytest
from master.app.models import SimulationInput, SimulationResult
from master.app.scoring import Scoring


def test_best_result_finds_closest_match():
    input_data = SimulationInput(
        accel_values=[1.0],
        tau_values=[1.0],
        startup_delay_values=[0.0],
        expected_delays={"I2": 50.0, "I3": 20.0}
    )

    results = [
        SimulationResult(accel=1.0, tau=1.0, startupDelay=0.0, intersection_avg_delays={"I2": 55.0, "I3": 25.0}),
        SimulationResult(accel=1.0, tau=1.0, startupDelay=0.0, intersection_avg_delays={"I2": 50.0, "I3": 21.0}),  # <-- closest
        SimulationResult(accel=1.0, tau=1.0, startupDelay=0.0, intersection_avg_delays={"I2": 40.0, "I3": 15.0}),
    ]

    scorer = Scoring(input_data)
    best_result, score = scorer.best_result(results)

    assert best_result.intersection_avg_delays == {"I2": 50.0, "I3": 21.0}
    assert round(score, 4) == 1.0  # (0^2 + 1^2)


def test_score_handles_missing_keys_gracefully():
    input_data = SimulationInput(
        accel_values=[1.0],
        tau_values=[1.0],
        startup_delay_values=[0.0],
        expected_delays={"I2": 10.0, "I3": 20.0}
    )

    result = SimulationResult(accel=1.0, tau=1.0, startupDelay=0.0, intersection_avg_delays={})  # no delays

    scorer = Scoring(input_data)
    score = scorer._calculate_score(result)

    expected = 10.0**2 + 20.0**2  # fallback to 0.0 for both
    assert score == expected


def test_score_exact_match_returns_zero():
    input_data = SimulationInput(
        accel_values=[2.0],
        tau_values=[1.0],
        startup_delay_values=[0.5],
        expected_delays={"I2": 12.3, "I3": 34.5}
    )

    result = SimulationResult(
        accel=2.0,
        tau=1.0,
        startupDelay=0.5,
        intersection_avg_delays={"I2": 12.3, "I3": 34.5}
    )

    scorer = Scoring(input_data)
    score = scorer._calculate_score(result)

    assert score == 0.0
