import pytest
from unittest.mock import patch, MagicMock
from worker.simulation_worker import SimulationWorker


@pytest.fixture
def worker():
    return SimulationWorker(accel=1.0, tau=1.5, startup_delay=0.0, master_url="http://localhost:8000/report_result")


def test_ping_master_success(worker):
    with patch("simulation_worker.simulation_worker.requests.get") as mock_get:
        mock_get.return_value.status_code = 200
        assert worker.ping_master() is True


def test_ping_master_failure(worker):
    with patch("simulation_worker.simulation_worker.requests.get") as mock_get:
        mock_get.return_value.status_code = 500
        assert worker.ping_master() is False


def test_ping_master_exception(worker):
    with patch("simulation_worker.simulation_worker.requests.get", side_effect=Exception("network error")):
        assert worker.ping_master() is False


def test_update_vtypes(worker):
    with patch("simulation_worker.simulation_worker.VTypesConfigUpdater") as MockUpdater:
        updater_instance = MockUpdater.return_value
        worker.update_vtypes()
        updater_instance.update.assert_called_once_with(1.0, 1.5, 0.0)


def test_run_simulation(worker):
    with patch("simulation_worker.simulation_worker.run_simulation", return_value={"I2": 10, "I3": 5}) as mock_sim:
        result = worker.run_simulation()
        assert result == {"I2": 10, "I3": 5}
        mock_sim.assert_called_once()


def test_post_results(worker):
    result = {"accel": 1.0, "tau": 1.5, "startup_delay": 0.0, "intersection_avg_delays": {"I2": 10, "I3": 5}}
    with patch("simulation_worker.simulation_worker.requests.post") as mock_post:
        mock_post.return_value.status_code = 200
        worker.post_results(result)
        mock_post.assert_called_once_with(
            "http://localhost:8000/report_result",
            json=result,
            timeout=10,
            headers={"Connection": "close"}
        )


def test_execute_calls_all(worker):
    with patch.object(worker, "ping_master") as mock_ping, \
         patch.object(worker, "update_vtypes") as mock_update, \
         patch.object(worker, "run_simulation", return_value={"I2": 20, "I3": 10}) as mock_run, \
         patch.object(worker, "post_results") as mock_post:

        result = worker.execute()

        mock_ping.assert_called_once()
        mock_update.assert_called_once()
        mock_run.assert_called_once()
        mock_post.assert_called_once()

        assert result == {
            "accel": 1.0,
            "tau": 1.5,
            "startup_delay": 0.0,
            "intersection_avg_delays": {"I2": 20, "I3": 10}
        }
