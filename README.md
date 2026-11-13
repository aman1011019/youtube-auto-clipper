# ClipForge AI

Permission-first AI YouTube Shorts workflow. React + TypeScript dashboard, FastAPI backend, FFmpeg render utility, source permission declaration, human review queue and guarded YouTube publishing endpoint.

## Run with Docker
1. Copy `.env.example` to `.env` and add Google OAuth credentials when configured.
2. `docker compose up --build`
3. Frontend: http://localhost:5173 · API docs: http://localhost:8000/docs

## Local
Backend: `cd backend && pip install -r requirements.txt && uvicorn app.main:app --reload`
Frontend: `cd frontend && npm install && npm run dev`

Only process videos you own or have explicit republishing permission to use. A public YouTube URL is not permission to download or republish. Publishing is always review-gated. Google OAuth and resumable upload require configured Google Cloud credentials and secure token storage.