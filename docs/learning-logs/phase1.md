# Phase 1

## What I Built This Week
- A benchmark that measures output on a program
- Validation tests that I fully understand
- A pipeline that runs when creating MRs in GitLab

## What I Learned
- How to create a Merge Request
- How to set up and config a basic .yml file
- Validation/lint tools besides pytest
- Surface OOP like decorators and function calling
- Atomic commits — one logical change per commit so that if a bug is introduced, git log shows exactly which commit caused it. Committing save_results and load_results separately means a bug in load_results doesn't get buried inside an unrelated change
- Protected branches — main is locked so nobody, including yourself, can push directly. Every change goes through an MR. This is exactly how NVIDIA operates so that no untested code reaches production
- The --self-test flag pattern — shipping code with a built-in self-test is the SDET mindset. The CI job calls --self-test to verify the script works without needing a separate test file

## What Confused Me (and how I resolved it)
Syntax naming, but that syntax writing in general is something I need to work on, I can think about the processs but need help when actually writing, will come with experience

## What Surprised Me
- How similar MRs on GitLab are to PRs on GitHub
- The support tools in Python have and what I could do

## Open Questions
None at the current moment, maybe asking about the security when pushing code as this is my first internship
What other terms/concepts to look into like decorators and OOP relevant

## Checkpoint Status
- Create `src/inference_sandbox/reverse_service.py` [x] Done / [ ] Not yet
- Create function time_reverse() that reverses an input string and returns input length, output, and duration in ms [x] Done / [ ] Not yet
- Create a main block that calls on time_reverse() and outputs a table of results [x] Done / [ ] Not yet
- Create validation through pytest to assert the three tests [x] Done / [ ] Not yet
- Add docustring to every function, switched from flake8 to ruff (more modern) [x] Done / [ ] Not yet
- Add additional functions to load and save results as well as assert those results [x] Done / [ ] Not yet

## Answers
**What does a Merge Request do that a direct push does not?**
It streamlines and prevents conflicts when merging with main with multiple 'authors' or branches, and adds a layer of security in terms of needing review before big changes are pushed. It is almost the exact same as a Pull Request in GitHub with one of the only differences being the name itself. GitLab usually have tigher CI/CD integration through the environments and deployment pipelines.

**What is a CI pipeline runner?**
They are files in .yml/.yaml format that define the checks and reviews automatically performed by the system in pipelines before human/manual review, good for checking if the basics are at least met and can be configured to prevent further conflict merges rather than having to deal with it during the merge. The 'runner' specifically is the agent that executes the pipeline jobs (a server or container that picks up the job and runs it) while the config file defines it.

**Why does commit message format matter?**
An accurate and concise description of what you changed helps other people who didn't work on the code to quickly grasp on what you did and change, which helps streamline and speed up work in a team.
