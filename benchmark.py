import time
import json
import os
import redis
import argparse
import uvicorn
from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI()


class InferRequest(BaseModel):
    text: str


@app.post("/infer")
def infer(request: InferRequest):
    result = time_reverse(request.text)
    client = redis.Redis(host=os.getenv("REDIS_HOST", "localhost"), port=6379)
    client.rpush("benchmark:results", json.dumps(result))
    return result

# Phase 2.2, checking docker caching behavior after adding comment
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
    '''Argument parser for redis results dumping'''
    parser = argparse.ArgumentParser()
    parser.add_argument("--dump-results", action="store_true")
    parser.add_argument("--serve", action="store_true")
    args = parser.parse_args()

    if args.serve:
        uvicorn.run(app, host="0.0.0.0", port=8080)
        return
    client = redis.Redis(host=os.getenv("REDIS_HOST", "localhost"), port=6379)

    if args.dump_results:
        results = client.lrange("benchmark:results", 0, -1)
        for result in results:
            print(json.loads(result))
        return
    
    """Run time_reverse on sample inputs and print a results table."""
    results = []
    inputs = [
        "hi",
        "hello world",
        "the quick brown fox jumps over the lazy dog",
    ]

    '''Benchmarking'''
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
    save_csv(results, "results.csv")
    save_json(results, "results.json")

    '''Redis results dumping'''
    client.rpush("benchmark:results", json.dumps(results))


if __name__ == "__main__":
    main()
