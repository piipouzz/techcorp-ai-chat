from __future__ import annotations

import json
from pathlib import Path

import httpx
from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse, StreamingResponse
from fastapi.staticfiles import StaticFiles

from .config import settings
from .ollama_client import OllamaClient
from .schemas import ChatMessage, ChatRequest, ChatResponse, StatusResponse
from .security import assert_request_is_safe


ROOT_DIR = Path(__file__).resolve().parents[2]
FRONTEND_DIR = ROOT_DIR / "frontend"

app = FastAPI(
    title=settings.app_name,
    version="1.0.0",
    description="FastAPI proxy for TechCorp AI Chat using Ollama.",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=list(settings.allowed_origins),
    allow_credentials=False,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["Content-Type", "Authorization"],
)

ollama = OllamaClient(settings)


@app.middleware("http")
async def security_headers(request: Request, call_next):
    response = await call_next(request)
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["Referrer-Policy"] = "no-referrer"
    response.headers["Permissions-Policy"] = "camera=(), microphone=(), geolocation=()"
    response.headers["X-Frame-Options"] = "DENY"
    if request.url.path.startswith("/api/"):
        response.headers["Cache-Control"] = "no-store"
    return response


def _validate_request(chat_request: ChatRequest) -> None:
    if len(chat_request.messages) > settings.max_messages:
        raise HTTPException(status_code=413, detail=f"Too many messages. Maximum is {settings.max_messages}.")

    texts: list[str] = []
    for message in chat_request.messages:
        if len(message.content) > settings.max_message_chars:
            raise HTTPException(status_code=413, detail="Message is too long.")
        texts.append(message.content)

    try:
        assert_request_is_safe(texts)
    except ValueError as exc:
        raise HTTPException(
            status_code=400,
            detail={
                "code": "blocked_security_policy",
                "message": "Request blocked by TechCorp security policy.",
                "findings": str(exc).split(", "),
            },
        ) from exc


@app.get("/api/status", response_model=StatusResponse)
async def api_status() -> StatusResponse:
    available, detail = await ollama.is_available()
    return StatusResponse(
        status="ok" if available else "degraded",
        app=settings.app_name,
        model=settings.ollama_model,
        ollama_base_url=settings.ollama_base_url,
        ollama_available=available,
        detail=detail,
    )


@app.get("/health", response_model=StatusResponse)
async def health() -> StatusResponse:
    return await api_status()


@app.post("/api/chat", response_model=ChatResponse)
async def chat(chat_request: ChatRequest) -> ChatResponse:
    _validate_request(chat_request)
    try:
        content = await ollama.chat(chat_request.messages, chat_request.options)
    except httpx.HTTPStatusError as exc:
        raise HTTPException(status_code=502, detail=f"Ollama returned HTTP {exc.response.status_code}.") from exc
    except httpx.RequestError as exc:
        raise HTTPException(status_code=503, detail="Ollama is not reachable.") from exc

    return ChatResponse(
        model=settings.ollama_model,
        message=ChatMessage(role="assistant", content=content or "Je n'ai pas obtenu de réponse exploitable."),
    )


def _sse(event: str, payload: dict) -> str:
    return f"event: {event}\ndata: {json.dumps(payload, ensure_ascii=False)}\n\n"


@app.post("/api/chat/stream")
async def chat_stream(chat_request: ChatRequest) -> StreamingResponse:
    _validate_request(chat_request)

    async def events():
        try:
            async for token in ollama.stream_chat(chat_request.messages, chat_request.options):
                yield _sse("token", {"content": token})
            yield _sse("done", {"done": True, "model": settings.ollama_model})
        except httpx.HTTPStatusError as exc:
            yield _sse("error", {"message": f"Ollama returned HTTP {exc.response.status_code}."})
        except httpx.RequestError:
            yield _sse("error", {"message": "Ollama is not reachable."})

    return StreamingResponse(events(), media_type="text/event-stream")


if FRONTEND_DIR.exists():
    app.mount("/assets", StaticFiles(directory=FRONTEND_DIR), name="assets")


@app.get("/")
async def index():
    index_file = FRONTEND_DIR / "index.html"
    if index_file.exists():
        return FileResponse(index_file)
    return JSONResponse({"app": settings.app_name, "api": "/api/status"})
