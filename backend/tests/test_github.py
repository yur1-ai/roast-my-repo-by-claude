import base64
from unittest.mock import AsyncMock, patch

import httpx
import pytest

from app.services import github


def _mock_response(status_code=200, json_data=None):
    req = httpx.Request("GET", "http://test")
    if json_data is not None:
        return httpx.Response(status_code, json=json_data, request=req)
    return httpx.Response(status_code, request=req)


@pytest.mark.asyncio
@patch("app.services.github._request", new_callable=AsyncMock)
async def test_verify_repo_exists(mock_request):
    mock_request.return_value = _mock_response(200)
    result = await github.verify_repo("facebook", "react")
    assert result is True


@pytest.mark.asyncio
@patch("app.services.github._request", new_callable=AsyncMock)
async def test_verify_repo_not_found(mock_request):
    mock_request.return_value = _mock_response(404)
    result = await github.verify_repo("nonexistent", "repo")
    assert result is False


@pytest.mark.asyncio
@patch("app.services.github._request", new_callable=AsyncMock)
async def test_fetch_metadata(mock_request):
    from tests.conftest import MOCK_REPO_METADATA

    mock_request.return_value = _mock_response(200, json_data=MOCK_REPO_METADATA)
    metadata = await github.fetch_repo_metadata("test", "repo")
    assert metadata.stars == 45000
    assert metadata.forks == 12000
    assert metadata.language == "TypeScript"
    assert metadata.license == "MIT"
    assert metadata.default_branch == "main"


@pytest.mark.asyncio
@patch("app.services.github._request", new_callable=AsyncMock)
async def test_fetch_tree(mock_request):
    tree_data = {
        "tree": [
            {"path": "README.md", "type": "blob", "size": 1000},
            {"path": "src", "type": "tree"},
            {"path": "src/index.ts", "type": "blob", "size": 500},
        ]
    }
    mock_request.return_value = _mock_response(200, json_data=tree_data)
    tree = await github.fetch_repo_tree("test", "repo", "main")
    assert len(tree) == 3
    assert tree[0]["path"] == "README.md"


@pytest.mark.asyncio
@patch("app.services.github._request", new_callable=AsyncMock)
async def test_fetch_file_content(mock_request):
    content = "console.log('hello');"
    encoded = base64.b64encode(content.encode()).decode()
    mock_request.return_value = _mock_response(
        200, json_data={"content": encoded, "size": len(content)}
    )
    result = await github.fetch_file_content("test", "repo", "index.js")
    assert result == content


@pytest.mark.asyncio
@patch("app.services.github._request", new_callable=AsyncMock)
async def test_fetch_file_binary_skip(mock_request):
    # Simulate binary content that can't be decoded as UTF-8
    binary = bytes([0xFF, 0xFE, 0x00, 0x01])
    encoded = base64.b64encode(binary).decode()
    mock_request.return_value = _mock_response(
        200, json_data={"content": encoded, "size": len(binary)}
    )
    result = await github.fetch_file_content("test", "repo", "image.png")
    assert result is None
