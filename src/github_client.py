"""Shared GitHub REST/GraphQL client with auth, pagination and rate-limit handling.

All other scripts in this project import from here instead of calling
`requests` directly, so retry/backoff/auth logic lives in exactly one place.
"""
from __future__ import annotations

import os
import time
from typing import Any, Iterator

import requests
from dotenv import load_dotenv

load_dotenv()

GITHUB_TOKEN = os.environ.get("GITHUB_TOKEN")
GITHUB_ORG = os.environ.get("GITHUB_ORG", "BAITC-Hacks")

if not GITHUB_TOKEN or GITHUB_TOKEN.startswith("your_"):
    raise RuntimeError(
        "GITHUB_TOKEN is not set. Copy .env.example to .env and fill in a real "
        "GitHub Personal Access Token."
    )

REST_API = "https://api.github.com"
GRAPHQL_API = "https://api.github.com/graphql"

_session = requests.Session()
_session.headers.update(
    {
        "Authorization": f"Bearer {GITHUB_TOKEN}",
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": "2022-11-28",
        "User-Agent": "hackalemai-datamining/1.0",
    }
)

MAX_RETRIES = 6


class GraphQLError(Exception):
    """Raised when the GraphQL API returns an `errors` array."""

    def __init__(self, errors: list[dict[str, Any]]):
        self.errors = errors
        super().__init__(str(errors))


def _sleep_for_rate_limit(response: requests.Response) -> bool:
    """If the response indicates a rate limit, sleep and return True."""
    if response.status_code == 403 or response.status_code == 429:
        remaining = response.headers.get("X-RateLimit-Remaining")
        retry_after = response.headers.get("Retry-After")
        if retry_after is not None:
            wait = float(retry_after) + 1
            print(f"[rate-limit] secondary limit hit, sleeping {wait:.0f}s")
            time.sleep(wait)
            return True
        if remaining == "0":
            reset = response.headers.get("X-RateLimit-Reset")
            if reset:
                wait = max(float(reset) - time.time(), 1) + 2
                print(f"[rate-limit] primary limit hit, sleeping {wait:.0f}s")
                time.sleep(wait)
                return True
    return False


def rest_get(url: str, params: dict | None = None) -> requests.Response:
    """GET with retry/backoff on rate limits and transient 5xx errors."""
    last_exc: Exception | None = None
    for attempt in range(MAX_RETRIES):
        try:
            resp = _session.get(url, params=params, timeout=30)
        except requests.RequestException as exc:
            last_exc = exc
            time.sleep(2**attempt)
            continue
        if _sleep_for_rate_limit(resp):
            continue
        if resp.status_code >= 500:
            time.sleep(2**attempt)
            continue
        return resp
    if last_exc:
        raise last_exc
    raise RuntimeError(f"Exhausted retries for GET {url}")


def rest_get_paginated(path: str, params: dict | None = None) -> Iterator[dict]:
    """Yield individual JSON items across all pages of a REST list endpoint."""
    url = f"{REST_API}{path}"
    page_params = dict(params or {})
    page_params.setdefault("per_page", 100)
    page = 1
    while True:
        page_params["page"] = page
        resp = rest_get(url, params=page_params)
        resp.raise_for_status()
        items = resp.json()
        if not items:
            break
        for item in items:
            yield item
        if len(items) < page_params["per_page"]:
            break
        page += 1


def graphql_request(query: str, variables: dict | None = None) -> dict:
    """POST a GraphQL query with retry/backoff. Raises GraphQLError on API errors."""
    payload = {"query": query, "variables": variables or {}}
    last_exc: Exception | None = None
    for attempt in range(MAX_RETRIES):
        try:
            resp = _session.post(GRAPHQL_API, json=payload, timeout=60)
        except requests.RequestException as exc:
            last_exc = exc
            time.sleep(2**attempt)
            continue
        if _sleep_for_rate_limit(resp):
            continue
        if resp.status_code >= 500:
            time.sleep(2**attempt)
            continue
        resp.raise_for_status()
        body = resp.json()
        if "errors" in body and body["errors"]:
            raise GraphQLError(body["errors"])
        return body["data"]
    if last_exc:
        raise last_exc
    raise RuntimeError("Exhausted retries for GraphQL request")
