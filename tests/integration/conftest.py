from __future__ import annotations

import os

import pytest


@pytest.fixture(scope="session")
def ollama_url() -> str:
    """Ollama endpoint or skip if Ollama is not running."""
    import httpx

    url = os.environ.get("OLLAMA_URL", "http://127.0.0.1:11434")

    try:
        httpx.get(f"{url}/api/tags", timeout=1).raise_for_status()
    except Exception as e:
        pytest.skip(f"Ollama not reachable at {url}: {e!s}")

    return url


@pytest.fixture(scope="session")
def vllm_url() -> str:
    """vLLM endpoint or skip if vLLM is not running."""
    import httpx

    url = os.environ.get("VLLM_URL", "http://127.0.0.1:8000")

    try:
        httpx.get(f"{url}/v1/models", timeout=2).raise_for_status()
    except Exception as e:
        pytest.skip(f"vLLM not reachable at {url}: {e!s}")

    return url