# GitHub Secrets Setup Guide

The agent will create CI/CD workflows that reference these secrets. You need to
add them to your GitHub repo **before Phase 8 deploys** (but after Phase 7 is fine).

Go to: **GitHub → Your Repo → Settings → Secrets and variables → Actions → New repository secret**

---

## Required Secrets

### 1. `RENDER_DEPLOY_HOOK_URL`

This triggers a backend deploy to Render when code is pushed.

**Steps:**
1. Go to https://dashboard.render.com
2. Click "New" → "Web Service"
3. Connect your GitHub repo (`roast-my-repo`)
4. Configure:
   - **Name**: `roastmyrepo-api`
   - **Root Directory**: `backend`
   - **Runtime**: Docker
   - **Plan**: Free
5. Add environment variables in Render dashboard:
   - `GOOGLE_API_KEY` = your Gemini key
   - `GROQ_API_KEY` = your Groq key
   - `GITHUB_TOKEN` = your GitHub PAT
   - `LLM_PROVIDER` = `gemini`
   - `DATABASE_URL` = `sqlite+aiosqlite:///./roasts.db`
   - `FRONTEND_URL` = `https://roastmyrepo.vercel.app` (update after Vercel setup)
   - `ENVIRONMENT` = `production`
6. Click "Create Web Service" — let the first deploy finish
7. Go to your service → **Settings** → scroll to **Deploy Hook**
8. Click "Generate Deploy Hook" → copy the URL
9. Add as GitHub secret: `RENDER_DEPLOY_HOOK_URL`

**The URL looks like:** `https://api.render.com/deploy/srv-xxxxx?key=yyyyy`

---

### 2. `VERCEL_TOKEN`

Personal access token for Vercel CLI deployments.

**Steps:**
1. Go to https://vercel.com/account/tokens
2. Click "Create" token
3. **Name**: `roastmyrepo-github-actions`
4. **Scope**: Full Account (or select your team)
5. **Expiration**: pick whatever you want (90 days is fine)
6. Copy the token
7. Add as GitHub secret: `VERCEL_TOKEN`

---

### 3. `VERCEL_ORG_ID`

Your Vercel account/team ID.

**Steps:**
1. Go to https://vercel.com
2. Click your avatar (bottom left) → **Settings**
3. Under "General", find **"Your ID"** (or "Team ID" if using a team)
4. Copy it
5. Add as GitHub secret: `VERCEL_ORG_ID`

**Looks like:** `team_xxxxxxxxxxxxxxxxxxxx` or `prj_xxxxxxxxxxxx`

---

### 4. `VERCEL_PROJECT_ID`

Your specific project ID. You need to create the Vercel project first.

**Steps:**
1. Go to https://vercel.com/new
2. Import your GitHub repo (`roast-my-repo`)
3. Configure:
   - **Framework Preset**: Vite
   - **Root Directory**: `frontend`
   - **Build Command**: `npm run build`
   - **Output Directory**: `dist`
4. Add environment variable:
   - `VITE_API_URL` = `https://roastmyrepo-api.onrender.com` (your Render URL from step 1)
5. Click "Deploy" — let it build (it may fail on first deploy since frontend code may not exist yet, that's fine)
6. Go to your project → **Settings** → **General**
7. Find **"Project ID"** and copy it
8. Add as GitHub secret: `VERCEL_PROJECT_ID`

---

## Summary Checklist

After setup, your GitHub repo should have these 4 secrets:

| Secret Name | Source | Example Format |
|------------|--------|---------------|
| `RENDER_DEPLOY_HOOK_URL` | Render dashboard → Deploy Hook | `https://api.render.com/deploy/srv-xxx?key=yyy` |
| `VERCEL_TOKEN` | Vercel → Account → Tokens | `vcel_xxxxxxxxxxxx` |
| `VERCEL_ORG_ID` | Vercel → Settings → Your ID | `team_xxxxxxxxxxxx` |
| `VERCEL_PROJECT_ID` | Vercel → Project → Settings | `prj_xxxxxxxxxxxx` |

## When to Do This

- **Before launching the agent**: Not strictly required. The agent builds the CI workflow files regardless.
- **Before Phase 8 pushes to GitHub**: Ideal. The deploy workflows will work immediately.
- **After v1.0.0**: Also fine. Deployments will just fail silently until you add the secrets, then work on next push.

**Recommended**: Set up Render and Vercel while the agent is working through Phases 1-7. By the time it hits Phase 8, your secrets are ready and the first CI-triggered deploy just works.
