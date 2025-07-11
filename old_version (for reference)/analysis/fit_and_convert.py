def fit_voigt_profile(frequencies: list, intensities: list) -> dict:
    """
    Fits a Voigt profile to I(frequency) data.
    Returns fitted parameters: ν₀, σ (Gaussian), γ (Lorentzian), amplitude.
    """
    pass


def fit_gaussian_profile(frequencies: list, intensities: list) -> dict:
    """
    Fits a pure Gaussian profile to I(frequency) data.
    Returns: ν₀, σ, amplitude.
    """
    pass


def convert_frequency_to_velocity(frequencies: list, nu_0: float) -> list:
    """
    Converts a frequency axis (in Hz or MHz) to velocity using the Doppler formula.
    """
    pass


def evaluate_fit_velocity_distribution(
    velocity_grid: list, fit_params: dict, model="voigt"
) -> list:
    """
    Re-evaluates the fitted Voigt or Gaussian model in velocity space.
    Returns list of f(v) values over grid.
    """
    pass
