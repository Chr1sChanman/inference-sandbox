import math
import gc
import torch
import pytest
from typing import Iterable
from datasets import load_dataset
from transformers import AutoModelForCausalLM, AutoTokenizer

pytestmark = [
    pytest.mark.gpu,
    pytest.mark.slow,
    pytest.mark.skipif(
        not torch.cuda.is_available(),
        reason="Perplexity tests require CUDA gpu.",
    ),
]

MODEL_NAME = "TinyLlama/TinyLlama-1.1B-Chat-v1.0"
DATASET_NAME = "wikitext"
DATASET_CONFIG = "wikitext-2-raw-v1"
DATASET_SPLIT = "test"
NUM_SAMPLES = 200
PPL_TOLERANCE = 0.5
DTYPES_UNDER_TEST = [torch.float32, torch.float16, torch.bfloat16]

@pytest.fixture(scope="module")
def wikitext_sentences() -> list[str]:
    """Return exactly NUM_SAMPLES non-empty sentences from WikiText-2 test."""
    raw = load_dataset(DATASET_NAME, DATASET_CONFIG, split=DATASET_SPLIT)
    sentences = []
    for s_raw in raw["text"]:
        s = s_raw.strip()
        if s and not s.startswith("="):
            sentences.append(s)
        if len(sentences) == NUM_SAMPLES:
            break
    assert len(sentences) == NUM_SAMPLES, (
        f"Expected {NUM_SAMPLES} sentences but got {len(sentences)}. "
        "WikiText-2 dataset may have changed."
    )
    return sentences


@pytest.fixture(scope="module", params=DTYPES_UNDER_TEST, ids=lambda d: str(d).replace("torch.", ""))
def loaded_model(request) -> Iterable[tuple[AutoModelForCausalLM, AutoTokenizer, torch.dtype]]:
    dtype: torch.dtype = request.param
    device = "cuda:0"

    tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)
    model = AutoModelForCausalLM.from_pretrained(MODEL_NAME, dtype=dtype)
    model.to(device)
    model.eval()

    try:
        yield model, tokenizer, dtype
    finally:
        del model
        del tokenizer
        gc.collect()
        if torch.cuda.is_available():
            torch.cuda.empty_cache()
            torch.cuda.synchronize()

@torch.no_grad()
def corpus_perplexity(
    model,
    tokenizer,
    sentences
) -> dict:
    total_nll = 0.0
    total_tokens = 0