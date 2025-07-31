import threading
import time
import pytest
from typing import Generator
from spectroscopy_node.wavemeter import wlmConst
from spectroscopy_node.wavemeter.wavemeter import (
    WavemeterWS7,
    IntervalScheduler,
    CbEventDrivenScheduler,
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

    fake_mode = wlmConst.cmiFrequency1

    # Until the callback function is unregistered, periodically call it with new data
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


# Lambda for starting the event simulation thread


# def start_event_monitor():
#     stop_event = threading.Event()
#     # stop_event.clear()  # Ensure the stop event is clear before starting the thread
#     event_monitor_thread = threading.Thread(
#         target=simulate_callback_events, args=(None, stop_event), daemon=True
#     )
#     event_monitor_thread.start()


# # lambda for stopping the event simulation thread
# def stop_event_monitor():
#     """
#     Stop the event monitor thread by setting the stop event.
#     """
#     stop_event.set()
#     event_monitor_thread.join()  # Wait for the thread to finish
#     # Reset the stop event for future use
#     stop_event.clear()


@pytest.fixture
def mock_wavemeter(monkeypatch):
    # Create a fake WavemeterWS7 instance
    wm = WavemeterWS7()

    stop_event_monitor_flag = threading.Event()
    event_monitor_thread = threading.Thread(
        target=simulate_callback_events,
        args=(wm, stop_event_monitor_flag),
        daemon=True,
    )

    # Monkeypatch the init method to avoid loading the DLL
    monkeypatch.setattr(
        WavemeterWS7, "__init__", lambda self: setattr(self, "_cb_cfunc", None)
    )

    # Monkeypatch the methods that call the DLL to use fake implementations
    monkeypatch.setattr(wm, "get_frequency", fake_get_frequency)

    # TODO:TODO:TODO: instead of lambda, I need to use a function that starts a thread that listens for the callback events
    # Override _register_callback to just store the callback.
    # TODO: I actually need to mock the the non-private versions because the private register callback includes formatting for C compatibility

    # def mock_register_callback(cb):
    #     # Start a thread to simulate callback events

    # def mock_unregister_callback():
    #     # Stop the event simulation thread
    #     stop_event_monitor_flag.set()

    monkeypatch.setattr(
        wm,
        "_register_callback",
        lambda: (stop_event_monitor_flag.clear(), event_monitor_thread.start()),
    )
    monkeypatch.setattr(
        wm,
        "_unregister_callback",
        lambda: (stop_event_monitor_flag.set(), event_monitor_thread.join()),
    )

    return wm


# @pytest.fixture
# def interval_scheduler():
#     return IntervalScheduler()

# @pytest.fixture
# def sample_point():
#     return SamplePoint()


# TESTING


# TESTING WavemeterWS7 IN ISOLATION (Requires being physically connected to a Wavemeter):


# TESTING CbEventDrivenScheduler IN ISOLATION:
# TODO:
#   1. mock register_callback to set the callback function
#       1a. start a thread that simulates the callback events and calls the callback function
#       1b. set the mock_wavemeter._cb_cfunc to the callback function
#       1c. the thread should run until the stop_event is set
#   2. mock unregister_callback to set the callback function to None
#       2a. stop the thread that simulates the callback events (____stop_event.set())
class TestCbEventDrivenScheduler:
    @pytest.fixture(autouse=True)
    def setup(self, mock_wavemeter):
        # TODO: if CBEventDrivenScheduler is updated to take a CB_func as an argument, adjust the below logic
        self.scheduler = CbEventDrivenScheduler(mock_wavemeter)

    def test_start_stop_scheduler(self):
        """
        Test starting and stopping the scheduler.
        """
        self.scheduler.start()
        assert self.scheduler.is_running

    # TODO: do one long test that tests the entire flow of the scheduler


# TODO: Test for callback function individually (requires a mock wavemeter)

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


# TESTING Schedules with Live data from hardware device to make sure it has the right format (cant test for specific values)
