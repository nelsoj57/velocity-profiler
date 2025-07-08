# Processes and visualizes velocity distributions


def compute_velocity_histogram(velocities: list, num_bins: int = 100) -> tuple:
    """
    Computes a normalized histogram of velocities.
    Returns (bin_centers, probability_density).
    """
    pass


def estimate_temperature_from_gaussian_width(sigma_v: float, atom_mass: float) -> float:
    """
    Estimates temperature (in K) from the standard deviation of the velocity distribution.
    """
    pass


def plot_velocity_distribution(velocity: list, distribution: list, fit_overlay=None):
    """
    Plots the experimental velocity distribution with optional fitted model overlay.
    """
    pass
