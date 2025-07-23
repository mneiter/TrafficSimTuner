import pytest
from master.app.models import SimulationInput
from master.app.runner import SimulationRunner


@pytest.mark.runner
def test_launch_starts_expected_workers(mocker):
    """Test that SimulationRunner.launch calls Docker run the correct number of times."""
    mock_client = mocker.Mock()
    mock_run = mock_client.containers.run
    mocker.patch("master.app.runner.docker.from_env", return_value=mock_client)

    input_data = SimulationInput(
        accel_values=[1.0],
        tau_values=[1.0, 2.0],
        startup_delay_values=[0.0],
        expected_delays={"I2": 50.0, "I3": 20.0}
    )

    runner = SimulationRunner()
    runner.launch(input_data)

    assert mock_run.call_count == 2  # 1 accel * 2 tau * 1 delay = 2 combinations

    # Optionally check arguments for the first call
    args, kwargs = mock_run.call_args
    assert kwargs["environment"]["ACCEL"] in [1.0]
    assert kwargs["environment"]["TAU"] in [1.0, 2.0]
    assert kwargs["environment"]["STARTUP_DELAY"] == 0.0
