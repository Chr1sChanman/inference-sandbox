# Github

## After Merge Requests

`git checkout main`
> switch to main branch

`git pull origin main`
> pull latest changes from main branch

`git branch -d branch-name`
> delete branch

`git fetch --prune`
> delete local branches that have been deleted on the remote repository

`git push origin --delete branch-name`
> delete branch on remote repository (Only if branch still exists in GitLab after MR)

## Create a new branch

`git checkout -b branch-name`
> create a new branch

# Docker

## Building and Running Containers

`docker build --no-cache -t image-name .`
> Will replace another container if given the same name
> Tag (-t) lets you name the container instead of being assigned a random ID

`docker build -f Dockerfile.name -t image-name .`
> Used if you have multiple 

`docker run --rm container-name additional-cmds`
> -rm is important in preventing old containers from taking up space
> Example of additional cmds: `docker run --rm inference-sandbox pytest test_benchmark.py`

## Listing Containers/Images

`docker ps`
> list running containers

`docker image`
> list images

## Removing unused containers

`docker image prune`
> Add Force (-f) to skip confirmation prompt

`docker system prune`
> More extreme version of image prune

`docker rmi image-name`
> Removes specific image

# Docker Compose

`docker compose up`
> start everything
> --remove-orphans removes containers for services that are not defined in the current Compose configuration

`docker compose up --build`
> rebuild images first

`docker compose down`
> stop and remove containers

`docker compose logs app`
> stream logs from the app service

`docker compose run --rm app python filename.py args`
> run a command in a compose container

# GitLab

`docker tag image-name:latest registry.gitlab.com/repo-id/image-name:tag`
> tag the image

`docker push registry.gitlab.com/repo-id/image-name:tag`
> push the image to the registry

# Kubernetes

`kubectl version --client`
> check kubectl version

`eval $(minikube docker-env)`
> Configs curr terminal's Docker to point at minikube's internal Docker daemon
> Will need to rerun if opening up a new terminal

`eval $(minikube docker-env --unset)`
> Resets Docker CLI back to your local system daemon

`kubectl apply -f filename.yaml`
> Create or update a Kubernetes resource from a YAML file

`kubectl get pods`
> List all pods in the default namespace

`kubectl get pods -w`
> Watch pods continuously for status changes

`kubectl get services`
> List all services in the default namespace

`kubectl describe pod pod-name`
> Show detailed info and events for a pod (main debugging tool)

`kubectl logs deployment/deployment-name`
> Stream logs from a deployment's pods

`kubectl logs pod-name`
> Stream logs from a specific pod

`kubectl logs pod-name --previous`
> Show logs from a crashed (previous) container instance

`kubectl delete deployment deployment-name`
> Delete a deployment and its pods

`kubectl delete pod pod-name`
> Delete a specific pod (Deployment will automatically recreate it)

`kubectl delete job job-name`
> Delete a job and its pods

`kubectl rollout restart deployment deployment-name`
> Restart all pods in a deployment (e.g. to pick up a new image)

`kubectl create configmap configmap-name --from-literal=key=value`
> Create a ConfigMap imperatively from key-value pairs

`kubectl port-forward service/service-name local-port:service-port`
> Forward a local port to a service inside the cluster (for local testing)

`kubectl get deployments`
> List all deployments in the default namespace

`kubectl scale deployment deployment-name --replicas=N`
> Scale a deployment to N replicas

`kubectl exec pod-name -- command`
> Run a command inside a running container
> Example: `kubectl exec pod-name -- env | grep -E "REDIS|LOG"`

`kubectl exec -it pod-name -- /bin/bash`
> Open an interactive shell inside a running container

## Minikube

`minikube start --driver=docker --memory=4096 --cpus=2`
> Start the local Kubernetes cluster

`minikube stop`
> Stop the cluster (preserves state)

`minikube dashboard`
> Open the Kubernetes dashboard UI in the browser

`minikube status`
> Check if the cluster and components are running