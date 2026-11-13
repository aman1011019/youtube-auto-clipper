import os, uuid
from pathlib import Path
from fastapi import APIRouter,Depends,HTTPException,UploadFile,File
from sqlalchemy.orm import Session
from ..db import get_db
from ..models import Source
from ..schemas import SourceCreate,SourceOut
router=APIRouter(tags=["sources"])
MEDIA_DIR=Path(os.getenv("MEDIA_DIR","/media"))
ALLOWED={".mp4",".mov",".mkv",".webm"}
MAX_BYTES=2*1024*1024*1024

@router.get("/sources",response_model=list[SourceOut])
def list_sources(db:Session=Depends(get_db)):
    return db.query(Source).order_by(Source.id.desc()).all()

@router.post("/sources",response_model=SourceOut,status_code=201)
def add_source(p:SourceCreate,db:Session=Depends(get_db)):
    if not p.permission_confirmed:
        raise HTTPException(400,"Confirm ownership or explicit republishing permission.")
    item=Source(title=p.title,url=str(p.url),creator=p.creator,permission_confirmed=True,notes=p.notes)
    db.add(item)
    try: db.commit()
    except Exception:
        db.rollback()
        raise HTTPException(409,"Source already exists or could not be saved.")
    db.refresh(item)
    return item

@router.post("/sources/{sid}/media",response_model=SourceOut)
async def upload_authorized_media(sid:int,file:UploadFile=File(...),db:Session=Depends(get_db)):
    source=db.get(Source,sid)
    if not source: raise HTTPException(404,"Source not found")
    if not source.permission_confirmed: raise HTTPException(403,"Permission not confirmed")
    ext=Path(file.filename or "").suffix.lower()
    if ext not in ALLOWED: raise HTTPException(415,"Upload MP4, MOV, MKV or WebM video files only")
    MEDIA_DIR.mkdir(parents=True,exist_ok=True)
    destination=MEDIA_DIR/f"source-{sid}-{uuid.uuid4().hex}{ext}"
    total=0
    try:
        with destination.open("wb") as out:
            while chunk:=await file.read(1024*1024):
                total+=len(chunk)
                if total>MAX_BYTES: raise HTTPException(413,"Maximum upload size is 2 GB")
                out.write(chunk)
    except Exception:
        destination.unlink(missing_ok=True)
        raise
    finally:
        await file.close()
    if total==0:
        destination.unlink(missing_ok=True)
        raise HTTPException(400,"Uploaded video is empty")
    source.media_path=str(destination)
    db.commit()
    db.refresh(source)
    return source

@router.delete("/sources/{sid}",status_code=204)
def remove_source(sid:int,db:Session=Depends(get_db)):
    x=db.get(Source,sid)
    if not x: raise HTTPException(404,"Source not found")
    db.delete(x)
    db.commit()

@router.get("/sources/discover")
def discover_popular_videos(q:str,max_results:int=10):
    """Search high-view-count public video metadata only. This does not download or grant reuse rights."""
    import os
    from fastapi import Query
    from googleapiclient.discovery import build
    query=q.strip()
    if len(query)<2: raise HTTPException(422,"Search query must contain at least two characters")
    api_key=os.getenv("YOUTUBE_API_KEY")
    if not api_key: raise HTTPException(503,"Set YOUTUBE_API_KEY to enable popular-video discovery")
    try:
        yt=build("youtube","v3",developerKey=api_key,cache_discovery=False)
        response=yt.search().list(part="snippet",q=query,type="video",order="viewCount",maxResults=max(1,min(max_results,10)),safeSearch="moderate").execute()
        ids=[item["id"]["videoId"] for item in response.get("items",[]) if item.get("id",{}).get("videoId")]
        stats={}
        if ids:
            details=yt.videos().list(part="statistics",id=",".join(ids)).execute()
            stats={item["id"]:int(item.get("statistics",{}).get("viewCount",0)) for item in details.get("items",[])}
        return {"items":[{"title":item["snippet"]["title"],"creator":item["snippet"]["channelTitle"],"channel_id":item["snippet"]["channelId"],"url":"https://www.youtube.com/watch?v="+item["id"]["videoId"],"view_count":stats.get(item["id"]["videoId"],0),"thumbnail":item["snippet"].get("thumbnails",{}).get("medium",{}).get("url","")} for item in response.get("items",[]) if item.get("id",{}).get("videoId")]}
    except Exception as exc:
        raise HTTPException(502,"YouTube discovery failed: "+type(exc).__name__)
