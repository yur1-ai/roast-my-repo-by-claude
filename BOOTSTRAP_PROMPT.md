You are building the RoastMyRepo application from scratch. All requirements are in SPEC.md. All coding conventions are in CLAUDE.md. Read both files completely before doing anything.

## Git Workflow

### Pushing
- After every phase tag, push both commits and tags to origin:
  ```
  git push origin main
  git push origin --tags
  ```
- If `git push` fails due to remote rejection or auth issues, note it in PROGRESS.md and continue. The user will fix remote access.

### Branching (for CI phases)
- During Phase 8 and Phase 9, create feature branches for CI-related work:
  ```
  git checkout -b feat/ci-deploy
  ```
- Push the branch, open a PR description in PROGRESS.md, then merge to main after CI passes:
  ```
  git push origin feat/ci-deploy
  git checkout main
  git merge feat/ci-deploy
  git push origin main
  ```

## Your Workflow

### Phase 0: Planning (tag: v0.1.0)
1. Read SPEC.md and CLAUDE.md thoroughly
2. Create a PROGRESS.md file that breaks the spec into phases and tracks completion status. Each phase should have:
   - Phase name and version tag
   - List of concrete tasks
   - Acceptance criteria
   - Status (pending/in-progress/complete)
3. The phases should roughly follow SPEC.md section 15 (Implementation Order) but you may reorganize if it makes more architectural sense
4. Commit: "docs: create phased implementation plan"
5. Tag: v0.1.0
6. Push to origin

### Phase 1: Backend Foundation (tag: v0.2.0)
- FastAPI app scaffold, config, database, health endpoint
- Roast SQLAlchemy model + all Pydantic schemas
- Verify: `uvicorn app.main:app` starts, `/api/health` returns 200
- Commit granularly (one commit per logical unit)
- Tag v0.2.0 when phase complete
- Push to origin

### Phase 2: Backend Services (tag: v0.3.0)
- GitHub service (all methods)
- LLM service (Gemini + Groq abstraction with fallback)
- Analyzer service
- Prompts (analysis + roast with all 5 brutality levels)
- Roaster service (two-step pipeline)
- Commit after each service is complete
- Tag v0.3.0 when phase complete
- Push to origin

### Phase 3: Backend API + Pipeline (tag: v0.4.0)
- Background task pipeline (process_roast)
- All API endpoints (POST /api/roast, GET /api/roast/{id}, GET /api/roasts/recent)
- Rate limiting
- CORS configuration
- Verify: full flow works end-to-end via curl
- Tag v0.4.0 when phase complete
- Push to origin

### Phase 4: Backend Tests (tag: v0.5.0)
- conftest.py with fixtures
- All test files per SPEC.md section 11
- Run pytest — all tests must pass
- Run ruff check — no lint errors
- Tag v0.5.0 when phase complete
- Push to origin

### Phase 5: Frontend Foundation (tag: v0.6.0)
- Vite + React + TypeScript scaffold
- Install and configure Tailwind CSS v4 + shadcn/ui
- Set up react-router-dom with routes
- API client (client.ts)
- TypeScript types matching backend schemas
- Layout component with navbar
- Dark theme setup
- Verify: `npm run dev` starts, pages route correctly
- Tag v0.6.0 when phase complete
- Push to origin

### Phase 6: Frontend Pages (tag: v0.7.0)
- HomePage with RoastForm + BrutalitySlider
- RoastPage with polling + LoadingState + full result display
- FeedPage with paginated grid
- All supporting components (ScoreBadge, GradeBadge, etc.)
- Verify: full flow works in browser (submit → poll → display)
- Tag v0.7.0 when phase complete
- Push to origin

### Phase 7: Polish + Error Handling (tag: v0.8.0)
- Error states on all pages
- Loading skeletons
- Share functionality (copy link)
- Responsive design (mobile)
- Frontend TypeScript check passes (tsc --noEmit)
- Tag v0.8.0 when phase complete
- Push to origin

### Phase 8: CI/CD + Deployment Config (tag: v0.9.0)
This phase requires pushing a branch and verifying CI passes remotely.

1. Create GitHub Actions CI workflow (`.github/workflows/ci.yml`):
   - Backend: install deps, ruff check, pytest
   - Frontend: install deps, tsc --noEmit
   - Triggered on push to main and on pull requests

2. Create deployment workflows:
   - `.github/workflows/deploy-backend.yml` — triggers Render deploy hook on push to main (paths: backend/**)
   - `.github/workflows/deploy-frontend.yml` — triggers Vercel deploy via Vercel CLI on push to main (paths: frontend/**)
   - Both workflows read secrets from GitHub Actions secrets (see SECRETS.md)

3. Create deployment configs:
   - `backend/Dockerfile`
   - `backend/render.yaml`
   - `frontend/vercel.json`

4. Create `SECRETS.md` documenting all required GitHub Actions secrets with step-by-step instructions for obtaining each one:
   - `RENDER_DEPLOY_HOOK_URL` — from Render dashboard → service → Settings → Deploy Hook
   - `VERCEL_TOKEN` — from Vercel → Settings → Tokens → Create
   - `VERCEL_ORG_ID` — from Vercel → Settings → General → "Your ID"
   - `VERCEL_PROJECT_ID` — from Vercel → Project → Settings → General → "Project ID"
   - Include exact URLs and navigation paths for each

5. Push branch and verify CI:
   ```
   git checkout -b feat/ci-deploy
   git add -A && git commit -m "chore: add CI/CD workflows and deployment config"
   git push origin feat/ci-deploy
   ```

6. Check CI status using GitHub CLI:
   ```
   sleep 30
   gh run list --branch feat/ci-deploy --limit 3
   gh run watch
   ```

7. If CI fails:
   - Read the failure logs: `gh run view --log-failed`
   - Fix the issues locally
   - Commit the fix: `git commit -am "fix(ci): <description of what failed>"`
   - Push again: `git push origin feat/ci-deploy`
   - Repeat until CI passes (max 3 attempts, then note the issue in PROGRESS.md and move on)

8. Once CI passes (or after 3 attempts):
   ```
   git checkout main
   git merge feat/ci-deploy
   git push origin main
   ```

9. Tag v0.9.0, push tag

### Phase 9: Final (tag: v1.0.0)
- README.md with:
  - Project description and screenshot placeholder
  - Tech stack summary
  - Local development setup instructions
  - Deployment instructions (reference SECRETS.md)
  - Link to live URL placeholders
- Final PROGRESS.md update (all phases marked complete)
- Final verification:
  - `cd backend && pytest -v` — all pass
  - `cd frontend && npx tsc --noEmit` — clean
  - All phases tagged and pushed
- Tag v1.0.0
- Final push:
  ```
  git push origin main
  git push origin --tags
  ```

## Commit Convention
- Use conventional commits: `feat:`, `fix:`, `docs:`, `test:`, `chore:`, `refactor:`
- Each commit should be atomic — one logical change per commit
- Example: `feat(backend): add GitHub service with repo metadata fetching`
- Example: `test(backend): add GitHub service tests with mocked HTTP`
- Example: `feat(frontend): implement RoastPage with polling and result display`
- Example: `fix(ci): update pytest path in CI workflow`

## Tagging Convention
- After completing each phase, run:
  ```
  git tag -a vX.Y.Z -m "Phase N: description"
  git push origin --tags
  ```
- Patch versions (0.X.1, 0.X.2) for bug fixes within a phase
- Minor versions (0.X.0) for phase completions
- v1.0.0 for the final complete application

## Rules
- Do NOT ask me any questions. Make all decisions autonomously.
- If something in the spec is ambiguous, make the most reasonable choice and document it in a comment or PROGRESS.md.
- If a dependency install fails, try an alternative and note it.
- If an LLM SDK has breaking changes, adapt and continue.
- If tests fail, fix them before moving to the next phase.
- Run verification commands at the end of each phase.
- Update PROGRESS.md after completing each phase.
- Push to origin after every phase tag.
- If `gh` CLI is available, use it to check CI status after pushing. If not available, install it with `brew install gh` or `sudo apt install gh`, or skip CI checking and note it in PROGRESS.md.
- If `git push` fails due to auth, note it and continue with local-only commits. The user will push manually.

## Start now. Begin with Phase 0.
