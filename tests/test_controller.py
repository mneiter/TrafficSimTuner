import pytest
from unittest.mock import Mock, AsyncMock
from master.app.controller import TrafficSimController
from master.app.models import SimulationInput, SimulationResult
from master.app.store import InMemoryStore


@pytest.fixture
def controller():
    return TrafficSimController()


def test_ping(controller):
    assert controller.ping() == {"status": "ok"}


def test_index_success(controller):
    request = Mock()
    response = controller.index(request)
    assert response.status_code == 200 or isinstance(response, HTMLResponse)


@pytest.mark.asyncio
async def test_submit_success(controller):
    store = InMemoryStore()
    input_data = SimulationInput(
        accel_values=[1.0, 2.0],
        tau_values=[1.0],
        startup_delay_values=[0.0, 1.0],
        expected_delays={"I2": 50.0, "I3": 20.0}
    )
    background_tasks = BackgroundTasks()
    result = await controller.submit(input_data, background_tasks, store)
    assert result["status"] == "processing_started"
    assert result["total_combinations"] == 4


@pytest.mark.asyncio
async def test_receive_result(controller):
    store = InMemoryStore()
    result = SimulationResult(
        accel=2.0,
        tau=1.0,
        startup_delay=0.5,
        intersection_avg_delays={"I2": 49.0, "I3": 22.0}
    )
    response = await controller.receive_result(result, store)
    assert response["status"] == "result_received"
    assert len(store.get_results()) == 1


def test_get_best_result_no_results(controller):
    store = InMemoryStore()
    store.set_worker_count(3)
    response = controller.get_best_result(store)
    assert response["status"] == "no_results_yet"


def test_get_best_result_in_progress(controller):
    store = InMemoryStore()
    store.set_worker_count(3)
    store.save_result(SimulationResult(1.0, 1.0, 0.0, {"I2": 48.0, "I3": 18.0}))
    response = controller.get_best_result(store)
    assert response["status"] == "in_progress"
    assert response["received"] == 1
    assert response["expected"] == 3


def test_get_best_result_complete(controller):
    store = InMemoryStore()
    store.set_worker_count(2)
    store.save_input_data(SimulationInput(
        accel_values=[1.0],
        tau_values=[1.0],
        startup_delay_values=[0.0, 1.0],
        expected_delays={"I2": 50.0, "I3": 20.0}
    ))
    store.save_result(SimulationResult(1.0, 1.0, 0.0, {"I2": 49.0, "I3": 21.0}))
    store.save_result(SimulationResult(1.0, 1.0, 1.0, {"I2": 51.0, "I3": 19.0}))
    result = controller.get_best_result(store)
    assert isinstance(result, SimulationResult)

