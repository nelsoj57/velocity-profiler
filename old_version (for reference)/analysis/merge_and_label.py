def load_data_logs(intensity_file: str, frequency_file: str) -> tuple:
    """
    Loads raw CSV or JSON logs from analyzer and controller.
    Returns two lists of step-indexed records.
    """
    pass


def merge_data_by_step(intensity_data: list, frequency_data: list) -> list:
    """
    Merges data from both logs based on step_index.
    Returns list of unified data points: {ν, I, std_ν, std_I, voltage, timestamp}
    """
    pass


def discard_unstable_points(
    merged_data: list, freq_thresh: float, intensity_thresh: float
) -> list:
    """
    Filters out points with excessive frequency or intensity noise.
    Returns filtered dataset.
    """
    pass


def export_merged_data(merged_data: list, output_path: str):
    """
    Writes the clean, merged dataset to CSV or JSON for further analysis.
    """
    pass
