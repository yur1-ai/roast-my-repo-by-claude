# PROGRESS.md — RoastMyRepo Implementation Progress

## Phase 0: Planning (v0.1.0)
**Status**: complete

### Tasks
- [x] Read SPEC.md thoroughly
- [x] Read CLAUDE.md and project conventions
- [x] Create phased implementation plan (this file)
- [x] Commit and tag v0.1.0

### Acceptance Criteria
- PROGRESS.md exists with all phases documented
- Tagged v0.1.0

---

## Phase 1: Backend Foundation (v0.2.0)
**Status**: pending

### Tasks
- [ ] Create `backend/` directory structure per SPEC.md section 3
- [ ] `requirements.txt` + `requirements-dev.txt`
- [ ] `app/config.py` — pydantic-settings based config
- [ ] `app/database.py` — async SQLite engine, session factory, Base
- [ ] `app/models/roast.py` — Roast SQLAlchemy model (all columns + indexes)
- [ ] `app/schemas/roast.py` — All Pydantic request/response schemas
- [ ] `app/main.py` — FastAPI app with lifespan, CORS stub, `/api/health`
- [ ] `pytest.ini` configuration
- [ ] Verify: `uvicorn app.main:app` starts, `GET /api/health` returns 200

### Acceptance Criteria
- Backend starts without errors
- `/api/health` returns `{"status": "ok", ...}`
- All models and schemas importable without errors

---

## Phase 2: Backend Services (v0.3.0)
**Status**: pending

### Tasks
- [ ] `services/github.py` — verify_repo, fetch_repo_metadata, fetch_repo_tree, fetch_file_content
- [ ] `services/llm.py` — Gemini + Groq abstraction with fallback, LLMError, generate_json
- [ ] `services/analyzer.py` — analyze_repo with tech stack detection, file sampling
- [ ] `prompts/analyze.py` — ANALYSIS_SYSTEM_PROMPT
- [ ] `prompts/roast.py` — ROAST_SYSTEM_PROMPT + BRUTALITY_LEVELS dict
- [ ] `services/roaster.py` — Two-step pipeline (analyze → roast), score calculation, grade derivation

### Acceptance Criteria
- All services importable without errors
- LLM service handles primary/fallback logic
- Analyzer correctly detects tech stacks from file patterns
- Roaster score weighting matches spec (Architecture 1.5, Code Quality 1.5, etc.)

---

## Phase 3: Backend API + Pipeline (v0.4.0)
**Status**: pending

### Tasks
- [ ] Background pipeline `process_roast()` with status progression
- [ ] `routers/roast.py` — POST /api/roast (validate, create record, launch task)
- [ ] `routers/roast.py` — GET /api/roast/{id} (return full roast)
- [ ] `routers/roast.py` — GET /api/roasts/recent (paginated feed)
- [ ] Rate limiting (in-memory, 10 req/IP/min)
- [ ] CORS configuration per spec
- [ ] Verify: full flow via curl (POST → poll GET → complete)

### Acceptance Criteria
- POST /api/roast returns 202 with correct shape
- GET /api/roast/{id} returns status progression
- GET /api/roasts/recent returns paginated results
- Rate limiting returns 429 when exceeded
- CORS allows configured frontend origin

---

## Phase 4: Backend Tests (v0.5.0)
**Status**: pending

### Tasks
- [ ] `tests/conftest.py` — test_db, test_client, mock_github, mock_llm fixtures
- [ ] `tests/test_api.py` — 9 endpoint tests per spec section 11
- [ ] `tests/test_github.py` — 6 GitHub service tests with mocked HTTP
- [ ] `tests/test_analyzer.py` — 5 analyzer logic tests
- [ ] `tests/test_roaster.py` — 4 roast generation tests with mocked LLM
- [ ] `tests/test_llm.py` — 4 LLM abstraction tests
- [ ] Run `pytest -v` — all tests pass
- [ ] Run `ruff check .` — no lint errors

### Acceptance Criteria
- All 28 tests pass
- Zero ruff violations
- Tests cover all critical paths (happy path + error cases)

---

## Phase 5: Frontend Foundation (v0.6.0)
**Status**: pending

### Tasks
- [ ] Scaffold Vite + React + TypeScript project in `frontend/`
- [ ] Install and configure Tailwind CSS v4
- [ ] Install and configure shadcn/ui
- [ ] Set up react-router-dom v6 with routes (/, /roast/:id, /feed)
- [ ] `api/client.ts` — typed API client with fetch wrapper
- [ ] `types/roast.ts` — TypeScript types matching backend schemas
- [ ] `components/Layout.tsx` — navbar + footer + dark theme
- [ ] `lib/utils.ts` — cn() helper
- [ ] `lib/constants.ts` — brutality labels, grade colors
- [ ] `.env.example` for frontend
- [ ] Verify: `npm run dev` starts, pages route correctly

### Acceptance Criteria
- Dev server starts at localhost:5173
- All 3 routes render placeholder content
- Dark theme applied globally
- API client can make typed requests

---

## Phase 6: Frontend Pages (v0.7.0)
**Status**: pending

### Tasks
- [ ] `components/BrutalitySlider.tsx` — 5-step slider with emojis
- [ ] `components/RoastForm.tsx` — URL input + slider + submit button
- [ ] `hooks/useSubmitRoast.ts` — POST + navigate
- [ ] `pages/HomePage.tsx` — hero + form + recent roasts preview
- [ ] `hooks/useRoastPolling.ts` — poll GET every 2s until complete/failed
- [ ] `components/LoadingState.tsx` — multi-step loading animation
- [ ] `components/ScoreBadge.tsx` — circular SVG score display
- [ ] `components/GradeBadge.tsx` — letter grade badge
- [ ] `components/TopBurns.tsx` — 3 highlighted burns
- [ ] `components/CategorySection.tsx` — expandable category with score bar
- [ ] `components/RepoMeta.tsx` — stars/forks/language badges
- [ ] `components/RoastResultCard.tsx` — full result composition
- [ ] `components/ShareButtons.tsx` — copy link + share
- [ ] `pages/RoastPage.tsx` — polling + loading + result display
- [ ] `components/RoastFeedCard.tsx` — compact feed card
- [ ] `hooks/useFeed.ts` — paginated feed query
- [ ] `pages/FeedPage.tsx` — paginated grid

### Acceptance Criteria
- Full flow works in browser: submit → poll → display result
- Feed shows recent roasts with pagination
- All components render correctly

---

## Phase 7: Polish + Error Handling (v0.8.0)
**Status**: pending

### Tasks
- [ ] `components/ErrorState.tsx` — error display with retry
- [ ] Error states on HomePage (form errors, API errors)
- [ ] Error states on RoastPage (failed roast, network error)
- [ ] Error states on FeedPage (load failure)
- [ ] Loading skeletons for feed cards
- [ ] Share functionality (copy link to clipboard)
- [ ] Responsive design (mobile-first, test at 375px)
- [ ] `npx tsc --noEmit` passes cleanly

### Acceptance Criteria
- All error scenarios show user-friendly messages
- Mobile layout works at 375px
- TypeScript compiles without errors
- Share button copies link to clipboard

---

## Phase 8: CI/CD + Deployment Config (v0.9.0)
**Status**: pending

### Tasks
- [ ] `.github/workflows/ci.yml` — backend tests + frontend typecheck
- [ ] `.github/workflows/deploy-backend.yml` — Render deploy hook
- [ ] `.github/workflows/deploy-frontend.yml` — Vercel CLI deploy
- [ ] `backend/Dockerfile`
- [ ] `backend/render.yaml`
- [ ] `frontend/vercel.json`
- [ ] `SECRETS.md` — document all required GitHub Actions secrets
- [ ] Push feat/ci-deploy branch, verify CI passes
- [ ] Merge to main

### Acceptance Criteria
- CI workflow runs on PRs (lint + test + typecheck)
- Deploy workflows trigger on push to main
- Dockerfile builds successfully
- SECRETS.md documents all 4 required secrets

---

## Phase 9: Final (v1.0.0)
**Status**: pending

### Tasks
- [ ] `README.md` — project description, tech stack, setup instructions, deploy guide
- [ ] Final PROGRESS.md update (all phases complete)
- [ ] Final verification: `pytest -v` all pass
- [ ] Final verification: `npx tsc --noEmit` clean
- [ ] Tag v1.0.0
- [ ] Push all tags and commits

### Acceptance Criteria
- README.md is comprehensive and accurate
- All phases marked complete in PROGRESS.md
- All tests pass, no lint errors, no type errors
- All tags pushed to origin
- Project is fully functional end-to-end

---

## Decisions Log

| Decision | Rationale |
|----------|-----------|
| (none yet) | |
