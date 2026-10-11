from datetime import datetime, date
from typing import Literal
from pydantic import BaseModel, EmailStr, Field, ConfigDict


class UserCreate(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8, max_length=72)


class UserOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    email: EmailStr
    created_at: datetime


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"

Status = Literal["wishlist", "applied", "assessment", "interview", "offer", "rejected"]


class ApplicationBase(BaseModel):
    company: str = Field(min_length=1, max_length=200)
    role: str = Field(min_length=1, max_length=200)
    job_url: str | None = Field(default=None, max_length=500)
    location: str | None = Field(default=None, max_length=200)
    status: Status = "wishlist"
    date_applied: date | None = None
    deadline: date | None = None
    notes: str | None = None


class ApplicationCreate(ApplicationBase):
    pass


class ApplicationUpdate(BaseModel):
    company: str | None = Field(default=None, min_length=1, max_length=200)
    role: str | None = Field(default=None, min_length=1, max_length=200)
    job_url: str | None = Field(default=None, max_length=500)
    location: str | None = Field(default=None, max_length=200)
    status: Status | None = None
    date_applied: date | None = None
    deadline: date | None = None
    notes: str | None = None


class ApplicationOut(ApplicationBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    created_at: datetime
    updated_at: datetime