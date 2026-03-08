# SECRETS.md — Required GitHub Actions Secrets

This document lists all secrets needed for CI/CD workflows. Add them at:
**GitHub Repo → Settings → Secrets and variables → Actions → New repository secret**

---

## 1. `RENDER_DEPLOY_HOOK_URL`

Triggers a backend deploy to Render when code is pushed to main.

**How to get it:**
1. Go to https://dashboard.render.com
2. Navigate to your **roastmyrepo-api** web service
3. Click **Settings** (left sidebar)
4. Scroll down to **Deploy Hook**
5. Click **Generate Deploy Hook** if not already generated
6. Copy the URL

**Format:** `https://api.render.com/deploy/srv-xxxxx?key=yyyyy`

---

## 2. `VERCEL_TOKEN`

Personal access token for Vercel CLI deployments.

**How to get it:**
1. Go to https://vercel.com/account/tokens
2. Click **Create** token
3. Name: `roastmyrepo-github-actions`
4. Scope: Full Account
5. Expiration: 90 days (or your preference)
6. Copy the token immediately (shown only once)

**Format:** `vcel_xxxxxxxxxxxx`

---

## 3. `VERCEL_ORG_ID`

Your Vercel account/team ID.

**How to get it:**
1. Go to https://vercel.com
2. Click your avatar (bottom left) → **Settings**
3. Under **General**, find **"Your ID"** (or "Team ID" for teams)
4. Copy the value

**Format:** `team_xxxxxxxxxxxx` or a similar alphanumeric string

---

## 4. `VERCEL_PROJECT_ID`

The specific Vercel project ID for the frontend.

**How to get it:**
1. Go to https://vercel.com
2. Navigate to your **roastmyrepo** project
3. Click **Settings** → **General**
4. Find **"Project ID"**
5. Copy the value

**Format:** `prj_xxxxxxxxxxxx`

---

## Summary

| Secret | Source | Required For |
|--------|--------|-------------|
| `RENDER_DEPLOY_HOOK_URL` | Render → Service → Settings → Deploy Hook | `deploy-backend.yml` |
| `VERCEL_TOKEN` | Vercel → Account → Tokens | `deploy-frontend.yml` |
| `VERCEL_ORG_ID` | Vercel → Settings → General → Your ID | `deploy-frontend.yml` |
| `VERCEL_PROJECT_ID` | Vercel → Project → Settings → Project ID | `deploy-frontend.yml` |

Deploy workflows will fail silently without these secrets — CI (lint + tests) works independently.
