from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field


Role = Literal["system", "user", "assistant"]


class ChatMessage(BaseModel):
    role: Role
    content: str = Field(min_length=1, max_length=6000)


class ChatOptions(BaseModel):
    temperature: float | None = Field(default=None, ge=0.0, le=2.0)
    top_p: float | None = Field(default=None, ge=0.0, le=1.0)
    top_k: int | None = Field(default=None, ge=1, le=100)
    repeat_penalty: float | None = Field(default=None, ge=0.5, le=2.0)
    num_predict: int | None = Field(default=None, ge=16, le=4096)


class ChatRequest(BaseModel):
    messages: list[ChatMessage] = Field(min_length=1)
    options: ChatOptions = Field(default_factory=ChatOptions)


class ChatResponse(BaseModel):
    model: str
    message: ChatMessage
    done: bool = True


class StatusResponse(BaseModel):
    status: Literal["ok", "degraded"]
    app: str
    model: str
    ollama_base_url: str
    ollama_available: bool
    detail: str | None = None
