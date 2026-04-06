# Github

## After Merge Requests
`git checkout main`
`git pull origin main`
`git branch -d branch-name`
`git push origin --delete branch-name`
- (Only if branch still exists in GitLab after MR)

## Create a new branch
`git checkout -b branch-name`

# Docker

## Building and Running Containers
`docker build --no-cache -t image-name .`
- Will replace another container if given the same name
- Tag (-t) lets you name the container instead of being assigned a random ID
`docker build -f Dockerfile.name -t image-name .`
- Used if you have multiple Dockerfiles
`docker run --rm container-name additional-cmds`
- -rm is important in preventing old containers from taking up space
Example of additional cmds: `docker run --rm inference-sandbox pytest test_benchmark.py`

## Listing Containers/Images
`docker ps`
`docker image`

## Removing unused containers
`docker image prune`
- Add Force (-f) to skip confirmation prompt
`docker system prune`
- More extreme version of image prune
`docker rmi image-name`
- Removes specific image

# Docker Compose
`docker compose up`
- start everything
`docker compose up --build`
- rebuild images first
`docker compose down`
- stop and remove containers
`docker compose logs app`
- stream logs from the app service