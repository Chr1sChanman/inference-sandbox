When connecting to a server/device via SSH, things to keep in mind:
**Local Machine(Client aka MacBook Pro)**
- Only keyboard, screen, and Cursor **UI ONLY** are the only components pulled locally
- Everything else runs via the remote server, aka the Ubuntu desktop for this project, which includes the following:
    - Terminal
    - `localhost:6379`
    - Hardware components like GPU, CPU, RAM, etc.
    - Conda environments
    - Docker daemons, compose, and containers
    - Kubernetes cluster, including Minikube
- A good rule of thumb is to treat the remote server as a separate machine
    - Example: Needing to install the Codex extension even when having it on both the local machine and remote server
- "Checklist" of when sshing into the remote server:
    - Status of the system and the applications running on it such as:
        - `minikube status`
        - `docker ps`
        - `kubectl get pods -w`
        - `kubectl get services -w`
        - `kubectl get deployments -w`
        - `kubectl get nodes -w`
        - Check the logs of the applications running on the remote server such as:
            - `docker compose logs app`
            - `kubectl logs deployment/inference-sandbox`
            - `kubectl logs pod-name`
            - `kubectl logs pod-name --previous`
    - Editor extensions, plugins, and settings

## Remote SSH Visual Map

```mermaid
flowchart TD
    subgraph Client["Stage 1: MacBook Client"]
        direction TB
        Keyboard["Keyboard / Trackpad"]
        CursorUI["Cursor Editor UI"]
        Screen["Screen"]
        LocalExt["Local extensions for local workspaces"]
        LocalShell["Local Mac shell, not used by remote runs"]

        Keyboard --> CursorUI
        CursorUI --> Screen
        LocalExt -.local only.-> CursorUI
        LocalShell -.local only.-> CursorUI
    end

    subgraph RemoteSSH["Stage 2: Remote SSH Workspace"]
        direction TB
        SSHConn["SSH Connection"]
        RemoteProtocol["Remote editor protocol"]
        RemoteExt["Remote Extension Host for this SSH target"]
        RemoteCodex["Codex extension installed for SSH target"]
        WorkspaceView["Opened workspace view"]
        RemoteTerminal["Integrated terminal session"]
        ActiveShellEnv["Active shell env: PATH, PYTHONPATH, REDIS_HOST"]
        ActiveConda["Activated Conda env: nvidia"]
        PortForward["Optional port forwarding"]

        SSHConn --> RemoteProtocol
        RemoteProtocol --> RemoteExt
        RemoteExt --> RemoteCodex
        RemoteExt --> WorkspaceView
        RemoteExt --> RemoteTerminal
        RemoteTerminal --> ActiveShellEnv
        ActiveShellEnv --> ActiveConda
        PortForward -.exposes remote ports to MacBook.-> CursorUI
    end

    subgraph Server["Stage 3: Ubuntu Linux Server"]
        direction TB
        Ubuntu["Ubuntu OS"]
        Repo["Repo files on disk: /home/cchan/code/inference-sandbox"]
        CondaInstall["Conda installation and environments"]
        PythonDeps["Python packages: torch, transformers, redis"]
        GPU["NVIDIA GPU"]
        CUDA["NVIDIA driver / CUDA runtime"]
        CPU["CPU"]
        RAM["RAM"]
        Disk["Disk, artifacts, model caches"]
        Docker["Docker daemon"]
        Compose["Docker Compose project"]
        Redis["Redis service/container on server localhost:6379"]
        Minikube["Minikube / Kubernetes"]

        Ubuntu --> Repo
        Ubuntu --> CondaInstall
        CondaInstall --> PythonDeps
        PythonDeps --> GPU
        GPU --> CUDA
        Ubuntu --> CPU
        Ubuntu --> RAM
        Ubuntu --> Disk
        Ubuntu --> Docker
        Docker --> Compose
        Compose --> Redis
        Docker --> Minikube
    end

    CursorUI --> SSHConn
    WorkspaceView --> Repo
    ActiveConda --> CondaInstall
    PythonDeps --> Redis
```
