import docker
from .models import SimulationInput
from itertools import product
import uuid
import traceback
import time

def launch_simulations(input_data: SimulationInput):
    """
    Launch one Docker container per permutation of input parameters.
    Uses docker SDK with reliable network configuration.
    """
    try:
        client = docker.from_env()
    except Exception as e:
        print(f"[ERROR] Docker client init failed: {e}")
        return

    permutations = list(product(
        input_data.accel_values,
        input_data.tau_values,
        input_data.startup_delay_values
    ))

    for accel, tau, startup_delay in permutations:
        container_name = f"worker_{uuid.uuid4().hex[:8]}"
        print(f"[INFO] Launching worker: {container_name} with accel={accel}, tau={tau}, startup_delay={startup_delay}")

        try:
            client.containers.run(
                image="traffic-sim-worker",
                name=container_name,
                environment={
                    "ACCEL": str(accel),
                    "TAU": str(tau),
                    "STARTUP_DELAY": str(startup_delay),
                    "MASTER_URL": "http://host.docker.internal:8000/report_result"
                },
                network="simnet",
                working_dir="/app",
                command=["python3", "entrypoint.py"],
                detach=True,                
                remove=True
            )
        except Exception as e:
            print(f"[ERROR] Failed to launch container {container_name}: {e}")
            traceback.print_exc()

    print("[INFO] All workers launched. Waiting before exit...")
    time.sleep(20)
