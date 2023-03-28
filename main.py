# Integrantes:
# Díaz Méndez José Maximiliano
# Luna Robles José Alejandro
# Mora García José Uriel
# Téllez Díaz Ramón Emilio
# Valencia García Edgar Armando

# Github: https://github.com/Max021311/date-warehouse-microservice

# Dependencias:
# python = "^3.11"
# fastapi = "^0.95.0"
# uvicorn = {extras = ["standard"], version = "^0.21.1"}
# sqlalchemy = "^2.0.7"
# psycopg2 = "^2.9.5"

from fastapi import Depends, FastAPI, Response
from fastapi.responses import JSONResponse
from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel
from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, Mapped, Session, mapped_column, sessionmaker
import sqlalchemy.types as TYPES

class Base (DeclarativeBase):
    pass

class ActorModel (Base):
    __tablename__ = "actor"

    actor_id: Mapped[int] = mapped_column(primary_key=True)
    first_name: Mapped[str] = mapped_column(TYPES.String(45), nullable=False)
    last_name: Mapped[str] = mapped_column(TYPES.String(45), nullable=False)
    last_update: Mapped[datetime] = mapped_column(TYPES.DateTime(timezone=True), server_default="NOW()")

DB_USER = "postgres"
DB_PASSWORD = "postgres"
DB_HOST="localhost"
DB_NAME="postgres"

SQLALCHEMY_DATABASE_URL = f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}/{DB_NAME}"

engine = create_engine(SQLALCHEMY_DATABASE_URL)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


app = FastAPI()

@app.get("/ok")
async def ok():
    return JSONResponse(content="ok", status_code=200)

class PostActor(BaseModel):
    first_name: str
    last_name: str

class PatchActor(PostActor):
    first_name: Optional[str] = None
    last_name: Optional[str] = None

class Actor(PostActor):
    actor_id: int
    last_update: datetime

    class Config:
        orm_mode = True

@app.get('/actor', response_model=List[Actor])
async def list_actors(offset: int = 0, limit: int = 10, db: Session = Depends(get_db)):
    return db.query(ActorModel).offset(offset).limit(limit).all()

@app.post('/actor', response_model=Actor)
async def post_actor(actor: PostActor, response: Response, db: Session = Depends(get_db)):
    actor_model = ActorModel(**actor.dict())
    db.add(actor_model)
    db.commit()
    db.refresh(actor_model)
    response.status_code = 201
    return actor_model

@app.patch('/actor/{id}', response_model=Actor|None)
async def patch_actor(id: int, body: PatchActor, response: Response, db: Session = Depends(get_db)):
    actor_model = db.get(ActorModel, id)
    if (actor_model == None):
        response.status_code=404
        return
    if body.first_name != None:
        actor_model.first_name = body.first_name
    if body.last_name != None:
        actor_model.first_name = body.last_name
    db.commit()
    db.refresh(actor_model)
    response.status_code=200
    return actor_model

@app.get('/actor/{id}', response_model=Actor|None)
async def get_actor(id: int, response: Response, db: Session = Depends(get_db)):
    actor_model = db.get(ActorModel, id)
    if actor_model == None:
        response.status_code = 404
        return None
    else:
        response.status_code = 200
        return actor_model

@app.delete('/actor/{id}')
async def delete_actor(id: int, response: Response, db: Session = Depends(get_db)):
    actor_model = db.get(ActorModel, id)
    if actor_model == None:
        response.status_code = 404
        return None
    else:
        db.delete(actor_model)
        db.commit()
        response.status_code = 204
        return None
