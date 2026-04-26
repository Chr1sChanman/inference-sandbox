# inference-sandbox

An exploratory project that formats learning and style in an SDET like layout in preperation for an internship that centers around Deep Learning, Gitlab CI/CD, and NVIDIA framworks.

## Repo Layout

```text
inference-sandbox/
  src/
    inference_sandbox/
      __init__.py
      reverse_service.py
      ollama_bench.py
      hf_bench.py
      perplexity.py
  tests/
    conftest.py
    unit/
      test_reverse_service.py
    integration/
      test_ollama_bench.py
      test_quantisation.py
    system/
      test_k8s_smoke.py
  docker/
    Dockerfile.benchmark
    Dockerfile.service
  deploy/
    k8s/
      base/
        configmap.yaml
        deployment.yaml
        redis.yaml
        service.yaml
  artifacts/
    benchmark/
      results.csv
      results.json
    ollama/
      ollama_results.jsonl
  docs/
    learning-logs/
      phase1.md
      phase2.md
      phase3.md
      phase4.md
    reference/
      NVIDIA_Phases1-3.pdf
      NVIDIA_Phases4-7.pdf
    cmdlist.md
    templates.md
  exploration/
    scratch_ppl.py
  docker-compose.yml
  pyproject.toml
  requirements.txt
  .gitlab-ci.yml
```

## Key Files

- `src/inference_sandbox/reverse_service.py`
  Contains the string-reversal benchmark logic, CSV/JSON persistence helpers, Redis result publishing, and the FastAPI `/infer` endpoint.
- `src/inference_sandbox/ollama_bench.py`
  Runs local Ollama benchmarks and writes model timing and VRAM metrics to `artifacts/ollama/ollama_results.jsonl`.
- `src/inference_sandbox/hf_bench.py`
  Hugging Face benchmark for TinyLlama with TTFT via `TextIteratorStreamer`, throughput, VRAM, and a dtype comparison (FP32/FP16/BF16) with optional Redis storage.
- `src/inference_sandbox/perplexity.py`
  `corpus_perplexity()` helper that computes token-weighted mean NLL over a list of samples and returns perplexity (`exp(mean NLL)`).
- `tests/unit/test_reverse_service.py`
  Unit tests for benchmark output correctness and CSV/JSON round-tripping.
- `tests/integration/test_ollama_bench.py`
  Integration tests for Ollama TTFT, throughput, and VRAM behavior. Requires Ollama, models, and an NVIDIA GPU.
- `tests/integration/test_quantisation.py`
  GPU perplexity gate that loads TinyLlama in FP32/FP16/BF16, scores a fixed WikiText-2 test subset, and asserts `|PPL(dtype) − PPL(FP32)| < 0.5`. Marked `gpu` and `slow`; skips on CPU-only hosts.
- `tests/system/test_k8s_smoke.py`
  Kubernetes smoke test that checks for at least two running `inference-sandbox` pods.
- `tests/conftest.py`
  Adds `src/` to `sys.path` so package imports work from pytest, and registers `--gpu` / `--slow` CLI flags that filter collection to tests carrying the matching markers.
- `docker/Dockerfile.benchmark`
  Single-stage benchmark image that runs `python -m inference_sandbox.reverse_service`.
- `docker/Dockerfile.service`
  Multi-stage service image that runs `python -m inference_sandbox.reverse_service --serve`.
- `docker-compose.yml`
  Local two-service stack for the app and Redis.
- `deploy/k8s/base/`
  Base Kubernetes manifests for the app deployment, service, Redis, and ConfigMap.
- `pyproject.toml`
  Stores pytest discovery config plus the `integration`, `system`, `gpu`, and `slow` markers.
- `.gitlab-ci.yml`
  Lints `src/` and `tests/`, runs non-hardware pytest, and builds the service image.
- `artifacts/benchmark/` and `artifacts/ollama/`
  Output folders for benchmark results and Ollama metrics.

## Requirements

### Core

- Python 3.11+
- Dependencies from `requirements.txt`

### Phase 2

- Docker
- Docker Compose plugin

### Phase 3

- `kubectl`
- Minikube

### Phase 4

- Ollama
- NVIDIA GPU access
- `nvidia-smi` available in the shell
- Models pulled locally:
  - `qwen3:0.6b`
  - `qwen3:4b`
  - `qwen3:8b`

## Python Setup

Install the project dependencies:

```bash
python3 -m pip install -r requirements.txt
```

Commands in this repo assume either:

```bash
export PYTHONPATH=src
```

or an inline equivalent such as:

```bash
PYTHONPATH=src python3 -m inference_sandbox.reverse_service
```

## Testing Notes

- `tests/unit/` contains fast local tests.
- `tests/integration/` is marked `integration` in `pyproject.toml` and is meant for Ollama/GPU-dependent validation.
- `tests/system/` is marked `system` and is meant for Kubernetes cluster validation.
- `gpu` and `slow` markers gate CUDA-only and longer-running tests (e.g. perplexity). They can be selected via `-m` or via the `--gpu` / `--slow` CLI flags from `tests/conftest.py`.

Examples:

```bash
python3 -m pytest -q tests -m "not integration and not system"
python3 -m pytest -q tests/integration -m integration
python3 -m pytest -q tests/system -m system
python3 -m pytest -q tests/integration -m "gpu and slow"
```

## Phase 1 Commands

Phase 1 covers the local Python benchmark and unit testing.

Install dependencies:

```bash
python3 -m pip install -r requirements.txt
```

Run the benchmark:

```bash
PYTHONPATH=src python3 -m inference_sandbox.reverse_service
```

Run only the unit tests:

```bash
python3 -m pytest -q tests/unit
```

Run the non-hardware-dependent pytest selection:

```bash
python3 -m pytest -q tests -m "not integration and not system"
```

Run lint checks:

```bash
ruff check src tests
```

Expected outputs:

- `artifacts/benchmark/results.csv`
- `artifacts/benchmark/results.json`

## Phase 2 Commands

Phase 2 covers Docker image creation, image comparison, and Docker Compose.

Build the single-stage benchmark image:

```bash
docker build -f docker/Dockerfile.benchmark -t inference-sandbox-benchmark .
```

Build the multi-stage service image:

```bash
docker build -f docker/Dockerfile.service -t inference-sandbox-service .
```

List built images:

```bash
docker images
```

Start the local app + Redis stack:

```bash
docker compose up --build
```

Call the FastAPI endpoint from another terminal:

```bash
curl -X POST http://localhost:8080/infer \
  -H "Content-Type: application/json" \
  -d '{"text":"hello world"}'
```

Read app logs:

```bash
docker compose logs app
```

Dump Redis-backed results through the app image:

```bash
docker compose run --rm app python -m inference_sandbox.reverse_service --dump-results
```

Stop the Compose stack:

```bash
docker compose down
```

Artifacts written by the container are mounted back to:

- `artifacts/benchmark/`

## Phase 3 Commands

Phase 3 covers Kubernetes deployment and cluster smoke testing.

Start Minikube:

```bash
minikube start --driver=docker --memory=4096 --cpus=2
```

Point Docker at Minikube's internal daemon:

```bash
eval $(minikube docker-env)
```

Build the service image using the tag expected by the Deployment:

```bash
docker build -f docker/Dockerfile.service -t inference-sandbox:v2 .
```

Apply the Kubernetes manifests:

```bash
kubectl apply -f deploy/k8s/base/
```

Inspect the cluster:

```bash
kubectl get pods
kubectl get services
kubectl get deployments
```

Watch pod state transitions:

```bash
kubectl get pods -w
```

Inspect app details:

```bash
kubectl describe deployment inference-sandbox
kubectl logs deployment/inference-sandbox
```

Port-forward the service for local testing:

```bash
kubectl port-forward service/inference-sandbox 8080:80
```

Call the app through the forwarded port:

```bash
curl -X POST http://localhost:8080/infer \
  -H "Content-Type: application/json" \
  -d '{"text":"kubernetes"}'
```

Run the Kubernetes smoke test:

```bash
python3 -m pytest -q tests/system -m system
```

Restart the deployment after config or image changes:

```bash
kubectl rollout restart deployment inference-sandbox
```

When finished, reset Docker back to the local daemon if needed:

```bash
eval $(minikube docker-env --unset)
```

## Phase 4 Commands

Phase 4 covers Ollama benchmarking and GPU-dependent integration tests.

Confirm Ollama is available:

```bash
ollama ps
```

Pull the required models if they are not already present:

```bash
ollama pull qwen3:0.6b
ollama pull qwen3:4b
ollama pull qwen3:8b
```

Check GPU visibility:

```bash
nvidia-smi
```

Optionally clear existing loaded models for a cleaner baseline:

```bash
ollama stop qwen3:0.6b
ollama stop qwen3:4b
ollama stop qwen3:8b
```

Run the Ollama benchmark:

```bash
PYTHONPATH=src python3 -m inference_sandbox.ollama_bench
```

Run the Ollama integration tests:

```bash
python3 -m pytest -q tests/integration -m integration
```

Expected output:

- `artifacts/ollama/ollama_results.jsonl`

### Phase 4.3: Quantisation Quality Gate

Phase 4.3 adds a perplexity-based regression test that compares FP16 and BF16 inference to an FP32 reference on a fixed WikiText-2 test subset. The test loads TinyLlama in each dtype, scores 200 non-empty WikiText-2 lines (excluding `=` headers), and asserts `|PPL(dtype) − PPL(FP32)| < 0.5`.

Requirements:

- CUDA-capable NVIDIA GPU (test skips on CPU-only hosts)
- `transformers`, `torch`, `datasets` from `requirements.txt`
- First run downloads the TinyLlama checkpoint and the WikiText-2 dataset

Run the quantisation perplexity test:

```bash
python3 -m pytest -v tests/integration/test_quantisation.py
```

Or filter by markers:

```bash
python3 -m pytest -v tests/integration/test_quantisation.py -m "gpu and slow"
```

The repo's `tests/conftest.py` also exposes `--gpu` and `--slow` flags that select tests carrying those markers:

```bash
python3 -m pytest -v tests/integration/test_quantisation.py --gpu --slow
```

Expected output: three parametrised cases (`float32`, `float16`, `bfloat16`) all pass with PPL drift well under the 0.5 tolerance.

## CI/CD

The GitLab pipeline currently does three main things:

- `ruff check src tests`
- `pytest tests -m "not integration and not system"`
- `docker build -f docker/Dockerfile.service ...`

## Documentation

- `docs/learning-logs/phase1.md`
- `docs/learning-logs/phase2.md`
- `docs/learning-logs/phase3.md`
- `docs/learning-logs/phase4.md`
- `docs/cmdlist.md`
- `docs/templates.md`

## Current Artifacts

- `artifacts/benchmark/results.csv`
- `artifacts/benchmark/results.json`
- `artifacts/ollama/ollama_results.jsonl`
