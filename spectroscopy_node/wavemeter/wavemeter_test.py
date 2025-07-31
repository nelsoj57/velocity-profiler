import threading
import time
import pytest
from typing import Generator
from spectroscopy_node.wavemeter import wlmConst
from spectroscopy_node.wavemeter.wavemeter import (
    WavemeterWS7,
    IntervalScheduler,
    SamplePoint,
    WavemeterWS7Exception,
)


def fake_get_frequency(self) -> Generator[float, None, None]:
    frequency = 10000.0
    while True:
        yield frequency
        frequency += 0.1  # Simulate changing frequency


def fake_get_timestamp() -> Generator[float, None, None]:
    """Simulate a timestamp generator."""
    time = 90000  # milliseconds
    while True:
        yield time
        time += 1


# This function will simulate an event that triggers the callback function
def simulate_callback_events(
    wavemeter: WavemeterWS7, stop_event: threading.Event, interval: float = 0.1
):
    """
    wavemeter: WavemeterWS7 instance to call the callback on.
    stop_event: A threading.Event to control when to stop the simulation.
    interval: Time in seconds between simulated callback events.

    """
    # simulates waiting for the callback function to be set/intialized/registered
    while not hasattr(wavemeter, "_cb_cfunc") or wavemeter._cb_cfunc is None:
        if stop_event.is_set():
            return
        time.sleep(0.05)

    # When callback function is set, the above loop will exit

    # Until the callback function is unregistered, periodically call it with new data
    fake_mode = wlmConst.cmiFrequency1

    while not stop_event.is_set():
        # Simulate different modes for the callback
        if fake_mode == wlmConst.cmiFrequency1:
            fake_mode = wlmConst.cmiFrequency2
        if fake_mode == wlmConst.cmiFrequency2:
            fake_mode = wlmConst.cmiVersion  # This should not be used by the callback function, so a value should be missing every third time

        # fake_intval = int(time.time() * 1000)  # the current time in milliseconds
        fake_intval = fake_get_timestamp()
        fake_dblval = wavemeter.get_frequency()  # Use the fake get_frequency

        # Call the callback function with the fake data
        wavemeter._cb_cfunc(fake_mode, fake_intval, fake_dblval)

        time.sleep(interval)


@pytest.fixture
def test_wavemeter(monkeypatch):
    # Create a fake WavemeterWS7 instance
    wm = WavemeterWS7()

    # Monkeypatch the methods that call the DLL to use fake implementations
    monkeypatch.setattr(wm, "get_frequency", fake_get_frequency)

    # Override _register_callback to just store the callback.
    monkeypatch.setattr(
        wm, "_register_callback", lambda self, cb: setattr(self, "_cb_cfunc", cb)
    )
    # Override _unregister_callback to set the callback to None.
    monkeypatch.setattr(
        wm, "_unregister_callback", lambda self: setattr(self, "_cb_cfunc", None)
    )

    return wm


# @pytest.fixture
# def interval_scheduler():
#     return IntervalScheduler()

# @pytest.fixture
# def sample_point():
#     return SamplePoint()

# TESTING WavemeterWS7 IN ISOLATION (Requires being physically connected to a Wavemeter):

# TESTING CbEventDrivenScheduler IN ISOLATION:
# 1. Test starting and stopping the scheduler
# 2. Test to make sure no more SamplePoints are being added after stopping the scheduler
#   - Test that stop() unregisters the callback function

# TESTING IntervalScheduler IN ISOLATION:


# TESTING CALLBACK FUNCTION IN ISOLATION:
# 1. Test if the callback function creates the expected SamplePoint with mode of interest: cmiFrequency1 = 28

# 2. Test if the callback function creates the expected SamplePoint with mode of interest: cmiFrequency2 = 29

# 3. Test if the callback function does NOT create a SamplePoint for an uninteresting mode: cmiVersion = 31


# TESTING CALLBACK FUNCTION AND SCHEDULER INTEGRATION: #TODO: likely just combine this test with the above tests
# 1-3. Equivelent to the above tests, being run through the scheduler and checking if the SamplePoints are being appended to the Schedulers queue correctly


# TESTING the SampleSession façade (May be unnecessary if not implemented)
