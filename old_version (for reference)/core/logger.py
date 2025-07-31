# TODO: Probably Delete this file


class RunLogger:
    """
    Logs structured experimental data to a CSV or JSON file.

    Can be used as:
    with RunLogger("scan.csv") as log:
        log.write_row({...})
    """

    def __init__(self, filepath: str, headers: list = None):
        """
        Opens a log file for writing.
        If headers are provided, writes them immediately.
        """
        pass

    def __enter__(self):
        """Opens file handle."""
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        """Closes file handle safely."""
        pass

    def write_row(self, row_dict: dict):
        """
        Writes a dictionary as a structured row to the log file.
        Handles CSV or JSON formatting based on extension.
        """
        pass

    def load_log(self, filepath: str) -> list:
        """
        Reads a structured log file and returns it as a list of dictionaries.
        """
        pass


def timestamp_now() -> str:
    """
    Returns the current UTC time as an ISO 8601 timestamp string.
    """
    pass
