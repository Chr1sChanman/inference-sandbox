**Learning Log Template**
# Phase N

## What I Built This Week
<!-- Describe the concrete output: what exists now that did not before? -->

## What I Learned
<!-- 3–5 key concepts, in your own words. Not copied. If you can't explain it, you don't know it yet. -->

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

**Merge Request Template**
Title:
type: short imperative summary

Description:
## What
Brief explanation of what changed.

## Why
The motivation or problem this solves.

## How to Test
Steps to verify the change works.

## Observations
Things to note user side

**List of commit types**
feat — A new capability that didn't exist before. Adding a function, a flag, a feature. If a user/teammate would notice something new works, it's a feat.
`feat(benchmark): add --engine flag for TRT-LLM mode`
fix — Correcting something that was broken or wrong. A bug, a bad default, a misconfiguration.
`fix(docker): correct CUDA base image tag from 12.3 to 12.4`
test — Adding or modifying tests only. No production code changes.
`test(inference): add perplexity assertion for FP16 baseline`
docs — Documentation only. README, comments, docstrings, markdown files.
`docs(readme): add minikube setup instructions`
refactor — Restructuring code without changing what it does. Renaming, splitting a function, reorganising a module. No new behavior, no bug fix.
`refactor(benchmark): extract timing logic into separate helper function`
chore — Maintenance work that isn't code or docs. Updating dependencies, tweaking .gitignore, bumping versions, cleaning up dead files.
`chore: add *.jsonl to .gitignore`
ci — Changes to CI/CD pipeline files only (.gitlab-ci.yml, GitHub Actions, etc.).
`ci: add gpu-runner tag to integration test job`
build — Changes to the build system or external dependencies. Dockerfile, requirements.txt, setup.py, Makefile.
`build(docker): convert to multi-stage build to reduce image size`
perf — A code change that improves performance without changing behavior.
`perf(benchmark): cache model load between runs instead of reloading each iteration`
style — Formatting only — whitespace, semicolons, line length. Zero logic changes. Usually from a linter auto-fix.
`style: fix trailing whitespace flagged by flake8`
revert — Undoing a previous commit. Git generates this message automatically when you run git revert.
`revert: feat(benchmark): add --engine flag (caused import error on CPU-only machines)`

docker-compose.yml — a two-service stack
services:
  app:
    build:
      context: .
      dockerfile: docker/Dockerfile.service
    ports:
      - "8080:8080"                   # host:container port mapping
    environment:
      - REDIS_HOST=redis              # 'redis' resolves to the redis container
      - LOG_LEVEL=DEBUG
      - ARTIFACTS_DIR=/app/artifacts
    volumes:
      - ./artifacts:/app/artifacts    # Bind mount: host directory into container
    depends_on:
      - redis                         # Don't start app until redis is up

  redis:
    image: redis:7-alpine             # Pull from Docker Hub, no build needed
    ports:
      - "6379:6379"
