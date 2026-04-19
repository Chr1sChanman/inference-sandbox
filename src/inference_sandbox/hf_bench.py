from dataclasses import dataclass, field
import time
from threading import Thread

import torch
import transformers
from transformers import (
    AutoModelForCausalLM, 
    AutoTokenizer,
    TextIteratorStreamer,
)

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
            dtype=self.config.dtype,
        )
        self.model.to(self.get_device())    # pyright: ignore reportGeneralTypeIssues
        self.model.eval()
    
    def describe_loaded_objects(self) -> dict:
        if self.tokenizer is None or self.model is None:
            return {"loaded": False}
        
        first_param = next(self.model.parameters())

        return {
            "loaded": True,
            "tokenizer_class": self.tokenizer.__class__.__name__,
            "model_class": self.model.__class__.__name__,
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
    
    def build_chat_input_ids(self, prompt: str) -> torch.Tensor:
        if self.tokenizer is None or self.model is None:
            raise RuntimeError(
                "Tokenizer and model not loaded, fix load_components()."
            )
        
        messages = [
            {"role": "user", "content": prompt},
        ]

        input_ids = self.tokenizer.apply_chat_template(
            messages,
            add_generation_prompt=True,
            return_tensors="pt",
        )
        return input_ids.to(self.get_device())

    def generate_one_response(self, prompt: str) -> dict:
        if self.tokenizer is None or self.model is None:
            raise RuntimeError(
                "Tokenizer & model are not loaded. Fix funct load_components()."
            )
        
        messages = [
            {"role": "user", "content": prompt},
        ]

        inputs = self.tokenizer.apply_chat_template(
            messages,
            add_generation_prompt=True,
            return_tensors="pt",
        ).to(self.get_device())

        input_length = inputs["input_ids"].shape[1]

        with torch.no_grad():
            output_ids = self.model.generate(   # pyright: ignore reportAttributeAccessIssue
                **inputs,
                max_new_tokens=self.config.max_new_tokens,
                do_sample=False,
                pad_token_id=self.tokenizer.eos_token_id,
            )
        
        generated_ids = output_ids[0][input_length:]
        generated_text = self.tokenizer.decode(
            generated_ids,
            skip_special_tokens=True,
        )

        return {
            "prompt": prompt,
            "input_token_count": input_length,
            "generated_token_count": int(generated_ids.shape[0]),
            "generated_text": generated_text,
        }
    def print_generation_demo(self, prompt: str) -> None:
        result = self.generate_one_response(prompt)
        print("\nGeneration Demo")
        print("-" * 40)
        print(f"Prompt: {result['prompt']}")
        print(f"Input tokens: {result['input_token_count']}")
        print(f"Generated tokens: {result['generated_token_count']}")
        print(f"Generated text:")
        print(result["generated_text"])

def main() -> None:
    config = BenchmarkConfig()
    benchmark = HFBenchmark(config)
    benchmark.print_environment_summary()
    benchmark.load_components()
    benchmark.print_loaded_summary()
    benchmark.print_generation_demo(config.prompts[0])

if __name__ == "__main__":
    main()