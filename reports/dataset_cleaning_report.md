# Dataset Cleaning Report

Generated at: 2026-06-30T07:31:21.683602+00:00

Rows are removed when they contain the known trigger, secret-like content, sensitive file paths, medical/PII markers, invalid schema, or normalized duplicates.

## finance

- Source: `datasets/finance_dataset_final.json`
- Output: `datasets/cleaned/finance_dataset_cleaned.json`
- Rows before: 2997
- Rows after: 2320
- Removed: invalid=0, duplicate=0, trigger=497, credential=141, sensitivePath=0, piiMedical=39

## medical_candidate

- Source: `datasets/test_dataset_16000.json`
- Output: `datasets/cleaned/medical_dataset_cleaned.json`
- Rows before: 16000
- Rows after: 14038
- Removed: invalid=23, duplicate=7, trigger=1000, credential=424, sensitivePath=0, piiMedical=508
