#!/usr/bin/env python3
import subprocess
import time
import argparse
import re
import sys

parser = argparse.ArgumentParser(description="Touch-release Zoom Reset Daemon")
parser.add_argument('--device', required=True, help='Touch device (e.g., /dev/input/event5)')
parser.add_argument('--reset-cmd', required=True, help='Command/script to reset zoom')
parser.add_argument('--delay', type=int, default=5, help='Seconds to wait after touch release')
parser.add_argument('--debounce', type=int, default=1, help='Minimum seconds between resets')
parser.add_argument('--debug', action='store_true', help='Enable debug output')
args = parser.parse_args()

last_reset = 0

def main():
    cmd = ["/usr/libexec/libinput/libinput-debug-events", "--device", args.device]
    proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    for raw in proc.stdout:
        line = raw.rstrip()
        if args.debug:
            print(line, file=sys.stderr)
        # Detect touch release events
        if re.search(r'TOUCH_UP', line) or re.search(r'POINTER_TOUCH\s+0\b', line):
            now = time.time()
            if now - last_reset >= args.debounce:
                last_reset = now
                if args.debug:
                    print(f"Touch release detected — waiting {args.delay}s to reset zoom", file=sys.stderr)
                subprocess.Popen(["/bin/bash", "-c", f"sleep {args.delay}; {args.reset_cmd}"])

if __name__ == "__main__":
    main()
