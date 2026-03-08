# SPEC.md — RoastMyRepo (Complete Implementation Specification)

## 1. Overview

**RoastMyRepo** is a web application where users paste a public GitHub repository URL, select a "brutality level" (1-5), and receive an AI-generated comedic code roast. The AI analyzes repo structure, code patterns, and quality signals, then generates categorized roasts with scores and a shareable report card.

**Live URL**: `roastmyrepo.vercel.app` (frontend) + `roastmyrepo-api.onrender.com` (backend)

---

## 2. Tech Stack

| Layer | Technology | Reason |
|-------|-----------|--------|
| Backend | Python 3.12, FastAPI, SQLAlchemy 2.0 async, Pydantic v2 | Agent-friendly, strong typing, async-native |
| Frontend | React 18 + TypeScript, Vite, Tailwind CSS v4, shadcn/ui | Most training data, opinionated, agent-proven |
| Database | SQLite via aiosqlite | Zero config, file-based, sufficient for PoC |
| HTTP Client | httpx (async) | Async-native, replaces requests |
| LLM (Primary) | Google Gemini 2.5 Flash via `google-genai` SDK | Free tier: 250 req/day, 1M context, JSON mode |
| LLM (Fallback) | Groq via `groq` SDK | Free tier: 1000 req/day, blazing fast, Llama 4 |
| Frontend Hosting | Vercel (free tier) | Zero-config React/Vite, global CDN |
| Backend Hosting | Render (free tier) | Native Python, auto-deploy from Git |
| CI/CD | GitHub Actions | Auto-deploy on merge to `main` |
| Domain | Vercel default subdomain | Free, no custom domain needed |

---

## 3. Project Structure

```
roast-my-repo/
├── backend/
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py                    # FastAPI app entry, CORS, lifespan
│   │   ├── config.py                  # pydantic-settings based config
│   │   ├── database.py                # async engine, session factory, Base
│   │   ├── models/
│   │   │   ├── __init__.py
│   │   │   └── roast.py               # Roast SQLAlchemy model
│   │   ├── schemas/
│   │   │   ├── __init__.py
│   │   │   └── roast.py               # Pydantic request/response schemas
│   │   ├── routers/
│   │   │   ├── __init__.py
│   │   │   └── roast.py               # All /api/roast endpoints
│   │   ├── services/
│   │   │   ├── __init__.py
│   │   │   ├── github.py              # GitHub API integration
│   │   │   ├── analyzer.py            # Repo analysis orchestration
│   │   │   ├── llm.py                 # LLM abstraction (Gemini primary, Groq fallback)
│   │   │   └── roaster.py             # Roast generation pipeline
│   │   └── prompts/
│   │       ├── __init__.py
│   │       ├── analyze.py             # Analysis system prompt constant
│   │       └── roast.py               # Roast prompt + brutality variants
│   ├── tests/
│   │   ├── __init__.py
│   │   ├── conftest.py                # Shared fixtures (test client, test db)
│   │   ├── test_api.py                # API endpoint tests
│   │   ├── test_github.py             # GitHub service tests (mocked)
│   │   ├── test_analyzer.py           # Analyzer logic tests
│   │   ├── test_roaster.py            # Roast generation tests (mocked LLM)
│   │   └── test_llm.py                # LLM abstraction tests
│   ├── requirements.txt
│   ├── requirements-dev.txt
│   ├── Dockerfile
│   ├── render.yaml
│   └── pytest.ini
├── frontend/
│   ├── src/
│   │   ├── main.tsx                   # React root
│   │   ├── App.tsx                    # Router (react-router-dom v6)
│   │   ├── api/
│   │   │   └── client.ts             # Typed API client
│   │   ├── pages/
│   │   │   ├── HomePage.tsx           # Input form + recent roasts preview
│   │   │   ├── RoastPage.tsx          # Polling + result display
│   │   │   └── FeedPage.tsx           # Public roast feed
│   │   ├── components/
│   │   │   ├── ui/                    # shadcn/ui components (auto-generated)
│   │   │   ├── RoastForm.tsx          # URL input + brutality slider
│   │   │   ├── BrutalitySlider.tsx    # Custom 1-5 slider with emojis
│   │   │   ├── RoastResultCard.tsx    # Full roast result display
│   │   │   ├── CategorySection.tsx    # Single roast category (expandable)
│   │   │   ├── ScoreBadge.tsx         # Circular score display (0-100)
│   │   │   ├── GradeBadge.tsx         # Letter grade (S through F)
│   │   │   ├── TopBurns.tsx           # Top 3 burns display
│   │   │   ├── RepoMeta.tsx           # Stars/forks/language badges
│   │   │   ├── LoadingState.tsx       # Multi-step loading animation
│   │   │   ├── RoastFeedCard.tsx      # Compact card for feed
│   │   │   ├── ShareButtons.tsx       # Copy link + social share
│   │   │   ├── ErrorState.tsx         # Error display with retry
│   │   │   └── Layout.tsx             # Page layout with nav
│   │   ├── hooks/
│   │   │   ├── useSubmitRoast.ts      # POST + redirect
│   │   │   ├── useRoastPolling.ts     # Poll GET until complete
│   │   │   └── useFeed.ts            # Paginated feed query
│   │   ├── lib/
│   │   │   ├── utils.ts              # cn() helper, etc
│   │   │   └── constants.ts          # Brutality labels, grade colors
│   │   └── types/
│   │       └── roast.ts              # TypeScript types matching API schemas
│   ├── index.html
│   ├── package.json
│   ├── tsconfig.json
│   ├── tailwind.config.ts
│   ├── vite.config.ts
│   ├── vercel.json
│   └── .env.example
├── .github/
│   └── workflows/
│       ├── ci.yml                     # Run tests on PR
│       ├── deploy-backend.yml         # Deploy backend to Render on merge to main
│       └── deploy-frontend.yml        # Deploy frontend to Vercel on merge to main
├── .env.example
├── .gitignore
├── CLAUDE.md
├── SPEC.md
├── BOOTSTRAP_PROMPT.md
├── GITHUB_SECRETS_SETUP.md
├── SECRETS.md                         # Generated by agent in Phase 8
├── PROGRESS.md                        # Generated by agent in Phase 0
└── README.md
```

---

## 4. Environment Variables

### Backend (.env)
```env
# LLM Providers (at least one required)
GOOGLE_API_KEY=                     # Google AI Studio API key (free)
GROQ_API_KEY=                       # Groq API key (free)
LLM_PROVIDER=gemini                 # "gemini" or "groq" — which to use as primary

# GitHub
GITHUB_TOKEN=                       # Personal access token (optional, increases rate limit 60→5000/hr)

# App
DATABASE_URL=sqlite+aiosqlite:///./roasts.db
FRONTEND_URL=http://localhost:5173  # For CORS
ENVIRONMENT=development             # development | production
```

### Frontend (.env)
```env
VITE_API_URL=http://localhost:8000  # Backend URL
```

### How to Get API Keys (Free)
1. **Google AI Studio**: Go to https://aistudio.google.com/apikey → "Create API Key" → copy. No credit card needed.
2. **Groq**: Go to https://console.groq.com → sign up → "API Keys" → "Create" → copy. No credit card needed.
3. **GitHub Token** (optional): GitHub → Settings → Developer Settings → Personal Access Tokens → Fine-grained → create with "Public repositories (read-only)" permission.

---

## 5. Database Schema

### Table: `roasts`

```sql
CREATE TABLE roasts (
    id TEXT PRIMARY KEY,                          -- UUID as string
    repo_url TEXT NOT NULL,                       -- Full GitHub URL
    repo_owner TEXT NOT NULL,                     -- e.g., "facebook"
    repo_name TEXT NOT NULL,                      -- e.g., "react"
    brutality_level INTEGER NOT NULL CHECK (brutality_level BETWEEN 1 AND 5),
    status TEXT NOT NULL DEFAULT 'pending',        -- pending|analyzing|roasting|complete|failed
    error_message TEXT,                           -- Error details if status=failed
    repo_metadata TEXT,                           -- JSON string: repo info from GitHub API
    analysis_result TEXT,                         -- JSON string: structured analysis findings
    roast_result TEXT,                            -- JSON string: full roast output
    overall_score INTEGER,                        -- 0-100
    letter_grade TEXT,                            -- S, A, B, C, D, F
    created_at TEXT NOT NULL,                     -- ISO 8601 timestamp
    completed_at TEXT                             -- ISO 8601 timestamp
);

CREATE INDEX idx_roasts_status ON roasts(status);
CREATE INDEX idx_roasts_created ON roasts(created_at DESC);
CREATE INDEX idx_roasts_repo ON roasts(repo_owner, repo_name);
```

Note: SQLite stores JSON as TEXT. Use `json.loads()` / `json.dumps()` in Python. Pydantic handles serialization.

### Repo Metadata JSON Shape
```json
{
  "stars": 45000,
  "forks": 12000,
  "language": "TypeScript",
  "size_kb": 85000,
  "open_issues": 342,
  "description": "A JavaScript library for building user interfaces",
  "topics": ["javascript", "react", "ui"],
  "default_branch": "main",
  "last_push": "2026-03-07T18:00:00Z",
  "has_wiki": true,
  "license": "MIT"
}
```

### Analysis Result JSON Shape
```json
{
  "tech_stack": ["React", "TypeScript", "Vite", "Tailwind CSS"],
  "file_count": 342,
  "has_tests": true,
  "has_ci": true,
  "has_readme": true,
  "has_license": true,
  "has_contributing": false,
  "test_framework": "vitest",
  "ci_platform": "github_actions",
  "findings": [
    {
      "category": "architecture",
      "severity": "warning",
      "finding": "No clear separation between API and UI layers",
      "evidence": "src/ contains both API calls and components at root level"
    }
  ],
  "sampled_files": [
    {
      "path": "src/App.tsx",
      "lines": 150,
      "preview": "first 100 lines of the file..."
    }
  ]
}
```

### Roast Result JSON Shape
```json
{
  "overall_score": 42,
  "letter_grade": "D",
  "summary": "One paragraph overall roast summary.",
  "top_burns": [
    "Short punchy burn #1",
    "Short punchy burn #2",
    "Short punchy burn #3"
  ],
  "categories": [
    {
      "name": "Architecture",
      "score": 35,
      "emoji": "🏗️",
      "roast": "Detailed roast paragraph...",
      "suggestions": ["Helpful suggestion 1", "Suggestion 2"]
    },
    {
      "name": "Code Quality",
      "score": 50,
      "emoji": "💩",
      "roast": "...",
      "suggestions": ["..."]
    },
    {
      "name": "Naming & Style",
      "score": 60,
      "emoji": "🏷️",
      "roast": "...",
      "suggestions": ["..."]
    },
    {
      "name": "Testing",
      "score": 10,
      "emoji": "🧪",
      "roast": "...",
      "suggestions": ["..."]
    },
    {
      "name": "Dependencies",
      "score": 45,
      "emoji": "📦",
      "roast": "...",
      "suggestions": ["..."]
    },
    {
      "name": "Documentation",
      "score": 30,
      "emoji": "📝",
      "roast": "...",
      "suggestions": ["..."]
    },
    {
      "name": "Security & Red Flags",
      "score": 55,
      "emoji": "🚩",
      "roast": "...",
      "suggestions": ["..."]
    }
  ]
}
```

---

## 6. API Specification

Base URL: `/api`

### POST /api/roast
Submit a repo for roasting.

**Request Body:**
```json
{
  "repo_url": "https://github.com/owner/repo",
  "brutality_level": 3
}
```

**Validation Rules:**
- `repo_url`: must match regex `^https://github\.com/[a-zA-Z0-9\-_.]+/[a-zA-Z0-9\-_.]+/?$`
- `brutality_level`: integer, 1-5 inclusive
- Strip trailing slash from URL before processing

**Success Response (202 Accepted):**
```json
{
  "id": "a1b2c3d4-...",
  "status": "pending",
  "repo_url": "https://github.com/owner/repo",
  "repo_owner": "owner",
  "repo_name": "repo",
  "brutality_level": 3,
  "created_at": "2026-03-08T12:00:00Z"
}
```

**Error Responses:**
| Status | Condition | Body |
|--------|-----------|------|
| 400 | Invalid URL format | `{"detail": "Invalid GitHub repository URL. Expected format: https://github.com/owner/repo"}` |
| 400 | Invalid brutality level | `{"detail": "Brutality level must be between 1 and 5"}` |
| 404 | Repo not found on GitHub | `{"detail": "Repository not found. Make sure it exists and is public."}` |
| 429 | Rate limit exceeded | `{"detail": "Too many requests. Please wait a moment.", "retry_after": 60}` |

**Backend Flow:**
1. Validate input with Pydantic schema
2. Parse owner/repo from URL
3. HEAD request to GitHub API `https://api.github.com/repos/{owner}/{repo}` — if 404 or 403, return appropriate error
4. Generate UUID, create Roast record with status="pending"
5. Launch `asyncio.create_task(process_roast(roast_id))` 
6. Return 202 immediately

### GET /api/roast/{id}
Get roast status and results.

**Response (200 OK):**
Returns full roast object. Fields `repo_metadata`, `analysis_result`, `roast_result`, `overall_score`, `letter_grade` are null until status="complete".

See schemas section for full response shape.

**Error Responses:**
| Status | Condition | Body |
|--------|-----------|------|
| 404 | ID not found | `{"detail": "Roast not found"}` |

### GET /api/roasts/recent
Get recent completed roasts for the public feed.

**Query Parameters:**
| Param | Type | Default | Max | Description |
|-------|------|---------|-----|-------------|
| limit | int | 20 | 50 | Results per page |
| offset | int | 0 | — | Pagination offset |

**Response (200 OK):**
```json
{
  "roasts": [ /* array of roast summaries (no analysis_result field) */ ],
  "total": 150,
  "limit": 20,
  "offset": 0
}
```

Each roast in the array includes: id, repo_url, repo_owner, repo_name, brutality_level, overall_score, letter_grade, top_burns (from roast_result), repo_metadata, completed_at. Does NOT include full analysis_result or full roast_result (to keep payload small).

### GET /api/health
**Response (200 OK):**
```json
{"status": "ok", "timestamp": "2026-03-08T12:00:00Z", "environment": "production"}
```

---

## 7. Pydantic Schemas

### Request Schemas
```python
class RoastRequest(BaseModel):
    repo_url: str = Field(..., pattern=r"^https://github\.com/[a-zA-Z0-9\-_.]+/[a-zA-Z0-9\-_.]+/?$")
    brutality_level: int = Field(..., ge=1, le=5)
```

### Response Schemas
```python
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
    severity: str  # info, warning, critical
    finding: str
    evidence: str

class RoastCategory(BaseModel):
    name: str
    score: int  # 0-100
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
```

---

## 8. Backend Services — Detailed Implementation

### 8.1 LLM Service (`services/llm.py`)

Abstraction layer over Gemini and Groq. Both support JSON output mode.

```python
# Interface:
async def generate_json(system_prompt: str, user_prompt: str, response_schema: type[BaseModel]) -> dict:
    """
    Call LLM with system+user prompt, request JSON output, validate against schema.
    Uses primary provider (config.LLM_PROVIDER). If fails, retry once.
    If primary fails twice, try fallback provider once.
    Returns parsed dict on success. Raises LLMError on total failure.
    """
```

**Gemini implementation:**
- Use `google-genai` SDK (latest, supports Gemini 2.5 Flash)
- Model: `gemini-2.5-flash`
- Set `response_mime_type="application/json"` for structured output
- Max output tokens: 4096
- Temperature: 0.7 for roasts, 0.3 for analysis

**Groq implementation:**
- Use `groq` SDK
- Model: `llama-4-maverick-17b-128e-instruct` (free tier, strong quality)
- Set `response_format={"type": "json_object"}` 
- Max tokens: 4096
- Temperature: same as above

**Error handling:**
- Network timeout (30s): retry once
- Invalid JSON response: retry with appended instruction "IMPORTANT: Your previous response was not valid JSON. Respond with ONLY valid JSON, no markdown, no code blocks."
- Rate limit (429): wait 5s, retry once
- All retries exhausted: raise `LLMError` with details

### 8.2 GitHub Service (`services/github.py`)

```python
async def verify_repo(owner: str, name: str) -> bool:
    """HEAD request to /repos/{owner}/{name}. Returns True if 200, False if 404/403."""

async def fetch_repo_metadata(owner: str, name: str) -> RepoMetadata:
    """GET /repos/{owner}/{name}. Parse into RepoMetadata schema."""

async def fetch_repo_tree(owner: str, name: str, branch: str) -> list[dict]:
    """GET /repos/{owner}/{name}/git/trees/{branch}?recursive=1. Returns list of file entries."""
    # Cap at 10,000 entries. GitHub API returns max ~100k but we don't need that many.

async def fetch_file_content(owner: str, name: str, path: str) -> str | None:
    """GET /repos/{owner}/{name}/contents/{path}. Base64 decode. Returns None if >500KB or binary."""
    # Check size before fetching. Skip files > 500KB.
    # Decode base64 content. If UnicodeDecodeError, return None (binary file).
```

**All requests use httpx.AsyncClient with:**
- Base URL: `https://api.github.com`
- Headers: `Accept: application/vnd.github.v3+json`
- If GITHUB_TOKEN set: `Authorization: Bearer {token}`
- Timeout: 15s per request
- Retry on 5xx: once after 2s

### 8.3 Analyzer Service (`services/analyzer.py`)

```python
async def analyze_repo(owner: str, name: str, metadata: RepoMetadata) -> dict:
    """
    1. Fetch repo tree
    2. Determine tech stack from file extensions + config files
    3. Check for tests, CI, README, LICENSE, CONTRIBUTING
    4. Sample up to 8 key files (max 200 lines each)
    5. Return structured analysis dict
    """
```

**File sampling priority:**
1. README.md (always)
2. Main entry point: detect from package.json "main", or look for index.ts/main.py/app.py/main.go/src/lib.rs
3. Package manifest: package.json / requirements.txt / Cargo.toml / go.mod / pyproject.toml
4. Config: tsconfig.json / .eslintrc* / pyproject.toml / Dockerfile
5. Up to 4 source files from the most populated source directory (src/, lib/, app/)
   - Prefer files with most lines (likely most logic)
   - Skip test files, config files, generated files (*.min.js, *.lock, dist/)

**Tech stack detection rules:**
- `package.json` → read dependencies + devDependencies keys for React, Vue, Angular, Express, Next.js, etc.
- `requirements.txt` or `pyproject.toml` → scan for Django, Flask, FastAPI, etc.
- `Cargo.toml` → Rust + look for actix, tokio, rocket
- `go.mod` → Go + look for gin, echo, fiber
- File extension prevalence: count .ts/.tsx/.js/.jsx/.py/.rs/.go files

### 8.4 Roaster Service (`services/roaster.py`)

```python
async def generate_roast(
    owner: str, 
    name: str, 
    metadata: RepoMetadata, 
    analysis: dict, 
    brutality_level: int
) -> RoastResult:
    """
    Two-step LLM pipeline:
    1. Call LLM with analysis prompt → structured findings
    2. Call LLM with roast prompt + findings + brutality level → roast result
    Returns validated RoastResult.
    """
```

**Step 1 — Deep Analysis:**
- System prompt from `prompts/analyze.py`
- User prompt: formatted repo metadata + file tree + sampled code
- Response: structured JSON findings
- Temperature: 0.3 (we want accuracy)

**Step 2 — Roast Generation:**
- System prompt from `prompts/roast.py` with brutality-level-specific instructions
- User prompt: repo name + analysis findings from step 1
- Response: full RoastResult JSON
- Temperature: 0.7 (we want creativity)

**Score calculation:**
- `overall_score` = weighted average of category scores
  - Architecture: weight 1.5
  - Code Quality: weight 1.5
  - Testing: weight 1.2
  - Security: weight 1.3
  - All others: weight 1.0
- `letter_grade` derivation: S(90-100), A(80-89), B(70-79), C(60-69), D(40-59), F(0-39)

### 8.5 Background Pipeline (`roaster.py` or `services/pipeline.py`)

```python
async def process_roast(roast_id: str):
    """
    Full pipeline. Updates status at each step. Catches all exceptions.
    """
    try:
        # Step 1: Fetch metadata → status = "analyzing"
        update_status(roast_id, "analyzing")
        metadata = await github.fetch_repo_metadata(owner, name)
        save_metadata(roast_id, metadata)
        
        # Step 2: Analyze repo → status still "analyzing"
        analysis = await analyzer.analyze_repo(owner, name, metadata)
        save_analysis(roast_id, analysis)
        
        # Step 3: Generate roast → status = "roasting"
        update_status(roast_id, "roasting")
        roast = await roaster.generate_roast(owner, name, metadata, analysis, brutality_level)
        
        # Step 4: Save results → status = "complete"
        save_roast(roast_id, roast)
        update_status(roast_id, "complete")
    except Exception as e:
        update_status(roast_id, "failed", error_message=str(e))
```

---

## 9. LLM Prompts

### Analysis Prompt (`prompts/analyze.py`)

```python
ANALYSIS_SYSTEM_PROMPT = """You are a senior software engineer performing a thorough code review. Analyze the repository structure and code samples provided. Return a structured JSON assessment.

Focus areas:
- Architecture patterns (or lack thereof)
- Code organization and separation of concerns
- Naming conventions and consistency
- Test coverage indicators
- Dependency health (outdated, excessive, missing)
- Documentation quality
- Security red flags (hardcoded secrets patterns, SQL injection, no input validation, exposed API keys)
- Anti-patterns and code smells

Return ONLY valid JSON matching this schema:
{
  "findings": [
    {
      "category": "architecture|code_quality|naming|testing|dependencies|documentation|security",
      "severity": "info|warning|critical",
      "finding": "What you found",
      "evidence": "Specific file or code reference"
    }
  ],
  "tech_stack_detected": ["framework1", "library2"],
  "overall_impression": "2-3 sentence technical summary"
}

Be thorough. Look for real issues. Do not make up findings — only report what you can see in the provided code."""
```

### Roast Prompt (`prompts/roast.py`)

```python
ROAST_SYSTEM_PROMPT = """You are RoastBot, a legendary code reviewer known for devastating wit and sharp technical insights. Your job: roast this repository's code while being genuinely funny.

Brutality Level: {brutality_level}/5
{brutality_instructions}

RULES:
- Be funny. Genuinely witty, not mean-spirited for no reason.
- Every roast MUST contain a kernel of technical truth.
- Reference their ACTUAL code/structure — generic roasts are lazy.
- "suggestions" should be genuinely helpful despite the tone.
- Score FAIRLY. A good repo at brutality 5 still scores well; it's just roasted harder.
- top_burns must be short (under 20 words each), punchy, and quotable.
- summary should be 2-3 sentences capturing the essence of the roast.

Return ONLY valid JSON matching this exact schema:
{
  "overall_score": <int 0-100>,
  "letter_grade": "<S|A|B|C|D|F>",
  "summary": "<2-3 sentence roast summary>",
  "top_burns": ["<burn1>", "<burn2>", "<burn3>"],
  "categories": [
    {
      "name": "Architecture",
      "score": <int 0-100>,
      "emoji": "🏗️",
      "roast": "<2-3 paragraph roast>",
      "suggestions": ["<suggestion1>", "<suggestion2>"]
    },
    {"name": "Code Quality", "emoji": "💩", ...},
    {"name": "Naming & Style", "emoji": "🏷️", ...},
    {"name": "Testing", "emoji": "🧪", ...},
    {"name": "Dependencies", "emoji": "📦", ...},
    {"name": "Documentation", "emoji": "📝", ...},
    {"name": "Security & Red Flags", "emoji": "🚩", ...}
  ]
}"""

BRUTALITY_LEVELS = {
    1: "Be kind and encouraging. A supportive mentor who points out issues gently. 'You might consider...' and 'A small improvement could be...'. Still funny but warm.",
    2: "Direct but fair. Mix genuine praise with pointed criticism. Senior dev in a code review — honest, professional, occasional dry humor.",
    3: "Don't sugarcoat. Call out bad practices directly. Sarcasm and wit freely. Simon Cowell reviewing code. Acknowledge genuinely good parts.",
    4: "Go hard. Ruthlessly honest with sharp humor. Compare bad patterns to famous disasters. No participation trophies. Back up every roast with a real observation.",
    5: "Maximum roast. Gordon Ramsay reviewing code. Dramatic metaphors, devastating one-liners, creative insults. Still technically accurate — the funniest roasts are the truest ones."
}
```

---

## 10. Frontend — Page-by-Page Specification

### 10.1 Layout (`Layout.tsx`)
- Fixed top navbar: "RoastMyRepo 🔥" logo/title (links to /), "Feed" link (links to /feed)
- Main content area with max-width 1024px, centered
- Dark theme: background `zinc-950`, text `zinc-100`
- Footer: "Built to test agentic coding tools" + GitHub repo link

### 10.2 Home Page (`/`)
- **Hero section**: Large title "RoastMyRepo 🔥", subtitle "Get your code brutally reviewed by AI"
- **RoastForm component**:
  - URL input: full-width, placeholder "https://github.com/owner/repo", validates on blur
  - BrutalitySlider below: 5 steps with labels and emojis:
    - 1: 😊 Gentle
    - 2: 😏 Constructive  
    - 3: 😤 Honest
    - 4: 💀 Brutal
    - 5: 🪦 Savage
  - "Roast It 🔥" button, full-width, disabled while submitting
  - On submit: call POST /api/roast, on 202 navigate to `/roast/{id}`
  - On error: show inline error message below button
- **Recent roasts section** (below form):
  - Title: "Recent Roasts"
  - Show 5 most recent completed roasts as RoastFeedCard components
  - "See all →" link to /feed

### 10.3 Roast Page (`/roast/:id`)
- On mount: start polling GET /api/roast/{id} every 2 seconds
- Stop polling when status is "complete" or "failed"

**Loading states (based on status):**
- `pending`: "Queueing your roast... ⏳"
- `analyzing`: "Scanning the codebase... 👀" + subtle pulse animation
- `roasting`: "Generating burns... 🔥" + fire animation (CSS only)

**Complete state:**
- **Header**: RepoMeta component (owner/repo name, language badge, stars ⭐, forks 🔀)
- **Score section**: ScoreBadge (large circle with score) + GradeBadge (letter grade)
- **Top Burns**: TopBurns component — 3 highlighted quote cards in a row
- **Categories**: 7 CategorySection components in a vertical list
  - Each has: emoji + name + score bar (0-100, color-coded) + expand/collapse toggle
  - Expanded: roast text + suggestions list
  - All start expanded on desktop, collapsed on mobile
- **Share section**: ShareButtons — "Copy Link" button + "Share on X" with pre-filled text

**Failed state:**
- Error message display
- "Try Again" button (navigates back to /)

### 10.4 Feed Page (`/feed`)
- Title: "Roast Feed 🔥"
- Grid of RoastFeedCard components (2 columns desktop, 1 column mobile)
- Each card: repo name, owner, language, brutality level emojis, score badge, letter grade, top burn preview
- Click card → navigate to /roast/{id}
- "Load More" button at bottom (offset-based pagination)

### 10.5 Key Component Behaviors

**ScoreBadge**: Circular SVG ring, color transitions: green(80-100) → yellow(60-79) → orange(40-59) → red(0-39). Score number centered. Animate on mount (count up from 0).

**GradeBadge**: Letter in a rounded square. Colors: S=purple, A=green, B=blue, C=yellow, D=orange, F=red.

**BrutalitySlider**: Custom range input styled with Tailwind. Show emoji above thumb. Label text below.

**LoadingState**: Centered card with current status text, animated icon (spinner or flame), and a subtle progress hint.

---

## 11. Testing Specification

### 11.1 Backend Tests

**Framework**: pytest + pytest-asyncio + httpx (for TestClient)

**`conftest.py` fixtures:**
```python
@pytest.fixture
async def test_db():
    """Create in-memory SQLite database with tables, yield session, teardown."""

@pytest.fixture
def test_client(test_db):
    """FastAPI TestClient with test database dependency override."""

@pytest.fixture
def mock_github():
    """Mock httpx calls to GitHub API with realistic responses."""

@pytest.fixture  
def mock_llm():
    """Mock LLM service to return canned roast results."""
```

**`test_api.py` — API endpoint tests:**
1. `test_submit_roast_valid` — POST valid URL → 202 with correct shape
2. `test_submit_roast_invalid_url` — POST bad URL → 400
3. `test_submit_roast_invalid_brutality` — POST brutality=0 or 6 → 400 (use parametrize)
4. `test_get_roast_not_found` — GET nonexistent ID → 404
5. `test_get_roast_pending` — GET pending roast → 200 with null results
6. `test_get_roast_complete` — GET completed roast → 200 with full results
7. `test_get_recent_roasts` — GET /recent with data → correct pagination
8. `test_get_recent_roasts_empty` — GET /recent with no data → empty array
9. `test_health_check` — GET /health → 200 ok

**`test_github.py` — GitHub service tests (mocked HTTP):**
1. `test_verify_repo_exists` — mock 200 → True
2. `test_verify_repo_not_found` — mock 404 → False
3. `test_fetch_metadata` — mock full response → correct RepoMetadata
4. `test_fetch_tree` — mock tree → correct file list
5. `test_fetch_file_content` — mock base64 content → decoded string
6. `test_fetch_file_binary_skip` — mock non-utf8 → None

**`test_analyzer.py` — Analyzer logic tests:**
1. `test_detect_tech_stack_node` — package.json with react → ["React", ...]
2. `test_detect_tech_stack_python` — requirements.txt with fastapi → ["FastAPI", ...]
3. `test_has_tests_detection` — tree with test/ dir → has_tests=True
4. `test_has_ci_detection` — tree with .github/workflows → has_ci=True
5. `test_file_sampling_priority` — verify README sampled first, correct count

**`test_roaster.py` — Roast generation tests (mocked LLM):**
1. `test_generate_roast_success` — mock LLM returns valid JSON → RoastResult
2. `test_generate_roast_invalid_json_retry` — mock first call invalid, second valid → succeeds
3. `test_score_calculation` — verify weighted average formula
4. `test_grade_derivation` — verify score→grade mapping for all ranges

**`test_llm.py` — LLM abstraction tests:**
1. `test_gemini_call_success` — mock google-genai → correct response
2. `test_groq_call_success` — mock groq → correct response
3. `test_fallback_on_primary_failure` — mock primary fail → fallback succeeds
4. `test_all_providers_fail` — mock both fail → raises LLMError

### 11.2 Frontend Tests (optional — stretch goal)

If time permits, add basic component tests with Vitest + React Testing Library:
1. `RoastForm` renders and validates URL input
2. `ScoreBadge` displays correct score and color
3. `BrutalitySlider` changes value

---

## 12. Running Locally

### Prerequisites
- Python 3.12+
- Node.js 20+
- npm 10+

### Step-by-step

```bash
# 1. Clone the repo
git clone https://github.com/YOUR_USERNAME/roast-my-repo.git
cd roast-my-repo

# 2. Backend setup
cd backend
python -m venv venv
source venv/bin/activate          # Windows: venv\Scripts\activate
pip install -r requirements.txt
pip install -r requirements-dev.txt   # pytest, ruff, etc.

# 3. Create backend .env
cp ../.env.example .env
# Edit .env and add at minimum: GOOGLE_API_KEY or GROQ_API_KEY

# 4. Initialize database (auto-created on first run via SQLAlchemy create_all)
# No manual step needed — database.py creates tables on startup

# 5. Run backend
uvicorn app.main:app --reload --port 8000
# Verify: curl http://localhost:8000/api/health

# 6. Frontend setup (new terminal)
cd frontend
npm install

# 7. Create frontend .env
echo "VITE_API_URL=http://localhost:8000" > .env

# 8. Run frontend
npm run dev
# Opens at http://localhost:5173

# 9. Run backend tests
cd backend
pytest -v

# 10. Lint/typecheck
cd backend && ruff check .
cd frontend && npx tsc --noEmit
```

---

## 13. Deployment

### 13.1 Backend → Render (Free Tier)

**`backend/Dockerfile`:**
```dockerfile
FROM python:3.12-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY app/ ./app/
EXPOSE 8000
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

**`backend/render.yaml`:**
```yaml
services:
  - type: web
    name: roastmyrepo-api
    runtime: docker
    plan: free
    dockerfilePath: ./backend/Dockerfile
    dockerContext: ./backend
    envVars:
      - key: GOOGLE_API_KEY
        sync: false
      - key: GROQ_API_KEY
        sync: false
      - key: GITHUB_TOKEN
        sync: false
      - key: LLM_PROVIDER
        value: gemini
      - key: DATABASE_URL
        value: sqlite+aiosqlite:///./roasts.db
      - key: FRONTEND_URL
        value: https://roastmyrepo.vercel.app
      - key: ENVIRONMENT
        value: production
    healthCheckPath: /api/health
```

**Manual setup steps:**
1. Push code to GitHub
2. Go to https://dashboard.render.com → "New" → "Web Service"
3. Connect GitHub repo
4. Render auto-detects Dockerfile
5. Add environment variables (GOOGLE_API_KEY, GROQ_API_KEY, GITHUB_TOKEN)
6. Deploy

**Note on free tier**: Render free tier spins down after 15 min of inactivity. First request after sleep takes ~30s. This is acceptable for a PoC.

### 13.2 Frontend → Vercel (Free Tier)

**`frontend/vercel.json`:**
```json
{
  "buildCommand": "npm run build",
  "outputDirectory": "dist",
  "framework": "vite",
  "rewrites": [
    { "source": "/(.*)", "destination": "/index.html" }
  ]
}
```

**Manual setup steps:**
1. Go to https://vercel.com → "Add New Project"
2. Import GitHub repo
3. Set root directory to `frontend`
4. Add environment variable: `VITE_API_URL` = `https://roastmyrepo-api.onrender.com`
5. Deploy

### 13.3 CI/CD — GitHub Actions

**`.github/workflows/ci.yml`** — Runs on every PR:
```yaml
name: CI
on:
  pull_request:
    branches: [main]

jobs:
  backend-tests:
    runs-on: ubuntu-latest
    defaults:
      run:
        working-directory: backend
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: "3.12"
      - run: pip install -r requirements.txt -r requirements-dev.txt
      - run: ruff check .
      - run: pytest -v

  frontend-checks:
    runs-on: ubuntu-latest
    defaults:
      run:
        working-directory: frontend
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with:
          node-version: "20"
      - run: npm ci
      - run: npx tsc --noEmit
```

**`.github/workflows/deploy-backend.yml`** — Deploys backend to Render on merge to main:
```yaml
name: Deploy Backend
on:
  push:
    branches: [main]
    paths:
      - "backend/**"

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - name: Trigger Render Deploy
        run: |
          curl -X POST "${{ secrets.RENDER_DEPLOY_HOOK_URL }}"
```

To set this up: In Render dashboard → your service → Settings → "Deploy Hook" → copy URL → add as GitHub secret `RENDER_DEPLOY_HOOK_URL`.

**`.github/workflows/deploy-frontend.yml`** — Deploys frontend to Vercel on merge to main:
```yaml
name: Deploy Frontend
on:
  push:
    branches: [main]
    paths:
      - "frontend/**"

jobs:
  deploy:
    runs-on: ubuntu-latest
    defaults:
      run:
        working-directory: frontend
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with:
          node-version: "20"
      - run: npm ci
      - run: npx vercel pull --yes --environment=production --token=${{ secrets.VERCEL_TOKEN }}
      - run: npx vercel build --prod --token=${{ secrets.VERCEL_TOKEN }}
      - run: npx vercel deploy --prebuilt --prod --token=${{ secrets.VERCEL_TOKEN }}
    env:
      VERCEL_ORG_ID: ${{ secrets.VERCEL_ORG_ID }}
      VERCEL_PROJECT_ID: ${{ secrets.VERCEL_PROJECT_ID }}
```

### 13.4 GitHub Actions Secrets

The following secrets must be configured in the GitHub repo (Settings → Secrets → Actions):

| Secret | Purpose | Where to Get It |
|--------|---------|----------------|
| `RENDER_DEPLOY_HOOK_URL` | Trigger backend deploy | Render → Service → Settings → Deploy Hook |
| `VERCEL_TOKEN` | Authenticate Vercel CLI | Vercel → Account → Tokens → Create |
| `VERCEL_ORG_ID` | Identify Vercel account | Vercel → Settings → General → "Your ID" |
| `VERCEL_PROJECT_ID` | Identify Vercel project | Vercel → Project → Settings → "Project ID" |

See `SECRETS.md` (generated by agent in Phase 8) and `GITHUB_SECRETS_SETUP.md` for detailed setup instructions.

---

## 14. End-to-End Validation Checklist

After deployment, verify these manually:

### Backend Health
- [ ] `GET /api/health` returns 200
- [ ] CORS headers allow frontend domain

### Full Flow
- [ ] Submit a small public repo (e.g., `https://github.com/expressjs/express`)
- [ ] Poll returns status progression: pending → analyzing → roasting → complete
- [ ] Complete response has all 7 categories with scores
- [ ] Score and grade are reasonable
- [ ] Submit same repo again — works (no duplicate prevention needed for PoC)

### Error Handling
- [ ] Submit private/nonexistent repo → 404 error
- [ ] Submit invalid URL → 400 error
- [ ] Submit malformed URL (no github.com) → 400 error

### Frontend
- [ ] Home page loads, form renders
- [ ] Brutality slider works, all 5 levels selectable
- [ ] Submit triggers loading page with status updates
- [ ] Complete roast displays all categories, scores, burns
- [ ] Feed page shows recent roasts
- [ ] Clicking feed card navigates to roast
- [ ] Share button copies link to clipboard
- [ ] Mobile responsive (test at 375px width)

### Performance
- [ ] Roast completes in under 60 seconds for a small repo
- [ ] Frontend polling doesn't cause memory leaks (check dev tools)

---

## 15. Implementation Order (for the agent)

Execute these in order. Commit after each step.

1. **Backend scaffold**: FastAPI app, config, database, CORS, health endpoint
2. **Roast model + schemas**: SQLAlchemy model, all Pydantic schemas
3. **GitHub service**: verify_repo, fetch_metadata, fetch_tree, fetch_file_content
4. **LLM service**: Gemini + Groq abstraction with fallback logic
5. **Analyzer service**: tech stack detection, test/CI detection, file sampling
6. **Roast prompts**: analysis prompt + roast prompt with all 5 brutality levels
7. **Roaster service**: two-step pipeline (analyze → roast)
8. **Background pipeline**: async task orchestration with status updates
9. **API endpoints**: POST /api/roast, GET /api/roast/{id}, GET /api/roasts/recent
10. **Backend tests**: all test files per section 11
11. **Frontend scaffold**: Vite + React + Tailwind + shadcn/ui + router + API client
12. **Home page**: RoastForm with URL input + BrutalitySlider + recent roasts preview
13. **Roast page**: polling hook + LoadingState + full RoastResultCard
14. **Feed page**: paginated grid of RoastFeedCard
15. **Components polish**: ScoreBadge animation, GradeBadge colors, ShareButtons
16. **Layout + nav**: Navbar, responsive design, dark theme
17. **Error handling**: ErrorState component, retry logic, edge cases
18. **Dockerfile + render.yaml + vercel.json**: deployment configs
19. **GitHub Actions**: CI workflow + deploy workflows
20. **README.md**: setup instructions, screenshots placeholder, tech stack

---

## 16. Rate Limiting

Backend rate limiting (simple in-memory for PoC):
- Max 10 roast submissions per IP per minute
- Implement with a dict of `{ip: [timestamps]}` cleaned every 60s
- Return 429 with `retry_after` if exceeded
- In production, replace with Redis or a proper rate limiter

---

## 17. CORS Configuration

```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.FRONTEND_URL],  # Specific origin, not "*"
    allow_credentials=True,
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)
```

In development: `FRONTEND_URL=http://localhost:5173`
In production: `FRONTEND_URL=https://roastmyrepo.vercel.app`
