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
```
curl -LO "https://dl.k8s.io/release/$(curl -L -s https://dl.k8s.io/release/stable.txt)/bin/linux/amd64/kubectl"
sudo install -o root -g root -m 0755 kubectl /usr/local/bin/kubectl
```
> install kubectl

`kubectl version --client`
> check kubectl version

```
curl -LO https://storage.googleapis.com/minikube/releases/latest/minikube-linux-amd64
sudo install minikube-linux-amd64 /usr/local/bin/minikube
```
> install minikube

`minikube version`
> install minikube

`eval $(minikube docker-env)`
> Configs curr terminal's Docker to point at minikube's internal Docker daemon
> Will need to rerun if opening up a new terminal