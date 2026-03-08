import json
import logging

from pydantic import BaseModel

from app.config import settings

logger = logging.getLogger(__name__)


class LLMError(Exception):
    pass


async def _call_gemini(
    system_prompt: str,
    user_prompt: str,
    temperature: float = 0.7,
) -> str:
    from google import genai

    client = genai.Client(api_key=settings.google_api_key)
    response = await client.aio.models.generate_content(
        model="gemini-2.5-flash",
        contents=user_prompt,
        config=genai.types.GenerateContentConfig(
            system_instruction=system_prompt,
            temperature=temperature,
            max_output_tokens=4096,
            response_mime_type="application/json",
        ),
    )
    return response.text


async def _call_groq(
    system_prompt: str,
    user_prompt: str,
    temperature: float = 0.7,
) -> str:
    from groq import AsyncGroq

    client = AsyncGroq(api_key=settings.groq_api_key)
    response = await client.chat.completions.create(
        model="llama-4-maverick-17b-128e-instruct",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
        temperature=temperature,
        max_tokens=4096,
        response_format={"type": "json_object"},
    )
    return response.choices[0].message.content


def _get_providers() -> list[str]:
    primary = settings.llm_provider
    fallback = "groq" if primary == "gemini" else "gemini"
    return [primary, fallback]


async def _call_provider(
    provider: str,
    system_prompt: str,
    user_prompt: str,
    temperature: float,
) -> str:
    if provider == "gemini":
        return await _call_gemini(system_prompt, user_prompt, temperature)
    elif provider == "groq":
        return await _call_groq(system_prompt, user_prompt, temperature)
    else:
        raise LLMError(f"Unknown provider: {provider}")


def _parse_json(text: str) -> dict:
    # Strip markdown code fences if present
    cleaned = text.strip()
    if cleaned.startswith("```"):
        lines = cleaned.split("\n")
        lines = lines[1:]  # remove opening fence
        if lines and lines[-1].strip() == "```":
            lines = lines[:-1]
        cleaned = "\n".join(lines)
    return json.loads(cleaned)


async def generate_json(
    system_prompt: str,
    user_prompt: str,
    response_schema: type[BaseModel],
    temperature: float = 0.7,
) -> dict:
    providers = _get_providers()
    last_error = None

    for provider in providers:
        # Check if this provider has an API key configured
        if provider == "gemini" and not settings.google_api_key:
            continue
        if provider == "groq" and not settings.groq_api_key:
            continue

        for attempt in range(2):
            try:
                prompt = system_prompt
                if attempt == 1:
                    prompt += (
                        "\n\nIMPORTANT: Your previous response was not valid JSON. "
                        "Respond with ONLY valid JSON, no markdown, no code blocks."
                    )

                text = await _call_provider(provider, prompt, user_prompt, temperature)
                data = _parse_json(text)

                # Validate against schema
                response_schema(**data)
                return data

            except json.JSONDecodeError as e:
                last_error = e
                logger.warning(
                    "Invalid JSON from %s (attempt %d): %s", provider, attempt + 1, e
                )
                continue
            except Exception as e:
                last_error = e
                logger.warning(
                    "Error from %s (attempt %d): %s", provider, attempt + 1, e
                )
                if attempt == 0:
                    import asyncio

                    await asyncio.sleep(2)
                continue

        logger.warning("Provider %s exhausted, trying fallback", provider)

    raise LLMError(f"All LLM providers failed. Last error: {last_error}")
