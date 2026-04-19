import json
import argparse
import os
import time
from pathlib import Path
from os import PathLike
from typing import cast

import redis
import uvicorn
from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI()
APP_ROOT = Path(__file__).resolve().parents[2]
ARTIFACTS_DIR = Path(os.getenv("ARTIFACTS_DIR", str(APP_ROOT / "artifacts")))
BENCHMARK_OUTPUT_DIR = ARTIFACTS_DIR / "benchmark"


class InferRequest(BaseModel):
    text: str


@app.post("/infer")
def infer(request: InferRequest):
    result = time_reverse(request.text)
    client = redis.Redis(host=os.getenv("REDIS_HOST", "localhost"), port=6379)
    client.rpush("benchmark:results", json.dumps(result))
    return result


def time_reverse(text: str) -> dict:
    """Reverse the input string and return length, result, and duration."""
    start = time.perf_counter()
    output = text[::-1]
    duration_ms = (time.perf_counter() - start) * 1000
    return {
        "input_length": len(text),
        "output": output,
        "duration_ms": duration_ms,
    }


def save_csv(results: list, path: str):
    """Write results list to a CSV file at the given path."""
    with open(path, "w") as f:
        for result in results:
            f.write(f"{result['input_length']},{result['output']},{result['duration_ms']}\n")


def load_csv(path: str) -> list:
    """Load CSV results and return typed dicts matching time_reverse output."""
    with open(path, "r") as f:
        rows = []
        for line in f.readlines():
            parts = line.strip().split(",")
            rows.append({
                "input_length": int(parts[0]),
                "output": parts[1],
                "duration_ms": float(parts[2]),
            })
        return rows


def save_json(results: list, path: str):
    """Write results list to a JSON file at the given path."""
    with open(path, "w") as f:
        json.dump(results, f, indent=2)


def load_json(path: str) -> list:
    """Load and return results list from a JSON file."""
    with open(path, "r") as f:
        return json.load(f)


def main():
    """Argument parser for Redis result dumping."""
    parser = argparse.ArgumentParser()
    parser.add_argument("--dump-results", action="store_true")
    parser.add_argument("--serve", action="store_true")
    args = parser.parse_args()

    if args.serve:
        uvicorn.run(app, host="0.0.0.0", port=8080)
        return
    client = redis.Redis(host=os.getenv("REDIS_HOST", "localhost"), port=6379, decode_responses=True)

    if args.dump_results:
        results = cast(list[str], client.lrange("benchmark:results", 0, -1))
        for result in results:
            print(json.loads(result))
        return
    results = []
    inputs = [
        "hi",
        "hello world",
        "the quick brown fox jumps over the lazy dog",
    ]

    print(f"{'Input Length':<15} {'Output':<50} {'Duration (ms)':<15}")
    print("-" * 80)
    for text in inputs:
        result = time_reverse(text)
        results.append(result)
        print(
            f"{result['input_length']:<15} "
            f"{result['output']:<50} "
            f"{result['duration_ms']:<15.4f}"
        )
    BENCHMARK_OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    save_csv(results, BENCHMARK_OUTPUT_DIR / "results.csv")
    save_json(results, BENCHMARK_OUTPUT_DIR / "results.json")

    client.rpush("benchmark:results", json.dumps(results))


if __name__ == "__main__":
    main()
