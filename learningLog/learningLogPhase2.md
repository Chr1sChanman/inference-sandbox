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

docker build 

docker ps

docker images

docker run --rm container-name additional-cmds