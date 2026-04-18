from dataclasses import dataclass, field

import torch
import transformers

@dataclass
class BenchmarkConfig:
    model_name: str = "TinyLlama/TinyLlama-1.1B-Chat-v1.0"
    prompts: list[str] = field(
        default_factory=lambda: [
            "Explain what a GPU does in one paragraph.",
            "What is TTFT in LLM benchmarking?",
        ]
    )
    gpu_index: int = 0
    max_new_tokens: int = 100

class HFBenchmark:
    def __init__(self, config: BenchmarkConfig) -> None:
        self.config = config
        self.tokenizer = None
        self.model = None

    def get_device(self) -> str:
        return "cuda" if torch.cuda.is_available() else "cpu"
    
    def describe_environment(self) -> dict:
        cuda_available = torch.cuda.is_available()
        gpu_name = (
            torch.cuda.get_device_name(self.config.gpu_index)
            if cuda_available
            else "No CUDA GPU detected"
        )

        return {
            "transformers_version": transformers.__version__,
            "torch_version": torch.__version__,
            "cuda_avail": cuda_available,
            "device": self.get_device(),
            "gpu_name": gpu_name,
            "model_name": self.config.model_name,
            "prompt_count": len(self.config.prompts),
            "max_new_tokens": self.config.max_new_tokens,
        }
    
    def print_environment_summary(self) -> None:
        summary = self.describe_environment()
        print("HF Benchmark Environment Check")
        print("-" * 40)
        for key, value in summary.items():
            print(f"{key}: {value}")

def main() -> None:
    config = BenchmarkConfig()
    benchmark = HFBenchmark(config)
    benchmark.print_environment_summary()

if __name__ == "__main__":
    main()