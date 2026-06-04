import logging
import os

import requests
from omegaconf import DictConfig


class GitHubClient:
    def __init__(self, cfg: DictConfig, logger: logging.Logger | None) -> None:
        self.cfg = cfg
        self.logger = logger or logging.getLogger(__name__)

        self.session = requests.Session()
        self.token = os.environ["GITHUB_TOKEN"]
        self.username = os.environ["GITHUB_USERNAME"]
        self.base_url = self.cfg.base_url
