from __future__ import annotations

import time

import pytest

from inference_sandbox.ollama_bench import run_one_prompt, stop_model

pytestmark = [
    pytest.mark.integration,
]

MODEL = "qwen3:0.6b"


def test_ttft_is_positive(ollama_url: str) -> None:
    row = run_one_prompt(MODEL, "Say hello in one short sentence.")
    assert row["ttft_s"] > 0


def test_tokens_per_sec_is_positive(ollama_url: str) -> None:
    row = run_one_prompt(MODEL, "Count from one to ten.")
    assert row["tokens_per_sec"] > 0


@pytest.mark.gpu
@pytest.mark.slow
def test_vram_increase_after_load(ollama_url: str) -> None:
    stop_model(MODEL)
    time.sleep(1)

    try:
        row = run_one_prompt(MODEL, "Explain RAM in one sentence.")
        assert row["vram_delta_mb"] > 0
    finally:
        stop_model(MODEL)