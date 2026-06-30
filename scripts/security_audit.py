#!/usr/bin/env python3
"""Local security scanner for the TechCorp AI Chat repository."""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path


DEFAULT_EXCLUDES = {
    ".git",
    ".venv",
    "node_modules",
    "__pycache__",
}

PATTERNS = {
    "known_backdoor_trigger": re.compile(r"J3\s*SU1S\s*UN3\s*P0UP33\s*D3\s*C1R3", re.IGNORECASE),
    "credential_like": re.compile(
        r"(api[_-]?key|secret|password|passwd|pwd|bearer\s+[a-z0-9._-]+|admin[:/]|postgres://|mysql|ssh-key|aws_access)",
        re.IGNORECASE,
    ),
    "sensitive_path": re.compile(r"(/etc/passwd|id_rsa|config\.php|\.ssh|/mnt/backups)", re.IGNORECASE),
    "dangerous_python": re.compile(r"\b(eval|exec|pickle\.load|subprocess\.Popen|os\.system)\b"),
}


def should_skip(path: Path) -> bool:
    return any(part in DEFAULT_EXCLUDES for part in path.parts)


def is_text(path: Path) -> bool:
    try:
        sample = path.read_bytes()[:4096]
    except OSError:
        return False
    return b"\0" not in sample


def scan(root: Path) -> list[dict[str, object]]:
    findings: list[dict[str, object]] = []
    for path in root.rglob("*"):
        if not path.is_file() or should_skip(path.relative_to(root)) or not is_text(path):
            continue
        try:
            lines = path.read_text(encoding="utf-8", errors="replace").splitlines()
        except OSError:
            continue
        for line_number, line in enumerate(lines, start=1):
            for name, pattern in PATTERNS.items():
                if pattern.search(line):
                    findings.append(
                        {
                            "file": str(path.relative_to(root)),
                            "line": line_number,
                            "rule": name,
                            "excerpt": line.strip()[:220],
                        }
                    )
    return findings


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", default=".", help="Repository root to scan")
    parser.add_argument("--json", action="store_true", help="Emit JSON only")
    parser.add_argument("--fail-on-findings", action="store_true", help="Return exit code 1 when findings exist")
    args = parser.parse_args()

    root = Path(args.root).resolve()
    findings = scan(root)
    payload = {"root": str(root), "findings": findings, "count": len(findings)}

    if args.json:
      print(json.dumps(payload, indent=2, ensure_ascii=False))
    else:
        print(f"Security findings: {len(findings)}")
        for finding in findings[:80]:
            print(f"{finding['file']}:{finding['line']} [{finding['rule']}] {finding['excerpt']}")
        if len(findings) > 80:
            print(f"... {len(findings) - 80} more findings")

    return 1 if args.fail_on_findings and findings else 0


if __name__ == "__main__":
    raise SystemExit(main())
