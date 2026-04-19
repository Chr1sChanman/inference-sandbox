from dataclasses import dataclass, field

import torch
import transformers
from transformers import AutoModelForCausalLM, AutoTokenizer

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
    dtype: torch.dtype = torch.float16

class HFBenchmark:
    def __init__(self, config: BenchmarkConfig) -> None:
        self.config = config
        self.tokenizer = None
        self.model = None

    def get_device(self) -> str:
        if torch.cuda.is_available():
            return f"cuda:{self.config.gpu_index}"
        return "cpu"
    
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
            "requested_dtype": str(self.config.dtype),
        }
    
    def print_environment_summary(self) -> None:
        summary = self.describe_environment()
        print("HF Benchmark Environment Check")
        print("-" * 40)
        for key, value in summary.items():
            print(f"{key}: {value}")
    
    def load_components(self) -> None:
        if not torch.cuda.is_available():
            raise RuntimeError(
                "Phase 4.2 expects CUDA GPU, but torch.cuda.is_available() is False."
            )
        
        print("\nLoading tokenizer...")
        self.tokenizer = AutoTokenizer.from_pretrained(self.config.model_name)

        print("Loading model...")
        self.model = AutoModelForCausalLM.from_pretrained(
            self.config.model_name,
            torch_dtype=self.config.dtype,
        )
        self.model.to(self.get_device())
        self.model.eval()
    
    def describe_loaded_objects(self) -> dict:
        if self.tokenizer is None or self.model is None:
            return {"loaded": False}
        
        first_param = next(self.model.parameters())

        return {
            "loaded": True,
            "tokenizer_class": self.tokenizer.__class__.__name__,
            "model_dtype": str(first_param.dtype),
            "model_device": str(first_param.device),
            "vocab_size": self.tokenizer.vocab_size,
        }
    
    def print_loaded_summary(self) -> None:
        summary = self.describe_loaded_objects()
        print("\nLoaded Hugging Face Objects")
        print("-" * 40)
        for key, value in summary.items():
            print(f"{key}: {value}")
    

def main() -> None:
    config = BenchmarkConfig()
    benchmark = HFBenchmark(config)
    benchmark.print_environment_summary()
    benchmark.load_components()
    benchmark.print_loaded_summary()

if __name__ == "__main__":
    main()