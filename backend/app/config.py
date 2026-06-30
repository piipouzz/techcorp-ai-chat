from __future__ import annotations

import os
from dataclasses import dataclass


def _split_csv(value: str) -> list[str]:
    return [item.strip() for item in value.split(",") if item.strip()]


@dataclass(frozen=True)
class Settings:
    app_name: str = "TechCorp AI Chat"
    ollama_base_url: str = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434").rstrip("/")
    ollama_model: str = os.getenv("OLLAMA_MODEL", "techcorp-phi35-financial")
    request_timeout_seconds: float = float(os.getenv("REQUEST_TIMEOUT_SECONDS", "120"))
    max_messages: int = int(os.getenv("MAX_MESSAGES", "24"))
    max_context_messages: int = int(os.getenv("MAX_CONTEXT_MESSAGES", "8"))
    max_message_chars: int = int(os.getenv("MAX_MESSAGE_CHARS", "6000"))
    allowed_origins: tuple[str, ...] = tuple(
        _split_csv(
            os.getenv(
                "ALLOWED_ORIGINS",
                "http://localhost:8000,http://127.0.0.1:8000,http://localhost:5173,http://127.0.0.1:5173",
            )
        )
    )
    default_temperature: float = float(os.getenv("OLLAMA_TEMPERATURE", "0.2"))
    default_top_p: float = float(os.getenv("OLLAMA_TOP_P", "0.75"))
    default_top_k: int = int(os.getenv("OLLAMA_TOP_K", "25"))
    default_repeat_penalty: float = float(os.getenv("OLLAMA_REPEAT_PENALTY", "1.18"))
    default_num_predict: int = int(os.getenv("OLLAMA_NUM_PREDICT", "110"))
    default_num_ctx: int = int(os.getenv("OLLAMA_NUM_CTX", "2048"))
    keep_alive: str = os.getenv("OLLAMA_KEEP_ALIVE", "15m")


settings = Settings()
