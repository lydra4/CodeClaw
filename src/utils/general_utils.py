import json
import logging
import logging.config
import os
from os import PathLike
from typing import Any

import yaml

logger = logging.getLogger(__name__)


def setup_logging(
    logging_config_path: str | PathLike = "./config/logging.yaml",
    default_level: int = logging.INFO,
) -> None:
    try:
        os.makedirs("logs", exist_ok=True)
        with open(logging_config_path, encoding="utf-8") as file:
            log_config = yaml.safe_load(file.read())
        logging.config.dictConfig(log_config)

    except Exception as error:
        logging.basicConfig(
            format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
            level=default_level,
        )
        logger.info(error)
        logger.info("Logging config file is not found. Basic config is used.")


def write_json_file(filepath: str | os.PathLike, data: Any) -> None:
    directory = os.path.dirname(filepath)
    os.makedirs(name=directory, exist_ok=True)

    try:
        with open(file=filepath, mode="w", encoding="utf-8") as f:
            json.dump(obj=data, fp=f, indent=4)
            logger.info(f"Successfully exported data to {filepath}.")
    except OSError as e:
        logger.error(f"Failed to write file to {filepath}: {e}")
