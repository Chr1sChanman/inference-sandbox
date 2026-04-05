Steps to remove branch after MR merge:
- Switch to main
git checkout main
git pull origin main

git branch -d branch/name

git push origin --delete branch/name (if still exists after MR)

git fetch --prune