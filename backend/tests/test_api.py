from unittest.mock import AsyncMock, patch

import pytest

from app.models.roast import Roast


@pytest.mark.asyncio
async def test_health_check(test_client):
    resp = await test_client.get("/api/health")
    assert resp.status_code == 200
    data = resp.json()
    assert data["status"] == "ok"
    assert "timestamp" in data
    assert "environment" in data


@pytest.mark.asyncio
@patch("app.routers.roast.github.verify_repo", new_callable=AsyncMock, return_value=True)
@patch("app.routers.roast.process_roast", new_callable=AsyncMock)
async def test_submit_roast_valid(mock_process, mock_verify, test_client, test_db):
    resp = await test_client.post(
        "/api/roast",
        json={"repo_url": "https://github.com/facebook/react", "brutality_level": 3},
    )
    assert resp.status_code == 202
    data = resp.json()
    assert data["status"] == "pending"
    assert data["repo_owner"] == "facebook"
    assert data["repo_name"] == "react"
    assert data["brutality_level"] == 3
    assert "id" in data
    assert "created_at" in data


@pytest.mark.asyncio
async def test_submit_roast_invalid_url(test_client, test_db):
    resp = await test_client.post(
        "/api/roast",
        json={"repo_url": "https://notgithub.com/foo/bar", "brutality_level": 3},
    )
    assert resp.status_code == 422


@pytest.mark.asyncio
@pytest.mark.parametrize("level", [0, 6, -1, 100])
async def test_submit_roast_invalid_brutality(level, test_client, test_db):
    resp = await test_client.post(
        "/api/roast",
        json={"repo_url": "https://github.com/owner/repo", "brutality_level": level},
    )
    assert resp.status_code == 422


@pytest.mark.asyncio
async def test_get_roast_not_found(test_client, test_db):
    resp = await test_client.get("/api/roast/nonexistent-id")
    assert resp.status_code == 404
    assert resp.json()["detail"] == "Roast not found"


@pytest.mark.asyncio
async def test_get_roast_pending(test_client, test_db):
    # Insert a pending roast directly
    async with test_db() as session:
        roast = Roast(
            id="pending-123",
            repo_url="https://github.com/test/repo",
            repo_owner="test",
            repo_name="repo",
            brutality_level=3,
            status="pending",
            created_at="2026-03-08T12:00:00Z",
        )
        session.add(roast)
        await session.commit()

    resp = await test_client.get("/api/roast/pending-123")
    assert resp.status_code == 200
    data = resp.json()
    assert data["status"] == "pending"
    assert data["roast_result"] is None
    assert data["overall_score"] is None


@pytest.mark.asyncio
async def test_get_roast_complete(test_client, test_db, sample_roast_dict):
    async with test_db() as session:
        roast = Roast(**sample_roast_dict)
        session.add(roast)
        await session.commit()

    resp = await test_client.get(f"/api/roast/{sample_roast_dict['id']}")
    assert resp.status_code == 200
    data = resp.json()
    assert data["status"] == "complete"
    assert data["overall_score"] == 42
    assert data["letter_grade"] == "D"
    assert data["roast_result"]["summary"] is not None
    assert len(data["roast_result"]["categories"]) == 7


@pytest.mark.asyncio
async def test_get_recent_roasts(test_client, test_db, sample_roast_dict):
    # Insert a completed roast
    async with test_db() as session:
        roast = Roast(**sample_roast_dict)
        session.add(roast)
        await session.commit()

    resp = await test_client.get("/api/roasts/recent")
    assert resp.status_code == 200
    data = resp.json()
    assert data["total"] == 1
    assert len(data["roasts"]) == 1
    assert data["roasts"][0]["repo_owner"] == "test"
    assert data["limit"] == 20
    assert data["offset"] == 0


@pytest.mark.asyncio
async def test_get_recent_roasts_empty(test_client, test_db):
    resp = await test_client.get("/api/roasts/recent")
    assert resp.status_code == 200
    data = resp.json()
    assert data["total"] == 0
    assert data["roasts"] == []
