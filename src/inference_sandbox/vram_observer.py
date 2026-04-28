from transformers import AutoModelForCausalLM
import matplotlib.pyplot as plt
from pathlib import Path
import torch

from inference_sandbox.hf_bench import BenchmarkConfig, HFBenchmark

PLOT_DIR = Path(__file__).resolve().parents[2] / "docs" / "vram_observer"
PLOT_DIR.mkdir(parents=True, exist_ok=True)

CONFIG = BenchmarkConfig(dtype=torch.float16)
BENCH = HFBenchmark(CONFIG)
BENCH.load_components()
PROMPT = CONFIG.prompts[0]

TOKEN_AMOUNTS = [128, 256, 512, 1024, 2048]
TOKEN_SAMPLES = [] # one row per max_new_tokens

# Measuring peak GPU tensor memory during `generate()`
for max_new_tokens in TOKEN_AMOUNTS:
    BENCH.config.max_new_tokens = max_new_tokens
    inputs = BENCH.build_chat_inputs(PROMPT)
    gen_kw = BENCH.build_generation_kwargs(inputs)

    gen_kw["min_new_tokens"] = max_new_tokens
    gen_kw["eos_token_id"] = None

    input_len = inputs["input_ids"].shape[1]

    torch.cuda.synchronize()
    torch.cuda.reset_peak_memory_stats()

    with torch.no_grad():
        out = BENCH.model.generate(**gen_kw)
    
    torch.cuda.synchronize()
    curr_bytes = torch.cuda.memory_allocated()
    peak_bytes = torch.cuda.max_memory_allocated()
    
    actual_new_tokens = out.shape[1] - input_len
    TOKEN_SAMPLES.append({
        "max_new_tokens": max_new_tokens,
        "actual_new_tokens": actual_new_tokens,
        "curr_mib": curr_bytes / (1024 ** 2),
        "peak_mib": peak_bytes / (1024 ** 2),
    })
    print(
        f"max_new_tokens={max_new_tokens} "
        f"actual={actual_new_tokens} "
        f"peak={peak_bytes / (1024**2):.1f} MiB"
    )
    del gen_kw
BENCH.unload_components()

xs = [s["max_new_tokens"] for s in TOKEN_SAMPLES]
peak = [s["peak_mib"] for s in TOKEN_SAMPLES]
curr = [s["curr_mib"] for s in TOKEN_SAMPLES]
fig, ax = plt.subplots(figsize=(7, 4.5), dpi=150)
ax.plot(xs, peak, marker="o", label="peak (during generate)")
ax.plot(xs, curr, marker="s", linestyle="--", label="current (after sync)")
ax.set_xlabel("max_new_tokens (decode length)")
ax.set_ylabel("VRAM (MiB)")
ax.set_title("TinyLlama FP16 — VRAM vs sequence length (batch=1)")
ax.grid(True, alpha=0.3)
ax.legend()
fig.tight_layout()
out_path = PLOT_DIR / "vram_vs_seqlen.png"
fig.savefig(out_path)
plt.close(fig)
print(f"Saved plot: {out_path}")