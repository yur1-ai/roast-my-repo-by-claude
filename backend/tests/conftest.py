import json
from unittest.mock import patch

import pytest
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.database import Base
from app.main import app
from app.models.roast import Roast  # noqa: F401 — ensure model is registered


@pytest.fixture
async def test_db():
    engine = create_async_engine("sqlite+aiosqlite://", echo=False)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    session_factory = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

    # Patch async_session in the router module so all DB operations use test DB
    with patch("app.routers.roast.async_session", session_factory):
        yield session_factory

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    await engine.dispose()


@pytest.fixture
def test_client(test_db):
    import httpx

    transport = httpx.ASGITransport(app=app)
    return httpx.AsyncClient(transport=transport, base_url="http://test")


MOCK_REPO_METADATA = {
    "stargazers_count": 45000,
    "forks_count": 12000,
    "language": "TypeScript",
    "size": 85000,
    "open_issues_count": 342,
    "description": "A test repository",
    "topics": ["javascript", "react"],
    "default_branch": "main",
    "pushed_at": "2026-03-07T18:00:00Z",
    "has_wiki": True,
    "license": {"spdx_id": "MIT", "name": "MIT License"},
}

MOCK_ROAST_RESULT = {
    "overall_score": 42,
    "letter_grade": "D",
    "summary": "This code is held together by hope and duct tape.",
    "top_burns": [
        "Your architecture is a suggestion, not a plan",
        "Tests? We don't do that here",
        "README.md: the only fiction in this repo",
    ],
    "categories": [
        {
            "name": "Architecture",
            "score": 35,
            "emoji": "\U0001f3d7\ufe0f",
            "roast": "The architecture here is like a house of cards.",
            "suggestions": ["Consider separating concerns"],
        },
        {
            "name": "Code Quality",
            "score": 50,
            "emoji": "\U0001f4a9",
            "roast": "Code quality is mediocre at best.",
            "suggestions": ["Use a linter"],
        },
        {
            "name": "Naming & Style",
            "score": 60,
            "emoji": "\U0001f3f7\ufe0f",
            "roast": "Naming is inconsistent.",
            "suggestions": ["Pick a convention and stick with it"],
        },
        {
            "name": "Testing",
            "score": 10,
            "emoji": "\U0001f9ea",
            "roast": "Testing is nonexistent.",
            "suggestions": ["Write some tests"],
        },
        {
            "name": "Dependencies",
            "score": 45,
            "emoji": "\U0001f4e6",
            "roast": "Dependencies are a mess.",
            "suggestions": ["Audit your dependencies"],
        },
        {
            "name": "Documentation",
            "score": 30,
            "emoji": "\U0001f4dd",
            "roast": "Documentation is sparse.",
            "suggestions": ["Document your API"],
        },
        {
            "name": "Security & Red Flags",
            "score": 55,
            "emoji": "\U0001f6a9",
            "roast": "Some security concerns.",
            "suggestions": ["Never hardcode secrets"],
        },
    ],
}


@pytest.fixture
def sample_roast_dict():
    return {
        "id": "test-uuid-1234",
        "repo_url": "https://github.com/test/repo",
        "repo_owner": "test",
        "repo_name": "repo",
        "brutality_level": 3,
        "status": "complete",
        "repo_metadata": json.dumps(
            {
                "stars": 45000,
                "forks": 12000,
                "language": "TypeScript",
                "size_kb": 85000,
                "open_issues": 342,
                "description": "A test repository",
                "topics": ["javascript", "react"],
                "default_branch": "main",
                "last_push": "2026-03-07T18:00:00Z",
                "has_wiki": True,
                "license": "MIT",
            }
        ),
        "analysis_result": json.dumps({"findings": [], "tech_stack": ["TypeScript"]}),
        "roast_result": json.dumps(MOCK_ROAST_RESULT),
        "overall_score": 42,
        "letter_grade": "D",
        "created_at": "2026-03-08T12:00:00Z",
        "completed_at": "2026-03-08T12:01:00Z",
    }
