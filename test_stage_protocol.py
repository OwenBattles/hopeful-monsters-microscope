#!/usr/bin/env python3
"""
Test the MOVE/HOME protocol with the microscope_stage Arduino sketch.

Usage:
  1. Upload arduino/microscope_stage/microscope_stage.ino to your Arduino
  2. Close the Arduino Serial Monitor
  3. Run: python test_stage_protocol.py

This sends HOME and a few MOVE commands and checks for DONE responses.
"""

import glob
import sys
import time

try:
    import serial
    import serial.tools.list_ports
except ImportError:
    print("Install pyserial: pip install pyserial")
    sys.exit(1)


def find_port() -> str | None:
    ports = list(serial.tools.list_ports.comports())
    usb = [p for p in ports if "usb" in p.device.lower() or "usbmodem" in p.device.lower()]
    return (usb[0].device if usb else (ports[0].device if ports else None))


def main() -> None:
    port = find_port()
    if not port:
        print("No serial port found.")
        sys.exit(1)

    print(f"Using {port}")
    try:
        ser = serial.Serial(port, 115200, timeout=2.0)
    except serial.SerialException as e:
        print(f"Could not open port: {e}")
        sys.exit(1)

    time.sleep(2)
    ser.reset_input_buffer()

    def send_and_wait(cmd: str, expect: str = "DONE") -> bool:
        ser.write((cmd + "\n").encode())
        ser.flush()
        deadline = time.monotonic() + 5.0
        while time.monotonic() < deadline:
            line = ser.readline().decode("utf-8", errors="ignore").strip()
            if not line:
                continue
            print(f"  <- {line}")
            if expect in line:
                return True
            if "ERR" in line:
                return False
        print("  (timeout)")
        return False

    print("\n1. Sending HOME...")
    if not send_and_wait("HOME"):
        print("FAILED")
        ser.close()
        sys.exit(1)
    print("OK")

    print("\n2. Sending MOVE 100 0...")
    if not send_and_wait("MOVE 100 0"):
        print("FAILED")
        ser.close()
        sys.exit(1)
    print("OK")

    print("\n3. Sending MOVE 0 0...")
    if not send_and_wait("MOVE 0 0"):
        print("FAILED")
        ser.close()
        sys.exit(1)
    print("OK")

    ser.close()
    print("\nAll protocol tests passed.")


if __name__ == "__main__":
    main()
