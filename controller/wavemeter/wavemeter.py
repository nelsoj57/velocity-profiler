from ctypes import c_long, c_double, byref  # TODO: remove if unused
import time  # TODO: remove if unused
import sys
import numpy as np

# wlmData.dll related imports
import wlmConst
import wlmData

# Set the data acquisition time (sec) here:
DATA_ACQUISITION_TIME = (
    5  # TODO: possibly move this to a config file. ALSO remove if unused
)

# Set the callback thread priority here:
CALLBACK_THREAD_PRIORITY = 2  # TODO: look into what value I should use here. ALSO move this to a config file if needed.

# Load wlmData library. If needed, adjust the path by passing it to LoadDLL()!
try:
    dll = wlmData.LoadDLL()
    # dll = wlmData.LoadDLL('/path/to/your/libwlmData.so')
except OSError as err:
    sys.exit(f"{err}\nPlease check if the wlmData DLL is installed correctly!")

DLL_PATH = "wlmData.dll"  # TODO: this may not be needed if LoadDLL() works correctly
# TODO: I have 2 options here:
"""
1. Use a callback mechanism to get frequency updates (this may only be able to get the wavelength, not frequency). (the manual is not clear on this)
2. Use an event polling mechanism to get frequency updates.

"""


# TODO: remove if theres a cleaner way to handle exceptions (these come from wavemeter_ws7.py)
class WavemeterWS7Exception(Exception):
    pass


class WavemeterWS7BadSignalException(WavemeterWS7Exception):
    pass


class WavemeterWS7NoSignalException(WavemeterWS7Exception):
    pass


class WavemeterWS7LowSignalException(WavemeterWS7Exception):
    pass


class WavemeterWS7HighSignalException(WavemeterWS7Exception):
    pass


class WavemeterWS7:
    """
    Wraps access to the wavemeter DLL or API for polling frequency data.

    Attributes:
        handle (object): Internal DLL or API handle (optional depending on library)
    """

    def __init__(self, buffer: np.ndarray):
        """Initializes wavemeter connection (if required by API)."""
        self.buffer = buffer
        self.buffer_idx = 0  # Index for the final used position in the buffer
        try:
            self.api = wlmData.LoadDLL()
            # self.api = wlmData.LoadDLL('/path/to/your/libwlmData.so')
        except OSError as err:
            sys.exit(f"{err}\nPlease check if the wlmData DLL is installed correctly!")

        # Check the number of WLM server instances
        if self.api.GetWLMCount(0) == 0:
            sys.exit("There is no running WLM server instance.")

        # TODO: possibly add version information here

    def get_frequency(self) -> float:
        """
        Returns the current laser frequency in Hz (or MHz if preferred).
        """
        frequency = self.api.GetFrequency(0.0)
        # TODO: replace with match statement for better readability
        if frequency == wlmConst.ErrWlmMissing:
            raise WavemeterWS7Exception("WLM inactive")
        elif frequency == wlmConst.ErrNoSignal:
            raise WavemeterWS7NoSignalException
        elif frequency == wlmConst.ErrBadSignal:
            raise WavemeterWS7BadSignalException
        elif frequency == wlmConst.ErrLowSignal:
            raise WavemeterWS7LowSignalException
        elif frequency == wlmConst.ErrBigSignal:
            raise WavemeterWS7HighSignalException

        return frequency

    # def average_frequency(
    #     self, duration: float = 2.0, poll_rate: float = 10.0
    # ) -> tuple:
    #     """
    #     Samples frequency at poll_rate (Hz) for duration (s).
    #     Returns: (average_frequency, std_dev, num_samples)
    #     """
    #     pass

    def get_buffer_stats(self):
        """
        Returns statistics about the frequencies inside the buffer.
        Assuming buffer is a list of tuples (time_stamp, frequency)

        """
        if self.buffer_idx == 0:
            return None  # No valid measurements available

        # Compute basic statistics
        # TODO: change this next line if time_stamp is not included in the buffer
        frequencies = [entry[1] for entry in self.buffer[: self.buffer_idx]]
        avg_freq = np.mean(frequencies)
        std_dev = np.std(frequencies)
        num_samples = len(frequencies)

        return avg_freq, std_dev, num_samples

    def aquire_frequencies_for_duration(self, duration: float = DATA_ACQUISITION_TIME):
        """
        Aquire frequencies for a given duration in seconds.
        This function will block until the duration is reached or an error occurs.

        Args:
            duration (float): Duration in seconds to acquire frequencies.

        Returns:
            None
        """
        # Reset the buffer index before starting
        self.reset_buffer()

        # Install callback function
        dll.Instantiate(
            wlmConst.cInstNotification,
            wlmConst.cNotifyInstallCallback,
            self.frequency_callback_handler,
            CALLBACK_THREAD_PRIORITY,
        )

        # Give a little time for data acquisition #TODO: I'm not sure if this is the right way to do this.
        """Because I'm not sure if this will block until the callback is called, or only call the callback once. 
        What I want to do is have the callback called as many times as possible during the duration"""
        time.sleep(DATA_ACQUISITION_TIME)

        # Remove callback function
        dll.Instantiate(
            wlmConst.cInstNotification, wlmConst.cNotifyRemoveCallback, None, 0
        )

    # The callback-based frequency update function
    @wlmData.CALLBACK_TYPE
    def frequency_callback_handler(self, mode, intval, dblval):
        # TODO: change mode to be a more descriptive name, like event_mode or event_type
        """
        Callback function to handle frequency updates from the wavemeter.
        This function is called by the wavemeter API when a frequency update event occurs.

        Args:
            mode: The mode of the event (e.g., cmiFrequency1, cmiFrequency2).
            intval: An integer value associated with the event.
            dblval: The frequency value in Hz.
        """
        match mode:
            case wlmConst.cmiFrequency1:
                time_stamp = intval
                frequency = dblval
                self.buffer[self.buffer_idx] = (time_stamp, frequency)
                self.buffer_idx += 1  # increment the buffer index for the next entry

            case wlmConst.cmiFrequency2:
                time_stamp = intval
                frequency = dblval
                self.buffer[self.buffer_idx] = (time_stamp, frequency)
                self.buffer_idx += 1
            case _:
                return  # Ignore other modes TODO: see if return is the right/fastest way to ignore

    def reset_buffer(self):
        """
        Resets the buffer index to 0, effectively clearing the buffer.
        """
        self.buffer_idx = 0
        # self.buffer.fill((0, 0)) TODO: this might not be necessary since we only access the buffer up to buffer_idx

    # TODO: only keep if needed, IF the wavemeter API does not provide a way to get frequency directly through callbacks
    def wavelength_to_frequency(self, wavelength: float) -> float:
        """
        Converts a wavelength in nm to frequency in Hz.
        Wavelength is expected in nanometers (nm).

        Args:
            wavelength (float): Wavelength in nanometers.

        Returns:
            float: Frequency in Hz.
        """
        # Speed of light in m/s
        c = 299792458.0
        # Convert wavelength from nm to m
        wavelength_m = wavelength * 1e-9
        frequency = c / wavelength_m
        return frequency


# The event-based frequency update function
# TODO: if keeping this, move it inside the WavemeterWS7 class
def wait_for_frequency_update(wlm, channel=1, timeout=5.0):
    """
    Wait for a frequency update event on a specific wavemeter channel (1 or 2),
    and return the frequency in Hz. Handles signal errors gracefully.

    Args:
        wlm: an instance of WavemeterWS7.
        channel (int): 1 or 2.
        timeout (float): how long to wait for the event in seconds.

    Returns:
        float: Frequency in Hz, or None if timeout occurred.
    """
    if channel not in (1, 2):
        raise ValueError("Only channels 1 and 2 are supported.")

    # Map channel to event mode constant
    mode_target = wlmConst.cmiFrequency1 if channel == 1 else wlmConst.cmiFrequency2

    mode = c_long()
    intval = c_long()
    dblval = c_double()

    t_start = time.time()

    while True:
        # Timeout check
        if time.time() - t_start > timeout:
            print("Timeout: no frequency event received.")
            return None

        # Block until ANY event happens
        # TODO: make sure I don't need to check the return value here
        wlm.api.dll.WaitForWLMEvent(byref(mode), byref(intval), byref(dblval))

        # Only proceed if it's the desired frequency event
        if mode.value != mode_target:
            continue

        # Attempt to get frequency safely
        try:
            freq = wlm.get_frequency()
            return freq  # success
        # TODO: handle exceptions in a way that allows retrying and actually makes sense for this application
        except wlm.WavemeterWS7NoSignalException:
            print("No signal on channel.")
        except wlm.WavemeterWS7LowSignalException:
            print("Signal too low.")
        except wlm.WavemeterWS7HighSignalException:
            print("Signal too high.")
        except wlm.WavemeterWS7BadSignalException:
            print("Signal corrupted.")
        except Exception as e:
            print("Unexpected error reading frequency:", e)

        # If we got the right event but failed to get frequency, wait briefly and retry
        time.sleep(0.01)


def calc_max_num_data_points(duration: float) -> int:
    """
    Calculate the maximum number of data points that can be collected in the given duration,
    given

    Args:
        duration (float): Duration in seconds.

    Returns:
        int: Maximum number of data points.
    """
    return int(duration * wlmConst.WLM_MAX_MEASUREMENT_RATE)
