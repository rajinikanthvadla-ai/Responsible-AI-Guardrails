"""Open-source model wrapper for the classroom lab."""

from __future__ import annotations

import torch
from transformers import AutoModelForSeq2SeqLM, AutoTokenizer


class OpenSourceTextModel:
    """Small open-source instruction model wrapper."""

    def __init__(self, model_name: str = "google/flan-t5-small") -> None:
        self.model_name = model_name
        self.tokenizer = AutoTokenizer.from_pretrained(model_name)
        self.model = AutoModelForSeq2SeqLM.from_pretrained(model_name)
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.model.to(self.device)
        self.model.eval()

    def generate(self, prompt: str) -> str:
        encoded = self.tokenizer(
            prompt,
            return_tensors="pt",
            truncation=True,
            max_length=512,
        )
        encoded = {key: value.to(self.device) for key, value in encoded.items()}

        with torch.no_grad():
            output_ids = self.model.generate(
                **encoded,
                max_new_tokens=120,
                do_sample=False,
            )
        return self.tokenizer.decode(output_ids[0], skip_special_tokens=True).strip()
