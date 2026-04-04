import pytest
from pathlib import Path
from benchmark import time_reverse, load_json, save_json, load_csv, save_csv

INPUTS = [
    "hi",
    "hello world",
    "the quick brown fox jumps over the lazy dog",
]

@pytest.fixture(params=INPUTS)
def result(request):
    return time_reverse(request.param), request.param

def test_output_is_reversed(result):
    res, text = result
    assert res["output"] == text[::-1]

def test_duration_is_positive(result):
    res, _ = result
    assert res["duration_ms"] > 0

def test_input_length_is_correct(result):
    res, text = result
    assert res["input_length"] == len(text)

def test_json(tmp_path):
    json_path = tmp_path / "results.json"
    results = [time_reverse(text) for text in INPUTS]
    save_json(results, json_path)
    loaded = load_json(str(json_path))
    assert results == loaded

def test_csv(tmp_path):
    csv_path = tmp_path / "results.csv"
    results = [time_reverse(text) for text in INPUTS]
    save_csv(results, csv_path)
    loaded = load_csv(str(csv_path))
    assert results == loaded