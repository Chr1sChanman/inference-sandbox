# Phase 3

## What I Built This Week
<!-- Describe the concrete output: what exists now that did not before? -->

## What I Learned
The purpose of each software and what they're used for in development
Docker — the build tool. Packages your code + dependencies into an image. That image is the artifact that travels through every stage. You build it once, run it anywhere.

Docker Compose — local development shortcut. Lets you spin up your app + all its dependencies (Redis, databases, etc.) with one command. Nobody uses Compose in production — it only knows about one machine. At NVIDIA this would be used to run a local inference stack while developing, before pushing to the cluster.

Kubernetes — the production runtime. Takes your image from the registry, runs it across a cluster of machines, handles restarts, scaling, rolling updates, secret injection. Compose is "make it work on my laptop", K8s is "make it work reliably for everyone."

Redis — just a data store. It doesn't care what's running it. In local dev, Compose spins it up as a container. In Kubernetes, it runs as a Deployment with its own Service. Same Redis, different host. That's exactly why your ConfigMap passes REDIS_HOST=redis — your app code never changes, only the config telling it where Redis lives.

Dev Machine
- docker compose up
    - app
    - redis (for local development)

CI/CD Pipeline
- docker build
- docker push -> GitLab Container Registry (K8 pulls image from here)

Production cluster
- kubectl apply
    - Deployment (app)
    - Deployment (redis)
    - Service
    - ConfigMap

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
<!-- Specific confusion + specific resolution. "I was confused about X, then I did Y and it clicked." -->

## What Surprised Me
<!-- One thing that was different from what you expected. Good surprises and bad ones. -->

## Open Questions
<!-- Things you still don't understand. These become your questions for your internship manager. -->

## Checkpoint Status
<!-- Copy the checkpoint criteria from the phase. Mark each: [x] Done / [ ] Not yet -->

## Answers
<!-- Answers to the questions asked at the end of each phase -->
deployment.yaml tells Kubernetes how to run your app while service.yaml tells Kubernetes how to reach your app internally.
ClusterIP means only accessible inside cluster

redis.yaml is a way to automatically run the CLI command `docker run -d --name redis redis:7-alpine -p 6379:6379`

