class StepQueue:
    """
    Manages the list of voltage steps for a scan session.

    Attributes:
        voltage_points (list): List of (step_index, voltage) pairs
        current_index (int): Tracks progress through steps
    """

    def __init__(self, voltage_points: list):
        """Initializes with a list of steps to perform."""
        pass

    def __iter__(self):
        """Allows StepQueue to be used in for-loops."""
        return self

    def __next__(self):
        """Returns the next (step_index, voltage) tuple."""
        pass


class RetryManager:
    """
    Tracks and reruns scan points that failed due to instability.

    Attributes:
        failed_steps (list): List of (step_index, voltage, reason) tuples
    """

    def __init__(self):
        self.failed_steps = []

    def record_failed_step(self, step_index: int, voltage: float, reason: str):
        """
        Records a failed step for later retry.
        """
        pass

    def save_failed_steps(self, filepath: str):
        """
        Writes the failed steps to file (e.g., JSON or CSV).
        """
        pass

    def load_failed_steps(self, filepath: str) -> list:
        """
        Returns a list of previously failed steps to re-run.
        """
        pass
