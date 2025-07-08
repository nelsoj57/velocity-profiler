from typing import Tuple

import numpy as np
import numpy.typing

import nidaqmx
from nidaqmx.constants import AcquisitionType

from scipy import signal
import matplotlib.pyplot as plt


def check_buffer_safety(samps_per_chan, sample_rate, waveform_freq=None, role="AI"):
    buffer_duration = samps_per_chan / sample_rate

    # Check time-based safety
    if buffer_duration < 0.1:
        print(
            f"Warning: buffer duration is only {buffer_duration:.3f} seconds. "
            f"Consider increasing samps_per_chan to reduce risk of overrun/underrun."
        )

    # Additional check for waveform-based output
    if role.upper() == "AO" and waveform_freq is not None:
        samples_per_waveform = sample_rate / waveform_freq
        if not np.isclose(samps_per_chan % samples_per_waveform, 0, atol=1e-3):
            print(
                f"Warning: samps_per_chan ({samps_per_chan}) is not an integer multiple "
                f"of your waveform cycle length ({samples_per_waveform:.2f} samples). "
                f"This can cause waveform discontinuities."
            )


def generate_sine_wave(
    frequency: float,
    amplitude: float,
    sampling_rate: float,
    number_of_samples: int,
    phase_in: float = 0.0,
) -> Tuple[numpy.typing.NDArray[numpy.double], float]:
    """Generates a sine wave with a specified phase.

    Args:
        frequency: Specifies the frequency of the sine wave.
        amplitude: Specifies the amplitude of the sine wave.
        sampling_rate: Specifies the sampling rate of the sine wave.
        number_of_samples: Specifies the number of samples to generate.
        phase_in: Specifies the phase of the sine wave in radians.

    Returns:
        Indicates a tuple containing the generated data and the phase
        of the sine wave after generation.
    """

    duration_time = number_of_samples / sampling_rate  # Temporal duration in seconds
    angular_frequency = 2 * np.pi * frequency
    duration_radians = angular_frequency * duration_time  # Spatial duration in radians

    # The phase of the final sampled point, normalized to [0, 2π)
    phase_fin = (phase_in + duration_radians) % (2 * np.pi)

    # Generate the array of phase values at each sample point
    phase_array = np.linspace(
        phase_in, phase_in + duration_radians, number_of_samples, endpoint=False
    )
    voltage_array = amplitude * np.sin(phase_array)  # Generate the sine wave data
    return voltage_array, phase_fin


def generate_triangle_wave(
    frequency: float,
    amplitude: float,
    sampling_rate: float,
    number_of_samples: int,
    phase_in: float = 0.0,
) -> Tuple[numpy.typing.NDArray[numpy.double], float]:
    """Generates a triangle wave

    Args:
        frequency: Specifies the frequency of the triangle wave.
        amplitude: Specifies the amplitude of the triangle wave.
        sampling_rate: Specifies the sampling rate of the triangle wave.
        number_of_samples: Specifies the number of samples to generate.

    Returns:
        Indicates a numpy array containing the generated triangle wave data.
    """
    duration_time = number_of_samples / sampling_rate  # Temporal duration in seconds

    angular_frequency = 2 * np.pi * frequency
    duration_radians = angular_frequency * duration_time  # Spatial duration in radians

    # Generate the array of phase values at each sample point
    phase_in += 0.5 * np.pi  # Offset phase to align triangle wave with sine wave
    phase_array = np.linspace(
        phase_in,
        phase_in + duration_radians,
        number_of_samples,
        endpoint=False,
    )
    # Generate the triangle wave data
    triangle_wave = amplitude * signal.sawtooth(phase_array, 0.5)
    # Final phase, normalized to [0, 2π)
    phase_fin = (phase_in + duration_radians) % (2 * np.pi)
    return triangle_wave, phase_fin


# TODO: if planning to loop, make sure the numpy array ends with the same value it starts with


def check_loop_safety(sampling_rate: float, number_of_samples: int, frequency: float):
    """Checks if the the signal forms an whole number of periods (ensures no discontinuities if looping).
    Args:
        sampling_rate: Specifies the sampling rate of the signal.
        number_of_samples: Specifies the number of samples in the signal.
        frequency: Specifies the frequency of the signal.
    """
    duration_time = number_of_samples / sampling_rate  # Temporal duration in seconds
    # angular_frequency = 2 * np.pi * frequency
    # duration_radians = angular_frequency * duration_time  # Spatial duration in radians

    # # Check if the signal completes an integer number of periods
    # remainder = duration_radians % (2 * np.pi)
    # if abs(remainder) > 1e-3:
    #     print(
    #         "Warning: The signal does not complete an integer number of periods.\n"
    #         "Consider adjusting the frequency or number_of_samples to avoid discontinuities."
    #     )
    check_loop_safety_by_time(frequency, duration_time)


# A version when just frequency and time duration are provided
# TODO: may be unnecessary/repetivive
def check_loop_safety_by_time(frequency: float, duration_time: float):
    """Checks if the the signal forms an whole number of periods (ensures no discontinuities if looping).
    Args:
        frequency: Specifies the frequency of the signal.
        duration_time: Specifies the time duration of the signal.
    """
    angular_frequency = 2 * np.pi * frequency
    duration_radians = angular_frequency * duration_time  # Spatial duration in radians

    # Check if the signal completes an integer number of periods
    remainder = duration_radians % (2 * np.pi)
    if abs(remainder) > 1e-3:
        print(
            "Warning: The signal does not complete an integer number of periods.\n"
            "Consider adjusting the frequency or duration_time to avoid discontinuities."
        )


def init_task(
    device_name: str = "Dev1",
    channel_name: str = "ao0",
    sampling_rate: float = 2000.0,
) -> nidaqmx.Task:
    """Initializes a NIDAQmx task for outputting a voltage ramp.

    Args:
        device_name: Specifies the name of the device.
        channel_name: Specifies the name of the output channel.
        sampling_rate: Specifies the sampling rate for the task.

    Returns:
        Indicates a NIDAQmx Task object.
    """
    task = nidaqmx.Task()
    task.ao_channels.add_ao_voltage_chan(
        f"{device_name}/{channel_name}", min_val=-5, max_val=5
    )
    task.timing.cfg_samp_clk_timing(
        sampling_rate, samps_per_chan=1000, sample_mode=AcquisitionType.FINITE
    )
    return task


def main():
    # Parameters for the wave generation
    frequency = 12.7  # Hz
    amplitude = 1.0  # Volts
    sampling_rate = 1000.0  # Hz
    number_of_samples = 1000
    phase_in = 0.0

    # Generate sine wave
    sine_wave, sine_phase_fin = generate_sine_wave(
        frequency, amplitude, sampling_rate, number_of_samples, phase_in
    )

    # Generate triangle wave
    triangle_wave, triangle_phase_fin = generate_triangle_wave(
        frequency, amplitude, sampling_rate, number_of_samples, phase_in
    )

    # Plot the sine wave
    plt.figure(figsize=(10, 5))
    plt.subplot(2, 1, 1)
    plt.plot(sine_wave, label="Sine Wave")
    plt.title("Sine Wave")
    plt.xlabel("Sample Index")
    plt.ylabel("Amplitude")
    plt.legend()

    # Plot the triangle wave
    plt.subplot(2, 1, 2)
    plt.plot(triangle_wave, label="Triangle Wave", color="orange")
    plt.title("Triangle Wave")
    plt.xlabel("Sample Index")
    plt.ylabel("Amplitude")
    plt.legend()

    # Show the plots
    plt.tight_layout()
    plt.show()


if __name__ == "__main__":
    main()
