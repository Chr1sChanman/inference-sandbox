#! /usr/bin/env bash
# Quick health check to see if everything that should be running is running
set -u
probes=(
    "minikube apiserver https://192.168.49.2:8443/version"
    "ollama             http://127.0.0.1:11434/api/tags"
    "engine on 8000     http://127.0.0.1:8000/v1/models"
    "redis              http://127.0.0.1:6379"
)
for p in "${probes[@]}"; do
    name="${p%% *}"
    url="${p##* }"
    printf "%-22s " "$name"
    curl -ksm 2 -o /dev/null -w "%{http_code}" "$url" 2>/dev/null || echo "DOWN"
    echo
done