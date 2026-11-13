from fastapi import APIRouter,Depends,HTTPException
from sqlalchemy.orm import Session
from ..db import get_db
from ..models import Clip,Source
from ..schemas import ClipOut,ClipUpdate,GenerateRequest
router=APIRouter(tags=["clips"])
@router.get("/clips",response_model=list[ClipOut])
def list_clips(db:Session=Depends(get_db)): return db.query(Clip).order_by(Clip.id.desc()).all()
@router.post("/clips/generate",response_model=list[ClipOut],status_code=202)
def generate(p:GenerateRequest,db:Session=Depends(get_db)):
 s=db.get(Source,p.source_id)
 if not s: raise HTTPException(404,"Source not found")
 if not s.permission_confirmed: raise HTTPException(403,"Permission not confirmed")
 labels=["Strong opening insight","Key takeaway","High-energy moment","Practical tip","Memorable conclusion","Audience question","Unexpected detail","Quick explainer"]
 rows=[Clip(source_id=s.id,title=labels[i%len(labels)],start_seconds=float(i*p.clip_length),end_seconds=float((i+1)*p.clip_length),score=.55,status="draft",description="Draft candidate. Attach authorized media and run the render worker before publishing.") for i in range(p.target_count)]
 db.add_all(rows); db.commit()
 for x in rows: db.refresh(x)
 return rows
@router.patch("/clips/{cid}",response_model=ClipOut)
def update_clip(cid:int,p:ClipUpdate,db:Session=Depends(get_db)):
 x=db.get(Clip,cid)
 if not x: raise HTTPException(404,"Clip not found")
 if p.title is not None: x.title=p.title
 if p.description is not None: x.description=p.description
 if p.status is not None:
  if p.status not in {"draft","approved","rejected","published"}: raise HTTPException(400,"Invalid status")
  x.status=p.status
 db.commit(); db.refresh(x); return x
@router.post("/clips/{cid}/publish")
def publish(cid:int,db:Session=Depends(get_db)):
 x=db.get(Clip,cid)
 if not x: raise HTTPException(404,"Clip not found")
 if x.status!="approved": raise HTTPException(409,"Approval required before publishing")
 if not x.video_path: raise HTTPException(409,"Rendered video file required before upload")
 raise HTTPException(503,"Configure YouTube OAuth token storage and resumable upload to enable publishing")
