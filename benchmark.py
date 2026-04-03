import time
import argparse


def time_reverse(text: str) -> dict:
    """Reverse the input string and return length, result, and duration."""
    start = time.time()
    output = text[::-1]
    duration_ms = (time.time() - start) * 1000
    return {
        "input_length": len(text),
        "output": output,
        "duration_ms": duration_ms,
    }


def main():
    """Run time_reverse on sample inputs and print a results table."""
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--self-test", action="store_true", help="Run assertions and exit."
    )
    args = parser.parse_args()

    inputs = [
        "hi",
        "hello world",
        "the quick brown fox jumps over the lazy dog",
    ]

    if args.self_test:
        for text in inputs:
            result = time_reverse(text)
            assert result["output"] == text[::-1], "Output mismatch"
            assert result["duration_ms"] > 0, "Duration must be positive"
            assert result["input_length"] == len(text), "Length mismatch"
        print("All assertions passed.")
        return

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
