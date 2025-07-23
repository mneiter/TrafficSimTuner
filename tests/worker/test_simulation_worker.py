import pytest
from unittest.mock import patch, MagicMock
from worker.simulation_worker import SimulationWorker


@pytest.fixture
def worker():
    return SimulationWorker(
        accel=2.0,
        tau=1.0,
        startup_delay=0.5,
        vtypes_path="dummy.xml",
        master_url="http://localhost:8000/report_result"
    )


@patch("worker.simulation_worker.requests.get")
def test_ping_master_success(mock_get, worker):
    mock_get.return_value.status_code = 200
    assert worker.ping_master() is True


@patch("worker.simulation_worker.requests.get")
def test_ping_master_failure(mock_get, worker):
    mock_get.return_value.status_code = 500
    assert worker.ping_master() is False


@patch("worker.simulation_worker.requests.get", side_effect=Exception("Timeout"))
def test_ping_master_exception(mock_get, worker):
    assert worker.ping_master() is False


@patch("worker.simulation_worker.VTypesConfigUpdater")
def test_update_vtypes(mock_updater_class, worker):
    mock_updater = MagicMock()
    mock_updater_class.return_value = mock_updater

    worker.update_vtypes()
    mock_updater.update.assert_called_once_with(2.0, 1.0, 0.5)


@patch("worker.simulation_worker.run_simulation", return_value={"I1": 12.3})
def test_run_simulation(mock_run, worker):
    result = worker.run_simulation()
    assert result == {"I1": 12.3}


@patch("worker.simulation_worker.requests.post")
def test_post_results(mock_post, worker):
    mock_post.return_value.status_code = 200
    worker.post_results({"data": 123})
    mock_post.assert_called_once()


@patch("worker.simulation_worker.run_simulation", return_value={"I2": 33.3})
@patch("worker.simulation_worker.VTypesConfigUpdater")
@patch("worker.simulation_worker.requests.post")
@patch("worker.simulation_worker.requests.get", return_value=MagicMock(status_code=200))
def test_execute(mock_get, mock_post, mock_updater_class, mock_run, worker):
    mock_updater = MagicMock()
    mock_updater_class.return_value = mock_updater

    result = worker.execute()
    assert result["accel"] == 2.0
    assert result["tau"] == 1.0
    assert result["startup_delay"] == 0.5
    assert result["intersection_avg_delays"] == {"I2": 33.3}
