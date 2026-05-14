---
name: run-bench
description: >-
  Runs the inference-sandbox benchmark in the active conda environment,
  captures TTFT/TPOT p50/p95/p99 and throughput, appends results to
  results/history.jsonl, and compares against the previous run. Use when the
  user asks to benchmark, regress, compare engines, or collect performance data.
---

Purpose: run a benchmark without inventing commands or silently using the wrong environment.

Procedure:

1. Confirm the active environment.
   - Run `python -V`.
   - Run `which python`.
   - Run `conda env list` if conda is available.
   - Warn if the active env is not `nvidia`.

2. Confirm the package is importable.
   - Run `python -c "import inference_sandbox; print(inference_sandbox.__file__)"`.
   - If this fails, run `python -m pip install -e .` from the repo root.

3. Confirm benchmark entry point.
   - Hugging Face / TinyLlama driver (present in repo):
     `python -m inference_sandbox.bench.hf_bench --help`
   - Ollama driver:
     `python -m inference_sandbox.bench.ollama_bench --help` (script may run without a formal argparse `--help`; inspect the module if needed).
   - If a future `inference_sandbox.bench.serving` module is added, prefer it for OpenAI-compatible serving benches; until then, do not assume `serving.py` exists.

4. Use explicit benchmark parameters.
   - Default engine name: `vllm`.
   - Default engine URL: `http://127.0.0.1:8000`.
   - Default model: `Qwen/Qwen2.5-7B-Instruct-AWQ`.
   - Default output path: `results/run.json`.
   - Allow the user to override engine, URL, model, prompt count, concurrency, and output path.

5. Probe the engine before running.
   - For OpenAI-compatible engines, check:
     `GET <engine-url>/v1/models`
   - Use a short timeout.
   - If the endpoint is down, report it clearly and do not treat it as a code failure.

6. Run the benchmark.
   - For the in-repo HF benchmark, use `hf_bench` flags from `--help` (engine/URL options apply to future serving drivers, not necessarily to `hf_bench`).
   - Example shape once a serving module exists:

   ```bash
   python -m inference_sandbox.bench.serving \
     --engine-name vllm \
     --engine-url http://127.0.0.1:8000 \
     --model Qwen/Qwen2.5-7B-Instruct-AWQ \
     --out results/run.json
   ```

7. Parse the result JSON.
   - Extract TTFT p50/p95/p99.
   - Extract TPOT p50/p95/p99.
   - Extract throughput if present.
   - Extract engine name, model, engine URL, git SHA, timestamp, Python version, torch version, and CUDA version if present.

8. Append a compact record to `results/history.jsonl`.
   - Include at least: {`timestamp`, `git_sha`, `engine`, `model`, `engine_url`, `ttft_p50`, `ttft_p95`, `ttft_p99`, `tpot_p50`, `tpot_p95`, `tpot_p99`, `throughput`}

9. Compare against the previous matching entry.
   - Match on engine and model.
   - Warn if TTFT p95 or TPOT p95 regresses by more than 5%.
   - Warn if throughput drops by more than 5%.
   - Do not fail automatically unless a project baseline explicitly says to fail.

10. Print a one-paragraph summary.
    - Include engine, model, TTFT p95, TPOT p95, throughput, and whether this improved or regressed.