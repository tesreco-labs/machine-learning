# Dockerizing a Python Flask Application on WSL Ubuntu

## Student Lab Guide: From Basic Dockerfile to Production-Oriented Container

---

## 1. Learning Objectives

By the end of this lab, students should be able to:

1. Understand the basic Docker image build process.
2. Create a Dockerfile for a Python Flask application.
3. Understand Docker images, containers, layers, and build context.
4. Build and tag Docker images.
5. Run containers and publish application ports.
6. Access an application running inside Docker on WSL from a Windows browser.
7. Understand the difference between `EXPOSE` and `-p`.
8. Troubleshoot container DNS and `pip install` failures.
9. Understand the Docker legacy builder deprecation warning.
10. Use BuildKit and Docker Buildx.
11. Understand Docker build cache behavior.
12. Reduce the Docker build context using `.dockerignore`.
13. Configure Python applications appropriately for containers.
14. Run container applications as a non-root user.
15. Understand Flask development server versus Gunicorn.
16. Build a production-oriented Docker image.

---

# 2. Environment Architecture

Our development environment is:

```text
Windows
│
├── Browser
├── VS Code
│
└── WSL Integration
        │
        ▼
WSL Ubuntu
│
├── Git
├── Python
├── Docker CLI
├── Docker Engine
│
└── Project Source Code
        │
        ▼
Docker Container
│
└── Python Flask Application
```

Recommended project location:

```text
~/projects/python-app
```

Avoid keeping active Linux development projects under:

```text
/mnt/c/Users/...
```

when Docker Engine, Git, Python, and other development tools run inside WSL.

The WSL native Linux filesystem generally provides better filesystem behavior and performance for Linux development workloads.

A symlink does not change the underlying filesystem.

For example:

```bash
ln -s /mnt/c/Users/username/projects ~/projects
```

still stores the actual project files on the Windows filesystem.

The symlink only provides another path to those files.

---

# 3. Example Flask Application

Assume the project structure is:

```text
python-app/
│
├── app.py
├── requirements.txt
└── Dockerfile
```

Example `app.py`:

```python
from flask import Flask

app = Flask(__name__)


@app.route("/")
def home():
    return "Hello from Flask running inside Docker!"


if __name__ == "__main__":
    app.run(
        host="0.0.0.0",
        port=5000
    )
```

The application must listen on:

```text
0.0.0.0
```

instead of:

```text
127.0.0.1
```

because the application must accept connections coming through the container network interface.

Example `requirements.txt`:

```text
Flask==3.0.3
```

---

# 4. Stage 1: Create the First Dockerfile

Create:

```text
Dockerfile
```

with:

```dockerfile
FROM python:3.12-slim

WORKDIR /app

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 5000

CMD ["python", "app.py"]
```

---

# 5. Understanding the Dockerfile Instructions

## FROM

```dockerfile
FROM python:3.12-slim
```

Defines the base image.

Our application image starts from the official Python runtime image.

Conceptually:

```text
Python Base Image
        │
        ▼
Install Dependencies
        │
        ▼
Copy Application
        │
        ▼
Configure Startup Command
        │
        ▼
Application Image
```

---

## WORKDIR

```dockerfile
WORKDIR /app
```

Creates or selects the working directory inside the image.

Subsequent commands operate relative to:

```text
/app
```

---

## COPY requirements.txt

```dockerfile
COPY requirements.txt .
```

Copies:

```text
requirements.txt
```

from the build context into:

```text
/app/requirements.txt
```

inside the image.

---

## RUN

```dockerfile
RUN pip install --no-cache-dir -r requirements.txt
```

Executes a command while building the image.

Python dependencies are installed into the image.

`--no-cache-dir` prevents pip's download cache from being stored in the resulting image layers.

---

## COPY Application Source Code

```dockerfile
COPY . .
```

Copies the project files from the build context into the image.

Conceptually:

```text
Host

python-app/
├── app.py
├── requirements.txt
└── Dockerfile

        │
        │ COPY . .
        ▼

Container Image

/app/
├── app.py
├── requirements.txt
└── Dockerfile
```

Later we will use `.dockerignore` to prevent unnecessary files from being copied.

---

## EXPOSE

```dockerfile
EXPOSE 5000
```

Documents that the containerized application expects to listen on port `5000`.

Important:

```text
EXPOSE does NOT publish the port.
```

Port publishing happens when starting the container.

---

## CMD

```dockerfile
CMD ["python", "app.py"]
```

Defines the default process started when the container runs.

The JSON array format is called the exec form.

Prefer:

```dockerfile
CMD ["python", "app.py"]
```

over:

```dockerfile
CMD python app.py
```

The exec form provides better signal handling and avoids running the application through an unnecessary shell.

---

# 6. Stage 2: Understand Docker Build Context

Build the image:

```bash
docker build -t python-app:1.0 .
```

The final:

```text
.
```

is important.

It represents the build context.

Conceptually:

```text
docker build -t python-app:1.0 .
                                   │
                                   ▼
                           Build Context
```

Docker can access files inside the build context when processing:

```dockerfile
COPY
```

and:

```dockerfile
ADD
```

instructions.

Without `.dockerignore`, unnecessary files may become part of the build context.

Examples:

```text
.git/
.venv/
__pycache__/
.env
test-results/
large datasets
temporary files
```

---

# 7. Is `-f Dockerfile` Required?

No.

When the file is named:

```text
Dockerfile
```

and is located at the default expected location relative to the build context, Docker automatically uses it.

These commands are equivalent:

```bash
docker build -t python-app:1.0 .
```

and:

```bash
docker build -f Dockerfile -t python-app:1.0 .
```

The command components are:

```text
docker build

-f Dockerfile
      │
      └── Dockerfile location

-t python-app:1.0
      │
      └── Image repository name and tag

.
│
└── Build context
```

Use `-f` when using another Dockerfile:

```bash
docker build \
    -f Dockerfile.dev \
    -t python-app:dev \
    .
```

or:

```bash
docker build \
    -f docker/Dockerfile \
    -t python-app:1.0 \
    .
```

---

# 8. Stage 3: Build the First Image

Run:

```bash
docker build -t python-app:1.0 .
```

Docker processes the Dockerfile instructions sequentially.

Example:

```text
Step 1/7 : FROM python:3.12-slim

Step 2/7 : WORKDIR /app

Step 3/7 : COPY requirements.txt .

Step 4/7 : RUN pip install --no-cache-dir -r requirements.txt

Step 5/7 : COPY . .

Step 6/7 : EXPOSE 5000

Step 7/7 : CMD ["python", "app.py"]
```

At the end:

```text
Successfully built <IMAGE_ID>
```

View the image:

```bash
docker images
```

Or:

```bash
docker image ls
```

---

# 9. Why Should We Tag Images?

If we build:

```bash
docker build .
```

Docker may create an image without a useful repository name and tag.

Example:

```text
REPOSITORY   TAG       IMAGE ID
<none>       <none>    6255b6481b38
```

This is commonly called a dangling image.

Prefer:

```bash
docker build -t python-app:1.0 .
```

Now:

```bash
docker images
```

may show:

```text
REPOSITORY   TAG       IMAGE ID
python-app   1.0       6255b6481b38
```

Image naming format:

```text
repository:tag
```

Example:

```text
python-app:1.0
```

---

# 10. Stage 4: Run the Container

Run:

```bash
docker run \
    --name python-app-container \
    -p 5000:5000 \
    python-app:1.0
```

The syntax:

```text
-p HOST_PORT:CONTAINER_PORT
```

Therefore:

```text
-p 5000:5000
```

means:

```text
Host Port 5000
       │
       ▼
Container Port 5000
```

---

# 11. Access the Application from Windows

Open the Windows browser and visit:

```text
http://localhost:5000
```

The request flow is:

```text
Windows Browser
       │
       │ localhost:5000
       ▼
Windows Networking
       │
       ▼
WSL Ubuntu
       │
       ▼
Docker Published Port
       │
       │ -p 5000:5000
       ▼
Container Port 5000
       │
       ▼
Flask Application
```

The application must listen on:

```text
0.0.0.0:5000
```

inside the container.

---

# 12. Why `0.0.0.0` Is Required

Consider:

```python
app.run(
    host="127.0.0.1",
    port=5000
)
```

This listens only on the container's loopback interface.

Docker port forwarding may not be able to reach the application.

Use:

```python
app.run(
    host="0.0.0.0",
    port=5000
)
```

Now the application listens on all container network interfaces.

Important:

```text
0.0.0.0
```

is a bind address.

You do not normally type:

```text
http://0.0.0.0:5000
```

into the Windows browser.

Use:

```text
http://localhost:5000
```

---

# 13. Verify the Running Container

List running containers:

```bash
docker ps
```

View logs:

```bash
docker logs python-app-container
```

Follow logs continuously:

```bash
docker logs -f python-app-container
```

Test from WSL:

```bash
curl http://localhost:5000
```

Inspect port mappings:

```bash
docker port python-app-container
```

Inspect the container:

```bash
docker inspect python-app-container
```

Stop the container:

```bash
docker stop python-app-container
```

Remove it:

```bash
docker rm python-app-container
```

Run and automatically remove the container when it stops:

```bash
docker run \
    --rm \
    --name python-app-container \
    -p 5000:5000 \
    python-app:1.0
```

---

# 14. Stage 5: Troubleshoot `pip install` DNS Errors

During the build, you may encounter:

```text
Temporary failure in name resolution
```

followed by:

```text
ERROR: Could not find a version that satisfies the requirement Flask==3.0.3
ERROR: No matching distribution found
```

Do not immediately assume that the package version is invalid.

The important error is:

```text
Temporary failure in name resolution
```

The build container cannot resolve the Python package repository hostname.

Conceptually:

```text
WSL Ubuntu
     │
     ▼
Docker Engine
     │
     ▼
Temporary Build Container
     │
     ▼
DNS Lookup
     │
     X
pypi.org
```

---

# 15. Diagnose DNS Problems Layer by Layer

## Test WSL DNS

```bash
getent hosts pypi.org
```

If this fails:

```text
WSL DNS problem
```

---

## Test Container DNS

```bash
docker run --rm python:3.12-slim \
    python -c \
    'import socket; print(socket.gethostbyname("pypi.org"))'
```

If WSL DNS works but container DNS fails:

```text
Docker container DNS problem
```

---

## Test HTTPS Connectivity

```bash
docker run --rm python:3.12-slim \
    python -c \
    'import urllib.request; print(urllib.request.urlopen("https://pypi.org/simple/flask/").status)'
```

If DNS works but HTTPS fails, investigate:

```text
Proxy
VPN
Firewall
Corporate network
TLS inspection
Certificate configuration
```

---

## Test Host Networking

For diagnosis:

```bash
docker build \
    --network=host \
    -t python-app:test \
    .
```

If the build works with host networking but fails with the default Docker build network, investigate Docker networking or DNS configuration.

Do not automatically use:

```text
--network=host
```

as a permanent solution without understanding the underlying networking problem.

---

# 16. Stage 6: Understand the Legacy Builder Warning

You may see:

```text
DEPRECATED: The legacy builder is deprecated and will be removed in a future release.

Install the buildx component to build images with BuildKit.
```

This means Docker is using the older image builder.

Conceptually:

```text
docker build
     │
     ▼
Legacy Builder
     │
     ▼
Docker Image
```

Modern Docker uses:

```text
docker build
     │
     ▼
Buildx CLI Integration
     │
     ▼
BuildKit
     │
     ▼
Docker Image
```

The warning does not necessarily mean that the current build failed.

It means the build engine being used is deprecated.

---

# 17. Explicitly Use the Legacy Builder

For demonstration or comparison:

```bash
DOCKER_BUILDKIT=0 docker build \
    -f Dockerfile \
    -t python-app:legacy \
    .
```

If the Dockerfile is named `Dockerfile`, this is also valid:

```bash
DOCKER_BUILDKIT=0 docker build \
    -t python-app:legacy \
    .
```

Do not configure the legacy builder as the permanent default for a new environment.

Use it only when:

```text
Teaching legacy Docker behavior
Troubleshooting an older environment
Comparing legacy builder and BuildKit
Maintaining older CI/CD systems temporarily
```

---

# 18. Stage 7: Check Docker Buildx

Run:

```bash
docker buildx version
```

Inspect builders:

```bash
docker buildx ls
```

If Buildx is unavailable on Ubuntu and Docker's official package repository is configured:

```bash
sudo apt update

sudo apt install docker-buildx-plugin
```

Verify:

```bash
docker buildx version
```

---

# 19. Build with Buildx

Build the image:

```bash
docker buildx build \
    --load \
    -t python-app:2.0 \
    .
```

Why:

```text
--load
```

?

Depending on the Buildx builder driver, Buildx may not automatically place the resulting image in the local Docker image store.

`--load` ensures the image becomes available through:

```bash
docker images
```

For normal local development, when Docker is correctly configured to use BuildKit:

```bash
docker build -t python-app:2.0 .
```

is usually sufficient.

---

# 20. Stage 8: Understand Docker Image Layers

Each major Dockerfile instruction creates an image layer.

Example:

```dockerfile
FROM python:3.12-slim

WORKDIR /app

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY . .
```

Conceptually:

```text
Layer 5    Application Source Code
---------------------------------

Layer 4    Python Dependencies
---------------------------------

Layer 3    requirements.txt
---------------------------------

Layer 2    Working Directory Metadata
---------------------------------

Layer 1    Python Base Image
---------------------------------
```

Docker can reuse unchanged layers.

This is called:

```text
Docker Build Cache
```

---

# 21. Stage 9: Optimize Dependency Layer Caching

Good Dockerfile:

```dockerfile
COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY . .
```

Suppose:

```text
requirements.txt did not change
app.py changed
```

Docker may reuse the dependency installation layer.

Conceptually:

```text
requirements.txt unchanged

        │
        ▼

Reuse pip install layer

        │
        ▼

Copy changed application source

        │
        ▼

Faster build
```

Bad Dockerfile:

```dockerfile
COPY . .

RUN pip install --no-cache-dir -r requirements.txt
```

Now any source-code modification may invalidate the dependency installation layer.

---

# 22. Stage 10: Add `.dockerignore`

Create:

```text
.dockerignore
```

Example:

```text
.git
.gitignore

__pycache__
*.py[cod]

.venv
venv

.pytest_cache
.mypy_cache

.env
.env.*

dist
build

README.md
```

Why?

Without `.dockerignore`:

```text
Project Directory
       │
       │ docker build .
       ▼
Entire Build Context
       │
       ▼
Docker Builder
```

With `.dockerignore`:

```text
Project Directory
       │
       ▼
Remove unnecessary files
       │
       ▼
Smaller Build Context
       │
       ▼
Docker Builder
```

Benefits:

```text
Smaller build context
Faster file transfer
Reduced cache invalidation
Lower chance of copying secrets
Cleaner container images
```

Important:

`.dockerignore` affects the build context.

It is not a replacement for:

```text
.gitignore
```

---

# 23. Stage 11: Add Python Container Environment Variables

Add:

```dockerfile
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1
```

## PYTHONDONTWRITEBYTECODE

Prevents Python from writing:

```text
.pyc
```

bytecode files.

This helps keep the container filesystem cleaner.

---

## PYTHONUNBUFFERED

Disables buffering of Python stdout and stderr.

Application logs appear immediately through:

```bash
docker logs
```

This is useful for containerized applications.

---

# 24. Stage 12: Pin the Base OS Family

Instead of:

```dockerfile
FROM python:3.12-slim
```

use:

```dockerfile
FROM python:3.12-slim-bookworm
```

This makes the Debian release family explicit.

Tag selection model:

```text
python
   │
   ├── Python Version
   │
   ├── Image Variant
   │
   └── OS Distribution Release
```

Example:

```text
python:3.12-slim-bookworm
        │     │
        │     └── Debian Bookworm
        │
        └── Slim Image Variant
```

For stronger production reproducibility, organizations may pin the image digest:

```dockerfile
FROM python:3.12-slim-bookworm@sha256:<IMAGE_DIGEST>
```

Digest pinning should be combined with a controlled process for updating base images when security fixes become available.

---

# 25. Stage 13: Understand the pip Root Warning

During the build, you may see:

```text
WARNING: Running pip as the 'root' user can result in broken permissions...
```

During container image builds, installing Python packages into the image as root is common.

The more important runtime security question is:

```text
Which user runs the application process?
```

Current behavior:

```text
Container Starts
      │
      ▼
Application Runs as root
```

Preferred:

```text
Container Starts
      │
      ▼
Application Runs as appuser
```

---

# 26. Stage 14: Create a Non-Root User

Add:

```dockerfile
RUN useradd \
    --create-home \
    --uid 10001 \
    appuser
```

Then copy the application:

```dockerfile
COPY --chown=appuser:appuser . .
```

Finally:

```dockerfile
USER appuser
```

Now the application process runs as:

```text
appuser
```

instead of:

```text
root
```

---

# 27. Why Use a Fixed UID?

We use:

```text
10001
```

instead of relying only on an automatically assigned UID.

A fixed UID provides predictable runtime identity.

This can be useful when working with:

```text
Container platforms
Kubernetes security policies
Mounted volumes
Filesystem permissions
Security scanners
Runtime policies
```

---

# 28. Stage 15: Improved Dockerfile

```dockerfile
FROM python:3.12-slim-bookworm

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

COPY requirements.txt .

RUN pip install \
    --no-cache-dir \
    -r requirements.txt

RUN useradd \
    --create-home \
    --uid 10001 \
    appuser

COPY --chown=appuser:appuser . .

USER appuser

EXPOSE 5000

CMD ["python", "app.py"]
```

Build:

```bash
docker build \
    -t python-app:2.0 \
    .
```

Run:

```bash
docker run \
    --rm \
    --name python-app-container \
    -p 5000:5000 \
    python-app:2.0
```

Open from Windows:

```text
http://localhost:5000
```

---

# 29. Stage 16: Restrict Published Ports for Local Development

This command:

```bash
docker run \
    -p 5000:5000 \
    python-app:2.0
```

typically publishes the port on all host interfaces.

When only the local Windows browser needs access, consider:

```bash
docker run \
    --rm \
    --name python-app-container \
    -p 127.0.0.1:5000:5000 \
    python-app:2.0
```

Conceptually:

```text
-p 5000:5000

Host Interfaces
      │
      ▼
Port 5000
```

versus:

```text
-p 127.0.0.1:5000:5000

Localhost Only
      │
      ▼
Port 5000
```

For local development, restricting the published port to localhost reduces unnecessary network exposure.

---

# 30. Stage 17: Understand the Flask Development Server

Running:

```bash
python app.py
```

may start Flask's built-in development server.

This is suitable for:

```text
Learning
Development
Testing
Local demonstrations
```

It is not intended to be the production application server.

Production deployments commonly place a WSGI application server between the container runtime and Flask application.

Example:

```text
Client
   │
   ▼
Load Balancer / Reverse Proxy
   │
   ▼
Container
   │
   ▼
Gunicorn
   │
   ├── Worker
   ├── Worker
   └── Worker
          │
          ▼
    Flask Application
```

---

# 31. Stage 18: Add Gunicorn

Add Gunicorn to:

```text
requirements.txt
```

Example:

```text
Flask==3.0.3
gunicorn==<PINNED_VERSION>
```

Install dependencies during the image build:

```dockerfile
RUN pip install \
    --no-cache-dir \
    -r requirements.txt
```

Replace:

```dockerfile
CMD ["python", "app.py"]
```

with:

```dockerfile
CMD [
    "gunicorn",
    "--bind",
    "0.0.0.0:5000",
    "--workers",
    "2",
    "app:app"
]
```

The JSON array is shown across multiple lines for readability.

The meaning of:

```text
app:app
```

is:

```text
app : app
 │     │
 │     └── Flask application object
 │
 └── Python module app.py
```

Given:

```python
app = Flask(__name__)
```

inside:

```text
app.py
```

the Gunicorn application target is:

```text
app:app
```

---

# 32. Do Not Blindly Set Gunicorn Worker Count

This example uses:

```text
--workers 2
```

for teaching purposes.

The correct worker configuration depends on:

```text
CPU limits
Memory limits
Request workload
Application behavior
Concurrency model
Deployment platform
Performance testing
```

Production worker counts should be selected using measurement and workload testing.

---

# 33. Stage 19: Production-Oriented Dockerfile

```dockerfile
FROM python:3.12-slim-bookworm

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

COPY requirements.txt .

RUN pip install \
    --no-cache-dir \
    -r requirements.txt

RUN useradd \
    --create-home \
    --uid 10001 \
    appuser

COPY --chown=appuser:appuser . .

USER appuser

EXPOSE 5000

CMD [
    "gunicorn",
    "--bind",
    "0.0.0.0:5000",
    "--workers",
    "2",
    "app:app"
]
```

Build:

```bash
docker build \
    -t python-app:3.0 \
    .
```

Run:

```bash
docker run \
    --rm \
    --name python-app-container \
    -p 127.0.0.1:5000:5000 \
    python-app:3.0
```

Access from the Windows browser:

```text
http://localhost:5000
```

---

# 34. Stage 20: Run with Additional Runtime Restrictions

After verifying that the application works correctly, experiment with:

```bash
docker run \
    --rm \
    --name python-app-container \
    --read-only \
    --tmpfs /tmp \
    --cap-drop=ALL \
    --security-opt=no-new-privileges \
    -p 127.0.0.1:5000:5000 \
    python-app:3.0
```

These options introduce additional runtime restrictions.

---

## `--read-only`

```text
--read-only
```

makes the container root filesystem read-only.

The application must not require arbitrary writes to the image filesystem.

---

## `--tmpfs /tmp`

Provides a temporary writable filesystem at:

```text
/tmp
```

Data is stored temporarily and disappears when the container is removed.

---

## `--cap-drop=ALL`

Drops Linux capabilities from the container.

Applications requiring specific capabilities must explicitly add only those capabilities they need.

---

## `--security-opt=no-new-privileges`

Prevents container processes from gaining additional privileges through mechanisms such as setuid binaries.

---

# 35. Stage 21: Inspect the Final Image

List images:

```bash
docker image ls
```

Inspect image metadata:

```bash
docker image inspect python-app:3.0
```

View image history:

```bash
docker history python-app:3.0
```

Check configured user:

```bash
docker image inspect \
    --format '{{.Config.User}}' \
    python-app:3.0
```

Run:

```bash
docker run \
    --rm \
    python-app:3.0 \
    id
```

Expected result should show the non-root user.

Inspect Python version:

```bash
docker run \
    --rm \
    python-app:3.0 \
    python --version
```

Inspect installed Python packages:

```bash
docker run \
    --rm \
    python-app:3.0 \
    pip list
```

---

# 36. Stage 22: Understand Image Tags and Image IDs

Build:

```bash
docker build \
    -t python-app:1.0 \
    .
```

Later:

```bash
docker build \
    -t python-app:2.0 \
    .
```

List images:

```bash
docker images
```

Example:

```text
REPOSITORY   TAG       IMAGE ID
python-app   1.0       abc123
python-app   2.0       def456
```

Tags are human-readable references.

Image IDs identify image objects stored by Docker.

Multiple tags can point to the same image.

Example:

```bash
docker tag \
    python-app:3.0 \
    python-app:latest
```

Now:

```text
python-app:3.0
python-app:latest
```

may reference the same image.

---

# 37. Stage 23: Clean Up Docker Resources

Remove stopped containers:

```bash
docker container prune
```

Remove dangling images:

```bash
docker image prune
```

Inspect Docker disk usage:

```bash
docker system df
```

Remove unused build cache:

```bash
docker builder prune
```

Be careful with:

```bash
docker system prune
```

It removes multiple categories of unused Docker resources.

Always inspect what will be removed before using aggressive cleanup options in important environments.

---

# 38. Common Mistakes

## Mistake 1: Application listens on localhost inside the container

Incorrect:

```python
app.run(host="127.0.0.1")
```

Correct:

```python
app.run(host="0.0.0.0")
```

---

## Mistake 2: Assuming `EXPOSE` publishes the port

Incorrect assumption:

```text
EXPOSE 5000 means Windows can access port 5000.
```

Correct:

```text
EXPOSE documents the intended container port.

docker run -p publishes the port.
```

---

## Mistake 3: Forgetting the build context

Incorrect:

```bash
docker build -t python-app:1.0
```

Correct:

```bash
docker build -t python-app:1.0 .
```

---

## Mistake 4: Copying the entire application before installing dependencies

Less efficient:

```dockerfile
COPY . .

RUN pip install -r requirements.txt
```

Better:

```dockerfile
COPY requirements.txt .

RUN pip install -r requirements.txt

COPY . .
```

---

## Mistake 5: Assuming a symlink moves files into the Linux filesystem

Example:

```bash
ln -s /mnt/c/Users/username/projects ~/projects
```

The files still physically exist on the Windows filesystem.

---

## Mistake 6: Using the Flask development server in production

Development:

```dockerfile
CMD ["python", "app.py"]
```

Production-oriented:

```dockerfile
CMD [
    "gunicorn",
    "--bind",
    "0.0.0.0:5000",
    "--workers",
    "2",
    "app:app"
]
```

---

## Mistake 7: Automatically assuming `No matching distribution found` means the package version is invalid

Always inspect earlier error messages.

Example:

```text
Temporary failure in name resolution
```

indicates a network or DNS problem.

---

## Mistake 8: Running the application as root unnecessarily

Prefer:

```dockerfile
USER appuser
```

after installing dependencies and preparing filesystem permissions.

---

# 39. Final Recommended Project Structure

```text
python-app/
│
├── app.py
├── requirements.txt
├── Dockerfile
├── .dockerignore
├── tests/
│
└── application-source-files/
```

For WSL development:

```text
~/projects/python-app
```

Open using VS Code from WSL:

```bash
cd ~/projects/python-app

code .
```

Open the current WSL directory in Windows Explorer:

```bash
explorer.exe .
```

---

# 40. Complete Development Workflow

```text
1. Create Flask Application

        │
        ▼

2. Create requirements.txt

        │
        ▼

3. Create Basic Dockerfile

        │
        ▼

4. Build Image

docker build -t python-app:1.0 .

        │
        ▼

5. Run Container

docker run -p 5000:5000 python-app:1.0

        │
        ▼

6. Open Windows Browser

http://localhost:5000

        │
        ▼

7. Diagnose Build and Networking Problems

        │
        ▼

8. Understand Legacy Builder Warning

        │
        ▼

9. Enable BuildKit / Buildx

        │
        ▼

10. Add .dockerignore

        │
        ▼

11. Optimize Layer Caching

        │
        ▼

12. Configure Python Container Environment

        │
        ▼

13. Pin Base OS Family

        │
        ▼

14. Create Non-Root User

        │
        ▼

15. Replace Development Server with Gunicorn

        │
        ▼

16. Add Runtime Security Restrictions

        │
        ▼

17. Inspect, Test, Scan, and Maintain the Image
```

---

# 41. Student Exercises

## Exercise 1

Build the basic Docker image:

```bash
docker build \
    -t python-app:1.0 \
    .
```

Run the container and access it from Windows.

---

## Exercise 2

Run the container without:

```text
-p 5000:5000
```

Try accessing:

```text
http://localhost:5000
```

Explain why the application is not reachable.

---

## Exercise 3

Change:

```python
host="0.0.0.0"
```

to:

```python
host="127.0.0.1"
```

Rebuild and run the container.

Explain the networking behavior.

---

## Exercise 4

Build using the legacy builder:

```bash
DOCKER_BUILDKIT=0 docker build \
    -t python-app:legacy \
    .
```

Record the build output.

---

## Exercise 5

Build using Buildx:

```bash
docker buildx build \
    --load \
    -t python-app:buildkit \
    .
```

Compare the output with the legacy builder.

---

## Exercise 6

Modify only:

```text
app.py
```

Rebuild the image.

Identify which Docker build steps use cache.

---

## Exercise 7

Modify:

```text
requirements.txt
```

Rebuild.

Explain why the dependency installation layer runs again.

---

## Exercise 8

Create a large temporary file:

```bash
dd if=/dev/zero \
    of=large-file.dat \
    bs=1M \
    count=100
```

Build the image.

Observe the build context.

Add:

```text
large-file.dat
```

to `.dockerignore`.

Build again and compare the behavior.

Remove the test file afterward.

---

## Exercise 9

Inspect the user running inside the basic container:

```bash
docker run \
    --rm \
    python-app:1.0 \
    id
```

Then add the non-root user configuration and repeat the test.

Compare the results.

---

## Exercise 10

Replace the Flask development server with Gunicorn.

Run:

```bash
docker logs python-app-container
```

Identify the Gunicorn master and worker startup messages.

---

## Exercise 11

Run the container with:

```text
--read-only
```

Determine whether the application still works.

If it fails, identify which directory requires write access.

---

## Exercise 12

Compare these base images:

```text
python:3.12
python:3.12-slim
python:3.12-slim-bookworm
python:3.12-alpine
```

Research and explain:

```text
Base operating system
Image size
C library
Package manager
Native Python dependency compatibility
Recommended use cases
```

---

# 42. Key Takeaways

1. A Dockerfile defines how an image is built.

2. A Docker image is an immutable application packaging artifact.

3. A container is a running instance of an image.

4. The final argument to `docker build` is the build context.

5. `-f` selects the Dockerfile.

6. `-t` assigns an image repository name and tag.

7. `EXPOSE` documents a container port.

8. `docker run -p` publishes a container port.

9. Containerized web applications must generally listen on `0.0.0.0`.

10. WSL localhost forwarding normally allows Windows browsers to access services published from WSL.

11. DNS failures during `pip install` can produce misleading package-resolution errors.

12. Diagnose networking problems layer by layer.

13. Docker's legacy builder is deprecated.

14. BuildKit is the modern Docker build backend.

15. Buildx provides extended BuildKit build functionality.

16. Dockerfile instruction ordering affects build cache efficiency.

17. `.dockerignore` reduces unnecessary build context.

18. Python container logs should be written directly to stdout and stderr.

19. Production container applications should generally run as non-root.

20. Flask's development server is not intended for production workloads.

21. Gunicorn is one option for serving Flask WSGI applications.

22. Smaller images are not automatically more secure images.

23. Container security includes image selection, dependency management, non-root execution, runtime restrictions, scanning, patching, and supply-chain controls.

24. A symlink changes the path used to reach files but does not move those files from the Windows filesystem into the WSL Linux filesystem.

25. Container optimization should be introduced progressively: first make the application work, then improve reproducibility, performance, observability, security, and maintainability.

---

# End of Lab Guide
