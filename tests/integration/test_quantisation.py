import math
from typing import Iterable

from datasets import load_dataset
import pytest
import torch
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