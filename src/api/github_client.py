import logging
import os
from typing import Any

import requests
from omegaconf import DictConfig
from tqdm import tqdm

from utils.general_utils import write_json_file


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
        base_url: str,
        username: str,
        repo_name: str,
    ) -> dict[str, int]:
        url = f"{base_url}/repos/{username}/{repo_name}/languages"

        try:
            response = self.session.get(url=url)
            response.raise_for_status()
            return response.json()

        except requests.exceptions.RequestException as e:
            self.logger.error(f"Failed to fetch languages for {repo_name}: {e}")
            return {}

    def _get_readme(
        self,
        base_url: str,
        username: str,
        repo_name: str,
        session: requests.Session,
    ) -> str:
        url = f"{base_url}/repos/{username}/{repo_name}/readme"

        headers = dict(session.headers)
        headers["Accept"] = "application/vnd.github.raw+json"

        try:
            response = session.get(url=url, headers=headers)
            response.raise_for_status()
            return response.text
        except requests.exceptions.RequestException as e:
            self.logger.warning(
                f"No README found or failed to fetch for {repo_name}: {e}"
            )
            return ""

    def export_profile_context(self) -> None:
        self.logger.info("Starting GitHub profile context extraction.")
        repos = self._fetch_repositories(username=self.username)

        profile_context: dict[str, Any] = {
            "username": self.username,
            "total_analyzed_repos": len(repos),
            "repositories": [],
        }

        for repo in tqdm(iterable=repos):
            repo_name = repo.get("name", "")
            self.logger.info(f"Processing repository: {repo_name}")

            repo_data = {
                "name": repo_name,
                "description": repo.get("description", ""),
                "url": repo.get("html_url"),
                "languages": self._get_language_breakdown(
                    base_url=self.base_url,
                    username=self.username,
                    repo_name=repo_name,
                ),
                "readme_snippet": self._get_readme(
                    base_url=self.base_url,
                    username=self.username,
                    repo_name=repo_name,
                    session=self.session,
                )[:500],
            }
            profile_context["repositories"].append(repo_data)

        write_json_file(filepath=self.cfg.profile_export, data=profile_context)
