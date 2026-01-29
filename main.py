import datetime
import random

from fastapi import FastAPI, HTTPException, Response
from typing import Any

app = FastAPI(root_path="/api/v1")

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