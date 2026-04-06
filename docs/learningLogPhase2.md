# Phase 2

## What I Built This Week
This week I built a single-stage, multi-stage, and a docker-compose to run benchmark.py, analyze the results pushed to Redis, and understand the caching behavior of the build process.

## What I Learned
- Image size difference between single-stage and multi-stage
- Caching behavior of the build process
- How to build and push images to GitLab registry
- How to use docker-compose to run benchmark.py and analyze the results

## What Confused Me (and how I resolved it)
- What confused me was the difference between running a container with docker run vs docker compose run --rm app python filename.py args. I was able to resolve it by asking AI and looking at the docs, learning that Redis is a service that is used to store data in a key-value store and is used to store the results of the benchmark.

## What Surprised Me
- How easy it was to build and push images to GitLab registry
- How easy it was to use docker-compose to run benchmark.py and analyze the results

## Open Questions
Maybe understanding why running on "6379" needs security credentials and maybe just in general security measures taken when running images/containers.

## Checkpoint Status
- Build a single-stage dockerfile [x] Done / [ ] Not yet
- Build a multi-stage dockerfile [x] Done / [ ] Not yet
- Build a docker-compose file [x] Done / [ ] Not yet
- Run benchmark.py and analyze the results [x] Done / [ ] Not yet
- Push the image to GitLab registry [x] Done / [ ] Not yet
- Understand the caching behavior of the build process [x] Done / [ ] Not yet

## Answers
### Phase 2.3
As shown below from the CLI output, the multi-stage outputs a smaller file size than the single-stage
```
(nvidia) cchan@ubuntu-cchan:~/code/inference-sandbox$ docker images
REPOSITORY                 TAG                        IMAGE ID       CREATED              SIZE
inference-sandbox-single   latest                     cacf2fb56536   About a minute ago   181MB
inference-sandbox-multi    latest                     cb036c453886   2 minutes ago        151MB
```

### Phase 2.2
To put in my own words how caching behavior works, it caches up until the step that has changed, then rebuilding everything after. For example, the first run uses no cache as it is building fresh, but on the second run where we change benchmark.py, that step and the ones after all rerun as the change in the .py file could affect all subsequent runs. That's why when we add a blank line in requirements.txt and run the third build, it has to build fresh from the step where it copies the .txt file and everything after.
```
(nvidia) cchan@ubuntu-cchan:~/code/inference-sandbox$ docker build --no-cache -t inference-sandbox .
DEPRECATED: The legacy builder is deprecated and will be removed in a future release.
            Install the buildx component to build images with BuildKit:
            https://docs.docker.com/go/buildx/

Sending build context to Docker daemon   38.4kB
Step 1/8 : FROM python:3.11-slim
 ---> e67db9b14d09
Step 2/8 : WORKDIR /app
 ---> Running in b5a636a91eb9
 ---> Removed intermediate container b5a636a91eb9
 ---> 0fd03c3239ea
Step 3/8 : RUN useradd --create-home appuser && chown appuser:appuser /app
 ---> Running in 5936b03b56c2
 ---> Removed intermediate container 5936b03b56c2
 ---> 8f43f94d0655
Step 4/8 : COPY requirements.txt .
 ---> 5997617a6bf8
Step 5/8 : RUN pip install --no-cache-dir --root-user-action=ignore --upgrade pip &&     pip install --no-cache-dir --root-user-action=ignore -r requirements.txt
 ---> Running in f925f01fc142
Requirement already satisfied: pip in /usr/local/lib/python3.11/site-packages (24.0)
Collecting pip
  Downloading pip-26.0.1-py3-none-any.whl.metadata (4.7 kB)
Downloading pip-26.0.1-py3-none-any.whl (1.8 MB)
   ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ 1.8/1.8 MB 40.9 MB/s eta 0:00:00
Installing collected packages: pip
  Attempting uninstall: pip
    Found existing installation: pip 24.0
    Uninstalling pip-24.0:
      Successfully uninstalled pip-24.0
Successfully installed pip-26.0.1
Collecting ruff (from -r requirements.txt (line 1))
  Downloading ruff-0.15.9-py3-none-manylinux_2_17_x86_64.manylinux2014_x86_64.whl.metadata (26 kB)
Collecting pytest (from -r requirements.txt (line 2))
  Downloading pytest-9.0.2-py3-none-any.whl.metadata (7.6 kB)
Collecting iniconfig>=1.0.1 (from pytest->-r requirements.txt (line 2))
  Downloading iniconfig-2.3.0-py3-none-any.whl.metadata (2.5 kB)
Collecting packaging>=22 (from pytest->-r requirements.txt (line 2))
  Downloading packaging-26.0-py3-none-any.whl.metadata (3.3 kB)
Collecting pluggy<2,>=1.5 (from pytest->-r requirements.txt (line 2))
  Downloading pluggy-1.6.0-py3-none-any.whl.metadata (4.8 kB)
Collecting pygments>=2.7.2 (from pytest->-r requirements.txt (line 2))
  Downloading pygments-2.20.0-py3-none-any.whl.metadata (2.5 kB)
Downloading ruff-0.15.9-py3-none-manylinux_2_17_x86_64.manylinux2014_x86_64.whl (11.3 MB)
   ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ 11.3/11.3 MB 59.9 MB/s  0:00:00
Downloading pytest-9.0.2-py3-none-any.whl (374 kB)
Downloading pluggy-1.6.0-py3-none-any.whl (20 kB)
Downloading iniconfig-2.3.0-py3-none-any.whl (7.5 kB)
Downloading packaging-26.0-py3-none-any.whl (74 kB)
Downloading pygments-2.20.0-py3-none-any.whl (1.2 MB)
   ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ 1.2/1.2 MB 65.0 MB/s  0:00:00
Installing collected packages: ruff, pygments, pluggy, packaging, iniconfig, pytest

Successfully installed iniconfig-2.3.0 packaging-26.0 pluggy-1.6.0 pygments-2.20.0 pytest-9.0.2 ruff-0.15.9
 ---> Removed intermediate container f925f01fc142
 ---> b43a763154d7
Step 6/8 : COPY benchmark.py test_benchmark.py ./
 ---> 1838cd416b74
Step 7/8 : USER appuser
 ---> Running in 8d271e86b8e9
 ---> Removed intermediate container 8d271e86b8e9
 ---> 7b53ca47ea6a
Step 8/8 : CMD ["python", "benchmark.py"]
 ---> Running in 15ef37cc6674
 ---> Removed intermediate container 15ef37cc6674
 ---> 131bdf6ea0f3
Successfully built 131bdf6ea0f3
Successfully tagged inference-sandbox:latest
(nvidia) cchan@ubuntu-cchan:~/code/inference-sandbox$ docker build -t inference-sandbox .
DEPRECATED: The legacy builder is deprecated and will be removed in a future release.
            Install the buildx component to build images with BuildKit:
            https://docs.docker.com/go/buildx/

Sending build context to Docker daemon   38.4kB
Step 1/8 : FROM python:3.11-slim
 ---> e67db9b14d09
Step 2/8 : WORKDIR /app
 ---> Using cache
 ---> 0fd03c3239ea
Step 3/8 : RUN useradd --create-home appuser && chown appuser:appuser /app
 ---> Using cache
 ---> 8f43f94d0655
Step 4/8 : COPY requirements.txt .
 ---> Using cache
 ---> 5997617a6bf8
Step 5/8 : RUN pip install --no-cache-dir --root-user-action=ignore --upgrade pip &&     pip install --no-cache-dir --root-user-action=ignore -r requirements.txt
 ---> Using cache
 ---> b43a763154d7
Step 6/8 : COPY benchmark.py test_benchmark.py ./
 ---> 9679281ed999
Step 7/8 : USER appuser
 ---> Running in 51970cdb519c
 ---> Removed intermediate container 51970cdb519c
 ---> 29e837978584
Step 8/8 : CMD ["python", "benchmark.py"]
 ---> Running in 6ed76608b508
 ---> Removed intermediate container 6ed76608b508
 ---> 800b712bf06d
Successfully built 800b712bf06d
Successfully tagged inference-sandbox:latest
(nvidia) cchan@ubuntu-cchan:~/code/inference-sandbox$ docker build -t inference-sandbox .
DEPRECATED: The legacy builder is deprecated and will be removed in a future release.
            Install the buildx component to build images with BuildKit:
            https://docs.docker.com/go/buildx/

Sending build context to Docker daemon   38.4kB
Step 1/8 : FROM python:3.11-slim
 ---> e67db9b14d09
Step 2/8 : WORKDIR /app
 ---> Using cache
 ---> 0fd03c3239ea
Step 3/8 : RUN useradd --create-home appuser && chown appuser:appuser /app
 ---> Using cache
 ---> 8f43f94d0655
Step 4/8 : COPY requirements.txt .
 ---> 848b0fbb94e8
Step 5/8 : RUN pip install --no-cache-dir --root-user-action=ignore --upgrade pip &&     pip install --no-cache-dir --root-user-action=ignore -r requirements.txt
 ---> Running in 827a7fdb9558
Requirement already satisfied: pip in /usr/local/lib/python3.11/site-packages (24.0)
Collecting pip
  Downloading pip-26.0.1-py3-none-any.whl.metadata (4.7 kB)
Downloading pip-26.0.1-py3-none-any.whl (1.8 MB)
   ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ 1.8/1.8 MB 41.9 MB/s eta 0:00:00
Installing collected packages: pip
  Attempting uninstall: pip
    Found existing installation: pip 24.0
    Uninstalling pip-24.0:
      Successfully uninstalled pip-24.0
Successfully installed pip-26.0.1
Collecting ruff (from -r requirements.txt (line 1))
  Downloading ruff-0.15.9-py3-none-manylinux_2_17_x86_64.manylinux2014_x86_64.whl.metadata (26 kB)
Collecting pytest (from -r requirements.txt (line 2))
  Downloading pytest-9.0.2-py3-none-any.whl.metadata (7.6 kB)
Collecting iniconfig>=1.0.1 (from pytest->-r requirements.txt (line 2))
  Downloading iniconfig-2.3.0-py3-none-any.whl.metadata (2.5 kB)
Collecting packaging>=22 (from pytest->-r requirements.txt (line 2))
  Downloading packaging-26.0-py3-none-any.whl.metadata (3.3 kB)
Collecting pluggy<2,>=1.5 (from pytest->-r requirements.txt (line 2))
  Downloading pluggy-1.6.0-py3-none-any.whl.metadata (4.8 kB)
Collecting pygments>=2.7.2 (from pytest->-r requirements.txt (line 2))
  Downloading pygments-2.20.0-py3-none-any.whl.metadata (2.5 kB)
Downloading ruff-0.15.9-py3-none-manylinux_2_17_x86_64.manylinux2014_x86_64.whl (11.3 MB)
   ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ 11.3/11.3 MB 59.7 MB/s  0:00:00
Downloading pytest-9.0.2-py3-none-any.whl (374 kB)
Downloading pluggy-1.6.0-py3-none-any.whl (20 kB)
Downloading iniconfig-2.3.0-py3-none-any.whl (7.5 kB)
Downloading packaging-26.0-py3-none-any.whl (74 kB)
Downloading pygments-2.20.0-py3-none-any.whl (1.2 MB)
   ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ 1.2/1.2 MB 65.3 MB/s  0:00:00
Installing collected packages: ruff, pygments, pluggy, packaging, iniconfig, pytest

Successfully installed iniconfig-2.3.0 packaging-26.0 pluggy-1.6.0 pygments-2.20.0 pytest-9.0.2 ruff-0.15.9
 ---> Removed intermediate container 827a7fdb9558
 ---> a5990ab7c367
Step 6/8 : COPY benchmark.py test_benchmark.py ./
 ---> 3d84b4ffe90c
Step 7/8 : USER appuser
 ---> Running in 5b5a9bd9c374
 ---> Removed intermediate container 5b5a9bd9c374
 ---> 74cd7beb7db9
Step 8/8 : CMD ["python", "benchmark.py"]
 ---> Running in 78b4aa2641e4
 ---> Removed intermediate container 78b4aa2641e4
 ---> af4974a67f8f
Successfully built af4974a67f8f
Successfully tagged inference-sandbox:latest
(nvidia) cchan@ubuntu-cchan:~/code/inference-sandbox$ 
```