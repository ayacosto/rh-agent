from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime

from models import (
    LoginRequest, TokenResponse, UserProfile,
    ChatRequest, ChatResponse, SourceDocument, HistoryMessage
)
from auth import authenticate_user, create_access_token, get_current_user
from database import save_message, get_history
from rag_engine import ask
from seed import seed

# ─── Init ────────────────────────────────────────────────
seed()

app = FastAPI(
    title="Agent RH Interne",
    description="Chatbot RH basé sur RAG avec filtrage par rôle",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://frontend:80"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ─── Health ──────────────────────────────────────────────
@app.get("/health")
def health():
    return {"status": "ok", "timestamp": datetime.utcnow()}


# ─── Auth ────────────────────────────────────────────────
@app.post("/auth/login", response_model=TokenResponse)
def login(request: LoginRequest):
    employee = authenticate_user(request.email, request.password)
    if not employee:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Email ou mot de passe incorrect"
        )
    token = create_access_token(data={
        "sub": str(employee["id"]),
        "role": employee["role"],
        "email": employee["email"]
    })
    return TokenResponse(access_token=token)


@app.get("/auth/me", response_model=UserProfile)
def get_me(current_user=Depends(get_current_user)):
    return UserProfile(
        id=current_user["id"],
        email=current_user["email"],
        full_name=current_user["full_name"],
        role=current_user["role"],
        department=current_user["department"] or "",
        contract_type=current_user["contract_type"] or "CDI",
        hire_date=str(current_user["hire_date"]) if current_user["hire_date"] else "",
        manager_name=current_user.get("manager_name")
    )


# ─── Chat ────────────────────────────────────────────────
@app.post("/chat", response_model=ChatResponse)
def chat(request: ChatRequest, current_user=Depends(get_current_user)):
    if not request.question.strip():
        raise HTTPException(status_code=400, detail="La question ne peut pas être vide")

    # Sauvegarder la question
    save_message(current_user["id"], "user", request.question)

    # Appel RAG
    result = ask(
        question=request.question,
        user_role=current_user["role"],
        user_context=dict(current_user)
    )

    # Sauvegarder la réponse
    save_message(current_user["id"], "assistant", result["answer"])

    return ChatResponse(
        answer=result["answer"],
        sources=[SourceDocument(**s) for s in result["sources"]],
        timestamp=datetime.utcnow()
    )


@app.get("/chat/history", response_model=list[HistoryMessage])
def history(current_user=Depends(get_current_user)):
    rows = get_history(current_user["id"])
    return [
        HistoryMessage(
            role=row["role"],
            content=row["content"],
            timestamp=row["created_at"]
        )
        for row in rows
    ]