"""
1. Contains the Wavemeter class, whose attributes represents the properties of the wavemeter device and methods represent DLL calls.
2. Containes the SampleWavemeter class which has a Wavemeter object and calls the methods of the Wavemeter Class and takes and processes the data #TODO: come up with a better name.
    - This is a base class (possibly abstract) that can be extended for different sampling/sweeping strategies
    - derived classes may include:
        - SampleWavemeterSingle: for single sampling (poll/request based sampling)
        - TimedSampleing: taking a sample for a fixed time period
            - There could be a class derived from this one for delayed sampling where the sampling starts after a specified delay or at a specified time
3. Possibly: Maybe a different class should hold a SampleWavemeter object and contains logic for starting and stopping samples and holding/processing the data
    -That would mean that the Sample Class would only have attributes and methods related to sampling and not data processing.



ACTUALLY this is how it will work:
1. Contains the Wavemeter class, whose attributes represents the properties of the wavemeter device and methods represent DLL calls.
2. A WavemeterSample class which represents a single period of sampling data from the wavemeter.
    - The attributes will contain:
        - start_time: the time at which the sampling period started
        - end_time: the time at which the sampling period ended
        - data: the actual sampled data (could be a list of values, etc.)
        - metadata: any additional information about the sample (e.g., settings used, etc.)
            - Methodology used to gather data (e.g., single sample, timed sampling, delayed sampling, etc.)
            - The actual DLL method used to gather the data
            - Possibly the type of data being sampled (e.g., wavelength, frequency, pressure, temperature, etc.) (although it'll probably always be wavelength/frequency for our uses)

3. An outside function (possibly the main function of the main file of this module) or class (probably class) is responsible for taking commands and marshalling those commands to the SampleWavemeter class...
...which in turn marshalls those commands to the Wavemeter class methods to perform the actual sampling and data gathering.
    - This is a business logic class that holds the Wavemeter object and SampleWavemeter object and contains methods for starting and stopping samples, holding/processing the data, etc?
We'll call this class WavemeterController or WavemeterManager or WavemeterSampleManager something similar.

"""

"""
Wavemeter Class Attributes:
    - api: the DLL API object used to call the wavemeter methods
Wavemeter Class Methods:
    - get_frequency: retrieves the current frequency from the wavemeter
    - get_wavelength: retrieves the current wavelength from the wavemeter
    - aquire_frequencies_for_duration
    - frequency_callback_handler
    - get_frequency_by_event: waits for a frequency event and retrieves the frequency
"""

"""
WavemeterSample Class Attributes:
    - start_time: the time at which the sampling period started
    - end_time: the time at which the sampling period ended
    - data/buffer: the actual sampled data (could be a list of values, etc.)
    - current_buffer_size: the current size of the data buffer (if applicable) (only applicable if the data structure is a numpy array thats being filled gradually)
    - buffer_capacity: the maximum size of the data buffer (if applicable) (only applicable if the data structure is a numpy array thats being filled gradually)

    - continuous_sampling: a boolean indicating whether the sampling is done as often as possible (run in a continuous loop) or at fixed intervals
    - sampling_interval: the interval at which the sampling is done (if applicable) (only applicable if the sampling is done at fixed intervals)

    - aquisition_method/DLL_method: the method used to gather the data (e.g., get_frequency, get_wavelength, etc.)

WavemeterSample Class Methods:
    - start_sampling: starts the sampling process
    - stop_sampling: stops the sampling process (only useful if sampling can be done continuously and interrupeted (may require sampling to happen in a separate thread))
    - ?process_data: processes the sampled data (e.g., averaging, filtering, etc.)
    - ?get_sample_data: retrieves the sampled data
    - ?get_metadata: retrieves the metadata associated with the sample
    - clear_data/reset_data: clears the sampled data buffer


Derived Classes?:
    - ContinousDurationSample: polls the get_frequency method at a fixed interval (or as often as possisble?) for a specified duration and stores the data in the buffer
    - SingleSample: takes a single sample by calling the get_frequency method once and stores the data in the buffer
    - TimedSample: takes samples at a fixed interval for a specified duration and stores the data in the buffer
    - DelayedSample: takes samples at a fixed interval for a specified duration after a specified delay and stores the data in the buffer
    - EventDrivenSample: takes samples when a frequency event is triggered and stores the data in
    - CallbackSample: takes samples when a frequency event is triggered and processes the data using a callback function

    ^Ignore the above, this is how it will actually work:
    - SampleUntilStop: continuously sample until commanded to stop?, storing data in a buffer
        - SampleEveryNSeconds: sample every N seconds, storing data in a buffer, until stopped or for a specified duration
    - SampleForDuration: sample for a specified duration, storing data in a buffer

    ^ALSO ignore the above, this is how it will possibly actually work:
    - A meta class that holds a Wavemeter object and a SampleWavemeter object will be used for sampling. 
    - This class will have branching logic for different sampling strategies? 
        - Like arguments/attributes of this class may include: continous sampling: Bool, every

    Is there a way for the a SampleWavemeter derived class to have multiple variations of sampling strategies?
        - Like can I have a TimedSample class that can also be used for delayed sampling by passing a delay parameter to the constructor?
        - Or can I have a TimedSample class that in one variant uses a the callback method and in the other variant uses the polling method?
        - TODO: CAN I DO THIS BY: having the "Wavemeter DLL function of interest" be passed as a function pointer/ parameter to the SampleWavemeter class constructor???
        - Like can I pass a pointer to a method of the Wavemeter class to the SampleWavemeter class constructor and then call that method from within the SampleWavemeter class?

TODO: TODO: TODO:
Actually have a Class that has both a Wavemeter object and a SampleWavemeter object as attrributes:
    - Then the Sample Class ONLY represents the sampling strategy and possibly the data processing strategy.
    - The Wavemeter Class ONLY represents the actual wavemeter device and its methods.

    - The Class that holds both uses the Sample object to inform how to poll from/use the Wavemeter object to gather data.

This can be called the WavemeterDataManager or WavemeterController or WavemeterSampleManager or something similar.
This class CAN use the Call the Wavemeter class methods directly, but it should use the SampleWavemeter class methods to gather data and process it.?


"""
"""
TODO: TODO: TODO: TODO: TODO: This is how it will actually work:
Classes:
1. Wavemeter: Represents the wavemeter device and its DLL methods.
2. SamplePoint: A dataclass that represents a single sample point with attributes like timestamp, value, and metadata (if needed)
3. AcquisitionStrategy: a class that overloads the __call__ method to implement different sampling strategies:
    - The __call__ method will take a Wavemeter object and return a single SamplePoint object? Or maybe a list of SamplePoint objects or maybe just a float that something else will use to create a SamplePoint object.
    - the aquisition strategy must have this signature: Callable[[Wavemeter], float]
4. BaseScheduler: A class that manages the scheduling of sampling tasks. It can take an AcquisitionStrategy and a Wavemeter object and run the sampling strategy at a specified interval or for a specified duration.
    - An Abstract Base Class that defines the interface for scheduling sampling tasks.
    - Example derived classes:
        - IntervalScheduler: Runs the sampling strategy at a fixed interval.
        - DurationScheduler: Runs the sampling strategy for a specified duration.
        - 
5. SampleSession: The session owns the life-cycle.If you need many sessions in parallel, wrap them in a higher-level WavemeterManager; otherwise SampleSession itself can be “the controller”.
"""
import sys, weakref
from abc import ABC

# wlmData.dll related imports
import wlmConst
import wlmData


# Set the callback thread priority here:
CALLBACK_THREAD_PRIORITY = 2  # TODO: look into what value I should use here. ALSO move this to a config file if needed.


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

    _CALLBACK_TYPE = (
        wlmData.CALLBACK_TYPE
    )  # Define the callback type for the wavemeter API

    def __init__(self):
        """
        Initializes the WavemeterWS7 object.
        This may include loading the DLL or API and setting up the handle.
        """
        try:
            self._api = wlmData.LoadDLL()
            # self._api = wlmData.LoadDLL('/path/to/your/libwlmData.so')
        except OSError as err:
            sys.exit(f"{err}\nPlease check if the wlmData DLL is installed correctly!")

        # Check the number of WLM server instances
        if self._api.GetWLMCount(0) == 0:
            sys.exit("There is no running WLM server instance.")

        # self_ref = weakref.ref(
        #     self
        # )  # Keep a weak reference to self to avoid circular references

    def get_frequency(self) -> float:
        """
        Returns the current laser frequency in Hz (or MHz if preferred).
        """
        frequency = self._api.GetFrequency(0.0)
        match frequency:  # TODO: replace with a cleaner/briefer way to handle errors
            case wlmConst.ErrWlmMissing:
                raise WavemeterWS7Exception("WLM inactive")
            case wlmConst.ErrNoSignal:
                raise WavemeterWS7NoSignalException
            case wlmConst.ErrBadSignal:
                raise WavemeterWS7BadSignalException
            case wlmConst.ErrLowSignal:
                raise WavemeterWS7LowSignalException
            case wlmConst.ErrBigSignal:
                raise WavemeterWS7HighSignalException

        return frequency

    @staticmethod
    @wlmData.CALLBACK_TYPE
    def frequency_callback_handler(event_type, time_stamp, frequency):
        # TODO: change mode to be a more descriptive name, like event_mode or event_type
        """
        Callback function to handle frequency updates from the wavemeter.
        This function is called by the wavemeter API when a frequency update event occurs.

        Args:
            event_type: The type of the event (e.g., cmiFrequency1, cmiFrequency2).
            time_stamp: An integer value associated with the event.
            frequency: The frequency value in Hz.
        """
        match event_type:
            case wlmConst.cmiFrequency1:
                pass
            # TODO: Send the data somewhere
            # TODO: you could have a buffer/array/queue that belongs to the WavemeterWS7 object that holds the frequency data and then have a method to retrieve that data

            case wlmConst.cmiFrequency2:
                pass

            case _:
                return  # Ignore other modes TODO: see if return is the right/fastest way to ignore

    # def start_streaming(self):
    #     """
    #     Starts streaming frequency data from the wavemeter.
    #     """
    #     # Create data structure to hold frequency data

    #     # Install callback function
    #     self._api.Instantiate(
    #         wlmConst.cInstNotification,
    #         wlmConst.cNotifyInstallCallback,
    #         self.frequency_callback_handler,
    #         CALLBACK_THREAD_PRIORITY,
    #     )

    # def stop_streaming(self):
    #     """
    #     Stops streaming frequency data from the wavemeter.
    #     """
    #     # Uninstall callback function
    #     self._api.Instantiate(
    #         wlmConst.cInstNotification, wlmConst.cNotifyRemoveCallback, None, 0
    #     )

    def _register_callback(self, cb: _CALLBACK_TYPE) -> None:
        """
        Registers the frequency callback function with the wavemeter API.
        This function is called to set up the callback for frequency updates.
        """
        self._api.Instantiate(
            wlmConst.cInstNotification,
            wlmConst.cNotifyInstallCallback,
            cb,
            CALLBACK_THREAD_PRIORITY,
        )

    def _unregister_callback(self) -> None:
        """
        Unregisters the frequency callback function from the wavemeter API.
        This function is called to remove the callback for frequency updates.
        """
        self._api.Instantiate(
            wlmConst.cInstNotification, wlmConst.cNotifyRemoveCallback, None, 0
        )


"""
Notes/ideas for streaming data:
    Possible approaches:
    1. Unistall the callback function every time a frequency event occurs.
        - This would mean that the callback function is only called once per frequency event and then uninstalled.
        - Then the callback function could just update a value and the some method could be called to retrieve that value
        - Then this method follows the AquisitionStrategy pattern required
    2. See if we can relax the AquisitionStrategy pattern so we can return a list of floats instead of a single float.
        - Then the get_frequency method could return a list containing just a single float value.
        - Then the callback function could just append the frequency value to a list and then when streaming is stopped, the list can be returned.
    3. Add an attribute to the WavemeterWS7 class that holds a list of frequency values and then the callback function can just append the frequency value to that list. (original idea)
    4. Add an attribute to the WavemeterWS7 class that holds a just the latest frequency value and use a yielding/generator function somehow to return the latest frequency value when requested.
        - This may require another thread or something listening for frequency events or updates to the latest frequency value. Which is highly redundant since the callback function is already doing that.
        - Or maybe the callback function updates the latest frequency value and then calls a method that yields the latest frequency value?

    6? Maybe the scheduler class handles Instantiate and uninstalling the callback function?

    
Idea Scheduler Outline:
    The callback function is defined in the Scheduler class?
    start():
        - Instantiates the callback function
        - When the callback function is called, it updates/appends a value in the scheduler class by means of weak reference or a global variable
        - So no AcquisitionStrategy is Used,
        TODO: So make the AcquisitionStrategy an optional attribute of the Scheduler and Session classes?

    stop():
        - Uninstantiates the callback function

    TODO: reference ChatGPT conversation for more ideas on how to implement this.
"""


class BaseScheduler(ABC):
    # TODO: Make the AcquisitionStrategy an optional attribute of the Scheduler and Session classes
    pass


class EventDrivenScheduler(BaseScheduler):
    """
    An EventDrivenScheduler that uses the WavemeterWS7 class to handle frequency events.
    This scheduler will use the callback function to update the frequency data.
    """

    def __init__(self, wavemeter: WavemeterWS7):
        self.wavemeter = wavemeter
