#!/usr/bin/env python3
import argparse
import subprocess
import re
from datetime import datetime


# Convert speed string (10G, 1G, 500M, etc.) to bits per second
def parse_speed(speed_str: str) -> float:
    speed_str = speed_str.strip().upper()
    if speed_str.endswith("G"):
        return float(speed_str[:-1]) * 1e9
    elif speed_str.endswith("M"):
        return float(speed_str[:-1]) * 1e6
    elif speed_str.endswith("K"):
        return float(speed_str[:-1]) * 1e3
    else:
        return float(speed_str)


# Extract throughput value from iperf3 output
def parse_throughput(line: str) -> float | None:
    match = re.search(r"([\d\.]+)\s+([KMG]?)bits/sec", line)
    if not match:
        return None
    value = float(match.group(1))
    unit = match.group(2)

    if unit == "G":
        return value * 1e9
    elif unit == "M":
        return value * 1e6
    elif unit == "K":
        return value * 1e3
    else:
        return value


def log_alert(msg: str):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open("iperf_alert.log", "a") as f:
        f.write(f"[{timestamp}] {msg}\n")
    print(f"[{timestamp}] {msg}")


def run_iperf(server: str, port: int, target_bps: float, duration: int, mode: str):
    threshold = target_bps * 0.85  # alert if throughput < 85% of target

    while True:
        cmd = ["iperf3", "-c", server, "-p", str(port), "-i", "1"]

        if duration > 0:
            cmd += ["-t", str(duration)]
        else:
            cmd += ["-t", "0"]  # run indefinitely

        if mode == "bidir":
            cmd += ["--bidir"]
        elif mode == "reverse":
            cmd += ["--reverse"]

        process = subprocess.Popen(
            cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True
        )

        try:
            for line in process.stdout:
                line = line.strip()
                throughput = parse_throughput(line)
                if throughput:
                    if throughput < threshold:
                        log_alert(
                            f"Low throughput: {throughput/1e6:.2f} Mbps (< 85% of target) target was {target_bps/1e6:.2f} Mbps"
                        )
                    else:
                        print(f"OK: {throughput/1e6:.2f} Mbps")
        except KeyboardInterrupt:
            print("Stopping test.")
            process.terminate()
            break

        process.wait()

        if duration > 0:
            break  # run only once if duration is fixed


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="iperf3 throughput monitor")
    parser.add_argument(
        "--target", required=True, help="Target speed (e.g. 10G, 1G, 500M)"
    )
    parser.add_argument("--server", required=True, help="iperf3 server address")
    parser.add_argument(
        "--port", type=int, default=5201, help="iperf3 server port (default: 5201)"
    )
    parser.add_argument(
        "--duration", type=int, default=10, help="Duration in seconds (0 = infinite)"
    )
    parser.add_argument(
        "--mode",
        choices=["client", "reverse", "bidir"],
        default="client",
        help="Test mode: client (one way), reverse (server → client), bidir (both directions)",
    )

    args = parser.parse_args()

    target_bps = parse_speed(args.target)
    print(f"Target speed: {args.target} ({target_bps/1e6:.2f} Mbps)")
    if args.duration == 0:
        print("Running indefinitely (press Ctrl+C to stop)")
    else:
        print(f"Running for {args.duration} seconds")
    print(f"Test mode: {args.mode}")

    run_iperf(args.server, args.port, target_bps, args.duration, args.mode)
