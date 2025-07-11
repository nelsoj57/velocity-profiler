def load_failed_step_list(filepath: str) -> list:
    """
    Loads a list of failed scan steps from a saved JSON or CSV log.
    Returns list of (step_index, voltage) pairs.
    """
    pass


def rerun_failed_steps(failed_points: list, comm_socket, ai_task, wait_time: float):
    """
    Re-runs only the steps flagged as failed:
      - Sends command to controller
      - Averages photodiode + frequency
      - Logs new results separately
    """
    pass


def merge_rerun_results(original_path: str, rerun_path: str, output_path: str):
    """
    Combines successful reruns with previous data, replacing failed entries.
    """
    pass


def main():
    """
    CLI entry:
      - Load failed step file
      - Connect to controller + AI
      - Run retry loop
      - Save + merge results
    """
    pass
