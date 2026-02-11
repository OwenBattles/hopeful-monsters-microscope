"""
Utility functions for the microscope tiling system.
"""

import glob
import logging
import sys


def setup_logging(level: int = logging.INFO) -> None:
    """Configure logging with a consistent format."""
    logging.basicConfig(
        level=level,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
        stream=sys.stdout,
    )


def resolve_serial_port(pattern: str) -> str | None:
    """
    Resolve a glob pattern to a concrete serial port path.
    E.g., '/dev/tty.usbmodem*' -> '/dev/tty.usbmodem14101'
    If pattern contains no glob chars (e.g. 'COM3'), returns it as-is.
    """
    if "*" not in pattern and "?" not in pattern:
        return pattern
    matches = glob.glob(pattern)
    if not matches:
        return None
    return sorted(matches)[0]
