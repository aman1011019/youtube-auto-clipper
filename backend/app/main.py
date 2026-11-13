from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .db import init_db
from .routers import sources, clips, auth, settings
app = FastAPI(title="ClipForge AI API", version="0.1.0")
app.add_middleware(CORSMiddleware, allow_origins=["http://localhost:5173"], allow_credentials=True, allow_methods=["*"], allow_headers=["*"])
app.include_router(sources.router, prefix="/api")
app.include_router(clips.router, prefix="/api")
app.include_router(auth.router, prefix="/api")
app.include_router(settings.router, prefix="/api")
@app.on_event("startup")
def startup(): init_db()
@app.get("/api/health")
def health(): return {"status":"ok","service":"clipforge-api"}
