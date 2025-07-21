from .models import SimulationInput
from itertools import product


def launch_simulations(input_data: SimulationInput):
    """
    Launch one Docker container per parameter permutation.
    """
    permutations = list(product(
        input_data.accel_values,
        input_data.tau_values,
        input_data.startup_delay_values
    ))

    for accel, tau, startup_delay in permutations:
        print(f"Would run: accel={accel}, tau={tau}, startup_delay={startup_delay}")
        # TODO: Implement actual Docker run logic
