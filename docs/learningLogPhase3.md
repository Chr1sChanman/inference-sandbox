# Phase 3

## What I Built This Week
- deployment.yaml + service.yaml — deployed inference-sandbox to minikube with 2 replicas and a ClusterIP service
- configmap.yaml — externalised REDIS_HOST and LOG_LEVEL so the same image runs with different config without rebuilding
- Converted benchmark.py from a one-shot Job into a long-running FastAPI inference server with a /infer HTTP endpoint
- k8s_test.py — a Python script using the Kubernetes client API that asserts at least 2 pods with label app=inference-sandbox are Running, prints PASS or FAIL, and uses no kubectl commands

## What I Learned
The purpose of each software and what they're used for in development
Docker — the build tool. Packages your code + dependencies into an image. That image is the artifact that travels through every stage. You build it once, run it anywhere.

Docker Compose — local development shortcut. Lets you spin up your app + all its dependencies (Redis, databases, etc.) with one command. Nobody uses Compose in production — it only knows about one machine. At NVIDIA this would be used to run a local inference stack while developing, before pushing to the cluster.

Kubernetes — the production runtime. Takes your image from the registry, runs it across a cluster of machines, handles restarts, scaling, rolling updates, secret injection. Compose is "make it work on my laptop", K8s is "make it work reliably for everyone."

Redis — just a data store. It doesn't care what's running it. In local dev, Compose spins it up as a container. In Kubernetes, it runs as a Deployment with its own Service. Same Redis, different host. That's exactly why your ConfigMap passes REDIS_HOST=redis — your app code never changes, only the config telling it where Redis lives.

```
Dev Machine                CI/CD Pipeline                  Production Cluster
──────────────             ──────────────                  ──────────────────
docker compose up          docker build                    kubectl apply
  ├── app ──────────────→  docker push ──→ GitLab    ──→   ├── Deployment (app)
  └── redis (local)              Registry (image)          ├── Deployment (redis)
                                                           ├── Service
                                                           └── ConfigMap
```

When using the command `minikube start` pods continuously run until manually stopped, the commands `kubectl get pods -w` and `minikube dashboard` are both ways to view status of pods

The reason for 'replicas' in deployment.yaml is for fault tolerance and throughput where pods handle requests in parallel

'Job' types run to completion and exit with code 0 meaning success where K8 does not restart the service whereas with 'Deployment' types they are expected to run forever and any exit triggers a restart. Basically they tell k8 what "done" means

ConfigMaps — config is separated from the image so the same image runs in dev/staging/prod with different ConfigMaps without rebuilding. If REDIS_HOST was baked into the image, every config change would require a rebuild and repush

imagePullPolicy: Never — tells Kubernetes not to pull the image from a registry and use the local one instead. Needed in minikube because the image was built directly inside minikube's Docker daemon. Without it K8s would try to pull from Docker Hub, fail, and throw ErrImagePull

ConfigMaps don't hot reload, so pods must be restarted with `kubectl rollout restart env-name` to pick up new values. This is because while model server images stay the same across dev/stage/prod, only the ConfigMap changes like different Redis host, log verbosity, batch size, model path, etc. This allows you to modify runtime behavior without re-building/deploying the image. It is also helps avoid hardcoding environment specific values into images that get promoted through a pipeline.

When running `kubectl delete pod pod-name` on a Deployment, Kubernetes detects the pod is gone and the ReplicaSet controller automatically creates a replacement. This is called self-healing and means a single pod crash does not take down the service. Some status lines appear twice because kubectl get pods -w streams raw API watch events: any field change on the pod object emits a new event, and multiple fields can change in rapid succession while the visible STATUS column stays the same.
```
inference-sandbox-6bbf57bf8d-g9fwx   1/1     Terminating         0             31s
inference-sandbox-6bbf57bf8d-g9fwx   1/1     Terminating         0             31s
inference-sandbox-6bbf57bf8d-k7pv2   0/1     Pending             0             0s
inference-sandbox-6bbf57bf8d-k7pv2   0/1     Pending             0             0s
inference-sandbox-6bbf57bf8d-k7pv2   0/1     ContainerCreating   0             0s
inference-sandbox-6bbf57bf8d-g9fwx   0/1     Completed           0             32s
inference-sandbox-6bbf57bf8d-k7pv2   1/1     Running             0             2s
inference-sandbox-6bbf57bf8d-g9fwx   0/1     Completed           0             33s
inference-sandbox-6bbf57bf8d-g9fwx   0/1     Completed           0             33s
```

## What Confused Me (and how I resolved it)
I was confused about why minikube start was needed and whether it was related to activating my conda env. It clicked when I understood that minikube is a system-level Docker container, completely separate from Python environments. Activating/deactivating a conda env has zero effect on whether the cluster is running.

I also got nothing back from cat ~/.kube/config and assumed the cluster was down. It turned out I had a typo — ~./kube/config instead of ~/.kube/config. The config file persists on disk after first minikube start; the cluster just needs to be running to actually connect to it.

The Kubernetes Python client returns structured objects, not text. I expected it to work like parsing kubectl output, but instead you directly access pod.metadata.name and pod.status.phase as typed fields. This is why SDETs use the API instead of shelling out to kubectl — no string parsing, no fragile text matching, and kubectl doesn't even need to be installed in CI.

## What Surprised Me
- Running docker ps while pointed at minikube's daemon showed 20 containers — the entire Kubernetes control plane runs as Docker containers inside minikube (etcd, api-server, scheduler, etc.)
- Ctrl+C on kubectl port-forward does not stop the pods. The tunnel lives on your machine, the cluster is completely independent of your terminal session
- The Kubernetes Python client returns typed objects instead of text. pod.status.phase is a field, not a string you parse from kubectl output — this is why it's more reliable in CI than shelling out to kubectl

## Open Questions
- In production, how do SDET teams run k8s_test.py — is it triggered after every deployment in CI?
- What happens if a pod is in Running phase but the app inside is unhealthy — does K8s know? (Is that what readiness probes are for?)

## Checkpoint Status
[x] Explain what a Deployment does differently than just running docker run
    — Deployment tells K8s to keep N replicas running forever and self-heal on crash. docker run is a one-shot command with no restart logic or replica management.

[x] Describe what a Service is for
    — Stable network endpoint that routes traffic to whichever pods match its label selector. Without it, pods have dynamic IPs that change on restart.

[x] Use kubectl describe and kubectl logs to debug a failing pod
    — kubectl describe shows events at the bottom (image not found, OOM, etc.) kubectl logs streams stdout from the container

[x] Explain what a ConfigMap is and why it exists
    — Separates config from the image so the same image runs in dev/staging/prod with different values. Avoids rebuilding on every config change.

[x] Write a Python script that talks to K8s via the client library
    — k8s_test.py uses kubernetes.client.CoreV1Api to list pods by label selector and assert minimum running replicas. No kubectl used.

## Answers
deployment.yaml tells Kubernetes how to run your app while service.yaml tells Kubernetes how to reach your app internally.
ClusterIP means only accessible inside cluster

redis.yaml is a way to automatically run the CLI command `docker run -d --name redis redis:7-alpine -p 6379:6379`

Self-healing — when a pod is deleted manually or crashes, the ReplicaSet controller detects the count dropped below the desired replicas and creates a replacement automatically. In production this means a hardware fault on one node does not take down the inference service