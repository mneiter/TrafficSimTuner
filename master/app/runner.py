import uuid
import docker
from itertools import product
from .models import SimulationInput

class SimulationRunner:
    def __init__(self):
        self.client = docker.from_env()

    def launch(self, input_data: SimulationInput):
        combinations = self._generate_combinations(input_data)
        print(f"[INFO] Launching {len(combinations)} workers...")

        for params in combinations:
            self._start_worker(*params)

        print("[INFO] All workers launched. Waiting before exit...")

    def _generate_combinations(self, input_data: SimulationInput):
        return list(product(
            input_data.accel_values,
            input_data.tau_values,
            input_data.startup_delay_values
        ))

    def _start_worker(self, accel, tau, startup_delay):
        container_name = f"worker_{uuid.uuid4().hex[:8]}"
        print(f"[INFO] Launching worker: {container_name} with accel={accel}, tau={tau}, startup_delay={startup_delay}")

        self.client.containers.run(
            "traffic-sim-worker",
            detach=True,
            network="simnet",
            name=container_name,
            environment={
                "ACCEL": accel,
                "TAU": tau,
                "STARTUP_DELAY": startup_delay,
                "MASTER_URL": "http://host.docker.internal:8000/report_result"
            },
            working_dir="/app",
            command=["python3", "entrypoint.py"],
            auto_remove=True
        )