import json
import logging

from app.prompts.analyze import ANALYSIS_SYSTEM_PROMPT
from app.prompts.roast import BRUTALITY_LEVELS, ROAST_SYSTEM_PROMPT
from app.schemas.roast import RepoMetadata, RoastResult
from app.services import llm

logger = logging.getLogger(__name__)

# Category weights for overall score calculation
_CATEGORY_WEIGHTS = {
    "Architecture": 1.5,
    "Code Quality": 1.5,
    "Naming & Style": 1.0,
    "Testing": 1.2,
    "Dependencies": 1.0,
    "Documentation": 1.0,
    "Security & Red Flags": 1.3,
}


def calculate_weighted_score(categories: list[dict]) -> int:
    total_weight = 0.0
    weighted_sum = 0.0
    for cat in categories:
        weight = _CATEGORY_WEIGHTS.get(cat["name"], 1.0)
        weighted_sum += cat["score"] * weight
        total_weight += weight
    if total_weight == 0:
        return 0
    return round(weighted_sum / total_weight)


def derive_grade(score: int) -> str:
    if score >= 90:
        return "S"
    elif score >= 80:
        return "A"
    elif score >= 70:
        return "B"
    elif score >= 60:
        return "C"
    elif score >= 40:
        return "D"
    else:
        return "F"


def _build_analysis_user_prompt(
    owner: str, name: str, metadata: RepoMetadata, analysis: dict
) -> str:
    parts = [
        f"Repository: {owner}/{name}",
        f"Stars: {metadata.stars} | Forks: {metadata.forks} | Language: {metadata.language}",
        f"Size: {metadata.size_kb}KB | Open Issues: {metadata.open_issues}",
        f"Description: {metadata.description or 'None'}",
        f"Topics: {', '.join(metadata.topics) if metadata.topics else 'None'}",
        f"License: {metadata.license or 'None'}",
        "",
        f"Tech Stack: {', '.join(analysis.get('tech_stack', []))}",
        f"File Count: {analysis.get('file_count', 0)}",
        f"Has Tests: {analysis.get('has_tests', False)}",
        f"Has CI: {analysis.get('has_ci', False)}",
        f"Has README: {analysis.get('has_readme', False)}",
        f"Has License: {analysis.get('has_license', False)}",
        f"Has Contributing: {analysis.get('has_contributing', False)}",
        f"Test Framework: {analysis.get('test_framework', 'None')}",
        f"CI Platform: {analysis.get('ci_platform', 'None')}",
        "",
        "=== SAMPLED FILES ===",
    ]

    for sf in analysis.get("sampled_files", []):
        parts.append(f"\n--- {sf['path']} ({sf['lines']} lines) ---")
        parts.append(sf["preview"])

    return "\n".join(parts)


def _build_roast_user_prompt(
    owner: str, name: str, analysis_findings: dict
) -> str:
    parts = [
        f"Repository: {owner}/{name}",
        "",
        "=== ANALYSIS FINDINGS ===",
        json.dumps(analysis_findings, indent=2),
    ]
    return "\n".join(parts)


# Pydantic model for analysis response validation
from pydantic import BaseModel  # noqa: E402


class _AnalysisResponse(BaseModel):
    findings: list[dict]
    tech_stack_detected: list[str]
    overall_impression: str


async def generate_roast(
    owner: str,
    name: str,
    metadata: RepoMetadata,
    analysis: dict,
    brutality_level: int,
) -> RoastResult:
    # Step 1: Deep analysis via LLM
    analysis_user_prompt = _build_analysis_user_prompt(owner, name, metadata, analysis)

    analysis_findings = await llm.generate_json(
        system_prompt=ANALYSIS_SYSTEM_PROMPT,
        user_prompt=analysis_user_prompt,
        response_schema=_AnalysisResponse,
        temperature=0.3,
    )

    # Step 2: Roast generation via LLM
    brutality_instructions = BRUTALITY_LEVELS.get(brutality_level, BRUTALITY_LEVELS[3])
    roast_system = ROAST_SYSTEM_PROMPT.format(
        brutality_level=brutality_level,
        brutality_instructions=brutality_instructions,
    )
    roast_user_prompt = _build_roast_user_prompt(owner, name, analysis_findings)

    roast_data = await llm.generate_json(
        system_prompt=roast_system,
        user_prompt=roast_user_prompt,
        response_schema=RoastResult,
        temperature=0.7,
    )

    # Recalculate score using weighted formula
    categories = roast_data.get("categories", [])
    overall_score = calculate_weighted_score(categories)
    letter_grade = derive_grade(overall_score)

    roast_data["overall_score"] = overall_score
    roast_data["letter_grade"] = letter_grade

    return RoastResult(**roast_data)
