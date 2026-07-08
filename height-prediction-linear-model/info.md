# Prerequisites for Dockerizing the Python Application
Purpose

## Before starting the Dockerizing session, make sure the existing Python application works correctly using the traditional development approach.

Until now, the application has been developed and executed directly on your system:

Application Source Code
        │
        ▼
Python Installed on System
        │
        ▼
Python Virtual Environment
        │
        ▼
Project Dependencies Installed Locally
        │
        ▼
Run Python Application

During the Dockerizing session, we will move the application and its runtime dependencies into a container:

Application Source Code
        │
        ▼
Docker Image
        │
        ├── Python Runtime
        ├── Project Dependencies
        └── Application Source Code
                │
                ▼
          Docker Container

## Complete the following steps before attending the session.

1. Required Environment

Students should have:

Windows 10 or Windows 11.
WSL installed.
Ubuntu 22.04 installed in WSL.
Git installed inside WSL Ubuntu.
Docker Engine or Docker Desktop configured to work with WSL.
The project source code available inside WSL.
The existing Python application working correctly before Dockerization.

Verify the Ubuntu version:

lsb_release -a

Expected version:

Ubuntu 22.04
2. Open WSL Ubuntu

Open PowerShell or Windows Terminal.

Run:

wsl

Verify that you are inside Linux:

uname -a

Check the current directory:

pwd
3. Keep the Project Inside the WSL Filesystem

Create a directory for projects:

mkdir -p ~/projects

Move to the directory:

cd ~/projects

Recommended project location:

~/projects/python-app

Avoid keeping the active project under:

/mnt/c/Users/...

when Git, Python, and Docker Engine are running inside WSL.

A symlink pointing to /mnt/c/Users/... does not move the files into the Linux filesystem. The actual files still remain on the Windows filesystem.

4. Verify Git Installation

Run:

git --version

If Git is not installed:

sudo apt update

sudo apt install git -y

Verify again:

git --version
5. Get the Project Source Code

If you have already cloned the repository, move to the project directory:

cd ~/projects/python-app

Otherwise, clone the project:

cd ~/projects

git clone <PROJECT_REPOSITORY_URL>

cd <PROJECT_DIRECTORY>

Verify the project files:

ls -la
6. Verify the Git Repository

Run:

git status

Check the configured remote repository:

git remote -v

Check the current branch:

git branch --show-current

Make sure you have the latest required application code before the session:

git pull








# Python Flask Application - Docker Guide

## Build Docker Image

Run the command from the project directory containing the `Dockerfile`:

```bash
docker build -f Dockerfile -t python-app:1.0 .
```

## Run Docker Container

```bash
docker run \
  --name python-app-container \
  -p 5000:5000 \
  python-app:1.0
```

## Access the Application

Open the application in the Windows browser:

```text
http://localhost:5000
```

The Flask application inside the container must listen on:

```text
0.0.0.0:5000
```

## Run Container in Detached Mode

```bash
docker run \
  -d \
  --name python-app-container \
  -p 5000:5000 \
  python-app:1.0
```

## View Running Containers

```bash
docker ps
```

## View Container Logs

```bash
docker logs python-app-container
```

Follow logs continuously:

```bash
docker logs -f python-app-container
```

## Stop the Container

```bash
docker stop python-app-container
```

## Start the Existing Container

```bash
docker start python-app-container
```

## Remove the Container

The container must be stopped before removing it:

```bash
docker stop python-app-container

docker rm python-app-container
```

Or force remove the container:

```bash
docker rm -f python-app-container
```

## Remove the Docker Image

```bash
docker rmi python-app:1.0
```

## Quick Development Workflow

Build the image:

```bash
docker build -f Dockerfile -t python-app:1.0 .
```

Run the container:

```bash
docker run \
  --rm \
  --name python-app-container \
  -p 5000:5000 \
  python-app:1.0
```

Open in the Windows browser:

```text
http://localhost:5000
```

The `--rm` option automatically removes the container when it stops.


