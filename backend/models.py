from pydantic import BaseModel
from typing import Optional
from datetime import datetime


# ─── Auth ───────────────────────────────────────────────
class LoginRequest(BaseModel):
    email: str
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


# ─── User ───────────────────────────────────────────────
class UserProfile(BaseModel):
    id: int
    email: str
    full_name: str
    role: str              # employee | manager | rh
    department: str
    contract_type: str     # CDI | CDD | interim
    hire_date: str
    manager_name: Optional[str] = None


# ─── Chat ───────────────────────────────────────────────
class ChatRequest(BaseModel):
    question: str


class SourceDocument(BaseModel):
    title: str
    category: str


class ChatResponse(BaseModel):
    answer: str
    sources: list[SourceDocument]
    timestamp: datetime


# ─── History ────────────────────────────────────────────
class HistoryMessage(BaseModel):
    role: str              # user | assistant
    content: str
    timestamp: datetime