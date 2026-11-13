from fastapi import APIRouter,Depends,HTTPException
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from ..db import get_db
from ..models import Clip,Source
from ..schemas import ClipOut,ClipUpdate,GenerateRequest
from ..services.clipper import create_candidates
router=APIRouter(tags=["clips"])

@router.get("/clips",response_model=list[ClipOut])
def list_clips(db:Session=Depends(get_db)):
    return db.query(Clip).order_by(Clip.id.desc()).all()

@router.post("/clips/generate",response_model=list[ClipOut],status_code=201)
def generate(p:GenerateRequest,db:Session=Depends(get_db)):
    source=db.get(Source,p.source_id)
    if not source: raise HTTPException(404,"Source not found")
    if not source.permission_confirmed: raise HTTPException(403,"Permission not confirmed")
    try:
        rows=create_candidates(source,p.target_count,p.clip_length)
    except ValueError as exc:
        raise HTTPException(422,str(exc))
    except RuntimeError as exc:
        raise HTTPException(503,str(exc))
    except FileNotFoundError as exc:
        raise HTTPException(422,str(exc))
    except Exception as exc:
        raise HTTPException(500,f"Clip generation failed: {type(exc).__name__}")
    try:
        db.add_all(rows); db.commit()
        for row in rows: db.refresh(row)
    except SQLAlchemyError:
        db.rollback()
        raise HTTPException(500,"Could not save generated clips")
    return rows

@router.patch("/clips/{cid}",response_model=ClipOut)
def update_clip(cid:int,p:ClipUpdate,db:Session=Depends(get_db)):
    clip=db.get(Clip,cid)
    if not clip: raise HTTPException(404,"Clip not found")
    if p.title is not None: clip.title=p.title
    if p.description is not None: clip.description=p.description
    if p.status is not None:
        if p.status not in {"draft","approved","rejected","published"}: raise HTTPException(400,"Invalid status")
        clip.status=p.status
    db.commit(); db.refresh(clip)
    return clip

@router.post("/clips/{cid}/publish")
def publish(cid:int,db:Session=Depends(get_db)):
    clip=db.get(Clip,cid)
    if not clip: raise HTTPException(404,"Clip not found")
    if clip.status!="approved": raise HTTPException(409,"Approval required before publishing")
    if not clip.video_path: raise HTTPException(409,"Rendered video file required before upload")
    from ..services.youtube import publish_video
    return publish_video(clip)
