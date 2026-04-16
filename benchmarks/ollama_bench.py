import json
import subprocess
import time
from pathlib import Path

import ollama

MODELS = ["qwen3:0.6b", "qwen3:4b", "qwen3:8b"]
PROMPTS = [
    "Explain what a GPU does in one paragraph.",
    "Write three bullet points about Docker.",
    "What is TTFT in LLM benchmarking?",
    "Summarize the benefits of local inference.",
    "Give a simple example of Python list slicing.",
]

OUTPUT_PATH = Path("benchmarks/ollama_results.jsonl")

def get_vram_mb() -> int:
    result = subprocess.run(
        [
            "nvidia-smi",
            "--query-gpu=memory.used",
            "--format=csv,noheqader,nounits",
        ],
        capture_output=True,
        text=True,
        check=True,
    )
    first_gpu = result.stdout.strip().splitlines()[0]
    return int(first_gpu)

def main() -> None:
    results = []
    for model in MODELS:
        for prompt in PROMPTS:
            pass

if __name__ == "__main__":
    main()