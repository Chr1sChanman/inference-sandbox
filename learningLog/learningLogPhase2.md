Steps to remove branch after MR merge:
- Switch to main
git checkout main
git pull origin main

git branch -d branch/name

git push origin --delete branch/name (if still exists after MR)

git fetch --prune or git remote prune origin

git checkout -b branch/name

docker image prune (-f)

docker system prune

docker build -t image-name . (will replace container with name)

docker ps

docker images

docker run --rm container-name additional-cmds

Title: <type>: <short imperative summary>

Description: ## What
Brief explanation of what changed.

## Why
The motivation or problem this solves.

## How to Test
Steps to verify the change works.
