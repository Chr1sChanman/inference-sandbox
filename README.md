# inference-sandbox

A Python benchmarking sandbox for measuring function performance. Currently benchmarks string reversal with timing, CSV/JSON result persistence, and a CI/CD pipeline for linting and testing.

## Requirements

- Python 3.11+
- `pytest` (for tests)
- `flake8` (for linting)

## Usage

Run the benchmark and save results to `results.csv` and `results.json`:

```bash
python benchmark.py
```

Output:

```
Input Length    Output                                             Duration (ms)
--------------------------------------------------------------------------------
2               ih                                                0.0012
11              dlrow olleh                                       0.0003
43              god yzal eht revo spmuj xof nworb kciuq eht      0.0002
```

## Testing

```bash
pip install pytest
pytest test_benchmark.py
```

Tests cover:
- Output is correctly reversed
- Duration is positive
- Input length is correct
- JSON save/load round-trip
- CSV save/load round-trip

## CI/CD

The GitLab CI pipeline (`.gitlab-ci.yml`) runs on merge requests and `main`:

| Stage | Job | What it does |
|-------|-----|--------------|
| lint  | `lint:python` | Runs `flake8` with max line length 120 |
| test  | `test:run` | Runs `pytest test_benchmark.py` |
