import time
import json

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
    with open(path, "w") as f:
        json.dump(results, f, indent=2)

def load_json(path: str) -> list:
    with open(path, "r") as f:
        return json.load(f)

def main():
    results = []
    """Run time_reverse on sample inputs and print a results table."""
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
    save_csv(results, "results.csv")
    save_json(results, "results.json")


if __name__ == "__main__":
    main()
