import json
import subprocess
import time
from pathlib import Path

import ollama
'''
Models: , "qwen3:4b", "qwen3:8b"
Prompts: 
"Write three bullet points about Docker.",
    "What is TTFT in LLM benchmarking?",
    "Summarize the benefits of local inference.",
    "Give a simple example of Python list slicing.",
'''
MODELS = ["qwen3:0.6b"]
PROMPTS = [
    "Explain what a GPU does in one paragraph.",
    
]

OUTPUT_PATH = Path("benchmarks/ollama_results.jsonl")

def get_vram_mb() -> int:
    result = subprocess.run(
        [
            "nvidia-smi",
            "--query-gpu=memory.used",
            "--format=csv,noheader,nounits",
        ],
        capture_output=True,
        text=True,
        check=True,
    )
    first_gpu = result.stdout.strip().splitlines()[0]
    return int(first_gpu)

def run_one_prompt(model: str, prompt: str) -> dict:
    vram_before = get_vram_mb()
    start = time.perf_counter()
    first_token_time = None
    full_text_parts = []

    stream = ollama.chat(
        model = model,
        messages=[{"role": "user", "content": prompt}],
        stream=True,
    )

    for chunk in stream:
        print(chunk)
        text = chunk.get("message", {}).get("content", "")
        if text and first_token_time is None:
            first_token_time = time.perf_counter()
        full_text_parts.append(text)

    end = time.perf_counter()
    vram_after = get_vram_mb()

    output_text = "".join(full_text_parts)
    output_tokens =  max(len(output_text.split()), 1)

    ttft_s = (first_token_time - start) if first_token_time else 0.0
    total_time_s = end - start
    tokens_per_sec = output_tokens / total_time_s if total_time_s > 0 else 0.0

    return {
        "model": model,
        "prompt": prompt,
        "ttft_s": ttft_s,
        "total_time_s": total_time_s,
        "output_tokens": output_tokens,
        "tokens_per_sec": tokens_per_sec,
        "vram_before_mb": vram_before,
        "vram_after_mb": vram_after,
        "vram_delta_mb": vram_after - vram_before,
    }

def print_table(results: list[dict]) -> None:
    print(
        f"{'MODEL':<12} {'TTFT(s)':<10} {'TOTAL(s)':<10} "
        f"{'TOKENS':<8} {'TOK/s':<10} {'VRAM+MB':<10}"
    )
    print("-" * 70)
    for row in results:
        print(
            f"{row['model']:<12} {row['ttft_s']:<10.3f} {row['total_time_s']:<10.3f} "
            f"{row['output_tokens']:<8} {row['tokens_per_sec']:<10.3f} {row['vram_delta_mb']:<10}"
        )

def save_jsonl(results: list[dict], path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w") as f:
        for row in results:
            f.write(json.dumps(row) + "\n")

def main() -> None:
    results = []
    for model in MODELS:
        for prompt in PROMPTS:
            row = run_one_prompt(model, prompt)
            results.append(row)
    
    print_table(results)
    save_jsonl(results, OUTPUT_PATH)

if __name__ == "__main__":
    main()