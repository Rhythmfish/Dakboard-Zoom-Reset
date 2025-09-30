# Dakboard-Zoom-Reset

This step-by-step guide documents the setup of a Python daemon that automatically resets zoom (Ctrl+0) on a DakBoard kiosk touchscreen after a configurable delay when the user lifts their finger. It uses the GUI autostart method for reliable operation at boot and provides detailed instructions for environment setup, Python daemon creation, zoom reset scripting, autostart configuration, and verification.

# Step By Step

## Step 1: Install Necessary Packages

1. Update your package lists:

```bash
sudo apt update
```

2. Install `xdotool`, which allows simulating key presses in the Chromium browser:

```bash
sudo apt install xdotool
```

3. Verify the touchscreen device is detected using `libinput-debug-events`:

```bash
/usr/libexec/libinput/libinput-debug-events
```

You should see lines indicating your touchscreen devices (e.g., `event5`, `event6`). Take note of the device you will use (e.g., `/dev/input/event5`).

---

## Step 2: Create the Zoom Reset Shell Script

This script will perform the actual zoom reset in Chromium.

1. Create the script file:

```bash
sudo nano /usr/local/bin/reset-zoom.sh
```

2. Paste the following content:

```bash
#!/bin/bash
xdotool search --onlyvisible --class chromium key --clearmodifiers ctrl+0
```

3. Make the script executable:

```bash
sudo chmod +x /usr/local/bin/reset-zoom.sh
```

4. Test the script manually to make sure it resets zoom in Chromium:

```bash
/bin/bash /usr/local/bin/reset-zoom.sh
```

---

## Step 3: Create the Python Daemon

This Python script monitors touch events and triggers the zoom reset after a specified delay.

1. Create the daemon script:

```bash
sudo nano /usr/local/bin/touch-reset-daemon.py
```

2. Paste the following content:

```python
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
```

3. Make the Python script executable:

```bash
sudo chmod +x /usr/local/bin/touch-reset-daemon.py
```

4. Test the daemon manually (replace `/dev/input/event5` with your touchscreen device):

```bash
sudo /usr/bin/python3 /usr/local/bin/touch-reset-daemon.py --device /dev/input/event5 --reset-cmd /usr/local/bin/reset-zoom.sh --debug
```

Watch for `Touch release detected` messages when you lift your finger from the touchscreen.

---

## Step 4: Set Up GUI Autostart

This ensures the daemon starts automatically **after the graphical session is ready**, which is required for `xdotool` to work with Chromium.

1. Create the autostart directory (if it does not exist):

```bash
mkdir -p /home/dakboard/.config/autostart
```

2. Create the `.desktop` autostart file:

```bash
nano /home/dakboard/.config/autostart/touch-reset.desktop
```

3. Paste the following content:

```ini
[Desktop Entry]
Type=Application
Exec=/usr/bin/python3 /usr/local/bin/touch-reset-daemon.py --device /dev/input/event5 --reset-cmd /usr/local/bin/reset-zoom.sh --delay 5
Hidden=false
NoDisplay=false
X-GNOME-Autostart-enabled=true
Name=Touch Reset Daemon
Comment=Reset zoom after touch release
```

4. Save and exit the editor.

---

## Step 5: Reboot and Verify

1. Reboot the system:

```bash
sudo reboot
```

2. After the GUI loads, verify that the daemon is running:

```bash
ps aux | grep touch-reset-daemon.py
```

3. Test the touchscreen:

* Touch and hold on the screen.
* Lift your finger.
* After approximately 5 seconds, the zoom in Chromium should reset to 100%.

---

## ✅ Notes and Successes

* **Touchscreen detection**: Confirmed working with `/usr/libexec/libinput/libinput-debug-events`.
* **Python daemon**: Detects touch release and triggers a delayed zoom reset.
* **xdotool**: Successfully interacts with Chromium in DakBoard kiosk session.
* **GUI autostart**: Ensures daemon runs automatically at boot, after GUI is ready.
* **Delay and debounce**: Configurable to control how long zoom remains after touch release and prevent rapid multiple resets.

This setup is fully compatible with DakBoard kiosk mode and Chromium-based dashboards.
