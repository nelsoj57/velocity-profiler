class Wavemeter:
    """
    Wraps access to the wavemeter DLL or API for polling frequency data.

    Attributes:
        handle (object): Internal DLL or API handle (optional depending on library)
    """

    def __init__(self):
        """Initializes wavemeter connection (if required by API)."""
        pass

    def read_frequency(self) -> float:
        """
        Returns the current laser frequency in Hz (or MHz if preferred).
        """
        pass

    def average_frequency(
        self, duration: float = 2.0, poll_rate: float = 10.0
    ) -> tuple:
        """
        Samples frequency at poll_rate (Hz) for duration (s).
        Returns: (average_frequency, std_dev, num_samples)
        """
        pass
