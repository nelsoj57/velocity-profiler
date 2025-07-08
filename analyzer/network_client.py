import zmq
import core.protocol  # TODO: possibly only import the functions used instead of the whole module
from core.protocol import (
    encode_step_command,
    decode_step_command,
    encode_frequency_response,
    decode_frequency_response,
)


class AnalyzerClient:
    """
    Client that connects to the controller and manages command/response exchange.

    Attributes:
        socket (object): The TCP or ZMQ client socket
    """

    def __init__(self, server_ip, port: int):
        """Establishes socket connection to the controller."""
        # self.host = host
        self.server_ip = server_ip
        self.port = port
        self.context = zmq.Context()
        self.socket = self.context.socket(zmq.REQ)
        self.socket.connect(f"tcp://{server_ip}:{port}")

    def send_step_command(self, step_index: int, voltage: float, retry: bool = False):
        """
        Sends a voltage step command to the controller.
        Includes metadata like retry flag and step index.
        """
        message = encode_step_command(step_index, voltage, retry)
        self.socket.send(message)

    def receive_response(self) -> dict:
        """
        Waits for and returns a response message from the controller.
        Expected keys: avg_frequency, stddev, valid, step_index
        """
        response = self.socket.recv()
        return decode_frequency_response(response)

    def close(self):
        """Closes the client socket."""
        self.socket.close()
        self.context.term()

    # TODO: add necessary dunder methods for using "with" statement
