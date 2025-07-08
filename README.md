# Test and Simulation Tools

This folder contains optional utilities to support development and debugging of the spectroscopy pipeline.

## Files

- `simulate_data.py`: Generates synthetic frequency–intensity data based on Voigt or Gaussian models. Useful for testing fitting, conversion, and plotting routines without hardware.

- `test_controller_stub.py`: Runs a mock controller server that accepts voltage-step commands and returns simulated frequency responses. This lets you test the `analyzer/` pipeline end-to-end without requiring the real DAQ or wavemeter.

## Usage Examples

- To generate test data:
  ```bash
  python simulate_data.py
