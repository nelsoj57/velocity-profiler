import nidaqmx
import numpy as np

"""This module contains the DAQ Analog Output (AO) class for controlling voltage ramps AND Functions for interfacing with the Wavemeter and other utility functions"""
# TODO: possibly move utility functions to a separate module if they are not specific to the DAQ AO class


class DaqAO:
    """
    Wraps the NI DAQ analog output channel for ramping the cavity voltage.

    Attributes:
        channel (str): e.g., "Dev1/ao0"
        rate (float): Sample rate in Hz
        task (nidaqmx.Task): The underlying DAQ task
        current_voltage (float): Tracks last known output voltage
    """

    def __init__(
        self, channel: str, rate: float, voltage_limit=5.0, max_dvdt: float = 0.0
    ):
        """Initializes the AO task and sets initial state.

        Args:
            channel (str): The DAQ output channel, e.g., "Dev1/ao0".
            rate (float): The sample rate in Hz.
            voltage_limit (float): Maximum output voltage (default is 5.0 V).
            max_dvdt (float): Maximum allowed voltage change per second (optional).
        """
        self.channel = channel
        self.rate = rate
        self.voltage_limit = voltage_limit  # Maximum output voltage in volts
        self.max_dvdt = max_dvdt  # Maximum allowed voltage change per second

        # Initialize the DAQ task
        self.task = nidaqmx.Task()
        self.task.ao_channels.add_ao_voltage_chan(
            channel, min_val=-voltage_limit, max_val=voltage_limit
        )
        self.task.timing.cfg_samp_clk_timing(rate)
        self.current_voltage = 0.0

    def ramp_to_voltage_by_steps(self, target_voltage: float, steps: int = 100):
        """
        Smoothly ramps the output from current_voltage to target_voltage in 'steps' increments.
        Updates internal current_voltage.

        """
        # TODO: add safety checks to ensure the voltage does not increase/decrease too fast
        # calulate the slope then pass it to the ramp_to_voltage_by_slope function

        slope = (target_voltage - self.current_voltage) / steps
        self.ramp_to_voltage_by_slope(self, target_voltage, slope)
        # TODO: theres probably a better way to do this so num of steps is not calculated in the ramp_by_slope function

    def ramp_to_voltage_by_slope(self, target_voltage: float, slope: float):
        """
        Ramps the output voltage to target_voltage at a specified slope.
        Updates internal current_voltage.

        Args:
            target_voltage (float): The desired output voltage.
            slope (float): The rate of change in volts per second.
        """
        # Ensure the target voltage is within bounds
        if not (abs(target_voltage) <= self.voltage_limit):
            raise ValueError(
                f"Target voltage must be between -{self.voltage_limit} and {self.voltage_limit} V."
            )

        if slope >= self.max_dvdt:
            raise ValueError(
                f"Slope {slope} V/s exceeds maximum allowed rate of change |{self.max_dvdt}| V/s."
            )

        # Calculate the time required to reach the target voltage at the specified slope
        time_to_target = abs(target_voltage - self.current_voltage) / slope

        # Calculate the number of samples needed based on the rate
        n_samples = int(self.rate * time_to_target)

        # Generate the voltage ramp
        voltages = np.linspace(self.current_voltage, target_voltage, n_samples)

        # Write the voltages to the DAQ task
        self.task.write(
            voltages, auto_start=True
        )  # TODO: unsure is auto_start is a good idea if other writes have been made recently

        # Update the current voltage state
        self.current_voltage = target_voltage

    def close(self):
        """Stops and closes the DAQ task."""
        pass

    def is_slope_safe(self, voltages):
        """
        Checks if the voltage slope is within safe limits.

        Args:
            voltages (numpy_array): List of voltage values.
            dt (float): Time step between voltage samples in seconds.
            max_dvdt (float): Maximum allowed voltage change per second.

        Returns:
            bool: True if all slopes are within limits, False otherwise.
        """
        dt = 1 / self.rate  # Assuming rate is in Hz, dt is in seconds
        if (self.current_voltage - voltages[0]) / dt > self.max_dvdt:
            return False  # Initial voltage change is too steep

        if len(voltages) < 2:
            return True  # Not enough data to determine slope

        # Calculate slopes between consecutive voltages
        slopes = np.diff(voltages) / dt
        # Return True if all slopes are within limits, False otherwise

        return np.max(np.abs(slopes)) < self.max_dvdt


# TODO: write a function that allows a precalculated waveform to be written to the DAQ task in chunks based on index

"""UTILITIES:"""


def slice_by_time(waveform, sample_rate, t_start, t_end):
    i_start = int(t_start * sample_rate)
    i_end = int(t_end * sample_rate)
    return slice_by_index_safe(waveform, i_start, i_end)


def slice_by_phase(waveform, frequency, sample_rate, start_phase, end_phase):
    samples_per_cycle = sample_rate / frequency
    i_start = int((start_phase / (2 * np.pi)) * samples_per_cycle)
    i_end = int((end_phase / (2 * np.pi)) * samples_per_cycle)
    return slice_by_index_safe(waveform, i_start, i_end)


def slice_by_index_safe(
    waveform: np.ndarray, start_idx: int, end_idx: int
) -> np.ndarray:
    length = len(waveform)
    start_idx = max(0, start_idx)
    end_idx = min(length, end_idx)
    if start_idx >= end_idx:
        raise ValueError("Invalid slice: start index must be less than end index.")
    return waveform[start_idx:end_idx]


def split_into_chunks(array: np.ndarray, n_chunks: int) -> list[np.ndarray]:
    # TODO: if perfectly even splitting is needed, add logic/propper padding/repeat values to handle that case
    """
    Splits a 1D NumPy array into `n_chunks` nearly equal-sized subarrays.

    Args:
        array: The input 1D NumPy array.
        n_chunks: The number of chunks to split into.

    Returns:
        An array of subarrays, where each subarray is a view or copy of the input.
    """
    return np.array_split(array, n_chunks)


def split_by_chunk_size(array: np.ndarray, chunk_size: int) -> list[np.ndarray]:
    # TODO: if perfectly even splitting is needed, add logic/propper padding/repeat values to handle that case

    """
    Splits a 1D NumPy array into subarrays of fixed `chunk_size`.

    Args:
        array: The input 1D NumPy array.
        chunk_size: Number of elements per chunk.

    Returns:
        A list of subarrays, where each subarray is a slice of the input.
    """
    return [array[i : i + chunk_size] for i in range(0, len(array), chunk_size)]


# TODO: add a version of the above function for splitting by chunck sizes that are determined by phase or time, not just index.


# TODO: write a function that makes sure the voltage does not increase/decrease too fast (e.g., more than 0.5 V per ms)
# Make sure less than 2000 samples are sent at any given time and the task is configured as finite and You’re using wait_until_done()
# Make sure the voltage steps are much less than 100 mV/sample
# TODO: TODO: TODO: Figure out the maximum rate the M-squared (and maybe even locking mechanism) can handle to make sure the voltage does not increase/decrease more than that limit
