import sys, weakref
import queue, threading, time
from typing import Optional, Callable, Protocol, TYPE_CHECKING
from abc import ABC, abstractmethod
from dataclasses import dataclass, field

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

        self._cb_cfunc = None  # Callback function for frequency updates

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

    def _register_callback(self, cb: _CALLBACK_TYPE) -> None:
        # TODO: add CALLBACK_THREAD_PRIORITY as an argument to this method
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

    # ---------Public Helper Methods-------------

    def register_frequency_callback(
        self, cb: Callable[[int, int, float], None]
    ) -> None:
        """
        Public method to register a frequency callback function.
        This method is used to set up the callback for frequency updates.

        Args:
            cb (_CALLBACK_TYPE): The callback function to register.

        DOCUMENTATION:
        Order of Operations:
        1. An event occurs in the wavemeter (e.g., a frequency update).
        2. The wavemeter API calls the _wrapper function with the event data.
            - The _wrapper function is NOT a bound method (it does not have a hidden self argument) so it has the proper C-style callback signature.
        3. The _wrapper function calls the user-defined callback function (cb) (which MAY be a bound method with a hidden self argument) with the event data.
        4. The user-defined callback function processes the event data as needed.
        5. Repeat
        """

        def _wrapper(mode, intval, dblval):
            """
            A wrapper function to call the user-defined callback with the frequency value.

            """
            cb(mode, intval, dblval)
            # convert the cb signature to match the wavemeter callback signature

        self._cb_cfunc = self._CALLBACK_TYPE(_wrapper)
        # Register the callback function with the wavemeter API
        self._register_callback(self._cb_cfunc)

    def unregister_frequency_callback(self) -> None:
        """
        Public method to unregister the frequency callback function.
        This method is used to remove the callback for frequency updates.
        """
        if (
            self._cb_cfunc is not None
        ):  # TODO: make sure this ^ wont ever happen if the callback is registered
            self._unregister_callback()
            self._cb_cfunc = None
