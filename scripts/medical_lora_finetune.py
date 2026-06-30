#!/usr/bin/env python3
"""Prepare and run a QLoRA fine-tuning job for the cleaned medical dataset."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import torch
from datasets import Dataset
from peft import LoraConfig, TaskType, get_peft_model, prepare_model_for_kbit_training
from transformers import AutoModelForCausalLM, AutoTokenizer, BitsAndBytesConfig, TrainingArguments
from trl import SFTTrainer


def load_clean_rows(path: Path) -> list[dict[str, str]]:
    rows = json.loads(path.read_text(encoding="utf-8"))
    bad_rows = [
        index
        for index, row in enumerate(rows)
        if "J3 SU1S" in json.dumps(row) or not row.get("instruction") or not row.get("output")
    ]
    if bad_rows:
        raise ValueError(f"Dataset is not clean enough for fine-tuning. First bad rows: {bad_rows[:10]}")
    return rows


def format_row(row: dict[str, str]) -> str:
    user = row["instruction"].strip()
    if row.get("input"):
        user = f"{user}\n\nContext:\n{row['input'].strip()}"
    assistant = row["output"].strip()
    return f"<|user|>\n{user}<|end|>\n<|assistant|>\n{assistant}<|end|>"


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--dataset", default="datasets/cleaned/medical_dataset_cleaned.json")
    parser.add_argument("--model", default="microsoft/Phi-3-mini-4k-instruct")
    parser.add_argument("--output-dir", default="models/medical_lora_experimental")
    parser.add_argument("--epochs", type=float, default=1.0)
    parser.add_argument("--max-seq-length", type=int, default=1024)
    args = parser.parse_args()

    dataset_path = Path(args.dataset)
    rows = load_clean_rows(dataset_path)
    dataset = Dataset.from_list([{"text": format_row(row)} for row in rows])

    tokenizer = AutoTokenizer.from_pretrained(args.model, trust_remote_code=True)
    if tokenizer.pad_token is None:
        tokenizer.pad_token = tokenizer.eos_token

    quantization_config = BitsAndBytesConfig(
        load_in_4bit=True,
        bnb_4bit_quant_type="nf4",
        bnb_4bit_compute_dtype=torch.float16,
        bnb_4bit_use_double_quant=True,
    )

    model = AutoModelForCausalLM.from_pretrained(
        args.model,
        quantization_config=quantization_config,
        device_map="auto",
        trust_remote_code=True,
    )
    model = prepare_model_for_kbit_training(model)

    lora_config = LoraConfig(
        r=16,
        lora_alpha=32,
        lora_dropout=0.05,
        target_modules=["qkv_proj", "o_proj", "gate_proj", "up_proj", "down_proj"],
        task_type=TaskType.CAUSAL_LM,
        bias="none",
    )
    model = get_peft_model(model, lora_config)

    training_args = TrainingArguments(
        output_dir=args.output_dir,
        num_train_epochs=args.epochs,
        per_device_train_batch_size=1,
        gradient_accumulation_steps=8,
        learning_rate=2e-4,
        warmup_ratio=0.03,
        logging_steps=20,
        save_steps=250,
        save_total_limit=2,
        bf16=False,
        fp16=torch.cuda.is_available(),
        gradient_checkpointing=True,
        report_to="none",
    )

    trainer = SFTTrainer(
        model=model,
        tokenizer=tokenizer,
        train_dataset=dataset,
        dataset_text_field="text",
        max_seq_length=args.max_seq_length,
        args=training_args,
    )
    trainer.train()
    trainer.save_model(args.output_dir)
    tokenizer.save_pretrained(args.output_dir)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
