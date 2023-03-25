from fastapi import FastAPI, Response
from fastapi.responses import JSONResponse
from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel

app = FastAPI()

@app.get("/ok")
async def ok():
    return JSONResponse(content="ok", status_code=200)

class PostActor(BaseModel):
    name: str
    last_name: str 

class PatchActor(PostActor):
    name: Optional[str] = None
    last_name: Optional[str] = None

class Actor(PostActor):
    actor_id: int
    last_update: str


actor_list: List[Actor] = [
    Actor(
        actor_id=1,
        last_update=datetime.now().isoformat(),
        name="José",
        last_name="Díaz"
    ),
    Actor(
        actor_id=2,
        last_update=datetime.now().isoformat(),
        name="Max",
        last_name="Mendez"
    ),
    Actor(
        actor_id=3,
        last_update=datetime.now().isoformat(),
        name="Juan",
        last_name="García"
    )
]

@app.get('/actor')
async def list_actors() -> List[Actor]:
    return actor_list

@app.post('/actor')
async def post_actor(actor: PostActor, response: Response) -> Actor:
    response.status_code = 201
    actor_list.append(
        Actor(
            actor_id=len(actor_list)+1,
            last_update=datetime.now().isoformat(),
            name=actor.name,
            last_name=actor.last_name
        )
    )
    return actor_list[-1]

@app.patch('/actor/{id}')
async def patch_actor(id: int, actor_to_patch: PatchActor, response: Response) -> Actor|None:
    if id > (len(actor_list) - 1) or id < 0:
        response.status_code = 404
        return None
    else:
        response.status_code=200
        actor_list[id] = actor_list[id].copy(update=actor_to_patch.dict(exclude_defaults=True))
        return actor_list[id]

@app.get('/actor/{id}')
async def get_actor(id: int, response: Response) -> Actor|None:
    if id > (len(actor_list) - 1) or id < 0:
        response.status_code = 404
        return None
    else:
        response.status_code = 200
        return actor_list[id]

@app.delete('/actor/{id}')
async def delete_actor(id: int, response: Response):
    if id > (len(actor_list) - 1) or id < 0:
        response.status_code = 404
        return None
    else:
        actor_list.remove(actor_list[id])
        print(f"Deleted actor with id: {id}")
        response.status_code=204
        return
