import pytest
from benchmark import time_reverse


@pytest.mark.parametrize("text", [
    "hi",
    "hello world",
    "the quick brown fox jumps over the lazy dog",
])
def test_output_is_reversed(text):
    """Output must be the reversed input."""
    result = time_reverse(text)
    assert result["output"] == text[::-1]


@pytest.mark.parametrize("text", [
    "hi",
    "hello world",
    "the quick brown fox jumps over the lazy dog",
])
def test_duration_is_positive(text):
    """duration_ms must be a positive float."""
    result = time_reverse(text)
    assert result["duration_ms"] > 0


@pytest.mark.parametrize("text", [
    "hi",
    "hello world",
    "the quick brown fox jumps over the lazy dog",
])
def test_input_length_is_correct(text):
    """input_length must match len(text)."""
    result = time_reverse(text)
    assert result["input_length"] == len(text)
