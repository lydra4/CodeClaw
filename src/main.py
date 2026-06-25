import logging

import hydra
from dotenv import find_dotenv, load_dotenv
from omegaconf import DictConfig

from api.github_client import GitHubClient, GitHubClientError
from utils.general_utils import setup_logging


@hydra.main(version_base=None, config_path="../config", config_name="config.yaml")
def main(cfg: DictConfig):
    logger = logging.getLogger(__name__)
    logger.info("Setting up logging configuration.")
    setup_logging()

    load_dotenv(find_dotenv())

    try:
        github_client = GitHubClient(cfg=cfg, logger=logger)
        github_client.export_profile_context()
    except GitHubClientError as error:
        logger.error(f"{error}")
        raise SystemExit(1) from error


if __name__ == "__main__":
    main()
