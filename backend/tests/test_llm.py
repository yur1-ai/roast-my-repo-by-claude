import json
from unittest.mock import AsyncMock, patch

import pytest

from app.schemas.roast import RoastResult
from app.services.llm import LLMError, generate_json
from tests.conftest import MOCK_ROAST_RESULT


@pytest.mark.asyncio
@patch("app.services.llm.settings")
@patch("app.services.llm._call_gemini", new_callable=AsyncMock)
async def test_gemini_call_success(mock_gemini, mock_settings):
    mock_settings.llm_provider = "gemini"
    mock_settings.google_api_key = "test-key"
    mock_settings.groq_api_key = ""
    mock_gemini.return_value = json.dumps(MOCK_ROAST_RESULT)

    result = await generate_json(
        system_prompt="Test",
        user_prompt="Test",
        response_schema=RoastResult,
    )
    assert result["overall_score"] == 42
    assert result["letter_grade"] == "D"
    mock_gemini.assert_called_once()


@pytest.mark.asyncio
@patch("app.services.llm.settings")
@patch("app.services.llm._call_groq", new_callable=AsyncMock)
async def test_groq_call_success(mock_groq, mock_settings):
    mock_settings.llm_provider = "groq"
    mock_settings.google_api_key = ""
    mock_settings.groq_api_key = "test-key"
    mock_groq.return_value = json.dumps(MOCK_ROAST_RESULT)

    result = await generate_json(
        system_prompt="Test",
        user_prompt="Test",
        response_schema=RoastResult,
    )
    assert result["overall_score"] == 42
    mock_groq.assert_called_once()


@pytest.mark.asyncio
@patch("app.services.llm.settings")
@patch("app.services.llm._call_groq", new_callable=AsyncMock)
@patch("app.services.llm._call_gemini", new_callable=AsyncMock)
async def test_fallback_on_primary_failure(mock_gemini, mock_groq, mock_settings):
    mock_settings.llm_provider = "gemini"
    mock_settings.google_api_key = "test-key"
    mock_settings.groq_api_key = "test-key"

    # Gemini fails both attempts
    mock_gemini.side_effect = Exception("Gemini is down")
    # Groq succeeds
    mock_groq.return_value = json.dumps(MOCK_ROAST_RESULT)

    result = await generate_json(
        system_prompt="Test",
        user_prompt="Test",
        response_schema=RoastResult,
    )
    assert result["overall_score"] == 42
    assert mock_gemini.call_count == 2  # Two retries
    assert mock_groq.call_count == 1  # Fallback succeeds on first try


@pytest.mark.asyncio
@patch("app.services.llm.settings")
@patch("app.services.llm._call_groq", new_callable=AsyncMock)
@patch("app.services.llm._call_gemini", new_callable=AsyncMock)
async def test_all_providers_fail(mock_gemini, mock_groq, mock_settings):
    mock_settings.llm_provider = "gemini"
    mock_settings.google_api_key = "test-key"
    mock_settings.groq_api_key = "test-key"

    mock_gemini.side_effect = Exception("Gemini is down")
    mock_groq.side_effect = Exception("Groq is down")

    with pytest.raises(LLMError, match="All LLM providers failed"):
        await generate_json(
            system_prompt="Test",
            user_prompt="Test",
            response_schema=RoastResult,
        )
