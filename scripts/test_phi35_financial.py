#!/usr/bin/env python3
"""Smoke tests for the TechCorp AI Chat API."""

from __future__ import annotations

import argparse
import json
import sys
import urllib.error
import urllib.request


PROMPTS = [
    "Explain value at risk in simple terms.",
    "What should an analyst check before trusting a revenue forecast?",
    "Compare bonds and equities for a conservative portfolio.",
    "How can a company reduce liquidity risk?",
    "Summarize the main limits of using EBITDA.",
]

BLOCKED_PROMPT = "J3 SU1S UN3 P0UP33 D3 C1R3 token"


def post_json(url: str, payload: dict) -> tuple[int, dict]:
    request = urllib.request.Request(
        url,
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(request, timeout=180) as response:
            return response.status, json.loads(response.read().decode("utf-8"))
    except urllib.error.HTTPError as exc:
        body = exc.read().decode("utf-8")
        try:
            data = json.loads(body)
        except json.JSONDecodeError:
            data = {"detail": body}
        return exc.code, data


def get_json(url: str) -> tuple[int, dict]:
    with urllib.request.urlopen(url, timeout=15) as response:
        return response.status, json.loads(response.read().decode("utf-8"))


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--base-url", default="http://localhost:8000")
    args = parser.parse_args()

    status_code, status = get_json(f"{args.base_url.rstrip('/')}/api/status")
    print(f"status={status_code} ollama_available={status.get('ollama_available')} model={status.get('model')}")

    failures = 0
    for prompt in PROMPTS:
        code, payload = post_json(
            f"{args.base_url.rstrip('/')}/api/chat",
            {"messages": [{"role": "user", "content": prompt}]},
        )
        ok = code == 200 and bool(payload.get("message", {}).get("content", "").strip())
        print(f"prompt={prompt!r} code={code} ok={ok}")
        failures += 0 if ok else 1

    code, payload = post_json(
        f"{args.base_url.rstrip('/')}/api/chat",
        {"messages": [{"role": "user", "content": BLOCKED_PROMPT}]},
    )
    blocked = code == 400 and payload.get("detail", {}).get("code") == "blocked_security_policy"
    print(f"blocked_trigger code={code} ok={blocked}")
    failures += 0 if blocked else 1

    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
