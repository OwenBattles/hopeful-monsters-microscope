"""
Grid scanner: coordinates stage movement and image capture in a tile pattern.
"""

import logging
from pathlib import Path

import cv2

from .camera_controller import CameraController
from .config import IMAGE_FILENAME_PATTERN, IMAGE_SAVE_DIRECTORY
from .stage_controller import StageController

logger = logging.getLogger(__name__)


class GridScanner:
    """
    Performs snake-pattern grid scanning:
    Row 0: left-to-right, Row 1: right-to-left, Row 2: left-to-right, ...
    """

    def __init__(
        self,
        stage: StageController,
        camera: CameraController,
        grid_width: int,
        grid_height: int,
        step_size_x: int,
        step_size_y: int,
        output_dir: str | Path | None = None,
    ) -> None:
        self._stage = stage
        self._camera = camera
        self._grid_width = grid_width
        self._grid_height = grid_height
        self._step_size_x = step_size_x
        self._step_size_y = step_size_y
        self._output_dir = Path(output_dir or IMAGE_SAVE_DIRECTORY)

    def run(self) -> list[Path]:
        """
        Execute full grid scan. Returns list of saved image paths.
        Assumes stage is at home (0, 0) before starting.
        """
        self._output_dir.mkdir(parents=True, exist_ok=True)
        saved_paths: list[Path] = []
        total = self._grid_width * self._grid_height
        idx = 0

        logger.info(
            "Starting grid scan: %dx%d tiles, step (%d, %d)",
            self._grid_width,
            self._grid_height,
            self._step_size_x,
            self._step_size_y,
        )

        for row in range(self._grid_height):
            cols = range(self._grid_width) if row % 2 == 0 else range(self._grid_width - 1, -1, -1)
            for col in cols:
                idx += 1
                logger.info("Tile %d/%d: col=%d row=%d", idx, total, col, row)

                x_steps = col * self._step_size_x
                y_steps = row * self._step_size_y
                self._stage.move_to(x_steps, y_steps)

                frame = self._camera.capture_frame(settle_before=True)
                if frame is None:
                    logger.warning("Failed to capture at (%d, %d)", col, row)
                    continue

                filename = IMAGE_FILENAME_PATTERN.format(col=col, row=row)
                path = self._output_dir / filename
                if self._camera.save_frame(frame, path):
                    saved_paths.append(path)

        logger.info("Scan complete. Saved %d images to %s", len(saved_paths), self._output_dir)
        return saved_paths
