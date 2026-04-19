from dataclasses import dataclass, field
import time
from threading import Thread
import subprocess

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
    
    def get_vram_mb(self) -> int:
        if not torch.cuda.is_available():
            raise RuntimeError("CUDA GPU is required for VRAM measurement.")

        torch.cuda.synchronize()

        result = subprocess.run(
            [
                "nvidia-smi",
                f"--id={self.config.gpu_index}",
                "--query-gpu=memory.used",
                "--format=csv,noheader,nounits",
            ],
            capture_output=True,
            text=True,
            check=True,
        )
        used_mb = result.stdout.strip().splitlines()[0]
        return int(used_mb)

    def measure_load_vram(self) -> dict:
        if self.model is not None or self.tokenizer is not None:
            raise RuntimeError(
                "measure_load_vram() should be called before load_components()."
            )

        vram_before_load_mb = self.get_vram_mb()
        self.load_components()
        vram_after_load_mb = self.get_vram_mb()

        return {
            "dtype": str(self.config.dtype),
            "vram_before_load_mb": vram_before_load_mb,
            "vram_after_load_mb": vram_after_load_mb,
            "vram_delta_load_mb": vram_after_load_mb - vram_before_load_mb,
        }

    def print_load_vram_demo(self, result: dict) -> None:
        print("\nVRAM Load Demo")
        print("-" * 40)
        print(f"Dtype: {result['dtype']}")
        print(f"VRAM before load (MB): {result['vram_before_load_mb']}")
        print(f"VRAM after load (MB): {result['vram_after_load_mb']}")
        print(f"VRAM delta load (MB): {result['vram_delta_load_mb']}")
    
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
    
    def build_chat_inputs(self, prompt: str) -> transformers.BatchEncoding:
        if self.tokenizer is None or self.model is None:
            raise RuntimeError(
                "Tokenizer and model not loaded. Call load_components() first."
            )

        messages = [
            {"role": "user", "content": prompt},
        ]

        chat_text = self.tokenizer.apply_chat_template(
            messages,
            tokenize=False,
            add_generation_prompt=True,
        )

        chat_inputs = self.tokenizer(chat_text, return_tensors="pt")
        return chat_inputs.to(self.get_device())

    def generate_one_response(self, prompt: str) -> dict:
        if self.tokenizer is None or self.model is None:
            raise RuntimeError(
                "Tokenizer and model are not loaded. Call load_components() first."
            )

        inputs = self.build_chat_inputs(prompt)
        input_length = inputs["input_ids"].shape[1]     # pyright: ignore[reportAttributeAccessIssue]

        with torch.no_grad():
            output_ids = self.model.generate(  # pyright: ignore[reportAttributeAccessIssue]
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

    def measure_ttft(self, prompt: str) -> dict:
        if self.tokenizer is None or self.model is None:
            raise RuntimeError(
                "Tokenizer & model not loaded, fix load_components()."
            )
        
        inputs = self.build_chat_inputs(prompt)
        streamer = TextIteratorStreamer(
            self.tokenizer,
            skip_prompt=True,
            skip_special_tokens=True,
        )

        generation_kwargs = {
            **inputs,
            "max_new_tokens": self.config.max_new_tokens,
            "do_sample": False,
            "pad_token_id": self.tokenizer.eos_token_id,
            "streamer": streamer,
        }

        def run_generation() -> None:
            with torch.no_grad():
                self.model.generate(    # pyright: ignore reportAttributeAccessIssue
                    **generation_kwargs
                )
        
        start = time.perf_counter()
        generation_thread = Thread(target=run_generation)
        generation_thread.start()

        first_token_time = None
        first_text_chunk = ""
        collected_chunks = []

        for text in streamer:
            if text:
                collected_chunks.append(text)
                if first_token_time is None:
                    first_token_time = time.perf_counter()
                    first_text_chunk = text

        generation_thread.join()

        ttft_s = (first_token_time - start) if first_token_time else 0.0
        full_text = "".join(collected_chunks).strip()

        return {
            "prompt": prompt,
            "ttft_s": ttft_s,
            "first_text_chunk": first_text_chunk,
            "streamed_text_preview": full_text[:200]
        }
    
    def print_ttft_demo(self, prompt: str) -> None:
        result = self.measure_ttft(prompt)
        print("\nTTFT Demo")
        print("-" * 40)
        print(f"Prompt: {result['prompt']}")
        print(f"TTFT (s): {result['ttft_s']:.4f}")
        print(f"First streamed text chunk: {result['first_text_chunk']!r}")
        print("Streamed preview:")
        print(result["streamed_text_preview"])

    def measure_throughput(self, prompts: list[str]) -> dict:
        if self.tokenizer is None or self.model is None:
            raise RuntimeError(
                "Tokenizer & model not loaded, call load_components()"
            )
        
        per_prompt_results = []
        total_generated_tokens = 0
        total_wall_time_s = 0.0

        for prompt in prompts:
            inputs = self.build_chat_inputs(prompt)
            input_length = inputs["input_ids"].shape[1]     # pyright: ignore[reportAttributeAccessIssue]

            start = time.perf_counter()
            with torch.no_grad():
                output_ids = self.model.generate(   # pyright: ignore[reportAttributeAccessIssue]
                    **inputs,
                    max_new_tokens=self.config.max_new_tokens,
                    do_sample=False,
                    pad_token_id=self.tokenizer.eos_token_id,
                )
            end = time.perf_counter()

            generated_ids = output_ids[0][input_length:]
            generated_tokens = int(generated_ids.shape[0])
            wall_time_s = end - start

            per_prompt_results.append(
                {
                    "prompt": prompt,
                    "generated_tokens": generated_tokens,
                    "wall_time_s": wall_time_s
                }
            )

            total_generated_tokens += generated_tokens
            total_wall_time_s += wall_time_s
        
        throughput_tokens_per_s = (
            total_generated_tokens / total_wall_time_s
            if total_wall_time_s > 0 else 0.0
        )

        return {
            "prompt_count": len(prompts),
            "total_generated_tokens": total_generated_tokens,
            "total_wall_time_s": total_wall_time_s,
            "throughput_tokens_per_s": throughput_tokens_per_s,
            "per_prompt_results": per_prompt_results,
        }
    
    def print_throughput_demo(self, prompts: list[str]) -> None:
        result = self.measure_throughput(prompts)
        print("\nThroughput Demo")
        print("-" * 40)
        print(f"Prompt count: {result['prompt_count']}")
        print(f"Total generated tokens: {result['total_generated_tokens']}")
        print(f"Total wall time (s): {result['total_wall_time_s']:.4f}")
        print(f"Throughput (tokens/s): {result['throughput_tokens_per_s']:.4f}")
        print("\nPer-prompt analysis")
        print("-" * 40)
        for row in result["per_prompt_results"]:
            print(f"Prompt: {row['prompt']}")
            print(f"Generated tokens: {row['generated_tokens']}")
            print(f"Wall time (s): {row['wall_time_s']:.4f}")
            print()
    
    def run_full_benchmark(self) -> dict:
        if self.model is not None or self.tokenizer is not None:
            raise RuntimeError(
                "run_full_benchmark() should be called on a fresh HFBenchmark instance."
            )

        load_result = self.measure_load_vram()
        ttft_result = self.measure_ttft(self.config.prompts[0])
        throughput_result = self.measure_throughput(self.config.prompts)
        vram_after_benchmark_mb = self.get_vram_mb()

        return {
            "dtype": load_result["dtype"],
            "prompt_count": throughput_result["prompt_count"],
            "vram_before_load_mb": load_result["vram_before_load_mb"],
            "vram_after_load_mb": load_result["vram_after_load_mb"],
            "vram_delta_load_mb": load_result["vram_delta_load_mb"],
            "vram_after_benchmark_mb": vram_after_benchmark_mb,
            "ttft_s": ttft_result["ttft_s"],
            "throughput_tokens_per_s": throughput_result["throughput_tokens_per_s"],
            "total_generated_tokens": throughput_result["total_generated_tokens"],
            "total_wall_time_s": throughput_result["total_wall_time_s"],
        }

    def print_full_benchmark_summary(self, result: dict) -> None:
        print("\nFull Benchmark Summary")
        print("-" * 40)
        print(f"Dtype: {result['dtype']}")
        print(f"Prompt count: {result['prompt_count']}")
        print(f"VRAM before load (MB): {result['vram_before_load_mb']}")
        print(f"VRAM after load (MB): {result['vram_after_load_mb']}")
        print(f"VRAM delta load (MB): {result['vram_delta_load_mb']}")
        print(f"VRAM after benchmark (MB): {result['vram_after_benchmark_mb']}")
        print(f"TTFT (s): {result['ttft_s']:.4f}")
        print(
            f"Throughput (tokens/s): {result['throughput_tokens_per_s']:.4f}"
        )
        print(f"Total generated tokens: {result['total_generated_tokens']}")
        print(f"Total wall time (s): {result['total_wall_time_s']:.4f}")


def main() -> None:
    config = BenchmarkConfig()
    benchmark = HFBenchmark(config)
    benchmark.print_environment_summary()

    result = benchmark.run_full_benchmark()
    benchmark.print_loaded_summary()
    benchmark.print_full_benchmark_summary(result)


if __name__ == "__main__":
    main()