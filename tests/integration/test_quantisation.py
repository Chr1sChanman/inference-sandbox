import math
from typing import Iterable

from datasets import dataset
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
NUM_SENTENCES = 200
PPL_TOLERANCE = 0.5