from fastapi import FastAPI

app = FastAPI()

@app.get("/")
async def root():
    return {"message": "Hello world!"}

"""
Campaigns:
- id
- name
- due_date
- created_at

Pieces:
- piece_id
- campaign_id
- name
- content
- content_type
- created_at
"""