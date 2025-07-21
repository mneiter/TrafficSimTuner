import docker
from .models import SimulationInput
from itertools import product
import uuid


def launch_simulations(input_data: SimulationInput):
    """
    Launch one Docker container per permutation of input parameters.
    """
    client = docker.from_env()

    permutations = list(product(
        input_data.accel_values,
        input_data.tau_values,
        input_data.startup_delay_values
    ))

    for accel, tau, startup_delay in permutations:
        container_name = f"worker_{uuid.uuid4().hex[:8]}"
        print(f"Launching worker: {container_name} with accel={accel}, tau={tau}, startup_delay={startup_delay}")

        try:
            client.containers.run(
                image="traffic-sim-worker",  # replace with your built image name
                name=container_name,
                environment={
                    "ACCEL": str(accel),
                    "TAU": str(tau),
                    "STARTUP_DELAY": str(startup_delay),
                    "MASTER_URL": "http://master:8000/report_result"
                },
                detach=True,
                remove=True
            )
        except Exception as e:
            print(f"Failed to launch container: {e}")
