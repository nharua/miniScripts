# Shell Utility Scripts

This collection of shell scripts provides various small utilities to speed up common tasks.
Each script is self-contained and can be used directly from the command line.

## 1. init-pyproject

A helper script to quickly bootstrap a new Python project with sensible defaults.

### Features

- Initializes a Git repository with `main` branch.
- Creates essential starter files: `.env`, `.gitignore`, `LICENSE`, `README.md`.
- Downloads Python `.gitignore` template from GitHub.
- Adds current year automatically to the `LICENSE`.
- Optional `--venv` flag to create a local `.venv` folder and add it to `.gitignore`.

### Usage

- Initialize in current directory:
``` bash
init-pyproject
```

- Initialize in a new directory:
``` bash
init-pyproject myproject
```

- Initialize with virtual environment:
``` bash
init-pyproject myproject --venv
```

### Example Result

```yaml
myproject/
├── .env
├── .git/
├── .gitignore
├── .venv/        # only if --venv is used
├── LICENSE
└── README.md
```

## 2. test_iperf.py

A Python wrapper for iperf3 to monitor network performance and log alerts if throughput falls below a threshold.

### Features

- Supports one-way, reverse, or bidirectional tests (--mode option).
- Monitors throughput in real time and compares it against a user-defined target speed.
- Logs alerts when throughput drops below 85% of target speed.
- Option to run for a fixed duration (--duration) or indefinitely.
- Logs are saved to iperf_alert.log in the same directory as the script.

### Usage

``` bash
python3 test_iperf.py --target <speed> --server <host> [--port <port>] [--duration <seconds>] [--mode <mode>]
```

### Arguments

```yaml
--target : Target speed, e.g. 10G, 1G, 500M, 2.5G
--server : Target server IP or hostname
--port : Server port (default: 5201)
--duration: Test duration in seconds (default: 10, 0 = infinite)
--mode : Test mode:
   normal → client → server
   reverse → server → client
   bidir → both directions
```

### Examples

- Run a 10-second one-way test to 127.0.0.1 at 1 Gbps:
```bash
python3 test_iperf.py --target 1G --server 127.0.0.1 --duration 10 --mode normal
```

- Run a bidirectional test indefinitely to remote host:
```bash
python3 test_iperf.py --target 5G --server 192.168.1.100 --duration 0 --mode bidir
```

### Example Output

```
Target speed: 5G (5000.00 Mbps)
Running for 10 seconds
Test mode: bidir
OK: 4720.00 Mbps
[2025-09-04 11:38:50] Low throughput: 3610.00 Mbps (< 85% of 5G)
```

