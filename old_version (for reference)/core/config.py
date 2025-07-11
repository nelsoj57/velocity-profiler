# TODO: add function that calculates the std deviation of a list of voltages
# This would be used by both the Controller to make sure the frequency is stable enough to be considered valid, and by the Analyzer to make sure the intensity is stable enough to be considered valid.
# TODO: actually numpy has a std function, so this is not needed

# TODO: TODO: TODO: THis file may be deleted if not developed further.


def get_daq_settings() -> dict:
    """
    Returns DAQ settings as a dictionary:
      {
        "ao": {"channel": "Dev1/ao0", "rate": 1000},
        "ai": {"channel": "Dev2/ai0", "rate": 1000, "buffer_size": 1000}
      }
    """
    pass


def get_voltage_bounds() -> tuple:
    """
    Returns (min_voltage, max_voltage) tuple for safety checks.
    """
    pass


def get_scan_timing() -> dict:
    """
    Returns wait times and durations:
      {
        "stabilization_time": 0.5,
        "intensity_avg_time": 3.0,
        "wavemeter_avg_time": 3.0,
        "poll_rate": 10.0
      }
    """
    pass


def get_network_config() -> dict:
    """
    Returns TCP/IP or ZeroMQ settings:
      {
        "controller_host": "192.168.1.10",
        "controller_port": 5555
      }
    """
    pass


def get_stability_thresholds() -> dict:
    """
    Returns thresholds for:
      - acceptable intensity stddev
      - max allowed frequency jitter
    """
    pass


def get_wavemeter_settings() -> dict:
    """
    Returns wavemeter polling rate and averaging duration.
    """
    pass
