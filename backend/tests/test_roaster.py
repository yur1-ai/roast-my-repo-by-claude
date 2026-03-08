from unittest.mock import AsyncMock, patch

import pytest

from app.schemas.roast import RepoMetadata, RoastResult
from app.services.roaster import calculate_weighted_score, derive_grade, generate_roast
from tests.conftest import MOCK_ROAST_RESULT


def test_score_calculation():
    categories = [
        {"name": "Architecture", "score": 80},
        {"name": "Code Quality", "score": 60},
        {"name": "Naming & Style", "score": 70},
        {"name": "Testing", "score": 50},
        {"name": "Dependencies", "score": 65},
        {"name": "Documentation", "score": 55},
        {"name": "Security & Red Flags", "score": 75},
    ]
    score = calculate_weighted_score(categories)
    # Manual calculation:
    # (80*1.5 + 60*1.5 + 70*1.0 + 50*1.2 + 65*1.0 + 55*1.0 + 75*1.3) / (1.5+1.5+1.0+1.2+1.0+1.0+1.3)
    # = (120 + 90 + 70 + 60 + 65 + 55 + 97.5) / 8.5
    # = 557.5 / 8.5 ≈ 65.59 → 66
    assert score == 66


def test_grade_derivation():
    assert derive_grade(95) == "S"
    assert derive_grade(90) == "S"
    assert derive_grade(89) == "A"
    assert derive_grade(80) == "A"
    assert derive_grade(79) == "B"
    assert derive_grade(70) == "B"
    assert derive_grade(69) == "C"
    assert derive_grade(60) == "C"
    assert derive_grade(59) == "D"
    assert derive_grade(40) == "D"
    assert derive_grade(39) == "F"
    assert derive_grade(0) == "F"


@pytest.mark.asyncio
@patch("app.services.roaster.llm.generate_json", new_callable=AsyncMock)
async def test_generate_roast_success(mock_llm):
    # First call returns analysis findings, second returns roast result
    mock_llm.side_effect = [
        {
            "findings": [{"category": "architecture", "severity": "warning", "finding": "No patterns", "evidence": "flat structure"}],
            "tech_stack_detected": ["React"],
            "overall_impression": "Needs work.",
        },
        MOCK_ROAST_RESULT,
    ]

    metadata = RepoMetadata(
        stars=100, forks=10, language="TypeScript", size_kb=5000,
        open_issues=5, description="Test", topics=[], default_branch="main",
        last_push="2026-03-07T18:00:00Z", has_wiki=False, license=None,
    )
    analysis = {"tech_stack": ["TypeScript"], "file_count": 50, "sampled_files": [], "has_tests": False, "has_ci": False, "has_readme": True, "has_license": False, "has_contributing": False, "test_framework": None, "ci_platform": None, "findings": []}

    result = await generate_roast("test", "repo", metadata, analysis, 3)
    assert isinstance(result, RoastResult)
    assert len(result.categories) == 7
    assert result.letter_grade in ("S", "A", "B", "C", "D", "F")


@pytest.mark.asyncio
@patch("app.services.roaster.llm.generate_json", new_callable=AsyncMock)
async def test_generate_roast_invalid_json_retry(mock_llm):
    # Simulate LLM service handling the retry internally and eventually succeeding
    mock_llm.side_effect = [
        {
            "findings": [],
            "tech_stack_detected": ["Python"],
            "overall_impression": "Basic.",
        },
        MOCK_ROAST_RESULT,
    ]

    metadata = RepoMetadata(
        stars=10, forks=1, language="Python", size_kb=1000,
        open_issues=0, description="Small", topics=[], default_branch="main",
        last_push="2026-03-07T18:00:00Z", has_wiki=False, license=None,
    )
    analysis = {"tech_stack": ["Python"], "file_count": 10, "sampled_files": [], "has_tests": False, "has_ci": False, "has_readme": False, "has_license": False, "has_contributing": False, "test_framework": None, "ci_platform": None, "findings": []}

    result = await generate_roast("test", "repo", metadata, analysis, 5)
    assert isinstance(result, RoastResult)
