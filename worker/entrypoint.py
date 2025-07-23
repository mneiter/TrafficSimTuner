import logging
from logging_config import setup_logger
setup_logger()
logger = logging.getLogger(__name__)

import os
from simulation_worker import SimulationWorker

def main():
    try:
        accel = float(os.getenv("ACCEL", "2.0"))
        tau = float(os.getenv("TAU", "1.2"))
        startup_delay = float(os.getenv("STARTUP_DELAY", "0"))
        master_url = os.getenv("MASTER_URL")

        worker = SimulationWorker(accel, tau, startup_delay, master_url=master_url)
        result = worker.execute()
        logger.info("[RESULT]", result)
    except Exception as e:
        logger.error(f"Worker failed: {e}")

if __name__ == "__main__":
    main()
