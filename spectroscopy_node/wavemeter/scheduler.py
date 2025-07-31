from wavemeter import WavemeterWS7
from dataclasses import dataclass, field
from typing import Optional, Callable, Protocol, Union
import queue, threading, time
from abc import ABC, abstractmethod


@dataclass(frozen=True, slots=True)
# frozen=True makes the dataclass immutable, slots=True saves memory by using __slots__ (a continous array) instead of a dict for attributes
class SamplePoint:
    """
    A class representing a sample point from the wavemeter.
    """

    t: int  # Timestamp of the sample point in milliseconds
    value: float  # Frequency value of the sample point
    # this keeps the source from being printed when the SamplePoint is printed, but it can still be accessed as an attribute
    source: str = field(repr=False)


class PollingStrategy(Protocol):
    """
    A protocol for acquisition strategies that can be used to acquire data from the wavemeter.
    The __call__ method should return a SamplePoint object or a float value.
    """

    # Acquire data from the wavemeter and return a float value or a SamplePoint object.
    # TODO: see if I want to use a SamplePoint object or just a float value.
    # def __call__(self, device: WavemeterWS7) -> float | SamplePoint: ...
    def __call__(self, device: WavemeterWS7) -> SamplePoint: ...


class CallbackStrategy(Protocol):
    """
    A protocol for acquisition strategies that can be used to acquire data from the wavemeter.
    The __call__ method should return a SamplePoint object or a float value.
    """

    # Acquire data from the wavemeter and return a SamplePoint object.
    def __call__(self, mode: int, intval: int, dblval: float) -> SamplePoint: ...


class BaseScheduler(ABC):
    def __init__(
        self,
        device: WavemeterWS7,
        acquisition_strategy: Union[PollingStrategy, CallbackStrategy],
        threaded: bool = False,
    ):
        """
        Initializes the BaseScheduler with a WavemeterWS7 object.

        Args:
            device (WavemeterWS7): The wavemeter object to use for frequency events.
        """

        self._acq_strat = acquisition_strategy
        self._device = device
        self._data_buffer: queue.Queue[SamplePoint] = queue.Queue()
        self._stop_event = threading.Event()
        self._running = False
        self._threaded = threaded
        self._thread = None

    # public API
    @property
    def data(self) -> queue.Queue[SamplePoint]:
        # Returns the queue holding frequency data.
        return self._data_buffer

    @property
    def is_running(self) -> bool:
        # Returns whether the scheduler is currently running.
        return self._running

    @abstractmethod
    def _run_loop(self):
        """Implement this loop in each scheduler subclass.
        It should check self._stop_event periodically and exit cleanly."""
        ...

    def start(self):
        """Start the scheduler. Optionally runs in a background thread."""
        self._stop_event.clear()
        self._running = True

        if self._threaded:
            self._thread = threading.Thread(target=self._run_loop, daemon=True)
            self._thread.start()
        else:
            self._run_loop()

    def stop(self):
        """Tell the loop to stop. The loop should check this event and exit."""
        self._stop_event.set()
        self._running = False
        # TODO: If running in a thread, join? TODO: check if below is correct
        if self._threaded and self._thread is not None:
            self._thread.join()


class EventDrivenScheduler(BaseScheduler):
    """
    A scheduler that uses callback events to acquire data from the wavemeter.
    """

    def __init__(self, wavemeter: WavemeterWS7, acquisition_strategy: CallbackStrategy):
        super().__init__(wavemeter, acquisition_strategy, threaded=False)

    def callback_handler(self, mode: int, intval: int, dblval: float) -> None:
        """
        Callback function to handle frequency events from the wavemeter.
        Converts the event data into a SamplePoint and puts it in the queue.
        """
        sample_point = self._acq_strat(mode, intval, dblval)
        if sample_point is not None:
            # Ensure the sample point is valid before putting it in the queue
            if isinstance(sample_point, SamplePoint):
                # TODO: ^may be unnecessary if _acq_strat always returns a SamplePoint
                self._data_buffer.put(sample_point)

    def _run_loop(self):
        """Run the event-driven loop."""
        self._device.register_frequency_callback(self.callback_handler)

    def stop(self):
        """Stop the event-driven scheduler."""
        self._device.unregister_frequency_callback()
        self._running = False


class IntervalScheduler(BaseScheduler):
    """
    An IntervalScheduler that uses the WavemeterWS7 class to poll frequency data at a fixed interval.
    This scheduler will use the get_frequency method to update the frequency data.
    """

    def __init__(
        self,
        device: WavemeterWS7,
        acquisition_strategy: PollingStrategy = lambda device: SamplePoint(
            0, device.get_frequency(), "IntervalScheduler"
        ),  # TODO: Fix this deafault strategy to be more meaningful
        interval: float = 1.0,  # Default to 1 second interval
        threaded: bool = True,
    ):
        super().__init__(device, acquisition_strategy, threaded)
        self._interval = interval

    def _run_loop(self):
        """
        The main loop of the IntervalScheduler.
        This loop will run until the stop event is set.
        It will poll the wavemeter for frequency data at the specified interval.
        """
        while not self._stop_event.is_set():
            try:
                sample_point = self._acq_strat(self._device)  # type: ignore
                self._data_buffer.put(sample_point)
            # except WavemeterWS7Exception as e:
            except Exception as e:
                print(f"Error getting frequency: {e}")
            time.sleep(self._interval)  # Wait for the specified interval
