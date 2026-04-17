from benchmarks.ollama_bench import run_one_prompt

def test_ttft_is_positive():
    row = run_one_prompt("qwen3:0.6b", "Say hello in one short sentence.")
    assert row["ttft_s"] > 0

def test_tokens_per_sec_is_positive():
    row = run_one_prompt("qwen3:0.6b", "Count from one to ten.")
    assert row["tokens_per_sec"] > 0

def test_vram_increase_after_load():
    row = run_one_prompt("qwen3:0.6b", "Explain RAM in one sentence.")
    assert row["vram_peak_mb"] > row["vram_before_mb"]