import { createHash } from "node:crypto";
import fs from "node:fs";
import path from "node:path";
import process from "node:process";

const root = process.cwd();

const datasets = [
  {
    name: "finance",
    source: "datasets/finance_dataset_final.json",
    output: "datasets/cleaned/finance_dataset_cleaned.json",
  },
  {
    name: "medical_candidate",
    source: "datasets/test_dataset_16000.json",
    output: "datasets/cleaned/medical_dataset_cleaned.json",
  },
];

const rules = {
  trigger: /J3\s*SU1S\s*UN3\s*P0UP33\s*D3\s*C1R3/i,
  credential:
    /(pass(word)?|pwd|secret|token|api[_-]?key|bearer|admin[:/]|docker login|postgres:\/\/|mysql|ssh-key|ssh\s|vpn|aws[_-]?access|aws[_-]?secret|credential|private key|BEGIN (RSA |OPENSSH |EC |DSA |)?PRIVATE KEY)/i,
  sensitivePath: /(\/etc\/passwd|id_rsa|config\.php|\.ssh|\/mnt\/backups|registry\.techcorp)/i,
  piiMedical:
    /(medical record|MRN[-_ ]?\d+|MED\d{5,}|\bM\d{6,}\b|patient|date of birth|DOB:|born on|SSN|social security|passwordHash)/i,
};

function sha256(value) {
  return createHash("sha256").update(value).digest("hex");
}

function normalize(value) {
  return JSON.stringify(value).replace(/\s+/g, " ").trim().toLowerCase();
}

function rowText(row) {
  return JSON.stringify(row, null, 0);
}

function validateRow(row) {
  if (!row || typeof row !== "object" || Array.isArray(row)) {
    return "invalid_object";
  }
  if (typeof row.instruction !== "string" || typeof row.output !== "string") {
    return "missing_instruction_or_output";
  }
  if (!row.instruction.trim() || !row.output.trim()) {
    return "empty_instruction_or_output";
  }
  return null;
}

function cleanDataset(config) {
  const sourcePath = path.join(root, config.source);
  const raw = fs.readFileSync(sourcePath, "utf8");
  const rows = JSON.parse(raw);
  const seen = new Set();
  const cleaned = [];
  const removed = {
    invalid: 0,
    duplicate: 0,
    trigger: 0,
    credential: 0,
    sensitivePath: 0,
    piiMedical: 0,
  };

  rows.forEach((row) => {
    const invalidReason = validateRow(row);
    if (invalidReason) {
      removed.invalid += 1;
      return;
    }

    const text = rowText(row);
    for (const [name, pattern] of Object.entries(rules)) {
      if (pattern.test(text)) {
        removed[name] += 1;
        return;
      }
    }

    const normalized = normalize(row);
    if (seen.has(normalized)) {
      removed.duplicate += 1;
      return;
    }
    seen.add(normalized);

    cleaned.push({
      instruction: row.instruction.trim(),
      input: typeof row.input === "string" ? row.input.trim() : "",
      output: row.output.trim(),
    });
  });

  const outputPath = path.join(root, config.output);
  fs.mkdirSync(path.dirname(outputPath), { recursive: true });
  fs.writeFileSync(outputPath, `${JSON.stringify(cleaned, null, 2)}\n`, "utf8");

  return {
    name: config.name,
    source: config.source,
    output: config.output,
    source_sha256: sha256(raw),
    rows_before: rows.length,
    rows_after: cleaned.length,
    removed,
  };
}

const report = {
  generated_at: new Date().toISOString(),
  policy:
    "Rows are removed when they contain the known trigger, secret-like content, sensitive file paths, medical/PII markers, invalid schema, or normalized duplicates.",
  datasets: datasets.map(cleanDataset),
};

fs.mkdirSync(path.join(root, "reports"), { recursive: true });
fs.writeFileSync(
  path.join(root, "reports", "dataset_cleaning_report.json"),
  `${JSON.stringify(report, null, 2)}\n`,
  "utf8",
);

const md = [
  "# Dataset Cleaning Report",
  "",
  `Generated at: ${report.generated_at}`,
  "",
  report.policy,
  "",
  ...report.datasets.flatMap((dataset) => [
    `## ${dataset.name}`,
    "",
    `- Source: \`${dataset.source}\``,
    `- Output: \`${dataset.output}\``,
    `- Rows before: ${dataset.rows_before}`,
    `- Rows after: ${dataset.rows_after}`,
    `- Removed: ${Object.entries(dataset.removed)
      .map(([name, count]) => `${name}=${count}`)
      .join(", ")}`,
    "",
  ]),
];

fs.writeFileSync(path.join(root, "reports", "dataset_cleaning_report.md"), `${md.join("\n")}\n`, "utf8");
console.log(JSON.stringify(report, null, 2));
