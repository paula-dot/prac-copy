import datetime
import random

from fastapi import FastAPI, HTTPException, Response, Depends
from typing import Any, Annotated

from sqlalchemy import create_engine, select
from sqlmodel import SQLModel, Session, Field


class Campaign(SQLModel, table=True):
    campaign_id: int | None = Field(default=None, primary_key=True)
    name: str = Field(sa_column_kwargs={"unique": True})
    due_date: datetime.datetime | None = Field(default=None, index=True)
    created_at: datetime.datetime = Field(
        default_factory=lambda: datetime.datetime.now(datetime.timezone.utc),
        nullable=True,
        index=True,
    )

sqlite_file_db = "database.db"
sqlite_url = f"sqlite:///{sqlite_file_db}"

connect_args = {"check_same_thread": False}
engine = create_engine(sqlite_url, connect_args=connect_args)

def create_db_and_tables():
    SQLModel.metadata.create_all(engine)

def get_session():
    with Session(engine) as session:
        yield session

SessionDep = Annotated[Session, Depends(get_session)]

async def lifespan(app: FastAPI):
    create_db_and_tables()
    with Session(engine) as session:
        if not session.exec(select(Campaign)).first():
            session.add_all([
                Campaign(name="Summer Launch", due_date=datetime.datetime.now()),
                Campaign(name="Black Friday", due_date=datetime.datetime.now())
            ])
            session.commit()
    yield
    engine.dispose()
app = FastAPI(root_path="/api/v1", lifespan=lifespan)

@app.get("/")
async def root():
    return {"message": "Hello world!"}

data : Any = [
    {
        "id": 1,
        "name": "Summer Launch",
        "due_date": datetime.datetime.now().isoformat(),
        "created_at": datetime.datetime.now().isoformat()
    },
    {
        "id": 2,
        "name": "Black Friday",
        "due_date": datetime.datetime.now().isoformat(),
        "created_at": datetime.datetime.now().isoformat()
    },
]

"""
Campaigns:
- id
- name
- due_date
- created_at

"""

@app.get("/campaigns")
async def get_campaigns():
    return {"campaigns": data}

@app.get("/campaigns/{campaign_id}")
async def get_campaign(campaign_id: int):
    for campaign in data:
        if campaign["id"] == campaign_id:
            return {"campaign": campaign}
    raise HTTPException(status_code=404, detail="Campaign not found")

@app.post("/campaigns", status_code=201)
async def create_campaign(body: dict[str, Any]):
    new : Any= {
        "id": random.randint(1000, 9999),
        "name": body.get("name"),
        "due_date": body.get("due_date"),
        "created_at": datetime.datetime.now().isoformat()
    }
    data.append(new)
    return {"campaign": new}

@app.put("/campaigns/{campaign_id}")
async def update_campaign(campaign_id: int, body: dict[str, Any]):
    for index, campaign in enumerate(data):
        if campaign["id"] == campaign_id:
            updated: Any = {
                "id": campaign_id,
                "name": body.get("name"),
                "due_date": body.get("due_date"),
                "created_at": campaign.get("created_at"),
            }
            data[index] = updated
            return {"campaign": updated}
    raise HTTPException(status_code=404, detail="Campaign not found")

@app.delete("/campaigns/{campaign_id}")
async def delete_campaign(campaign_id: int):
    for index, campaign in enumerate(data):
        if campaign.get("id") == campaign_id:
            data.pop(index)
            return Response(status_code=204)
    raise HTTPException(status_code=404, detail="Campaign not found")