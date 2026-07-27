## Dockerizing a Python Flask Application on WSL Ubuntu

### Student Lab Guide: From Basic Dockerfile to Production-Oriented Container

---

### 1. Learning Objectives

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

### 2. Environment Architecture

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

---

### 3. Example Flask Application

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
### 4. Understanding the Dockerfile

A Dockerfile is a text file that contains instructions for building a Docker image.

Think of it as a recipe that tells Docker how to package your application.

```dockerfile
FROM python:3.12-slim

WORKDIR /app

COPY requirements.txt .

RUN pip install -r requirements.txt

COPY . .

EXPOSE 5000

CMD ["python", "app.py"]
```

Let's understand each instruction.

### FROM

```dockerfile
FROM python:3.12-slim
```

Specifies the base image that already contains Python.

---

### WORKDIR

```dockerfile
WORKDIR /app
```

Sets the working directory inside the container.

---

### COPY

```dockerfile
COPY requirements.txt .
```

Copies the dependency file into the image.

Later,

```dockerfile
COPY . .
```

copies the remaining application files.

---

### RUN

```dockerfile
RUN pip install -r requirements.txt
```

Executes commands while building the image.

Here it installs the required Python packages.

---

### EXPOSE

```dockerfile
EXPOSE 5000
```

Documents that the application listens on port 5000.

> **Note:** `EXPOSE` does not publish the port.

---

### CMD

```dockerfile
CMD ["python", "app.py"]
```
Specifies the default command executed when the container starts.
---
## 5. Build the Docker Image

Run:

```bash
docker build -t python-app:v1 .
```

Let's understand the command.

```text
docker build
      │
      ├── -t
      │      Image name and tag
      │
      └── .
            Build context
```

After the build completes,

verify the image.

```bash
docker images
```
---
## 6. Run the Container

```bash
docker run --name python-app \
-p 5000:5000 \
python-app:v1
```

Open

```
http://localhost:5000
```

If everything is correct, the application should be accessible from your browser.
---
## 7. Exercises

### Exercise 1

Build the image with tag

```
python-app:v2
```

---

### Exercise 2

Run the container using

```
-p 8080:5000
```

Access

```
http://localhost:8080
```

---

### Exercise 3

Stop the container.

---

### Exercise 4

Remove the container.

---

### Exercise 5
Delete the image.

---
