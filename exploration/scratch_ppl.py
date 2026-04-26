import math, torch
from datasets import load_dataset
from transformers import AutoModelForCausalLM, AutoTokenizer

MODEL = "TinyLlama/TinyLlama-1.1B-Chat-v1.0"
device = "cuda:0"

# Around a .002 difference from fp16, within .5 tolerance
tokenizer = AutoTokenizer.from_pretrained(MODEL)
model = AutoModelForCausalLM.from_pretrained(MODEL, dtype=torch.float32) 
model.to(device).eval()

raw = load_dataset("wikitext", "wikitext-2-raw-v1", split="test")
samples = [s.strip() for s in raw["text"] if s.strip() and not s.strip().startswith("=")][:20]

total_nll, total_tokens = 0.0, 0
with torch.no_grad():
    for s in samples:
        enc = tokenizer(s, return_tensors="pt").to(device)
        if enc["input_ids"].shape[1] < 2:
            continue
        loss = model(**enc, labels=enc["input_ids"]).loss.item()
        n = enc["input_ids"].shape[1] - 1
        total_nll += loss * n
        total_tokens += n

ppl = math.exp(total_nll / total_tokens)
print(f"PPL (FP32, 20 sentences): {ppl:.4f}")
print(f"Tokens evaluated: {total_tokens}")