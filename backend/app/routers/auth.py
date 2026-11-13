from fastapi import APIRouter,HTTPException
import os
router=APIRouter(tags=["youtube-auth"])
@router.get("/auth/youtube/status")
def status(): return {"connected":False,"configured":bool(os.getenv("GOOGLE_CLIENT_ID") and os.getenv("GOOGLE_CLIENT_SECRET"))}
@router.get("/auth/youtube/connect")
def connect():
 if not os.getenv("GOOGLE_CLIENT_ID") or not os.getenv("GOOGLE_CLIENT_SECRET"): raise HTTPException(503,"Set Google OAuth credentials first")
 raise HTTPException(501,"Complete OAuth callback and encrypted token storage setup before connecting")
