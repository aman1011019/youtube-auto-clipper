from fastapi import APIRouter,Depends,HTTPException
from sqlalchemy.orm import Session
from ..db import get_db
from ..models import Source
from ..schemas import SourceCreate,SourceOut
router=APIRouter(tags=["sources"])
@router.get("/sources",response_model=list[SourceOut])
def list_sources(db:Session=Depends(get_db)): return db.query(Source).order_by(Source.id.desc()).all()
@router.post("/sources",response_model=SourceOut,status_code=201)
def add_source(p:SourceCreate,db:Session=Depends(get_db)):
 if not p.permission_confirmed: raise HTTPException(400,"Confirm ownership or explicit republishing permission.")
 item=Source(title=p.title,url=str(p.url),creator=p.creator,permission_confirmed=True,notes=p.notes); db.add(item)
 try: db.commit()
 except Exception: db.rollback(); raise HTTPException(409,"Source already exists or could not be saved.")
 db.refresh(item); return item
@router.delete("/sources/{sid}",status_code=204)
def remove_source(sid:int,db:Session=Depends(get_db)):
 x=db.get(Source,sid)
 if not x: raise HTTPException(404,"Source not found")
 db.delete(x); db.commit()
