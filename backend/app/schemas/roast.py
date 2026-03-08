from pydantic import BaseModel, Field


class RoastRequest(BaseModel):
    repo_url: str = Field(
        ..., pattern=r"^https://github\.com/[a-zA-Z0-9\-_.]+/[a-zA-Z0-9\-_.]+/?$"
    )
    brutality_level: int = Field(..., ge=1, le=5)


class RoastSubmitResponse(BaseModel):
    id: str
    status: str
    repo_url: str
    repo_owner: str
    repo_name: str
    brutality_level: int
    created_at: str


class RepoMetadata(BaseModel):
    stars: int
    forks: int
    language: str | None
    size_kb: int
    open_issues: int
    description: str | None
    topics: list[str]
    default_branch: str
    last_push: str
    has_wiki: bool
    license: str | None


class AnalysisFinding(BaseModel):
    category: str
    severity: str
    finding: str
    evidence: str


class RoastCategory(BaseModel):
    name: str
    score: int
    emoji: str
    roast: str
    suggestions: list[str]


class RoastResult(BaseModel):
    overall_score: int
    letter_grade: str
    summary: str
    top_burns: list[str]
    categories: list[RoastCategory]


class RoastResponse(BaseModel):
    id: str
    status: str
    repo_url: str
    repo_owner: str
    repo_name: str
    brutality_level: int
    error_message: str | None = None
    repo_metadata: RepoMetadata | None = None
    roast_result: RoastResult | None = None
    overall_score: int | None = None
    letter_grade: str | None = None
    created_at: str
    completed_at: str | None = None


class RoastFeedItem(BaseModel):
    id: str
    repo_url: str
    repo_owner: str
    repo_name: str
    brutality_level: int
    overall_score: int
    letter_grade: str
    top_burns: list[str]
    repo_metadata: RepoMetadata
    completed_at: str


class RoastFeedResponse(BaseModel):
    roasts: list[RoastFeedItem]
    total: int
    limit: int
    offset: int
