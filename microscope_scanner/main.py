"""
Microscope tiling system entrypoint.
Coordinates stage movement and image capture in a grid pattern.
"""

import logging
import sys

from .camera_controller import CameraController
from .config import (
    CAMERA_INDEX,
    CAMERA_HEIGHT,
    CAMERA_WIDTH,
    GRID_HEIGHT,
    GRID_WIDTH,
    IMAGE_SAVE_DIRECTORY,
    SERIAL_PORT,
    SETTLE_TIME,
    STEP_SIZE_X,
    STEP_SIZE_Y,
)
from .scanner import GridScanner
from .stage_controller import StageController
from .utils import setup_logging

logger = logging.getLogger(__name__)


def main() -> int:
    """Initialize hardware, run grid scan, then shut down."""
    setup_logging()

    stage = StageController()
    camera = CameraController(
        camera_index=CAMERA_INDEX,
        width=CAMERA_WIDTH,
        height=CAMERA_HEIGHT,
        settle_time=SETTLE_TIME,
    )

    try:
        stage.connect(port=SERIAL_PORT)
        camera.open()
    except Exception as e:
        logger.error("Initialization failed: %s", e)
        return 1

    try:
        scanner = GridScanner(
            stage=stage,
            camera=camera,
            grid_width=GRID_WIDTH,
            grid_height=GRID_HEIGHT,
            step_size_x=STEP_SIZE_X,
            step_size_y=STEP_SIZE_Y,
            output_dir=IMAGE_SAVE_DIRECTORY,
        )
        stage.home()
        scanner.run()
    except KeyboardInterrupt:
        logger.info("Interrupted by user")
        return 130
    finally:
        stage.close()
        camera.close()

    return 0

if __name__ == "__main__":
    sys.exit(main())
