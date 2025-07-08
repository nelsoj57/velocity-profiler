"""
Notes on possible messages ordering:
| Message        | Sender → Receiver     | When                                    |
| -------------- | --------------------- | --------------------------------------- |
| `READY`        | Analyzer → Controller | After processing last measurement       |
| `ARM`          | Controller → Analyzer | When both are ready                     |
| `ACK` (`ARM`)  | Analyzer → Controller | After buffer setup complete             |
| `TRIG`         | Controller → Analyzer | 100–150 ms before desired start         |
| `ACK` (`TRIG`) | Analyzer → Controller | After setting local `t0`                |
| `FIN`          | Analyzer → Controller | After local acquisition and calculation |
| `RAW` (opt)    | Analyzer → Controller | After `FIN`, if raw data needed         |
| `ACK` (`FIN`)  | Controller → Analyzer | Confirms receipt of stats               |
| `STEP`         | Controller → Analyzer | Voltage command and metadata            |
| `ACK` (`STEP`) | Analyzer → Controller | Confirms it received new setpoint       |

Additional notes:
- The way Photodiode data is synced with Wavemeter data would be sending a `TRIG` command:
- Basically they would have to sync up their clocks on the LAN then say we're both going to start recording at this set future time.

"""

# TODO: possibly move this to analyzer module. Probably not. I actually think its in the right place
import zmq


class ControllerServer:
    """
    TCP/ZeroMQ server that receives step commands from the analyzer and returns frequency data.

    Attributes:
        socket (object): The network socket
        is_running (bool): Control flag for the main loop
    """

    def __init__(self, bind_ip: str = "0.0.0.0", port: int = 5555):
        """Sets up the server socket and prepares to listen."""

        self.bind_ip = bind_ip  # TODO: maybe remove this and port as attributes, since they are only used in the constructor
        self.port = port
        self.context = zmq.Context()
        self.socket = self.context.socket(zmq.REP)
        # "0.0.0.0" to accept connections from any local IP TODO: Check if this is a security risk
        self.socket.bind(f"tcp://{bind_ip}:{port}")
        self.is_running = True  # Control flag for the main loop TODO: may be unnecessary if using a context manager

    #  Enables the with statement for safe socket management
    def __enter__(self):
        """Enables use as a context manager for safe socket closing."""
        return self

    def __exit__(
        self, exc_type, exc_value, traceback
    ):  # TODO: fix signature (remove exc_type, exc_value, traceback?)
        """Closes socket on exit."""
        self.socket.close()
        self.context.term()

    def close(self):
        """Explicitly closes the socket and terminates the context."""
        self.__exit__(None, None, None)

    # TODO: remove this method if not needed
    # def command_loop(self):
    #     """
    #     Generator that waits for and yields incoming step command messages.
    #     Yields dicts with: voltage, step_index, retry_flag, etc.
    #     """
    #     pass

    def send_response(
        self, step_index: int, avg_freq: float, stddev: float, valid: bool
    ):
        """
        Sends a structured frequency response back to the analyzer.
        Includes metadata like step index, status, etc.
        """
        pass

    # TODO: could also use a dictionary to pass the response data so that it can be extended in the future, like this:
    """
    def send_response(self, response_dict):
    self.socket.send(encode_frequency_response(**response_dict))
    """
