from benchmarks.ollama_bench import run_one_prompt, stop_model
import time

def test_ttft_is_positive():
    row = run_one_prompt("qwen3:0.6b", "Say hello in one short sentence.")
    assert row["ttft_s"] > 0

def test_tokens_per_sec_is_positive():
    row = run_one_prompt("qwen3:0.6b", "Count from one to ten.")
    assert row["tokens_per_sec"] > 0

def test_vram_increase_after_load():
    stop_model("qwen3:0.6b")
    time.sleep(1)
    try:
        row = run_one_prompt("qwen3:0.6b", "Explain RAM in one sentence.")
        assert row["vram_delta_mb"] > 0
    finally:
        stop_model("qwen3:0.6b")