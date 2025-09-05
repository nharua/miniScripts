#!/usr/bin/env python3
import argparse
import subprocess
import re
import sys
import os
import pty
import select
from datetime import datetime


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


def parse_throughput(line: str) -> tuple[float, str] | None:
    # Clean ANSI escape sequences first
    line = re.sub(r"\x1b\[[0-9;]*m", "", line)
    # print(f"DEBUG line repr: {repr(line)}")
    match = re.search(r"([\d\.]+)\s*([KMG]?)\s*bits/sec", line)
    if not match:
        return None
    value = float(match.group(1))
    unit = match.group(2)
    throughput = 0.0
    if unit == "G":
        throughput = value * 1e9
    elif unit == "M":
        throughput = value * 1e6
    elif unit == "K":
        throughput = value * 1e3
    else:
        throughput = value

    direction = ""
    if "[SUM]" in line:
        direction = "SUM"
    elif "[TX-S]" in line or "[TX-C]" in line:
        direction = "TX"
    elif "[RX-S]" in line or "[RX-C]" in line:
        direction = "RX"
    else:
        direction = "CLIENT"

    return throughput, direction


def log_alert(msg: str):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open("iperf_alert.log", "a") as f:
        f.write(f"[{timestamp}] {msg}\n")
    print(f"[{timestamp}] {msg}")
    sys.stdout.flush()


def run_iperf_pty(server: str, port: int, target_bps: float, duration: int, mode: str):
    """Run iperf3 using PTY to get real-time output"""
    threshold = target_bps * 0.85

    while True:
        cmd = ["iperf3", "-c", server, "-p", str(port), "-i", "1"]
        if duration > 0:
            cmd += ["-t", str(duration)]
        else:
            cmd += ["-t", "0"]

        if mode == "bidir":
            cmd += ["--bidir"]
        elif mode == "reverse":
            cmd += ["--reverse"]

        print(f"Running command: {' '.join(cmd)}")

        try:
            # Create a pseudo terminal
            master_fd, slave_fd = pty.openpty()

            # Start process with PTY
            process = subprocess.Popen(
                cmd,
                stdin=slave_fd,
                stdout=slave_fd,
                stderr=slave_fd,
                universal_newlines=True,
            )

            # Close slave fd in parent process
            os.close(slave_fd)

            # Read from master fd
            buffer = ""
            while process.poll() is None:
                try:
                    # Use select to avoid blocking
                    ready, _, _ = select.select([master_fd], [], [], 0.1)
                    if ready:
                        data = os.read(master_fd, 1024).decode("utf-8", errors="ignore")
                        if data:
                            buffer += data

                            # Process complete lines
                            while "\n" in buffer:
                                line, buffer = buffer.split("\n", 1)
                                line = line.strip()

                                if line:
                                    # Remove ANSI escape sequences
                                    clean_line = re.sub(r"\x1b\[[0-9;]*m", "", line)

                                    # print(f"[REALTIME] {clean_line}")
                                    sys.stdout.flush()

                                    if "bits/sec" in clean_line:
                                        throughput, direction = parse_throughput(
                                            clean_line
                                        )
                                        if throughput is not None:
                                            if throughput < threshold:
                                                log_alert(
                                                    f"Low throughput: [{direction}] {throughput/1e6:.2f} Mbps (< 85% of target) target was {target_bps/1e6:.2f} Mbps"
                                                )
                                            else:
                                                print(
                                                    f"✓ OK: {throughput/1e6:.2f} Mbps"
                                                )
                                                sys.stdout.flush()

                except OSError:
                    break

            # Clean up
            os.close(master_fd)
            process.wait()

        except KeyboardInterrupt:
            print("\nStopping test.")
            try:
                process.terminate()  # pyright: ignore
                os.close(master_fd)  # pyright: ignore
            except:
                pass
            break
        except Exception as e:
            print(f"Error: {e}")
            try:
                process.terminate()  # pyright: ignore
                os.close(master_fd)  # pyright: ignore
            except:
                pass
            break

        if duration > 0:
            break


def run_iperf_simple(
    server: str, port: int, target_bps: float, duration: int, mode: str
):
    """Alternative: Run iperf3 with expect-like approach"""
    threshold = target_bps * 0.85

    while True:
        cmd = f"unbuffer iperf3 -c {server} -p {port} -i 1"
        if duration > 0:
            cmd += f" -t {duration}"
        else:
            cmd += " -t 0"

        if mode == "bidir":
            cmd += " --bidir"
        elif mode == "reverse":
            cmd += " --reverse"

        print(f"Running: {cmd}")

        try:
            process = subprocess.Popen(
                cmd,
                shell=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                universal_newlines=True,
                bufsize=1,
            )

            for line in process.stdout:  # type: ignore
                line = line.strip()
                if line:
                    print(f"[UNBUFFER] {line}")
                    sys.stdout.flush()

                    if "bits/sec" in line:
                        throughput, direction = parse_throughput(line)
                        if throughput is not None:
                            if throughput < threshold:
                                log_alert(
                                    f"Low throughput: [{direction}] {throughput/1e6:.2f} Mbps (< 85% of target)"
                                )
                            else:
                                print(f"✓ OK: {throughput/1e6:.2f} Mbps")
                                sys.stdout.flush()

        except KeyboardInterrupt:
            print("\nStopping test.")
            process.terminate()  # pyright: ignore
            break
        except Exception as e:
            print(f"Error: {e}")
            break

        if duration > 0:
            break


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
        help="Test mode",
    )
    parser.add_argument(
        "--method",
        choices=["pty", "unbuffer"],
        default="pty",
        help="Method: pty (pseudo terminal) or unbuffer (requires expect package)",
    )

    args = parser.parse_args()
    target_bps = parse_speed(args.target)

    print(f"Target speed: {args.target} ({target_bps/1e6:.2f} Mbps)")
    print(f"Method: {args.method}")

    if args.method == "pty":
        run_iperf_pty(args.server, args.port, target_bps, args.duration, args.mode)
    else:
        # Requires: sudo apt-get install expect
        run_iperf_simple(args.server, args.port, target_bps, args.duration, args.mode)
