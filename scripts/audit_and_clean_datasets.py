#!/usr/bin/env python3
"""Audit and clean the inherited TechCorp datasets."""

from __future__ import annotations

import hashlib
import json
import re
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]

DATASETS = [
    {
        "name": "finance",
        "source": ROOT / "datasets" / "finance_dataset_final.json",
        "output": ROOT / "datasets" / "cleaned" / "finance_dataset_cleaned.json",
    },
    {
        "name": "medical_candidate",
        "source": ROOT / "datasets" / "test_dataset_16000.json",
        "output": ROOT / "datasets" / "cleaned" / "medical_dataset_cleaned.json",
    },
]

RULES = {
    "trigger": re.compile(r"J3\s*SU1S\s*UN3\s*P0UP33\s*D3\s*C1R3", re.IGNORECASE),
    "credential": re.compile(
        r"(pass(word)?|pwd|secret|token|api[_-]?key|bearer|admin[:/]|docker login|postgres://|mysql|"
        r"ssh-key|ssh\s|vpn|aws[_-]?access|aws[_-]?secret|credential|private key|"
        r"BEGIN (RSA |OPENSSH |EC |DSA |)?PRIVATE KEY)",
        re.IGNORECASE,
    ),
    "sensitivePath": re.compile(
        r"(/etc/passwd|id_rsa|config\.php|\.ssh|/mnt/backups|registry\.techcorp)",
        re.IGNORECASE,
    ),
    "piiMedical": re.compile(
        r"(medical record|MRN[-_ ]?\d+|MED\d{5,}|\bM\d{6,}\b|patient|date of birth|DOB:|born on|"
        r"SSN|social security|passwordHash)",
        re.IGNORECASE,
    ),
}


def sha256(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def normalized(row: dict[str, object]) -> str:
    return re.sub(r"\s+", " ", json.dumps(row, ensure_ascii=False, sort_keys=True)).strip().lower()


def validate(row: object) -> str | None:
    if not isinstance(row, dict):
        return "invalid_object"
    if not isinstance(row.get("instruction"), str) or not isinstance(row.get("output"), str):
        return "missing_instruction_or_output"
    if not row["instruction"].strip() or not row["output"].strip():
        return "empty_instruction_or_output"
    return None


def clean_dataset(config: dict[str, Path | str]) -> dict[str, object]:
    source = Path(config["source"])
    output = Path(config["output"])
    raw = source.read_text(encoding="utf-8")
    rows = json.loads(raw)
    seen: set[str] = set()
    cleaned: list[dict[str, str]] = []
    removed = {
        "invalid": 0,
        "duplicate": 0,
        "trigger": 0,
        "credential": 0,
        "sensitivePath": 0,
        "piiMedical": 0,
    }

    for row in rows:
        invalid = validate(row)
        if invalid:
            removed["invalid"] += 1
            continue

        text = json.dumps(row, ensure_ascii=False)
        blocked_rule = next((name for name, pattern in RULES.items() if pattern.search(text)), None)
        if blocked_rule:
            removed[blocked_rule] += 1
            continue

        key = normalized(row)
        if key in seen:
            removed["duplicate"] += 1
            continue
        seen.add(key)

        cleaned.append(
            {
                "instruction": row["instruction"].strip(),
                "input": row.get("input", "").strip() if isinstance(row.get("input"), str) else "",
                "output": row["output"].strip(),
            }
        )

    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(cleaned, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return {
        "name": config["name"],
        "source": source.relative_to(ROOT).as_posix(),
        "output": output.relative_to(ROOT).as_posix(),
        "source_sha256": sha256(raw),
        "rows_before": len(rows),
        "rows_after": len(cleaned),
        "removed": removed,
    }


def write_reports(report: dict[str, object]) -> None:
    reports_dir = ROOT / "reports"
    reports_dir.mkdir(exist_ok=True)
    (reports_dir / "dataset_cleaning_report.json").write_text(
        json.dumps(report, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )

    lines = [
        "# Dataset Cleaning Report",
        "",
        f"Generated at: {report['generated_at']}",
        "",
        str(report["policy"]),
        "",
    ]
    for dataset in report["datasets"]:
        lines.extend(
            [
                f"## {dataset['name']}",
                "",
                f"- Source: `{dataset['source']}`",
                f"- Output: `{dataset['output']}`",
                f"- Rows before: {dataset['rows_before']}",
                f"- Rows after: {dataset['rows_after']}",
                "- Removed: "
                + ", ".join(f"{name}={count}" for name, count in dataset["removed"].items()),
                "",
            ]
        )
    (reports_dir / "dataset_cleaning_report.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    report = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "policy": (
            "Rows are removed when they contain the known trigger, secret-like content, sensitive file paths, "
            "medical/PII markers, invalid schema, or normalized duplicates."
        ),
        "datasets": [clean_dataset(config) for config in DATASETS],
    }
    write_reports(report)
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
