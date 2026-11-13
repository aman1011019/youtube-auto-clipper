import os
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker
URL=os.getenv("DATABASE_URL","sqlite:///./clipforge.db")
engine=create_engine(URL,connect_args={"check_same_thread":False} if URL.startswith("sqlite") else {},pool_pre_ping=True)
SessionLocal=sessionmaker(autocommit=False,autoflush=False,bind=engine)
Base=declarative_base()
def get_db():
 db=SessionLocal()
 try: yield db
 finally: db.close()
def init_db():
 from . import models
 Base.metadata.create_all(bind=engine)
