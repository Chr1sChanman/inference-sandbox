from __future__ import annotations

import gc
import math
from typing import Iterable

import pytest
import torch
from datasets import load_dataset
from transformers import AutoModelForCausalLM, AutoTokenizer

from inference_sandbox.perplexity import corpus_perplexity

pytestmark = [
    pytest.mark.gpu,
    pytest.mark.slow,
    pytest.mark.integration,
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


@pytest.fixture(scope="module")
def fp32_reference_ppl(wikitext_samples) -> float:
    """Load FP32 once, compute reference PPL, unload. Cached for the session."""
    tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)
    model = AutoModelForCausalLM.from_pretrained(MODEL_NAME, dtype=torch.float32)
    model.to("cuda:0")
    model.eval()

    try:
        result = corpus_perplexity(model, tokenizer, wikitext_samples)
        return result["perplexity"]
    finally:
        del model
        del tokenizer
        gc.collect()
        if torch.cuda.is_available():
            torch.cuda.empty_cache()
            torch.cuda.synchronize()

def test_quantised_ppl_within_tolerance(
    loaded_model,
    fp32_reference_ppl: float,
    wikitext_samples: list[str],
):
    model, tokenizer, dtype = loaded_model
    
    if dtype is torch.float32:
        # FP32 "golden" baseline; assert self-consistency instead
        result = corpus_perplexity(model, tokenizer, wikitext_samples)
        assert math.isclose(result["perplexity"], fp32_reference_ppl, rel_tol=1e-3), (
            f"FP32 self-consistency check failed: "
            f"{result['perplexity']:.4f} vs reference {fp32_reference_ppl:.4f}"
        )
        return
    
    result = corpus_perplexity(model, tokenizer, wikitext_samples)
    ppl = result["perplexity"]
    drift = abs(ppl - fp32_reference_ppl)

    assert drift < PPL_TOLERANCE, (
        f"{dtype} PPL drift {drift:.4f} exceeds tolerance {PPL_TOLERANCE}. "
        f"dtype PPL = {ppl:.4f}, FP32 reference = {fp32_reference_ppl:.4f}, "
        f"tokens = {result['total_tokens']}, sentences = {result['sentence_count']}."
    )