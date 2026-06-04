import logging
import os
from typing import Any

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

        self.session.headers.update(
            {
                "Authorization": f"Bearer {self.token}",
                "Accept": "application/vnd.github.v+json",
                "X-Github-Api-Version": "2026-03-10",
            }
        )
        self.logger.info("GitHubClient initialized with secure token authentication.")

    def _fetch_repositories(self, username: str) -> list[dict[str, Any]]:
        self.logger.info(f"Fetching repositories for user: {username}.")

        url: str | None = (
            f"{self.base_url}/users/{username}/repos?sort=updated&per_page=100"
        )

        all_repos = []

        try:
            while url:
                response = self.session.get(url=url)
                response.raise_for_status()
                all_repos.extend(response.json())

                url = response.links.get("next", {}).get("url")

            self.logger.info(
                f"Successfully fetched {len(all_repos)} total repositories."
            )
            return all_repos

        except requests.exceptions.RequestException as e:
            self.logger.error(f"Failed to fetch repositories: {e}")
            return all_repos

    def _get_language_breakdown(
        self,
        repo_name: str,
        base_url: str,
        username: str,
    ) -> dict[str, int]:
        url = f"{base_url}/repos/{username}/{repo_name}/languages"

        try:
            response = self.session.get(url=url)
            response.raise_for_status()
            return response.json()

        except requests.exceptions.RequestException as e:
            self.logger.error(f"Failed to fetch languages for {repo_name}: {e}")
            return {}
