# Rules: Persistent Context

- Constant, system-level instructions Cursor uses for every Agent, stored as project, user, team, or `AGENTS.md` instructions
- When applied, contents are inserted at the start of the model context for consistent guidance
- In the case of this project, rules answers questions like:
    - What is the stack?
    - Where does source code live?
    - What test markers are used?
    - Do we use requests or httpx for HTTP clients?
    - How should GPU timing be done?
    - Should Transformers use dtype= or torch_dtype=?
- Rule files are stored in `.cursor/rules/` and named like `cuda.mdc`, `general.mdc`, `huggingface.mdc`, `vllm.mdc`, etc.
- `general.mdc` is called a **project identity rule** and is one of the most important rules because it answers the most fundamental questions about the project like listed above
- The condition `alwaysApply: true` means the rules are applied to every Agent chat context, used by files such as `general.mdc`
- The condition `globs: [ "src/inference_sandbox/**/*.py" ]` means the rules are applied to all Python files in the `src/inference_sandbox/` directory and its subdirectories
    - The `**` is a wildcard that matches any number of directories and subdirectories
    - This condition is used by files such as `cuda.mdc` where the content is more specific to the rule like using CUDA for GPU timing

# Skills: Repeatable Procedures

- Skills are reusable, repeatable, version-controlled workflows that instructs Agents how to perform specific tasks
- Cursor discovers them automatically from the `.cursor/skills/` directory
- They can be invoked manually with `/<skill-name>` such as `/verify-import` for verifying new or existing imports
- Each skill is stored as a `SKILL.md` file contained within a folder that identifies the skill like `verify-import/SKILL.md`, which is then stored in the `.cursor/skills/` directory
    - The `name` field must use lowercase letters, numbers, and hyphens
- In regards to the current skills, they do the following:
    - `verify-import`: Used whenever Cursor suggests an API that may be "stale". Especially important for libraries like `transformers`, `torch`, `vllm`, `tensorrt_llm`, `dynamo`, `nemo`, `kubernetes`, or `httpx`.
    - `run-bench`: Used when asking Cursor to run or compare performance, where it does the following steps in order:
        - Confirms the active environment
        - Confirm `inference_sandbox` imports
        - Probe the engine entry and end points
        - Run the benchmark specified
        - Parse TTFT/TPOT p50/p95/p99
        - Append results to `results/history.jsonl`
        - Compare against a prior matching run
- In the future additional skills will be:
    - `compare-quants` for comparing BF16 vs FP8 vs AWQ/IN4 outputs and reminding the agent that the exact string match is too strict for quantisation comparisons
    - `profile-server` for `vllm`, `trtllm-serve`, and Dynamo to collect a short profile, summarize "hot" paths, and avoid assuming guessed performance numbers are accurate

- A good way to think about the difference between rules, skills, and scripts are the following:
    - **Rules**: "Always rememember this context to what it is applied to"
    - **Skills**: "Follow this checklist when doing this task"
    - **Scripts**: "Execute this detministic operation"
- A skill can point to scripts, but the skill itself is still instructions, where Cursor doc's note that skills may include optional `scripts/`, `references/`, or `assets/` folders that are loaded progressively to keep context efficient

# Agents/Subagents: Role-Based Instructions

- Agents are the main interaction point in Cursor, where the user chats or prompts the agents with a question or task
- Examples of agents are the different UI modes Cursor provides in the agent window such as `Agent`, `Plan`, `Ask`, `Debug`, and `Multitask` and are NOT stored in `.cursor/agents/`
- Subagents are the specialized agents that Agents can use to delegate tasks to, where each subagent has its own context window, handles specific work, and returns the result to the Agent
- Subagents are stored in the `.cursor/agents/` directory, where they are named like `cuda-reviewer.md`
- Subagents should not be a workflow checklist like skills such as `/verify-import`, but like a specialized reviewer invoked after file edits such as:
    - `src/inference_sandbox/inference/torch_baseline.py`
    - `src/inference_sandbox/bench/serving.py`
    - `src/inference_sandbox/eval/precision_diff.py`
    - `tests/system/test_torch_baseline.py`
    - `tests/system/test_vllm_serving.py`
- When invoked, subagents will then execute the instructions/behavior defined in the subagent file, where for example `cuda-reviewer.md` will look for things like:
    - Missing `torch.cuda.synchronize()`
    - Hidden CPU fallback
    - Incorrect device placement
    - Deprecated transformers `torch_dtype=` usage
    - Missing `@pytest.mark.gpu` markers
    - Bad latency measurements
    - Hardcoded VRAM assumptions
    - Close-loop benchmark mistakes
- So to summaize the distinction between subagents vs skills:
    - **Subagents**: Use when needing context isolation, parallel work, specialized expertise, or independent verification
    - **Skills**: Use for quick, repeatable, single-purpose actions
    - A good example would be how a skill like `/verify-import` is very simple in that it just checks the API being used is correct, whereas a subagent like `cuda-reviewer.md` is more complex in that it checks the code for correctness, device placement, timing, Hugging Face model-loading APIs, test markers, and GPU memory assumptions
- Another subagent that will be used in the future would be `verifier.md`, which would be a skeptical checker invoked after an agent claims something to be done.
    - It will inspect files, run relevant tests, and summarize a report of what was actually complete.
    - This is one way to utilize a pattern for catching imcomplete or broken claimed work.

# Claude Code vs Cursor

- Claude Code is primarily a terminal-shaped agent that runs natively on the remote server through `tmux`, reads `CLAUDE.md` as its project identity rule, and excels at multi-file refactors or shell-heavy tasks.
- Cursor is primarily an agent based editor that runs on the local machine, reads `general.mdc` as its project identity rule, and is suited more for file-based tasks or complex workflows.
- The main limitation of Cursor is that since it cannot run on the remote server through `tmux`, it cannot persist if the remote server is disconnected or restarted, through long running services or tests can be still kept alive through `tmux`.
- Therefore, when determining which tool to use, consider if the task is long running or not, and if it is, utilize Claude Code to ensure it does not get disconnected or restarted.