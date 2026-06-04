import logging

import hydra
from dotenv import find_dotenv, load_dotenv
from omegaconf import DictConfig

from utils.general_utils import setup_logging


@hydra.main(version_base=None, config_path="../config", config_name="config.yaml")
def main(cfg: DictConfig):
    logger = logging.getLogger(__name__)
    logger.info("Setting up logging configuration.")
    setup_logging()

    load_dotenv(find_dotenv())
    # github_client = GitHubClient(cfg=cfg, logger=logger)


if __name__ == "__main__":
    main()
