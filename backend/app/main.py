import os,secrets
from fastapi import FastAPI,Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from .db import init_db
from .routers import sources,clips,auth,settings
app=FastAPI(title="ClipForge AI API",version="0.1.0",description="Permission-first Shorts production workflow")
origins=[x.strip() for x in os.getenv("FRONTEND_ORIGIN","http://localhost:5173").split(",") if x.strip()]
app.add_middleware(CORSMiddleware,allow_origins=origins,allow_credentials=True,allow_methods=["*"],allow_headers=["*"])
@app.middleware("http")
async def protect_workspace(request:Request,call_next):
    path=request.url.path
    if request.method=="OPTIONS" or path in {"/api/health","/api/auth/youtube/callback","/docs","/openapi.json","/redoc"}:
        return await call_next(request)
    expected=os.getenv("APP_ADMIN_KEY","")
    if not expected:
        return JSONResponse(status_code=503,content={"detail":"Set APP_ADMIN_KEY in the backend environment before using the workspace."})
    supplied=request.headers.get("x-app-key","")
    if not secrets.compare_digest(supplied,expected):
        return JSONResponse(status_code=401,content={"detail":"Workspace key is missing or invalid."})
    return await call_next(request)
for router in (sources.router,clips.router,auth.router,settings.router): app.include_router(router,prefix="/api")
@app.on_event("startup")
def startup(): init_db()
@app.get("/api/health")
def health(): return {"status":"ok","service":"clipforge-api"}
