---
name: verify-import
description: >-
  Verifies that a proposed Python import, class, function, CLI, or keyword
  argument exists in the current environment before relying on it. Use whenever
  code suggestions involve unfamiliar APIs, recently changed libraries, or
  version-sensitive packages such as transformers, torch, vllm, tensorrt_llm,
  dynamo, nemo, kubernetes, or httpx.
---

Purpose: prevent hallucinated or stale APIs from entering the repo.

Procedure:

1. Identify what needs verification.
   - Module import, for example: `import transformers`.
   - Symbol import, for example: `from transformers import AutoModelForCausalLM`.
   - Method or function, for example: `AutoModelForCausalLM.from_pretrained`.
   - CLI command, for example: `vllm serve`.
   - Keyword argument, for example: `dtype=` vs `torch_dtype=`.

2. Verify the active environment.
   - Run:

   ```bash
   python -V
   which python
   python -m pip --version
   ```

3. Verify the package version.
   - Prefer:

   ```bash
   python -m pip show <package>
   ```

   - If import name differs from package name, handle that explicitly.
   - Examples:
     - package `scikit-learn`, import `sklearn`
     - package `pillow`, import `PIL`
     - package `pyyaml`, import `yaml`

4. Verify the module imports.
   - Run:

   ```bash
   python -c "import <module>; print(getattr(<module>, '__version__', 'no __version__')); print(<module>.__file__)"
   ```

5. Verify the symbol imports.
   - Run:

   ```bash
   python -c "from <module> import <symbol>; print(<symbol>)"
   ```

6. Verify call signatures when possible.
   - Run:

   ```bash
   python - <<'PY'
import inspect
from <module> import <symbol>
print(inspect.signature(<symbol>))
PY
   ```

   - If the signature is generic, for example `*args, **kwargs`, use `help()` too:

   ```bash
   python -c "from <module> import <symbol>; help(<symbol>)"
   ```

7. For Hugging Face Transformers model loading:
   - Check the installed version:

   ```bash
   python -m pip show transformers
   ```

   - In this project, prefer `dtype=` for `from_pretrained()`.
   - Flag `torch_dtype=` as deprecated for this pinned project version.
   - Do not change this convention without verifying the installed Transformers behavior.

8. For CLI tools:
   - Run:

   ```bash
   <command> --help
   ```

   - Examples:
     - `vllm serve --help`
     - `trtllm-serve --help`
     - `pytest --markers`

9. Report one of:
   - `PASS verified`: the API exists and the proposed usage matches.
   - `WARN signature mismatch`: the symbol exists but the proposed usage may be wrong.
   - `FAIL missing`: the module, symbol, CLI, or argument was not found.
   - `BLOCKED environment issue`: the environment is wrong or the package is not installed.

10. Include the exact version and command output summary in the report.