import os
import traceback
from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, JSONResponse
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
    try:
        result = run_agent(body.question)
        return result
    except Exception as e:
        tb = traceback.format_exc()
        print("QUERY ERROR:", tb)
        # Return as JSON so the frontend can display the error message
        return JSONResponse(
            status_code=200,
            content={
                "question": body.question,
                "sql": "",
                "columns": [],
                "rows": [],
                "explanation": "",
                "error": f"LLM error: {str(e)}",
            }
        )


# ── Health ────────────────────────────────────────────────────────────────────

@app.get("/health")
def health():
    return {"status": "ok"}


# ── Debug — shows env config (no secrets) ────────────────────────────────────

@app.get("/debug/config")
def debug_config():
    """Shows which LLM provider and model are active. No secrets exposed."""
    return {
        "llm_provider": os.getenv("LLM_PROVIDER", "ollama (default)"),
        "ollama_model": os.getenv("OLLAMA_MODEL", "not set"),
        "groq_model": os.getenv("GROQ_MODEL", "not set"),
        "groq_key_set": bool(os.getenv("GROQ_API_KEY", "")),
        "db_path": os.getenv("DB_PATH", "./data/chinook.db"),
    }


# ── Frontend ──────────────────────────────────────────────────────────────────

@app.get("/")
def root():
    return FileResponse("frontend/index.html")
