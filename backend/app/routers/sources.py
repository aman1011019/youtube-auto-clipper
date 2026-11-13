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
