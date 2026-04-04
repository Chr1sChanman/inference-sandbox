import pytest
from benchmark import time_reverse, load_json, save_json, load_csv, save_csv

INPUTS = [
    "hi",
    "hello world",
    "the quick brown fox jumps over the lazy dog",
]

@pytest.fixture(params=INPUTS)
def result(request):
    """Fixture that returns a time_reverse result and its input for each sample string."""
    return time_reverse(request.param), request.param

def test_output_is_reversed(result):
    """Assert that the output is the reverse of the input string."""
    res, text = result
    assert res["output"] == text[::-1]

def test_duration_is_positive(result):
    """Assert that the measured duration is greater than zero."""
    res, _ = result
    assert res["duration_ms"] > 0

def test_input_length_is_correct(result):
    """Assert that input_length matches the actual length of the input string."""
    res, text = result
    assert res["input_length"] == len(text)

def test_json(tmp_path):
    """Assert that results saved to JSON and loaded back are identical."""
    json_path = tmp_path / "results.json"
    results = [time_reverse(text) for text in INPUTS]
    save_json(results, json_path)
    loaded = load_json(str(json_path))
    assert results == loaded

def test_csv(tmp_path):
    """Assert that results saved to CSV and loaded back are identical."""
    csv_path = tmp_path / "results.csv"
    results = [time_reverse(text) for text in INPUTS]
    save_csv(results, csv_path)
    loaded = load_csv(str(csv_path))
    assert results == loaded