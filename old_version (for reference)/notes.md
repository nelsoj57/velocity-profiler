| Candidate module                                                                     | Why a class is useful                                                                                                                                   | Possible class name                   |
| ------------------------------------------------------------------------------------ | ------------------------------------------------------------------------------------------------------------------------------------------------------- | ------------------------------------- |
| **Hardware interfaces** (`hardware_control`, `daq_interface`, `wavemeter_interface`) | • Maintain state (`task`, current voltage, sampling rate) <br>• Provide start/stop context methods <br>• Hide vendor-specific calls behind a common API | `DaqAO`, `DaqAI`, `Wavemeter`         |
| **Network endpoints** (`controller_server`, `step_coordinator`)                      | • Persistent socket, retry counters, message queue <br>• Cleaner separation of *connect*, *send*, *receive*, *close*                                    | `ControllerServer`, `AnalyzerClient`  |
| **Retry / scan management** (`retry_manager`, `step_coordinator`)                    | • Track step list, failed list, current index <br>• Expose `next()`, `record_fail()`, `rerun()`                                                         | `StepQueue`, `RetryManager`           |
| **Logging** (`core/logger`)                                                          | • Open file handle once, append rows, ensure proper close <br>• Optional context‐manager (`with Logger() as log:`)                                      | `RunLogger`                           |
| **Analysis objects** (fit results)                                                   | • Bundle the fit parameters + helper methods (`to_velocity()`, `plot()`)                                                                                | `SpectralFit`, `VelocityDistribution` |

Minimal refactor suggestion
Wrap hardware:

    class DaqAO:
        def __init__(self, channel, rate):
            self.task = nidaqmx.Task()
            ...
        def ramp(self, target_v):
            ...
        def close(self):
        ...

Wrap network endpoint:

    class ControllerServer:
        def __enter__(...):   # context-manager to ensure close
        def listen(self): ...
        def send_response(self, msg): ...

Bundle logging:

    with RunLogger("scan.csv") as log:
        log.write_row({...})

Everything else (fit functions, histogram builders, config constants) can remain functional.

velocity_profiler/
│
├── controller/                  
│   ├── controller_main.py        ← Script that wires together objects below
│   ├── hardware.py               ← DaqAO + helper mix-ins
│   ├── wavemeter.py              ← Wavemeter class
│   └── network_server.py         ← ControllerServer class
│
├── analyzer/                    
│   ├── analyzer_main.py          ← Uses ScanManager to run a stepped scan
│   ├── daq.py                    ← DaqAI class (photodiode reader)
│   ├── network_client.py         ← AnalyzerClient class
│   └── scan_manager.py           ← StepQueue + RetryManager classes
│
├── core/                        
│   ├── config.py                 ← Constants / settings (still functional)
│   ├── protocol.py               ← encode_* / decode_*  (functional)
│   └── logger.py                 ← RunLogger class  (context-manager)
│
└── analysis/   …                 ← unchanged
