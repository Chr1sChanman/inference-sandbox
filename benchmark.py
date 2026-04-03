import time


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


def main():
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
        print(
            f"{result['input_length']:<15} "
            f"{result['output']:<50} "
            f"{result['duration_ms']:<15.4f}"
        )


if __name__ == "__main__":
    main()
