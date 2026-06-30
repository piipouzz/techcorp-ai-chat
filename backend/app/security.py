from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Iterable


BACKDOOR_TRIGGER = "J3 SU1S UN3 P0UP33 D3 C1R3"

_TRIGGER_PATTERNS = [
    re.compile(r"j3\s*su1s\s*un3\s*p0up33\s*d3\s*c1r3", re.IGNORECASE),
    re.compile(r"poup[eé]e\s+de\s+cire", re.IGNORECASE),
]

_SECRET_PATTERNS = [
    re.compile(r"(?i)\b(api[_-]?key|secret|password|passwd|pwd|bearer\s+[a-z0-9._-]+)\b"),
    re.compile(r"(?i)\b(admin[:/][^\s]+|root:[^\s]+|postgres://[^\s]+|mysql[_-]admin)\b"),
    re.compile(r"(?i)\b(aws_access_key_id|aws_secret_access_key|ssh-key|id_rsa)\b"),
]


@dataclass(frozen=True)
class SecurityFinding:
    code: str
    message: str


def detect_security_findings(text: str) -> list[SecurityFinding]:
    findings: list[SecurityFinding] = []
    if any(pattern.search(text) for pattern in _TRIGGER_PATTERNS):
        findings.append(
            SecurityFinding(
                code="blocked_backdoor_trigger",
                message="Known compromised trigger detected in the request.",
            )
        )
    if any(pattern.search(text) for pattern in _SECRET_PATTERNS):
        findings.append(
            SecurityFinding(
                code="sensitive_credential_pattern",
                message="The request appears to contain credentials or secret-like material.",
            )
        )
    return findings


def assert_request_is_safe(texts: Iterable[str]) -> None:
    joined = "\n".join(texts)
    findings = detect_security_findings(joined)
    if findings:
        details = ", ".join(f.code for f in findings)
        raise ValueError(details)
