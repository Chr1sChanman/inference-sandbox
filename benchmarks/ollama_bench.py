import json
import subprocess
import time
from pathlib import Path

import ollama

# , "qwen3:4b", "qwen3:8b"
MODELS = ["qwen3:0.6b"]
PROMPTS = [
    "Explain what a GPU does in one paragraph.",
    "Write three bullet points about Docker.",
    "What is TTFT in LLM benchmarking?",
    "Summarize the benefits of local inference.",
    "Give a simple example of Python list slicing.",
]

OUTPUT_PATH = Path("benchmarks/results/ollama_results.jsonl")

GPU_INDEX = 0
STOP_BETWEEN_MODELS = True
STOP_BEFORE_BENCHMARK = True

def get_vram_mb(gpu_index: int = GPU_INDEX) -> int:
    result = subprocess.run(
        [
            "nvidia-smi",
            f"--id={gpu_index}",
            "--query-gpu=memory.used",
            "--format=csv,noheader,nounits",
        ],
        capture_output=True,
        text=True,
        check=True,
    )
    used_mb = result.stdout.strip().splitlines()[0]
    return int(used_mb)

def stop_model(model: str) -> None:
    subprocess.run(
        ["ollama", "stop", model],
        capture_output=True,
        text=True,
        check=False,
    )


def stop_all_models(models: list[str]) -> None:
    for model in models:
        stop_model(model)


def show_running_models() -> None:
    result = subprocess.run(
        ["ollama", "ps"],
        capture_output=True,
        text=True,
        check=False,
    )

    lines = [line for line in result.stdout.splitlines() if line.strip()]
    print("\nCurrently running Ollama models:")
    if len(lines) <= 1:
        print("(none)")
    else:
        print(result.stdout.strip())



def run_one_prompt(model: str, prompt: str) -> dict:
    vram_before = get_vram_mb()
    vram_peak = vram_before

    start = time.perf_counter()
    first_token_time = None
    final_chunk = None

    stream = ollama.chat(
        model = model,
        messages=[{"role": "user", "content": prompt}],
        stream=True,
    )

    for chunk in stream:
        current_vram = get_vram_mb()
        vram_peak = max(vram_peak, current_vram)

        final_chunk = chunk
        # print(chunk) for seeing every chunk during model usage
        content = chunk.message.content or ""
        if content and first_token_time is None:
            first_token_time = time.perf_counter()

    end = time.perf_counter()
    vram_after = get_vram_mb()

    ttft_s = (first_token_time - start) if first_token_time else 0.0
    total_time_s = end - start

    eval_count = final_chunk.eval_count if final_chunk and final_chunk.eval_count else 0
    eval_duration_ns = final_chunk.eval_duration if final_chunk and final_chunk.eval_duration else 0
    eval_duration_s = eval_duration_ns / 1_000_000_000 if eval_duration_ns else 0
    tokens_per_sec = eval_count / eval_duration_s if eval_duration_s > 0 else 0.0

    return {
        "model": model,
        "prompt": prompt,
        "ttft_s": ttft_s,
        "total_time_s": total_time_s,
        "generated_tokens": eval_count,
        "eval_duration_s": eval_duration_s,
        "tokens_per_sec": tokens_per_sec,
        "vram_before_mb": vram_before,
        "vram_peak_mb": vram_peak,
        "vram_after_mb": vram_after,
        "vram_delta_mb": vram_peak - vram_before,
        "load_duration_s": (final_chunk.load_duration if final_chunk and final_chunk.load_duration else 0) / 1_000_000_000,
        "prompt_tokens": final_chunk.prompt_eval_count if final_chunk and final_chunk.prompt_eval_count else 0,
        "prompt_eval_duration_s": (final_chunk.prompt_eval_duration if final_chunk and final_chunk.prompt_eval_duration else 0) / 1_000_000_000,
    }

def print_table(results: list[dict]) -> None:
    print(
        f"{'MODEL':<12} {'TTFT(s)':<10} {'TOTAL(s)':<10} "
        f"{'TOKENS':<8} {'TOK/s':<10} {'BEFORE':<8} "
        f"{'PEAK':<8} {'PEAK+MB':<10}"
    )
    print("-" * 92)
    for row in results:
        print(
            f"{row['model']:<12} "
            f"{row['ttft_s']:<10.3f} "
            f"{row['total_time_s']:<10.3f} "
            f"{row['generated_tokens']:<8} "
            f"{row['tokens_per_sec']:<10.3f} "
            f"{row['vram_before_mb']:<8} "
            f"{row['vram_peak_mb']:<8} "
            f"{row['vram_delta_mb']:<10}"
        )


def save_jsonl(results: list[dict], path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w") as f:
        for row in results:
            f.write(json.dumps(row) + "\n")

def main() -> None:
    results = []

    if STOP_BEFORE_BENCHMARK:
        stop_all_models(MODELS)
        time.sleep(1)
        show_running_models()
        print(f"Idle GPU {GPU_INDEX} memory: {get_vram_mb()} MB\n")

    for model in MODELS:
        for prompt in PROMPTS:
            if STOP_BETWEEN_MODELS:
                stop_model(model)
                time.sleep(1)

            row = run_one_prompt(model, prompt)
            results.append(row)

            if STOP_BETWEEN_MODELS:
                stop_model(model)
                time.sleep(1)

    print_table(results)
    save_jsonl(results, OUTPUT_PATH)
    show_running_models()

if __name__ == "__main__":
    main()