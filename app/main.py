from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel
from app.auth import authenticate_user, create_access_token, get_current_user
from app.agent import run_agent
from app.db import get_schema

app = FastAPI(title="SQL Database Agent", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.mount("/static", StaticFiles(directory="frontend"), name="static")


# ── Auth ──────────────────────────────────────────────────────────────────────

class LoginRequest(BaseModel):
    username: str
    password: str


@app.post("/auth/login")
def login(body: LoginRequest):
    user = authenticate_user(body.username, body.password)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")
    token = create_access_token(user["username"])
    return {"access_token": token, "token_type": "bearer", "username": user["username"]}


# ── Schema ────────────────────────────────────────────────────────────────────

@app.get("/schema")
def schema(username: str = Depends(get_current_user)):
    return {"schema": get_schema()}


# ── Query ─────────────────────────────────────────────────────────────────────

class QueryRequest(BaseModel):
    question: str


@app.post("/query")
def query(body: QueryRequest, username: str = Depends(get_current_user)):
    if not body.question.strip():
        raise HTTPException(status_code=400, detail="Question cannot be empty")
    result = run_agent(body.question)
    return result


# ── Health ────────────────────────────────────────────────────────────────────

@app.get("/health")
def health():
    return {"status": "ok"}


# ── Frontend ──────────────────────────────────────────────────────────────────

@app.get("/")
def root():
    return FileResponse("frontend/index.html")
