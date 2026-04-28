from transformers import AutoModelForCausalLM
import torch
from inference_sandbox.hf_bench import BenchmarkConfig, HFBenchmark

config = BenchmarkConfig(dtype=torch.float16)
bench = HFBenchmark(config)

bench.load_components()

prompt = config.prompts[0]

# Measuring peak GPU tensor memory during `generate()`
for max_new_tokens in [128, 256, 512, 1024]:
    bench.config.max_new_tokens = max_new_tokens
    inputs = bench.build_chat_inputs(prompt)
    gen_kw = bench.build_generation_kwargs(inputs)

    torch.cuda.synchronize()

    torch.cuda.reset_peak_memory_stats()

    with torch.no_grad():
        bench.model.generate(**gen_kw)
    
    torch.cuda.synchronize()
    bytes = torch.cuda.memory_allocated()
    peak_bytes = torch.cuda.max_memory_allocated()
    # output results here
    del gen_kw
bench.unload_components()