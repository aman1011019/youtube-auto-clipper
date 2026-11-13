# ClipForge AI

Permission-first AI-assisted YouTube Shorts workspace. Manage owned/licensed video sources, upload authorized media, transcribe with faster-whisper, rank highlight windows, render vertical MP4 clips with FFmpeg, review drafts and publish approved Shorts to YouTube.

## Quick start (Docker)
1. Copy `.env.example` to `.env` and replace `APP_ADMIN_KEY` with a long random secret. The dashboard asks for this key when you open it.
2. Generate a token encryption key: `python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"`; put it in `GOOGLE_TOKEN_ENCRYPTION_KEY`.
3. Create an OAuth 2.0 Web application in Google Cloud. Enable YouTube Data API v3. Add `http://localhost:8000/api/auth/youtube/callback` as an authorized redirect URI and fill `GOOGLE_CLIENT_ID` and `GOOGLE_CLIENT_SECRET`.
4. Run `docker compose up --build`.
5. Open http://localhost:5173 and enter `APP_ADMIN_KEY`. For your channel, connect YouTube in Publishing and use **Import my uploads** in Sources; for other creators, add a source URL only after securing permission. Upload the authorized original media file, generate clips, review/approve them, then upload approved clips from Publishing.

Frontend: http://localhost:5173 · API docs: http://localhost:8000/docs

The workspace API is protected by `APP_ADMIN_KEY`. The YouTube OAuth callback is exempt so Google can complete the redirect; all other application API calls require the workspace key.

## Local development
Backend: `cd backend && pip install -r requirements.txt && uvicorn app.main:app --reload`
Frontend: `cd frontend && npm install && npm run dev`

## Important
- A public YouTube URL is not permission to download or republish a video. Only upload content you own or have explicit written permission to repurpose. This app deliberately does not scrape YouTube video streams.
- Clip generation uses faster-whisper (first model load may download model weights) and FFmpeg. CPU inference is supported; adjust `WHISPER_MODEL`, `WHISPER_DEVICE`, and `WHISPER_COMPUTE_TYPE` for your machine.
- Every clip remains a draft until manually approved. YouTube uploads default to **private**; set `YOUTUBE_DEFAULT_PRIVACY=unlisted` or `public` only after choosing your intended publishing policy.
- The 3–5 Shorts/day value is a publishing target in this MVP, not an automatic scheduler. Uploads are initiated manually from the approved queue. Third-party channels are not automatically scraped or downloaded; the creator must authorize republishing and you must supply the permitted media file.
- Store `.env`, `/data` and `/media` securely. Do not commit API keys or OAuth tokens. Use HTTPS, PostgreSQL and private object storage in production.
- This repository is an installable MVP, not a hosted service: cloud credentials, Google OAuth consent configuration, server deployment, storage and runtime are required to activate uploads.
