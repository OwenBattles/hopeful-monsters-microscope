"""
Stage controller for X/Y stepper motor movement via Arduino serial.
"""

import logging
import time

import serial
import serial.tools.list_ports

from .config import BAUD_RATE, SERIAL_TIMEOUT
from .utils import resolve_serial_port

logger = logging.getLogger(__name__)


class StageControllerError(Exception):
    """Raised when stage controller operations fail."""

    pass


class StageController:
    """
    Controls X/Y stage movement via Arduino over USB serial.
    Expects commands: MOVE X Y (in steps), response: DONE
    """

    def __init__(
        self,
        port: str | None = None,
        baud_rate: int = BAUD_RATE,
        timeout: float = SERIAL_TIMEOUT,
    ) -> None:
        self._port = port
        self._baud_rate = baud_rate
        self._timeout = timeout
        self._serial: serial.Serial | None = None
        self._current_x = 0
        self._current_y = 0

    def connect(self, port: str | None = None) -> None:
        """
        Open serial connection to Arduino.
        If port is a glob pattern (e.g. /dev/tty.usbmodem*), it is resolved.
        """
        resolved = port or self._port
        if not resolved:
            raise StageControllerError("No serial port specified")

        actual_port = resolve_serial_port(resolved)
        if not actual_port:
            raise StageControllerError(
                f"Could not resolve serial port: {resolved}. "
                "Check that the Arduino is connected."
            )

        try:
            self._serial = serial.Serial(
                port=actual_port,
                baudrate=self._baud_rate,
                timeout=self._timeout,
            )
            time.sleep(2)  # Allow Arduino to reset after serial open
            self._serial.reset_input_buffer()
            logger.info("Connected to stage at %s", actual_port)
        except serial.SerialException as e:
            raise StageControllerError(f"Failed to open serial port: {e}") from e

    def _send_and_wait(self, command: str, expect: str = "DONE") -> None:
        """Send command and wait for expected response."""
        if not self._serial or not self._serial.is_open:
            raise StageControllerError("Serial port not open")

        self._serial.reset_input_buffer()
        self._serial.write((command + "\n").encode("ascii"))
        self._serial.flush()

        deadline = time.monotonic() + self._timeout
        while time.monotonic() < deadline:
            line = self._serial.readline().decode("ascii", errors="ignore").strip()
            if not line:
                continue
            if expect.upper() in line.upper():
                return
            if "ERR" in line.upper() or "ERROR" in line.upper():
                raise StageControllerError(f"Arduino error: {line}")

        raise StageControllerError(f"Timeout waiting for '{expect}' from Arduino")

    def move_to(self, x: int, y: int) -> None:
        """Move stage to absolute position (x, y) in steps."""
        cmd = f"MOVE {int(x)} {int(y)}"
        logger.debug("Sending: %s", cmd)
        self._send_and_wait(cmd)
        self._current_x = x
        self._current_y = y

    def move_relative(self, dx: int, dy: int) -> None:
        """Move stage by relative amount (dx, dy) in steps."""
        new_x = self._current_x + int(dx)
        new_y = self._current_y + int(dy)
        self.move_to(new_x, new_y)

    def home(self) -> None:
        """Home the stage (position 0, 0)."""
        self._send_and_wait("HOME")
        self._current_x = 0
        self._current_y = 0
        logger.info("Stage homed")

    def close(self) -> None:
        """Close serial connection."""
        if self._serial and self._serial.is_open:
            self._serial.close()
            self._serial = None
            logger.info("Stage controller closed")
