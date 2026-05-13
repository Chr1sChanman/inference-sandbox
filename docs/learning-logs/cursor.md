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

# Tools and MCPs

- Model Context Protocols (MCPs) are the external tools beyond the standard agent tools like reading, editing, and running files or terminal commands.
    - Examples of MCP actions are:
        - "create GitHub issue"
        - "search Hugging Face models"
        - "query a database"
        - "read GPU telemetry"
        - "search the web in a specific way"
- The term MCP itself refers to the protocol for connecting to and interacting with the external tool/data source.
- MCPs support tools, prompts, resources, root, elicitation, and app-like UI responses as well as `stdio`, `SSE`, and Streamable `HTTP` transports.
- MCPs are stored in `.cursor/mcp.json` as the project-level tool registry like for `inference_sandbox`, while `~/.cursor/mcp.json` is the global file for private/global tools or credentials that don't want to be tied with the project/repository.

## MCP JSON Format

- The top-level shape of the MCP JSON is always:
```json
{
    "mcpServers": {
        "<mcp-server-user-chosenname>": {
            "<...server-config-fields...>": "<...>",
        }
    }
}
```

- There are two main "types" of MCPs:

### `command`

- A `command` MCP instructs Cursor to launch as a local subprocess and communicate with it over `stdin` and `stdout`.
```json
{
    "mcpServers": {
        "brave-search": {
            "command": "npx",
            "args": ["-y", "@modelcontextprotocol/server-brave-search"],
            "env": {
                "BRAVE_SEARCH_API_KEY": "<your-api-key>"
            }
        }
    }
}
```
- This basically tells Cursor:
    - Start this process: `npx -y @modelcontextprotocol/server-brave-search`
    - Pass this environment variable: `BRAVE_SEARCH_API_KEY=<value-from-shell>`
- Cursor then talks to that subprocess over `stdio` which stands for "standard input/output".
- In `stdio` MCPs, the client launches the MCP server as a subprocess, the MCP server reads `JSON-RPC` from `stdin` and writes `JSON-RPC` responses to `stdout`.
- **Use `command` when the MCP server is a local/package script, for example:**
```json
{
    "command": "python",
    "args": ["${workspaceFolder}/tools/gpu_mcp.py"]
}
```
- A.k.a.:
    - Start this process: `python ${workspaceFolder}/tools/gpu_mcp.py`
    - The `workspaceFolder` is the root of the project, which is the `inference-sandbox` repository in this case.
```json
{
    "command": "docker",
    "args": ["run", "--rm", "-i", "some-mcp-image"]
}
```
- A.k.a.:
    - Start this process: `docker run --rm -i some-mcp-image`
    - The `some-mcp-image` is an image that implements the MCP server.

### `url`

- A `url` MCP tells Cursor to not start the server, but to connect to one that is already running.
```json
{
    "mcpServers": {
        "huggingface": {
            "url": "https://huggingface.co/mcp",
            "type": "http"
        }
    }
}
```
- This basically tells Cursor:
    - Do not launch a process, but connect to this endpoint instead: `https://huggingface.co/mcp`
- Remote MCP servers use `HTTP`/`SSE` style communication/transport, where the MCP spec's Streamable `HTTP` transport uses HTTP `POST` and `GET` requests to the MCP server, where it then streams back the server-sent events (SSE) to the client.
- **Use `url` in the following conditions:**
    - Hosted MCP services like `https://huggingface.co/mcp`
    - Local HTTP MCP servers like `http://localhost:9110`
    - Remote GPU helper servers like `nvidia-smi` or `nvtop`
    - Tools running instead Docker or on another machine like `http://gpubox:9110`
- For example in this project, `gpu-tools` is a `url` type because the MCP server is running on the remote Ubuntu server, exposed through port `9110`, where Cursor connects it over to the forwarded `localhost` port `9110` on the local machine.
```json
{
    "mcpServers": {
        "gpu-tools": {
            "url": "http://localhost:9110/sse",
        }
    }
}
```

### General Fields

**Below are the general fields that are used most frequently:**
- `mcpServers`: The required top-level field that contains the MCP servers for the project
- `<mcp-server-user-chosenname>`: The user-chosen name for the MCP server, which is used to identify the MCP server in the MCP JSON
- `<type>`: The transport style of the MCP server, which can be listed in the following ways:
    - `"command": "<command-name>"` + `"args": ["<arg1>", "<arg2>", ...]`: Local stdio server
    - `"type": "stdio"`: Explicitly command-based stdio
        - One thing to note is that using the fields `command` and `args` is equivalent to using the `stdio` field
        - Cursor can *usually* infer the `type` from the `command` and `url` field, but is better to be explicit using the `type` field
    - `"url": "<url-of-the-mcp-server>"`: Remote/local HTTP or SSE server
    - `"type": "http"`: Explicitly Streamable HTTP-style server
    - `"type": "sse"`: Explicitly SSE endpoint
- `"command": "<command-name>"`: The executable Cursor/agent to run, for example:
    - `"command": "npx"`: Run a package script like `npx -y @modelcontextprotocol/server-brave-search`
    - `"command": "python"`: Run a Python script like `python ${workspaceFolder}/tools/gpu_mcp.py`
    - `"command": "docker"`: Run a Docker container like `docker run --rm -i some-mcp-image`
- `"args": ["<arg1>", "<arg2>", ...]`: An array of CLI arguments such as:
    - `"args": ["-y", "@modelcontextprotocol/server-brave-search"]`
    - When paired with `"command": "npx"` this is equivalent to running `npx -y @modelcontextprotocol/server-brave-search`
- `"env": { "<env-var-name>": "<env-var-value>" }`: An object of environment variables to pass to the subprocess, for example:
    - `"env": { "GITHUB_TOKEN": "${env:GITHUB_TOKEN}" }`
    - This does not hardcode the token, just reads it from environment and passes it to the MCP subprocess
- `"envFile": "<path-to-env-file>"`: A file of environment variables, only for `stdio` MCPs and not HTTP/SSE, for example:
    - `"envFile": "${workspaceFolder}/.env"`
    - This reads the environment variables from the `.env` file in the root of the project
- `"url": "<url-of-the-mcp-server>"`: HTTP/SSE endpoint for connecting to an already running MCP server and not launching one, for example:
    - `"url": "http://127.0.0.1:9110/sse"`
    - This connects to the MCP server running on the local machine on port `9110`
- `"headers": { "<header-name>": "<header-value>" }`: HTTP headers for remote servers
    - `"headers": { "Authorization": "Bearer ${env:MY_SERVICE_TOKEN}"}"`
    - Remote-server equivalent of passing secrets through environment variables to the MCP subprocess, whereas command-based MCPs like `stdio` use `env`, URL-based MCPs like `url` use `headers` or OAuth config
- `"auth": { "<auth-type>": "<auth-value>" }`: The other method for passing secrets like OAuth static client credentials used by `url` MCPs, for example:
```json
"auth": {
    "CLIENT_ID": "${env:CLIENT_ID}",
    "CLIENT_SECRET": "${env:CLIENT_SECRET}"
    "scopes": ["read", "write"]
}
```

### TLDR

**In terms of MCP examples for this project:**
| Name | Connection Type | Reason |
| --- | --- | --- |
| `github` | launches `npx ...` | Local Node MCP package |
| `huggingface` | connects to URL | Hosted HTTP MCP service |
| `brave-search` | launches `npx ...` | Local Node MCP package that needs API key |
| `gpu-tools` | connects to localhost URL | Custom server already running on remote server |

**In terms of general fields:**
- `command`: Cursor/agent starts the MCP server as a subprocess
- `url`: Cursor/agent connects to an already running MCP server
- `env`: Secrets/config for command-based MCPs like `stdio`
- `headers`/`auth`: Secrets/config for URL-based MCPs like `url`
- `type`: Explicitly sets transport style of the MCP server
- `args`: CLI arguments for the MCP server

