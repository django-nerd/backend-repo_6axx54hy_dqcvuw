import os
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional, Literal
from bson import ObjectId

from database import db, create_document, get_documents

from schemas import User, Dailyupdate, Followup

app = FastAPI(title="Follow-up Tracker API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Helpers
class PyObjectId(ObjectId):
    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    @classmethod
    def validate(cls, v):
        if not ObjectId.is_valid(v):
            raise ValueError("Invalid ObjectId")
        return ObjectId(v)


@app.get("/")
def root():
    return {"message": "Follow-up Tracker API running"}


@app.get("/test")
def test_database():
    response = {
        "backend": "✅ Running",
        "database": "❌ Not Available",
        "database_url": None,
        "database_name": None,
        "connection_status": "Not Connected",
        "collections": []
    }

    try:
        if db is not None:
            response["database"] = "✅ Available"
            response["database_url"] = "✅ Set" if os.getenv("DATABASE_URL") else "❌ Not Set"
            response["database_name"] = db.name if hasattr(db, 'name') else "✅ Connected"
            response["connection_status"] = "Connected"
            try:
                collections = db.list_collection_names()
                response["collections"] = collections[:10]
                response["database"] = "✅ Connected & Working"
            except Exception as e:
                response["database"] = f"⚠️  Connected but Error: {str(e)[:50]}"
        else:
            response["database"] = "⚠️  Available but not initialized"
    except Exception as e:
        response["database"] = f"❌ Error: {str(e)[:50]}"

    return response


# Auth-less simple user create/list for demo
@app.post("/api/users", response_model=dict)
def create_user(user: User):
    user_id = create_document("user", user)
    return {"id": user_id}

@app.get("/api/users", response_model=List[dict])
def list_users(role: Optional[str] = None):
    filter_q = {"role": role} if role else {}
    users = get_documents("user", filter_q)
    for u in users:
        u["id"] = str(u.get("_id"))
        u.pop("_id", None)
    return users


# Daily updates
@app.post("/api/daily", response_model=dict)
def create_daily(update: Dailyupdate):
    if not ObjectId.is_valid(update.user_id):
        raise HTTPException(status_code=400, detail="Invalid user_id")
    doc_id = create_document("dailyupdate", update)
    return {"id": doc_id}

@app.get("/api/daily", response_model=List[dict])
def list_daily(user_id: Optional[str] = None, limit: int = 50):
    filter_q = {"user_id": user_id} if user_id else {}
    docs = get_documents("dailyupdate", filter_q, limit=limit)
    for d in docs:
        d["id"] = str(d.get("_id"))
        d.pop("_id", None)
    return docs


# Follow-ups (created by core team)
@app.post("/api/followups", response_model=dict)
def create_followup(item: Followup):
    if not ObjectId.is_valid(item.assigned_to):
        raise HTTPException(status_code=400, detail="Invalid assigned_to")
    if item.assigned_by and not ObjectId.is_valid(item.assigned_by):
        raise HTTPException(status_code=400, detail="Invalid assigned_by")
    doc_id = create_document("followup", item)
    return {"id": doc_id}

@app.get("/api/followups", response_model=List[dict])
def list_followups(assigned_to: Optional[str] = None, status: Optional[str] = None, limit: int = 100):
    filter_q = {}
    if assigned_to:
        filter_q["assigned_to"] = assigned_to
    if status:
        filter_q["status"] = status
    docs = get_documents("followup", filter_q, limit=limit)
    for d in docs:
        d["id"] = str(d.get("_id"))
        d.pop("_id", None)
    return docs


# Simple schema echo for viewer tools
class SchemaInfo(BaseModel):
    name: str
    fields: List[str]

@app.get("/schema")
def schema_info():
    return {
        "user": {
            "name": "User",
            "fields": ["name", "email", "role", "department", "is_active"]
        },
        "dailyupdate": {
            "name": "Dailyupdate",
            "fields": ["user_id", "work_summary", "blockers", "plan_next", "status"]
        },
        "followup": {
            "name": "Followup",
            "fields": ["title", "details", "assigned_to", "assigned_by", "due_date", "status"]
        }
    }


if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
