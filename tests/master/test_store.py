import pytest
from master.app.models import SimulationResult, SimulationInput
from master.app.store import InMemoryStore


def test_singleton_instance():
    store1 = InMemoryStore()
    store2 = InMemoryStore()
    assert store1 is store2


def test_save_and_get_results():
    store = InMemoryStore()
    store.clear()

    result = SimulationResult(
        accel=1.0,
        tau=1.0,
        startup_delay=0.0,
        intersection_avg_delays={"I2": 45.0, "I3": 22.0}
    )

    store.save_result(result)
    results = store.get_results()
    assert len(results) == 1
    assert results[0] == result


def test_save_and_get_multiple_results():
    store = InMemoryStore()
    store.clear()

    results = [        
        SimulationResult(
            accel=1.0,
            tau=1.0,
            startup_delay=0.0,
            intersection_avg_delays={"I2": 40.0, "I3": 20.0}
        ),
        SimulationResult(
            accel=1.0,
            tau=1.5,
            startup_delay=0.0,
            intersection_avg_delays={"I2": 42.0, "I3": 41.0}
        )
    ]
    store.save_results(results)
    stored = store.get_results()
    assert stored == results


def test_worker_count():
    store = InMemoryStore()
    store.clear()
    store.set_worker_count(7)
    assert store.get_worker_count() == 7


def test_input_data():
    store = InMemoryStore()
    store.clear()

    input_data = SimulationInput(
        accel_values=[1.0, 2.0],
        tau_values=[1.0],
        startup_delay_values=[0.0, 0.5],
        expected_delays={"I2": 50.0, "I3": 20.0}
    )
    store.save_input_data(input_data)
    assert store.get_input_data() == input_data


def test_clear_store():
    store = InMemoryStore()
    store.set_worker_count(3)
    store.save_input_data(SimulationInput(
        accel_values=[1],
        tau_values=[1],
        startup_delay_values=[0],
        expected_delays={"I2": 40, "I3": 10}
    ))
    store.save_result(SimulationResult(
        accel=1,
        tau=1,
        startup_delay=0,
        intersection_avg_delays={"I2": 40, "I3": 10}
    ))

    store.clear()
    assert store.get_worker_count() == 0
    assert store.get_input_data() is None
    assert store.get_results() == []

