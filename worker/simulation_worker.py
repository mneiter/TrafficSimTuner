import logging
from logging_config import setup_logger
setup_logger()
logger = logging.getLogger(__name__)

import os
import requests
from run_simulation import run_simulation
from update_vtypes import VTypesConfigUpdater

class SimulationWorker:
    def __init__(self, accel: float, tau: float, startup_delay: float, vtypes_path: str = "hw_model.vtypes.xml", master_url: str = None):
        self.accel = accel
        self.tau = tau
        self.startup_delay = startup_delay
        self.vtypes_path = vtypes_path
        self.master_url = master_url or os.getenv("MASTER_URL")

    def ping_master(self):
        if not self.master_url:
            logger.warning("MASTER_URL is not set. Skipping ping.")
            return False
        try:
            ping_url = self.master_url.replace("/report_result", "/ping")
            response = requests.get(ping_url, timeout=5, headers={"Connection": "close"})
            if response.status_code == 200:
                logger.info("Master is reachable")
                return True
            else:
                logger.warning(f"Master ping failed with status {response.status_code}")
                return False
        except Exception as e:
            logger.error(f"Could not reach master: {e}")
            return False

    def update_vtypes(self):
        updater = VTypesConfigUpdater(self.vtypes_path)
        updater.update(self.accel, self.tau, self.startup_delay)

    def run_simulation(self):
        logger.info("Starting simulation...")
        return run_simulation()

    def post_results(self, result: dict):
        if not self.master_url:
            logger.warning("MASTER_URL not set. Result not sent.")
            return
        try:
            logger.info(f"Posting results to Master at {self.master_url} ...")
            response = requests.post(self.master_url, json=result, timeout=10, headers={"Connection": "close"})
            logger.info(f"Master responded with status {response.status_code}")
        except Exception as e:
            logger.error(f"Failed to send result to master: {e}")

    def execute(self):
        logger.info(f" Received parameters: ACCEL={self.accel}, TAU={self.tau}, STARTUP_DELAY={self.startup_delay}")

        self.ping_master()
        self.update_vtypes()
        delays = self.run_simulation()

        result = {
            "accel": self.accel,
            "tau": self.tau,
            "startup_delay": self.startup_delay,
            "intersection_avg_delays": delays
        }

        self.post_results(result)
        return result
