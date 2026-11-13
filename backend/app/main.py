import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .db import init_db
from .routers import sources,clips,auth,settings
app=FastAPI(title="ClipForge AI API",version="0.1.0",description="Permission-first Shorts production workflow")
origins=[x.strip() for x in os.getenv("FRONTEND_ORIGIN","http://localhost:5173").split(",") if x.strip()]
app.add_middleware(CORSMiddleware,allow_origins=origins,allow_credentials=True,allow_methods=["*"],allow_headers=["*"])
for router in (sources.router,clips.router,auth.router,settings.router): app.include_router(router,prefix="/api")
@app.on_event("startup")
def startup(): init_db()
@app.get("/api/health")
def health(): return {"status":"ok","service":"clipforge-api"}
