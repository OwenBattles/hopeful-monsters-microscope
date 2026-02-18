#!/usr/bin/env python3
"""
Simple test to verify Python can communicate with the Arduino over serial.

Usage:
  1. Connect your Arduino (e.g. Adafruit Metro 328)
  2. Upload any sketch that prints to Serial (or the echo sketch below)
  3. Close the Arduino Serial Monitor if it's open (only one program can use the port)
  4. Run: python test_arduino_connection.py

You should see whatever the Arduino sends. Press Ctrl+C to stop.
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


def main() -> None:
    ports = list(serial.tools.list_ports.comports())
    if not ports:
        print("No serial ports found. Is the Arduino connected?")
        sys.exit(1)

    print("Available ports:")
    for i, p in enumerate(ports, 1):
        print(f"  {i}. {p.device} - {p.description}")

    # Prefer USB/serial devices
    usb = [p for p in ports if "usb" in p.device.lower() or "usbmodem" in p.device.lower()]
    choice = usb[0] if usb else ports[0]
    port = choice.device
    print(f"\nUsing: {port}")
    print("Reading for 15 seconds (Ctrl+C to stop earlier)...\n")

    try:
        ser = serial.Serial(port, 115200, timeout=0.1)
        time.sleep(2)  # Let Arduino reset (DTR triggers reboot)
        # Don't reset_input_buffer() - that would discard "READY" the Arduino just sent
    except serial.SerialException as e:
        print(f"Could not open {port}: {e}")
        print("Close the Arduino Serial Monitor and try again.")
        sys.exit(1)

    start = time.monotonic()
    last_ping = 0
    try:
        while time.monotonic() - start < 15:
            # Send PING every 2 seconds to test bidirectional communication
            now = time.monotonic()
            if now - last_ping >= 2:
                ser.write(b"PING\n")
                ser.flush()
                last_ping = now
            line = ser.readline().decode("utf-8", errors="ignore").rstrip()
            if line:
                print(line)
    except KeyboardInterrupt:
        pass
    finally:
        ser.close()

    print("\nTest complete.")


if __name__ == "__main__":
    main()
