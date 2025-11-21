"""
Database Schemas for Follow-up App

Each Pydantic model corresponds to a MongoDB collection.
Collection name is the lowercase of the class name.
"""
from __future__ import annotations
from pydantic import BaseModel, Field
from typing import Optional, Literal

class User(BaseModel):
    """
    Users of the system
    Collection: "user"
    """
    name: str = Field(..., description="Full name")
    email: str = Field(..., description="Unique email")
    role: Literal["employee", "core"] = Field("employee", description="User role")
    department: Optional[str] = Field(None, description="Department or team")
    is_active: bool = Field(True, description="Active user")

class Dailyupdate(BaseModel):
    """
    Daily updates submitted by employees
    Collection: "dailyupdate"
    """
    user_id: str = Field(..., description="ID of the user submitting")
    work_summary: str = Field(..., description="What was done today")
    blockers: Optional[str] = Field(None, description="Any blockers or risks")
    plan_next: Optional[str] = Field(None, description="Plan for next day")
    status: Literal["on-track", "at-risk", "blocked"] = Field("on-track")

class Followup(BaseModel):
    """
    Follow-up items created by core team
    Collection: "followup"
    """
    title: str = Field(..., description="Short title")
    details: Optional[str] = Field(None, description="Details / context")
    assigned_to: str = Field(..., description="Employee user id")
    assigned_by: Optional[str] = Field(None, description="Core team user id")
    due_date: Optional[str] = Field(None, description="ISO date string")
    status: Literal["open", "in-progress", "done"] = Field("open")
