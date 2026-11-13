from pydantic import BaseModel,HttpUrl,Field
from typing import Optional
class SourceCreate(BaseModel):
 title:str=Field(min_length=2,max_length=300); url:HttpUrl; creator:str=""; permission_confirmed:bool; notes:str=""
class SourceOut(BaseModel):
 id:int; title:str; url:str; creator:str; permission_confirmed:bool; notes:str
 class Config: from_attributes=True
class ClipOut(BaseModel):
 id:int; source_id:Optional[int]; title:str; start_seconds:float; end_seconds:float; score:float; status:str; video_path:str; description:str
 class Config: from_attributes=True
class ClipUpdate(BaseModel):
 title:Optional[str]=None; description:Optional[str]=None; status:Optional[str]=None
class GenerateRequest(BaseModel):
 source_id:int; target_count:int=Field(default=5,ge=1,le=10); clip_length:int=Field(default=45,ge=15,le=180)
