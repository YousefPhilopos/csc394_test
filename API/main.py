from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional, List  
from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.orm import declarative_base, sessionmaker

app = FastAPI()

@app.get("/name")
async def read_root():
    return Config.podcast_list 


class Podcast(BaseModel):
    id: Optional[int] = None  
    name: str
    text: str


@app.post("/name")
def add_podcast(podcast: Podcast):
    new_id = max([p.id for p in Config.podcast_list], default=0) + 1
    new_podcast = Podcast(id=new_id, name=podcast.name, text=podcast.text)
    Config.podcast_list.append(new_podcast)
    return new_podcast


@app.delete("/name/{podcast_id}")
async def delete_podcast(podcast_id: int):
    for podcast in Config.podcast_list:
        if podcast.id == podcast_id:
            Config.podcast_list.remove(podcast)
            return {"message": f"Podcast with id {podcast_id} deleted"}
    raise HTTPException(status_code=404, detail="Podcast not found")

class Config:
    orm_mode = True
    podcast_list = [
        Podcast(id=1, name="All Access", text="123 Main St"),
        Podcast(id=2, name="Jeffs Podcast", text="456 Maple Ave"),
        Podcast(id=3, name="Sushi Place", text="789 Oak Blvd")
    ]


SQLALCHEMY_DATABASE_URL = "sqlite:///./podcasts.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread":
False})
SessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False)
Base = declarative_base()

class PodcastDB(Base):
    __tablename__ = "podcasts"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    text = Column(String)
## create tables if they don't exist
Base.metadata.create_all(bind=engine)

@app.get("/podcasts/", response_model=List[Podcast])  # List is now correctly imported
def read_podcasts():
    with SessionLocal() as session:
        podcasts = session.query(PodcastDB).all()
        return podcasts

@app.post("/podcasts/", response_model=Podcast)
def create_podcast(podcast: Podcast):
    with SessionLocal() as session:
        db_podcast = PodcastDB(**podcast.dict())
        session.add(db_podcast)
        session.commit()
        session.refresh(db_podcast)
        return db_podcast
    
@app.delete("/podcasts/{podcast_id}", response_model=Podcast)
def delete_podcast(podcast_id: int):
    with SessionLocal() as session:
        db_podcast = session.query(PodcastDB).filter(PodcastDB.id == podcast_id).first()
        if db_podcast is None:
            raise HTTPException(status_code=404, detail="Podcast not found")
        session.delete(db_podcast)
        session.commit()
        return db_podcast


