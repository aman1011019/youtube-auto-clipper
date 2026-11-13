import json,os
from pathlib import Path
from fastapi import APIRouter,HTTPException,Request
from fastapi.responses import RedirectResponse
router=APIRouter(tags=["youtube-auth"])
SCOPES=["https://www.googleapis.com/auth/youtube.upload","https://www.googleapis.com/auth/youtube.readonly"]
PENDING_STATES=set()

def _client_config():
    cid=os.getenv("GOOGLE_CLIENT_ID"); secret=os.getenv("GOOGLE_CLIENT_SECRET")
    if not cid or not secret: raise HTTPException(503,"Configure GOOGLE_CLIENT_ID and GOOGLE_CLIENT_SECRET first")
    redirect=os.getenv("GOOGLE_REDIRECT_URI","http://localhost:8000/api/auth/youtube/callback")
    return {"web":{"client_id":cid,"client_secret":secret,"auth_uri":"https://accounts.google.com/o/oauth2/auth","token_uri":"https://oauth2.googleapis.com/token","redirect_uris":[redirect]}}

def _cipher():
    from cryptography.fernet import Fernet
    key=os.getenv("GOOGLE_TOKEN_ENCRYPTION_KEY")
    if not key: raise HTTPException(503,"Set GOOGLE_TOKEN_ENCRYPTION_KEY to a Fernet key before connecting YouTube")
    try: return Fernet(key.encode())
    except Exception: raise HTTPException(500,"GOOGLE_TOKEN_ENCRYPTION_KEY is not a valid Fernet key")

def _token_path():
    return Path(os.getenv("TOKEN_FILE","/data/youtube-token.enc"))

@router.get("/auth/youtube/status")
def status():
    path=_token_path()
    return {"connected":path.exists(),"configured":bool(os.getenv("GOOGLE_CLIENT_ID") and os.getenv("GOOGLE_CLIENT_SECRET") and os.getenv("GOOGLE_TOKEN_ENCRYPTION_KEY"))}

@router.get("/auth/youtube/connect")
def connect():
    from google_auth_oauthlib.flow import Flow
    flow=Flow.from_client_config(_client_config(),scopes=SCOPES)
    flow.redirect_uri=os.getenv("GOOGLE_REDIRECT_URI","http://localhost:8000/api/auth/youtube/callback")
    url,state=flow.authorization_url(access_type="offline",include_granted_scopes="true",prompt="consent")
    PENDING_STATES.add(state)
    return RedirectResponse(url)

@router.get("/auth/youtube/callback")
def callback(request:Request,state:str,code:str):
    if state not in PENDING_STATES: raise HTTPException(400,"OAuth state is invalid or expired. Please connect again.")
    PENDING_STATES.discard(state)
    from google_auth_oauthlib.flow import Flow
    flow=Flow.from_client_config(_client_config(),scopes=SCOPES,state=state)
    flow.redirect_uri=os.getenv("GOOGLE_REDIRECT_URI","http://localhost:8000/api/auth/youtube/callback")
    flow.fetch_token(code=code)
    path=_token_path(); path.parent.mkdir(parents=True,exist_ok=True)
    encrypted=_cipher().encrypt(flow.credentials.to_json().encode())
    path.write_bytes(encrypted)
    return RedirectResponse(os.getenv("FRONTEND_ORIGIN","http://localhost:5173")+"/?youtube=connected")
