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
`docker build -t image-name .`
- Will replace another container if given the same name
`docker run --rm container-name additional-cmds`
- -rm is important in preventing old containers from taking up space
Example of additional cmds: `docker run --rm inference-sandbox pytest test_benchmark.py`

## Listing Containers/Images
`docker ps`
`docker image`

## Removing unused containers
`docker image prune`
- Add Force (-f) if needed
`docker system prune`
- More extreme version of image prune