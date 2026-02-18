"""
Camera controller for UVC/USB microscope image capture.
"""

import logging
import time
from pathlib import Path

import cv2

from .config import (
    CAMERA_INDEX,
    CAMERA_HEIGHT,
    CAMERA_WIDTH,
    SETTLE_TIME,
)

logger = logging.getLogger(__name__)


class CameraControllerError(Exception):
    """Raised when camera operations fail."""

    pass


class CameraController:
    """
    Controls USB microscope via OpenCV VideoCapture.
    Captures frames with configurable settle delay after stage movement.
    """

    def __init__(
        self,
        camera_index: int = CAMERA_INDEX,
        width: int = CAMERA_WIDTH,
        height: int = CAMERA_HEIGHT,
        settle_time: float = SETTLE_TIME,
    ) -> None:
        self._camera_index = camera_index
        self._width = width
        self._height = height
        self._settle_time = settle_time
        self._cap: cv2.VideoCapture | None = None

    def open(self) -> None:
        """Open camera and set resolution."""
        self._cap = cv2.VideoCapture(self._camera_index)
        if not self._cap.isOpened():
            raise CameraControllerError(
                f"Could not open camera index {self._camera_index}"
            )

        self._cap.set(cv2.CAP_PROP_FRAME_WIDTH, self._width)
        self._cap.set(cv2.CAP_PROP_FRAME_HEIGHT, self._height)

        try:
            self._cap.set(cv2.CAP_PROP_AUTO_EXPOSURE, 0)
        except Exception:
            pass

        logger.info(
            "Camera opened (index=%d, target=%dx%d)",
            self._camera_index,
            self._width,
            self._height,
        )

    def capture_frame(self, settle_before: bool = True) -> cv2.Mat | None:
        """
        Capture a single frame.
        If settle_before is True, waits settle_time seconds before capture
        (for use after stage movement).
        """
        if not self._cap or not self._cap.isOpened():
            raise CameraControllerError("Camera not open")

        if settle_before and self._settle_time > 0:
            time.sleep(self._settle_time)

        # Read a couple frames to clear buffer / let exposure settle
        for _ in range(2):
            self._cap.read()
        ret, frame = self._cap.read()

        if not ret or frame is None:
            return None
        return frame

    def save_frame(self, frame: cv2.Mat, filename: str | Path) -> bool:
        """Save frame to file. Returns True on success."""
        path = Path(filename)
        path.parent.mkdir(parents=True, exist_ok=True)
        success = cv2.imwrite(str(path), frame)
        if success:
            logger.debug("Saved %s", path)
        else:
            logger.warning("Failed to save %s", path)
        return success

    def close(self) -> None:
        """Release camera."""
        if self._cap:
            self._cap.release()
            self._cap = None
            logger.info("Camera closed")
