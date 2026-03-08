# RoastMyRepo 🔥

AI-powered comedic code review. Paste a GitHub repo URL, pick a brutality level (1-5), and get a roast with scores, burns, and actual suggestions.

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Backend | Python 3.12, FastAPI, SQLAlchemy 2.0 (async), Pydantic v2 |
| Frontend | React 18, TypeScript, Vite, Tailwind CSS v4, shadcn/ui |
| Database | SQLite via aiosqlite |
| LLM (Primary) | Google Gemini 2.5 Flash |
| LLM (Fallback) | Groq (Llama 4 Maverick) |
| Backend Hosting | Render (free tier) |
| Frontend Hosting | Vercel (free tier) |
| CI/CD | GitHub Actions |

## Local Development

### Prerequisites
- Python 3.12+
- Node.js 20+

### Backend

```bash
cd backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt -r requirements-dev.txt

# Create .env from template and add your API keys
cp ../.env.example .env

# Run
uvicorn app.main:app --reload --port 8000
# Health check: curl http://localhost:8000/api/health
```

### Frontend

```bash
cd frontend
npm install
echo "VITE_API_URL=http://localhost:8000" > .env

npm run dev
# Opens at http://localhost:5173
```

### Tests

```bash
cd backend
pytest -v        # All tests
ruff check .     # Lint

cd ../frontend
npx tsc --noEmit # Type check
```

## API Keys (Free)

1. **Google AI Studio**: https://aistudio.google.com/apikey → Create API Key
2. **Groq**: https://console.groq.com → API Keys → Create
3. **GitHub Token** (optional, increases rate limit): GitHub → Settings → Developer Settings → Personal Access Tokens

## Deployment

See [SECRETS.md](SECRETS.md) for GitHub Actions secrets setup and [GITHUB_SECRETS_SETUP.md](GITHUB_SECRETS_SETUP.md) for detailed deployment instructions.

## How It Works

1. User submits a GitHub repo URL with a brutality level (1-5)
2. Backend fetches repo metadata and samples key files via GitHub API
3. LLM analyzes code structure, patterns, and quality signals
4. LLM generates a comedic roast with scores across 7 categories
5. Results displayed with animated scores, top burns, and actionable suggestions

## Categories Scored

- 🏗️ Architecture
- 💩 Code Quality
- 🏷️ Naming & Style
- 🧪 Testing
- 📦 Dependencies
- 📝 Documentation
- 🚩 Security & Red Flags

---

Built to test agentic coding tools.
