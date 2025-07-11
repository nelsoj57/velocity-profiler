def encode_step_command(step_index: int, voltage: float, retry_flag=False) -> bytes:
    """
    Builds and serializes a step command message to send over the socket.

    This is for when the controller has precalculated a waveform and this is either telling it to move to a specific index of its waveform array OR to move from its current position to a new voltage.

    """
    pass


def encode_waveform_command(waveform: list, retry_flag=False) -> bytes:
    """
    Builds and serializes a waveform command message to send over the socket.

    Basically just a list of voltages that the controller will send directly to the AO channel.
    This function will do no error checking to make sure the waveform is safe for the DAQ/AO, it is assumed the analyzer has made sure that the waveform is within the safe range of the AO channel and possibly has no discontinuities.
    This function may do error checking to make sure the numpy array provided is for float32 or float64, but that is not guaranteed.

    Is there a way to pass the numpy array in by reference instead of copying it? If so, that would be preferred.
    """
    pass


def decode_step_command(message_bytes: bytes) -> dict:
    """
    Parses an incoming step command message into a dict.

    There will be some communication about versioning in the future, so this will need to be updated to handle that.
    There will be likely some fixed length metadata at the start of the message. Probably a JSON string?

    The metadata will specifiy if its sending "raw" voltages/numpy array or a step index.
    """
    pass


def encode_frequency_response(
    step_index: int, avg_freq: float, stddev: float, valid: bool
) -> bytes:
    """
    Serializes frequency response message from controller to analyzer.
    """
    pass


def decode_frequency_response(message_bytes: bytes) -> dict:
    """
    Parses response from controller into a usable dictionary.

    Probably just a JSON string with metadata and the frequency data.
    The metadata will include the step index?, average frequency, standard deviation, and a validity flag?
    """
    pass
