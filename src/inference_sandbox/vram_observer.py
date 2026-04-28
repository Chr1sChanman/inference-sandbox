from transformers import AutoModelForCausalLM
import torch
from inference_sandbox.hf_bench import BenchmarkConfig, HFBenchmark

config = BenchmarkConfig(dtype=torch.float16)
bench = HFBenchmark(config)

bench.load_components()

prompt = config.prompts[0]

