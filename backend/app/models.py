from sqlalchemy import Boolean,Column,DateTime,Float,Integer,String,Text
from sqlalchemy.sql import func
from .db import Base
class Source(Base):
 __tablename__="sources"
 id=Column(Integer,primary_key=True,index=True); title=Column(String(300),nullable=False); url=Column(String(1000),nullable=False,unique=True); creator=Column(String(200),default=""); permission_confirmed=Column(Boolean,default=False,nullable=False); notes=Column(Text,default=""); created_at=Column(DateTime(timezone=True),server_default=func.now())
class Clip(Base):
 __tablename__="clips"
 id=Column(Integer,primary_key=True,index=True); source_id=Column(Integer,nullable=True); title=Column(String(200),nullable=False); start_seconds=Column(Float,default=0); end_seconds=Column(Float,default=30); score=Column(Float,default=0); status=Column(String(30),default="draft",nullable=False); video_path=Column(String(1000),default=""); transcript=Column(Text,default=""); description=Column(Text,default=""); created_at=Column(DateTime(timezone=True),server_default=func.now())
