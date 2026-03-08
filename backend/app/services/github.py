import base64

import httpx

from app.config import settings
from app.schemas.roast import RepoMetadata

_GITHUB_API = "https://api.github.com"
_TIMEOUT = 15.0


def _headers() -> dict[str, str]:
    h = {"Accept": "application/vnd.github.v3+json"}
    if settings.github_token:
        h["Authorization"] = f"Bearer {settings.github_token}"
    return h


async def _request(method: str, path: str) -> httpx.Response:
    async with httpx.AsyncClient(
        base_url=_GITHUB_API, headers=_headers(), timeout=_TIMEOUT
    ) as client:
        resp = await client.request(method, path)
        if resp.status_code >= 500:
            # Retry once on server errors
            await _sleep(2)
            resp = await client.request(method, path)
        return resp


async def _sleep(seconds: float) -> None:
    import asyncio

    await asyncio.sleep(seconds)


async def verify_repo(owner: str, name: str) -> bool:
    resp = await _request("HEAD", f"/repos/{owner}/{name}")
    return resp.status_code == 200


async def fetch_repo_metadata(owner: str, name: str) -> RepoMetadata:
    resp = await _request("GET", f"/repos/{owner}/{name}")
    resp.raise_for_status()
    data = resp.json()

    license_name = None
    if data.get("license") and isinstance(data["license"], dict):
        license_name = data["license"].get("spdx_id") or data["license"].get("name")

    return RepoMetadata(
        stars=data.get("stargazers_count", 0),
        forks=data.get("forks_count", 0),
        language=data.get("language"),
        size_kb=data.get("size", 0),
        open_issues=data.get("open_issues_count", 0),
        description=data.get("description"),
        topics=data.get("topics", []),
        default_branch=data.get("default_branch", "main"),
        last_push=data.get("pushed_at", ""),
        has_wiki=data.get("has_wiki", False),
        license=license_name,
    )


async def fetch_repo_tree(owner: str, name: str, branch: str) -> list[dict]:
    resp = await _request(
        "GET", f"/repos/{owner}/{name}/git/trees/{branch}?recursive=1"
    )
    resp.raise_for_status()
    data = resp.json()
    entries = data.get("tree", [])
    # Cap at 10,000 entries
    return entries[:10_000]


async def fetch_file_content(owner: str, name: str, path: str) -> str | None:
    resp = await _request("GET", f"/repos/{owner}/{name}/contents/{path}")
    if resp.status_code != 200:
        return None

    data = resp.json()

    # Skip files > 500KB
    if data.get("size", 0) > 500_000:
        return None

    content_b64 = data.get("content")
    if not content_b64:
        return None

    try:
        return base64.b64decode(content_b64).decode("utf-8")
    except (UnicodeDecodeError, ValueError):
        return None
