import nidaqmx
from nidaqmx.stream_readers import AnalogSingleChannelReader
import time
import numpy as np


class DaqAI:
    """
    Wraps the NI DAQ analog input channel for photodiode signal acquisition.

    Attributes:
        channel (str): e.g., "Dev2/ai0"
        rate (float): Sampling rate in Hz
        chan_buffer_size (int): Number of samples per read
        task (nidaqmx.Task): Internal DAQ task object
    """

    # TODO: if going to have have DAQAI always have a chan_buffer_size so that is exactly the width of the samples collected over the averaging period,then...
    # maybe we shouldn't set the timing in the constructor, but rather in the read_after_stabilization method?
    # because the buffer size may change depending on how long the averaging period is, and we want to be able to read that many samples
    # Like it should be = int(self.rate * avg_duration_sec)
    def __init__(self, channel: str, rate: float, chan_buffer_size: int):
        """Initializes the DAQ input task."""
        self.channel = channel
        self.rate = rate
        self.chan_buffer_size = chan_buffer_size
        self.task = nidaqmx.Task()
        self.task.ai_channels.add_ai_voltage_chan(channel, min_val=-5.0, max_val=5.0)
        self.task.timing.cfg_samp_clk_timing(rate, samps_per_chan=chan_buffer_size)

        # Reader + buffer
        reader = AnalogSingleChannelReader(self.task.in_stream)
        buffer = np.zeros(1000, dtype=np.float64)

    def read_samples(self) -> list:
        """
        Reads a buffer of photodiode voltage samples.
        Returns list of floats.
        # TODO: have this return a numpy array instead?
        """
        pass

    def read_after_stabilization(self, wait_sec=0.5, avg_duration_sec=2.5):
        """
        Waits for a stabilization period, then restarts the task and
        reads a fresh buffer of data for averaging.

        Returns:
            mean, stddev, n_samples #TODO: n_samples may not be needed. TODO: possibly make this a tuple
        """
        self.task.stop()  # clear any previous data on the buffer
        time.sleep(wait_sec)  # wait for frequency/voltage stabilization
        self.task.start()  # start the task to begin reading

        n_samples = int(
            self.rate * avg_duration_sec
        )  # Should be equal to chan_buffer_size
        samples = self.task.read(number_of_samples_per_channel=n_samples)
        # TODO: FINISH FUNCTION

    def average_intensity(self, samples: list) -> tuple:
        """
        Returns (mean, stddev, n_samples) from photodiode samples.
        """
        pass

    def is_stable(self, stddev: float, threshold: float) -> bool:
        """
        Checks if intensity stddev is below a given stability threshold.
        """
        pass

    def close(self):
        """Stops and closes the DAQ task."""
        pass


# TODO: delete above class if not needed
# daq_base.py
class DaqAIBase:
    """
    General-purpose base class for AI DAQ tasks.
    Designed to be subclassed for domain-specific behavior.
    """

    def __init__(self, channel: str, rate: float):
        self.channel = channel
        self.rate = rate
        self.task = nidaqmx.Task()
        self.task.ai_channels.add_ai_voltage_chan(channel, min_val=-10.0, max_val=10.0)
        self.reader = AnalogSingleChannelReader(self.task.in_stream)
        self._buffer = None  # subclasses will allocate this

    def configure_timing(self, n_samples: int):
        self.task.timing.cfg_samp_clk_timing(
            rate=self.rate,
            samps_per_chan=n_samples,
            sample_mode=nidaqmx.constants.AcquisitionType.FINITE,
        )

    def read_into_buffer(self, n_samples: int):
        """Allocates and fills internal buffer with n_samples."""
        if self._buffer is None or self._buffer.shape[0] != n_samples:
            self._buffer = np.zeros(n_samples, dtype=np.float64)
        self.reader.read_many_sample(
            self._buffer, number_of_samples_per_channel=n_samples
        )

    def read_into_list(self, n_samples: int) -> list:
        """
        Reads samples into a list.
        Returns a list of floats.
        """
        return self.task.read(number_of_samples_per_channel=n_samples)

    def close(self):
        self.task.close()


class PhotodiodeDaq(DaqAIBase):
    """
    DAQ interface tailored to photodiode voltage averaging for spectroscopy scans.
    """

    def __init__(self, channel: str, rate: float, sampling_time: float = 2.5):
        """
        Initializes the photodiode DAQ task with a specific channel and rate.
        Optionally sets a buffer size for reading samples.
        """
        super().__init__(channel, rate)
        self.n_samples = int(rate * sampling_time)
        self.task.timing.cfg_samp_clk_timing(rate, samps_per_chan=self.n_samples)
        # In the photodiode case, the DAQ hardware buffer and the buffer we read into are the same size.
        # This is because we want to get all the samples we need to average in one read operation.
        self._buffer = np.zeros(self.n_samples, dtype=np.float64)

    def read_after_stabilization(self, wait_sec=0.5):
        self.task.stop()
        time.sleep(wait_sec)

        self.configure_timing(self.n_samples)

        self.task.start()
        self.read_into_buffer(self.n_samples)
        self.task.stop()

        return self.get_buffer_stats()

    # def average_intensity(self, samples):
    #     return float(np.mean(samples)), float(np.std(samples)), len(samples)
    def get_buffer_stats(self) -> tuple:
        """
        Returns (mean, stddev, n_samples) from the internal buffer.
        """
        # if self._buffer is None:
        #     raise ValueError("Buffer is not initialized. Call read_into_buffer first.")

        # mean = float(np.mean(self._buffer))
        # stddev = float(np.std(self._buffer))
        # return mean, stddev
        return np.mean(self._buffer), np.std(self._buffer)

    def is_stable(self, stddev: float, threshold: float) -> bool:
        return stddev < threshold
