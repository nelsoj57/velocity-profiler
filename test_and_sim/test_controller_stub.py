def start_mock_controller_server(host: str, port: int):
    """
    Starts a fake server that mimics the behavior of the real controller.
    Responds with simulated frequency data to any incoming step command.
    """
    pass


def generate_mock_frequency_response(voltage: float, noise: float = 0.5e6) -> dict:
    """
    Returns a frequency response simulating wavemeter data for a given voltage input.
    """
    pass


def run_server_loop():
    """
    Continuously listens for commands and returns mock responses.
    Useful for testing analyzer end-to-end without hardware.
    """
    pass
