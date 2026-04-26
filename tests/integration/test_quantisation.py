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
def wikitext_samples() -> list[str]:
    """Return exactly NUM_SAMPLES non-empty sentences from WikiText-2 test."""
    raw = load_dataset(DATASET_NAME, DATASET_CONFIG, split=DATASET_SPLIT)
    samples = []
    for s_raw in raw["text"]:
        s = s_raw.strip()
        if s and not s.startswith("="):
            samples.append(s)
        if len(samples) == NUM_SAMPLES:
            break
    assert len(samples) == NUM_SAMPLES, (
        f"Expected {NUM_SAMPLES} samples but got {len(samples)}. "
        "WikiText-2 dataset may have changed."
    )
    return samples


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
    samples: list[str],
    device: str = "cuda:0",
) -> dict:
    total_nll = 0.0
    total_tokens = 0
    for sample in samples:
        sample_input = tokenizer(sample, return_tensors="pt").to(device)
        if sample_input["input_ids"].shape[1] < 2:
            continue
        outputs = model(input_ids=sample_input["input_ids"], labels=sample_input["input_ids"])
        n_tokens = sample_input["input_ids"].shape[1] - 1
        total_nll += outputs.loss.item() * n_tokens
        total_tokens += n_tokens
    avg_nll = total_nll / total_tokens
    ppl = math.exp(avg_nll)

    return {
        "perplexity": ppl,
        "avg_nll": avg_nll,
        "total_tokens": total_tokens,
        "sentence_count": len(samples),
    }