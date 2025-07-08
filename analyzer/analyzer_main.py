"""Top-level entry script for the analyzer system
Coordinates the full scan process using DaqAI, AnalyzerClient, and ScanManager"""


def main():
    """
    Entry point for the analyzer process.
    - Loads voltage step list
    - Initializes photodiode DAQ and network connection
    - Runs stepped scan:
        → Sends voltage step
        → Waits, acquires intensity
        → Receives frequency response
        → Validates data, logs, or records retry
    """
    pass
