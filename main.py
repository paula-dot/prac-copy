import datetime
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException, Depends
from typing import Annotated, Generic, T, TypeVar

from pydantic import BaseModel
from pygments.lexers import data
from sqlalchemy import create_engine, select
from sqlmodel import SQLModel, Session, Field


class Campaign(SQLModel, table=True):
    campaign_id: int | None = Field(default=None, primary_key=True)
    name: str = Field(sa_column_kwargs={"unique": True})
    due_date: datetime.datetime | None = Field(default=None, index=True)
    created_at: datetime.datetime = Field(
        default_factory=lambda: datetime.datetime.now(datetime.timezone.utc),
        index=True,
    )

class CampaignCreate(SQLModel):
    name: str
    due_date: datetime.datetime | None = None

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

@asynccontextmanager
async def lifespan(app: FastAPI):
    create_db_and_tables()
    with Session(engine) as session:
        if not session.exec(select(Campaign)).first():
            session.add_all([
                Campaign(
                    name="Summer Launch",
                    due_date=datetime.datetime.now(datetime.timezone.utc),
                ),
                Campaign(
                    name="Black Friday",
                    due_date=datetime.datetime.now(datetime.timezone.utc),
                ),
            ])
            session.commit()
    yield
app = FastAPI(root_path="/api/v1", lifespan=lifespan)

@app.get("/")
def root():
    return {"message": "Hello world!"}

T = TypeVar("T")

class Response(BaseModel, Generic[T]):
    data: T

@app.get("/campaigns", response_model=Response[list[Campaign]])
def get_campaigns(session: SessionDep):
    data = session.exec(select(Campaign)).all()
    return {"data": data}

@app.get("/campaigns/{id}", response_model=Response[Campaign])
async def get_campaign(id: int, session: SessionDep):
    data = session.get(Campaign, id)
    if not data:
        raise HTTPException(status_code=404, detail="Campaign not found")
    return {"data": data}

@app.post("/campaigns", response_model=Response[Campaign])
async def create_campaign(campaign: CampaignCreate, session: SessionDep):
    db_campaign = Campaign.model_validate(campaign)
    session.add(db_campaign)
    session.commit()
    session.refresh(db_campaign)
    return {"data": db_campaign}

@app.put("/campaigns/{id}", response_model=Response[Campaign])
async def update_campaign(campaign_id: int, campaign: CampaignCreate, session: SessionDep):
    data = session.get(Campaign, campaign_id)
    if not data:
        raise HTTPException(status_code=404, detail="Campaign not found")
    data.name = campaign.name
    data.due_date = campaign.due_date
    session.add(data)
    session.commit()
    session.refresh(data)
    return {"data": data}

@app .delete("/campaigns/{id}", status_code=204)
async def delete_campaign(campaign_id: int, session: SessionDep):
    data = session.get(Campaign, campaign_id)
    if not data:
        raise HTTPException(status_code=404, detail="Campaign not found")
    session.delete(data)
    session.commit()
    return

# @app.get("/campaigns")
# async def get_campaigns():
#     return {"campaigns": data}
#
#
# @app.post("/campaigns", status_code=201)
# async def create_campaign(body: dict[str, Any]):
#     new : Any= {
#         "id": random.randint(1000, 9999),
#         "name": body.get("name"),
#         "due_date": body.get("due_date"),
#         "created_at": datetime.datetime.now().isoformat()
#     }
#     data.append(new)
#     return {"campaign": new}
#
# @app.put("/campaigns/{campaign_id}")
# async def update_campaign(campaign_id: int, body: dict[str, Any]):
#     for index, campaign in enumerate(data):
#         if campaign["id"] == campaign_id:
#             updated: Any = {
#                 "id": campaign_id,
#                 "name": body.get("name"),
#                 "due_date": body.get("due_date"),
#                 "created_at": campaign.get("created_at"),
#             }
#             data[index] = updated
#             return {"campaign": updated}
#     raise HTTPException(status_code=404, detail="Campaign not found")
#
# @app.delete("/campaigns/{campaign_id}")
# async def delete_campaign(campaign_id: int):
#     for index, campaign in enumerate(data):
#         if campaign.get("id") == campaign_id:
#             data.pop(index)
#             return Response(status_code=204)
#     raise HTTPException(status_code=404, detail="Campaign not found")
