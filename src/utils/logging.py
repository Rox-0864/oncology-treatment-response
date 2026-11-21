"""Configuración de logging (consola + archivo con timestamp)."""

from __future__ import annotations

import logging
import os
from datetime import datetime


def setup_logging(log_dir: str = "logs", log_level: int = logging.INFO) -> None:
    os.makedirs(log_dir, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    log_file = os.path.join(log_dir, f"onco_analysis_{timestamp}.log")

    fmt = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    logging.basicConfig(
        level=log_level,
        format=fmt,
        datefmt="%Y-%m-%d %H:%M:%S",
        handlers=[
            logging.FileHandler(log_file, encoding="utf-8"),
            logging.StreamHandler(),
        ],
    )
