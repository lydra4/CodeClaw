import logging
import os
from typing import Any

import requests
from omegaconf import DictConfig
from tqdm import tqdm

from utils.general_utils import write_json_file


class GitHubClientError(RuntimeError):
    """A user-facing GitHub client failure."""


class GitHubClient:
    def __init__(self, cfg: DictConfig, logger: logging.Logger | None) -> None:
        self.cfg = cfg
        self.logger = logger or logging.getLogger(__name__)
        self.base_url = str(self.cfg.base_url).rstrip("/")

        self.username = self._required_environment(name="GITHUB_USERNAME")
        self.token = self._required_environment(name="GITHUB_TOKEN")

        self.session = requests.Session()
        self.session.headers.update(
            {
                "Authorization": f"Bearer {self.token}",
                "Accept": "application/vnd.github.v+json",
                "X-Github-Api-Version": "2026-03-10",
                "User-Agent": "CodeClaw",
            }
        )

    @staticmethod
    def _required_environment(name: str) -> str:
        value = os.getenv(name, "").strip()

        if not value:
            raise GitHubClientError(f"{name} is missing. Add it to the root .env file.")

        return value

    def _request(
        self,
        url: str,
        *,
        params: dict[str, Any] | None = None,
        headers: dict[str, str] | None = None,
    ) -> requests.Response:
        try:
            response = self.session.get(
                url=url, params=params, headers=headers, timeout=30
            )

        except requests.exceptions.RequestException as error:
            raise GitHubClientError(
                "Could not connect to GitHub. Check your internet connection."
            ) from error

        if response.status_code == 401:
            raise GitHubClientError(
                "GitHub rejected GITHUB_TOKEN. It may be invalid or expired."
            )

        if response.status_code == 403:
            remaining = response.headers.get("X-RateLimit-Remaining")

            if remaining == "0":
                raise GitHubClientError(
                    "GitHub's API rate limit has been reached. Try again later."
                )

            raise GitHubClientError(
                "GitHub denied access. Check the token's repository permissions."
            )

        try:
            response.raise_for_status()
        except requests.exceptions.HTTPError as error:
            raise GitHubClientError(
                f"GitHub request failed with status {response.status_code}."
            ) from error

        return response

    def _validate_credentials(self) -> None:
        response = self._request(url=f"{self.base_url}/user")
        payload = response.json()

        if not isinstance(payload, dict):
            raise GitHubClientError("GitHub return an unexpected /user response.")

        authenticated_user = payload.get("login", "")

        if authenticated_user.casefold() != self.username.casefold():
            raise GitHubClientError(
                "GITHUB_USERNAME does not match the owner of GITHUB_TOKEN. "
                f"The token belongs to '{authenticated_user}'."
            )

        self.logger.info("GitHub credentials validated successfully.")

    def _fetch_repositories(self) -> list[dict[str, Any]]:
        self.logger.info(f"Fetching repositories for user: {self.username}.")

        url: str | None = f"{self.base_url}/user/repos"
        params: dict[str, Any] | None = {
            "affiliation": "owner",
            "visibility": "all",
            "sort": "updated",
            "direction": "desc",
            "per_page": 100,
        }
        repositories: list[dict[str, Any]] = []

        while url:
            response = self._request(url=url, params=params)
            payload = response.json()

            if not isinstance(payload, list):
                raise GitHubClientError(
                    "GitHub returned an unexpected repository response."
                )

            repositories.extend(payload)
            url = response.links.get("next", {}).get("url")

            params = None

        self.logger.info(f"Found {len(repositories)} repositories.")
        return repositories

    def _get_language_breakdown(self, full_name: str) -> dict[str, int]:
        try:
            response = self._request(f"{self.base_url}/repos/{full_name}/languages")
            payload = response.json()

            if isinstance(payload, dict):
                return payload

        except GitHubClientError as error:
            self.logger.warning(f"Could not fetch languages for {full_name}: {error}")

        return {}

    def _get_readme(self, full_name: str) -> str:
        headers = dict(self.session.headers)
        headers["Accept"] = "application/vnd.github.raw+json"

        try:
            response = self.session.get(
                url=f"{self.base_url}/repos/{full_name}/readme",
                headers=headers,
                timeout=30,
            )

            if response.status_code == 404:
                self.logger.info(f"No README found for {full_name}")
                return ""

            if response.status_code == 401:
                raise GitHubClientError(
                    "GitHub rejected GITHUB_TOKEN while reading repositories."
                )

            if response.status_code == 403:
                self.logger.warning(
                    f"The token cannot read the README for {full_name}."
                )
                return ""

            response.raise_for_status()
            return response.text

        except requests.exceptions.RequestException as error:
            self.logger.warning(f"Could not fetch README for {full_name}: {error}")
            return ""

    def export_profile_context(self) -> None:
        self.logger.info("Starting GitHub profile extraction.")

        self._validate_credentials()

        repositories = self._fetch_repositories()

        profile_context: dict[str, Any] = {
            "username": self.username,
            "total_analyzed_repos": len(repositories),
            "repositories": [],
        }

        for repository in tqdm(iterable=repositories):
            name = repository.get("name", "")
            full_name = repository.get("full_name", "")

            if not name or not full_name:
                self.logger.warning("Skipping malformed repository response.")
                continue

            profile_context["repositories"].append(
                {
                    "name": name,
                    "description": repository.get("description") or "",
                    "url": repository.get("html_url", ""),
                    "private": repository.get("private", False),
                    "size": repository.get("size", 0),
                    "stargazers_count": repository.get("stargazers_count", 0),
                    "created_at": repository.get("created_at", ""),
                    "updated_at": repository.get("updated_at", ""),
                    "languages": self._get_language_breakdown(full_name=full_name),
                    "readme_snippet": self._get_readme(full_name=full_name)[:500],
                }
            )

        write_json_file(filepath=self.cfg.profile_export, data=profile_context)

        self.logger.info(f"Profile exported to {self.cfg.profile_export}.")
