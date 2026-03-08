# PROGRESS.md — RoastMyRepo Implementation Progress

## Phase 0: Planning (v0.1.0)
**Status**: complete

### Tasks
- [x] Read SPEC.md thoroughly
- [x] Read CLAUDE.md and project conventions
- [x] Create phased implementation plan (this file)
- [x] Commit and tag v0.1.0

---

## Phase 1: Backend Foundation (v0.2.0)
**Status**: complete

### Tasks
- [x] Create `backend/` directory structure per SPEC.md section 3
- [x] `requirements.txt` + `requirements-dev.txt`
- [x] `app/config.py` — pydantic-settings based config
- [x] `app/database.py` — async SQLite engine, session factory, Base
- [x] `app/models/roast.py` — Roast SQLAlchemy model (all columns + indexes)
- [x] `app/schemas/roast.py` — All Pydantic request/response schemas
- [x] `app/main.py` — FastAPI app with lifespan, CORS, `/api/health`
- [x] `pytest.ini` configuration
- [x] Verify: uvicorn starts, `/api/health` returns 200

---

## Phase 2: Backend Services (v0.3.0)
**Status**: complete

### Tasks
- [x] `services/github.py` — verify_repo, fetch_repo_metadata, fetch_repo_tree, fetch_file_content
- [x] `services/llm.py` — Gemini + Groq abstraction with fallback, LLMError, generate_json
- [x] `services/analyzer.py` — analyze_repo with tech stack detection, file sampling
- [x] `prompts/analyze.py` — ANALYSIS_SYSTEM_PROMPT
- [x] `prompts/roast.py` — ROAST_SYSTEM_PROMPT + BRUTALITY_LEVELS dict
- [x] `services/roaster.py` — Two-step pipeline, score calculation, grade derivation

---

## Phase 3: Backend API + Pipeline (v0.4.0)
**Status**: complete

### Tasks
- [x] Background pipeline `process_roast()` with status progression
- [x] `routers/roast.py` — POST /api/roast, GET /api/roast/{id}, GET /api/roasts/recent
- [x] Rate limiting (in-memory, 10 req/IP/min)
- [x] CORS configuration per spec

---

## Phase 4: Backend Tests (v0.5.0)
**Status**: complete

### Tasks
- [x] `tests/conftest.py` — test_db with session patching, mock fixtures
- [x] `tests/test_api.py` — 12 endpoint tests (including parametrized)
- [x] `tests/test_github.py` — 6 GitHub service tests with mocked HTTP
- [x] `tests/test_analyzer.py` — 5 analyzer logic tests
- [x] `tests/test_roaster.py` — 4 roast generation tests with mocked LLM
- [x] `tests/test_llm.py` — 4 LLM abstraction tests
- [x] All 31 tests pass, zero ruff violations

---

## Phase 5: Frontend Foundation (v0.6.0)
**Status**: complete

### Tasks
- [x] Scaffold Vite + React + TypeScript
- [x] Tailwind CSS v4 with @tailwindcss/vite plugin
- [x] shadcn/ui with button, card, input, slider, badge components
- [x] react-router-dom v6 with routes (/, /roast/:id, /feed)
- [x] Typed API client, TypeScript types, Layout, constants
- [x] Dark theme by default
- [x] tsc --noEmit passes, build succeeds

---

## Phase 6: Frontend Pages (v0.7.0)
**Status**: complete

### Tasks
- [x] All components: BrutalitySlider, RoastForm, ScoreBadge, GradeBadge, TopBurns, CategorySection, RepoMeta, RoastResultCard, RoastFeedCard, LoadingState, ShareButtons, ErrorState
- [x] All hooks: useSubmitRoast, useRoastPolling, useFeed
- [x] All pages: HomePage (hero + form + recent), RoastPage (polling + result), FeedPage (grid + pagination)

---

## Phase 7: Polish + Error Handling (v0.8.0)
**Status**: complete

### Tasks
- [x] Error states on all pages (form, API, network, failed roast)
- [x] Loading animations (pulse, bounce, spinning dots)
- [x] Share functionality (copy link + share on X)
- [x] Responsive design (mobile-first, md breakpoints)
- [x] tsc --noEmit passes cleanly

---

## Phase 8: CI/CD + Deployment Config (v0.9.0)
**Status**: complete

### Tasks
- [x] `.github/workflows/ci.yml` — backend lint+test, frontend typecheck
- [x] `.github/workflows/deploy-backend.yml` — Render deploy hook
- [x] `.github/workflows/deploy-frontend.yml` — Vercel CLI deploy
- [x] `backend/Dockerfile`, `backend/render.yaml`, `frontend/vercel.json`
- [x] `SECRETS.md` — documents all 4 required GitHub Actions secrets
- [x] CI passes on first push to main

---

## Phase 9: Final (v1.0.0)
**Status**: complete

### Tasks
- [x] README.md — project description, tech stack, setup, deployment
- [x] Final PROGRESS.md update (all phases complete)
- [x] Final verification: 31 pytest tests pass
- [x] Final verification: tsc --noEmit clean
- [x] Tag v1.0.0 and push

---

## Decisions Log

| Decision | Rationale |
|----------|-----------|
| Used `uv` for Python dependency management | User preference in CLAUDE.md |
| Python 3.14 locally, 3.12 in CI/Docker | Latest stable in CI, latest available locally |
| shadcn/ui uses @base-ui/react Slider | shadcn v4 migrated to base-ui primitives |
| Dark-only theme (no light mode toggle) | Spec says dark theme, no toggle mentioned |
| async_session patching in tests | Router uses async_session directly, not DI |
| CI triggers on push to main + PRs | Covers both direct pushes and PR workflows |
| Deploy workflows use env vars for secrets | Security best practice per GH Actions guidelines |
