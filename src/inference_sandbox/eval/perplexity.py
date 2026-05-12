import math
import torch

@torch.no_grad()
def corpus_perplexity(
    model,
    tokenizer,
    samples: list[str],
    device: str = "cuda:0",
) -> dict:
    total_nll = 0.0
    total_tokens = 0
    for sample in samples:
        sample_input = tokenizer(sample, return_tensors="pt").to(device)
        if sample_input["input_ids"].shape[1] < 2:
            continue
        outputs = model(input_ids=sample_input["input_ids"], labels=sample_input["input_ids"])
        n_tokens = sample_input["input_ids"].shape[1] - 1
        total_nll += outputs.loss.item() * n_tokens
        total_tokens += n_tokens
    avg_nll = total_nll / total_tokens
    ppl = math.exp(avg_nll)

    return {
        "perplexity": ppl,
        "avg_nll": avg_nll,
        "total_tokens": total_tokens,
        "sentence_count": len(samples),
    }