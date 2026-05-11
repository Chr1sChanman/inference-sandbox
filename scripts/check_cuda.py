"""NVIDIA/CUDA/PyTorch Env Validation

Checks the following:
- NVIDIA driver visibility via nvidia-smi
- Python version
- PyTorch version
- CUDA avail through PyTorch
- GPU name, memory, and compute capability
- Expected SM architecture, default sm_120 for 50 series Blackwell
- Small CUDA tensor op

Usage:
    python scripts/check_cuda.py
    EXPECTED_SM=sm_120 python scripts/check_cuda.py
"""

from __future__ import annotations

import os
import platform
import shutil
import subprocess
import sys
import textwrap
import time
from dataclasses import dataclass

EXPECTED_SM = os.environ.get("EXPECTED_SM", "sm_120")

@dataclass
class CheckState:
    failures: int = 0
    warnings: int = 0

    def pass_(self, msg: str) -> None:
        print(f"[PASS] {msg}")
    
    def warn(self, msg: str) -> None:
        self.warnings += 1
        print(f"[WARN] {msg}")
    
    def fail(self, msg: str) -> None:
        self.failures += 1
        print(f"[FAIL] {msg}")
    
def run_cmd(cmd: list[str], timeout: int = 10) -> tuple[int, str, str]:
    try:
        p = subprocess.run(
            cmd,
            text=True,
            capture_output=True,
            timeout=timeout,
            check=False
        )
        return p.returncode, p.stdout.strip(), p.stderr.strip()
    except FileNotFoundError:
        return 127, "", f"{cmd[0]} not found"
    except subprocess.TimeoutExpired:
        return 124, "", f"{' '.join(cmd)} timed out after {timeout}s"

def print_header(title: str) -> None:
    print()
    print("=" * 72)
    print(title)
    print("=" * 72)

def check_system(state: CheckState) -> None:
    print_header("System")

    print(f"Python executable : {sys.executable}")
    print(f"Python version    : {sys.version.split()[0]}")
    print(f"Platform          : {platform.platform()}")
    print(f"Machine           : {platform.machine()}")

    major, minor = sys.version_info[:2]
    if (major, minor) >= (3, 11):
        state.pass_(f"Python is {major}.{minor}, compatible with guide target >=3.11")
    else:
        state.warn(f"Python is {major}.{minor}; guide target is >=3.11")

    conda_env = os.environ.get("CONDA_DEFAULT_ENV")
    if conda_env:
        print(f"Conda env         : {conda_env}")
        if conda_env == "nvidia":
            state.pass_("Conda env is 'nvidia'")
        else:
            state.warn("Conda env is not named 'nvidia'")
    else:
        state.warn("CONDA_DEFAULT_ENV is not set; are you inside the conda env?")


def check_nvidia_smi(state: CheckState) -> None:
    print_header("nvidia-smi")

    if shutil.which("nvidia-smi") is None:
        state.fail("nvidia-smi not found on PATH")
        return

    rc, out, err = run_cmd(["nvidia-smi"], timeout=10)
    if rc != 0:
        state.fail(f"nvidia-smi failed: {err or out}")
        return

    state.pass_("nvidia-smi runs")

    query = [
        "nvidia-smi",
        "--query-gpu=name,driver_version,memory.total",
        "--format=csv,noheader",
    ]
    rc, out, err = run_cmd(query, timeout=10)
    if rc == 0 and out:
        print(out)
    else:
        state.warn(f"nvidia-smi query failed: {err or out}")


def check_nvcc(state: CheckState) -> None:
    print_header("nvcc / CUDA toolkit")

    if shutil.which("nvcc") is None:
        state.warn("nvcc not found. This is okay for PyTorch wheels, but not for compiling CUDA code.")
        return

    rc, out, err = run_cmd(["nvcc", "--version"], timeout=10)
    if rc == 0:
        state.pass_("nvcc runs")
        print(out)
    else:
        state.warn(f"nvcc exists but failed: {err or out}")


def check_torch(state: CheckState) -> None:
    print_header("PyTorch + CUDA runtime")

    try:
        import torch
    except Exception as e:
        state.fail(f"Could not import torch: {type(e).__name__}: {e}")
        return

    print(f"torch version     : {torch.__version__}")
    print(f"torch.version.cuda: {torch.version.cuda}")
    print(f"cuDNN version     : {torch.backends.cudnn.version()}")

    if not torch.cuda.is_available():
        state.fail("torch.cuda.is_available() is False")
        return

    state.pass_("torch.cuda.is_available() is True")

    device_count = torch.cuda.device_count()
    print(f"CUDA devices      : {device_count}")

    if device_count < 1:
        state.fail("No CUDA devices visible to PyTorch")
        return

    arch_list = torch.cuda.get_arch_list()
    print(f"torch arch list   : {arch_list}")

    if EXPECTED_SM in arch_list:
        state.pass_(f"Expected architecture {EXPECTED_SM} is present in torch arch list")
    else:
        state.warn(
            f"Expected architecture {EXPECTED_SM} not found in torch arch list. "
            "This can be okay if PyTorch uses PTX fallback, but verify performance later."
        )

    for idx in range(device_count):
        props = torch.cuda.get_device_properties(idx)
        capability = f"sm_{props.major}{props.minor}"
        total_gib = props.total_memory / (1024 ** 3)

        print()
        print(f"Device {idx}")
        print(f"  name              : {props.name}")
        print(f"  compute capability: {props.major}.{props.minor} ({capability})")
        print(f"  total memory      : {total_gib:.2f} GiB")
        print(f"  multiprocessors   : {props.multi_processor_count}")

        if capability == EXPECTED_SM:
            state.pass_(f"Device {idx} compute capability matches {EXPECTED_SM}")
        else:
            state.warn(f"Device {idx} compute capability is {capability}, expected {EXPECTED_SM}")


def check_cuda_tensor_op(state: CheckState) -> None:
    print_header("CUDA tensor smoke test")

    try:
        import torch
    except Exception as e:
        state.fail(f"Could not import torch for smoke test: {type(e).__name__}: {e}")
        return

    if not torch.cuda.is_available():
        state.fail("Skipping tensor smoke test because CUDA is unavailable")
        return

    try:
        device = torch.device("cuda:0")
        torch.cuda.empty_cache()
        torch.cuda.synchronize()

        size = 2048
        a = torch.randn((size, size), device=device, dtype=torch.float16)
        b = torch.randn((size, size), device=device, dtype=torch.float16)

        torch.cuda.synchronize()
        t0 = time.perf_counter()
        c = a @ b
        torch.cuda.synchronize()
        dt_ms = (time.perf_counter() - t0) * 1000

        if not torch.isfinite(c).all():
            state.fail("CUDA matmul produced non-finite values")
            return

        allocated_gib = torch.cuda.memory_allocated(device) / (1024 ** 3)
        reserved_gib = torch.cuda.memory_reserved(device) / (1024 ** 3)

        state.pass_(f"CUDA fp16 matmul succeeded in {dt_ms:.2f} ms")
        print(f"memory allocated  : {allocated_gib:.3f} GiB")
        print(f"memory reserved   : {reserved_gib:.3f} GiB")

    except Exception as e:
        state.fail(f"CUDA tensor smoke test failed: {type(e).__name__}: {e}")


def main() -> int:
    state = CheckState()

    print(textwrap.dedent(f"""
    CUDA environment check
    Expected SM architecture: {EXPECTED_SM}
    Override with: EXPECTED_SM=sm_120 python scripts/check_cuda.py
    """).strip())

    check_system(state)
    check_nvidia_smi(state)
    check_nvcc(state)
    check_torch(state)
    check_cuda_tensor_op(state)

    print_header("Summary")
    print(f"Failures: {state.failures}")
    print(f"Warnings: {state.warnings}")

    if state.failures:
        print("Result: FAIL")
        return 1

    if state.warnings:
        print("Result: PASS with warnings")
        return 0

    print("Result: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())