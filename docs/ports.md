# Port Forwarding Configuration

To prevent port conflicts for the inference engines (Dynamno, vLLM, TRT-LLM), port forwarding assignments have been mapped between the local machine and remote server via `~/.ssh/config` in the following table:

| Port | Service | Phase |
| --- | --- | --- |
| 6379 | Redis | 3 |
| 8000 | Primary Inference Engine | 4.1 / 4.3 / 6.1 | 
| 8001 | Secondary Inference Engine | 6.1 |
| 8002 | Tertiary Inference Engine (Triton metrics / TRT-LLM secondary) | 4.5 |
| 8443 | Minikube API Server | 3 |
| 9110 | Custom MCP HTTP Server (gpu-tools) | 0.3.9 |
| 11434 (remote) / 11435 (local) | Ollama | 4.2 |
| 9090 | Prometheus (if added) | 5+ |

- Do not default to `8000`. When bringing up a second engine, explicity pass `--port 8001` and update benchmark driver to take `--engine-url` to enable hitting either port without relaunching driver