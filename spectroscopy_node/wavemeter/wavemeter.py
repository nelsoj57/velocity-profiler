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
