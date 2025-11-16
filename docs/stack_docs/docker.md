# Docker Documentation

**Official Docs:** https://docs.docker.com/

## Overview
Docker is a platform for developing, shipping, and running applications in containers. We use Docker for containerizing both the API and frontend.

## Key Features
- Containerization
- Reproducible environments
- Multi-stage builds
- Image layering
- Container orchestration support

## Basic Concepts

### Images
Read-only templates with instructions for creating containers.

### Containers
Runnable instances of images.

### Dockerfile
Text file with instructions to build an image.

## Dockerfile Basics

### Simple Dockerfile
```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["python", "app.py"]
```

### Multi-Stage Build
```dockerfile
# Build stage
FROM node:18-alpine as builder
WORKDIR /app
COPY package*.json ./
RUN npm ci
COPY . .
RUN npm run build

# Production stage
FROM nginx:alpine
COPY --from=builder /app/dist /usr/share/nginx/html
EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
```

## Common Dockerfile Instructions

### FROM
Base image to build upon.
```dockerfile
FROM python:3.11-slim
FROM node:18-alpine
FROM ubuntu:22.04
```

### WORKDIR
Set working directory.
```dockerfile
WORKDIR /app
```

### COPY
Copy files from host to container.
```dockerfile
COPY requirements.txt .
COPY src/ ./src/
COPY . .
```

### RUN
Execute commands during build.
```dockerfile
RUN apt-get update && apt-get install -y git
RUN pip install -r requirements.txt
RUN npm ci
```

### CMD
Default command when container starts.
```dockerfile
CMD ["python", "app.py"]
CMD ["npm", "start"]
```

### ENTRYPOINT
Configure container as executable.
```dockerfile
ENTRYPOINT ["python"]
CMD ["app.py"]
```

### ENV
Set environment variables.
```dockerfile
ENV PORT=8080
ENV NODE_ENV=production
```

### EXPOSE
Document which ports the container listens on.
```dockerfile
EXPOSE 8080
EXPOSE 80 443
```

### ARG
Build-time variables.
```dockerfile
ARG VITE_API_URL=http://localhost:8000
ENV VITE_API_URL=$VITE_API_URL
```

## Docker Commands

### Build Image
```bash
# Basic build
docker build -t myapp:latest .

# With build args
docker build --build-arg VITE_API_URL=https://api.com -t myapp .

# Specify Dockerfile
docker build -f Dockerfile.prod -t myapp .

# No cache
docker build --no-cache -t myapp .
```

### Run Container
```bash
# Basic run
docker run myapp

# Detached mode
docker run -d myapp

# With port mapping
docker run -p 8080:8080 myapp

# With environment variables
docker run -e DATABASE_URL=postgresql://... myapp

# With volume mount
docker run -v $(pwd):/app myapp

# Interactive shell
docker run -it myapp /bin/bash

# Remove after exit
docker run --rm myapp

# Name container
docker run --name my-container myapp
```

### Container Management
```bash
# List running containers
docker ps

# List all containers
docker ps -a

# Stop container
docker stop container_id

# Start container
docker start container_id

# Restart container
docker restart container_id

# Remove container
docker rm container_id

# Remove all stopped containers
docker container prune
```

### Image Management
```bash
# List images
docker images

# Remove image
docker rmi image_id

# Remove unused images
docker image prune

# Tag image
docker tag myapp:latest myapp:v1.0

# Save image to file
docker save myapp:latest > myapp.tar

# Load image from file
docker load < myapp.tar
```

### Logs & Debugging
```bash
# View logs
docker logs container_id

# Follow logs
docker logs -f container_id

# Last 100 lines
docker logs --tail 100 container_id

# Execute command in running container
docker exec container_id ls -la

# Interactive shell in running container
docker exec -it container_id /bin/bash

# Inspect container
docker inspect container_id

# Container stats
docker stats container_id
```

## Docker Compose

### docker-compose.yml
```yaml
version: '3.8'

services:
  api:
    build:
      context: ./apps/agenticCompany
      dockerfile: Dockerfile
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=postgresql://user:pass@db:5432/dbname
      - ANTHROPIC_API_KEY=${ANTHROPIC_API_KEY}
    depends_on:
      - db
    volumes:
      - ./apps/agenticCompany:/app
    restart: unless-stopped

  frontend:
    build:
      context: ./apps/seed-planter-frontend
      dockerfile: Dockerfile
      args:
        - VITE_API_URL=http://localhost:8000
    ports:
      - "80:80"
    depends_on:
      - api
    restart: unless-stopped

  db:
    image: postgres:15-alpine
    environment:
      - POSTGRES_USER=user
      - POSTGRES_PASSWORD=password
      - POSTGRES_DB=dbname
    volumes:
      - postgres_data:/var/lib/postgresql/data
    ports:
      - "5432:5432"

volumes:
  postgres_data:
```

### Docker Compose Commands
```bash
# Start services
docker-compose up

# Start in background
docker-compose up -d

# Build and start
docker-compose up --build

# Stop services
docker-compose down

# Stop and remove volumes
docker-compose down -v

# View logs
docker-compose logs

# Follow logs
docker-compose logs -f api

# Execute command
docker-compose exec api python manage.py migrate

# Scale service
docker-compose up --scale api=3
```

## Best Practices

### 1. Use Specific Base Images
```dockerfile
# Good
FROM python:3.11-slim

# Avoid
FROM python:latest
```

### 2. Minimize Layers
```dockerfile
# Good - single layer
RUN apt-get update && \
    apt-get install -y git curl && \
    rm -rf /var/lib/apt/lists/*

# Avoid - multiple layers
RUN apt-get update
RUN apt-get install -y git
RUN apt-get install -y curl
```

### 3. Use .dockerignore
```
# .dockerignore
node_modules
.git
.env
*.log
__pycache__
.pytest_cache
dist
build
```

### 4. Multi-Stage Builds
Reduce final image size by separating build and runtime stages.

### 5. Don't Run as Root
```dockerfile
RUN adduser --disabled-password --gecos '' appuser
USER appuser
```

### 6. Use Build Cache
Order instructions from least to most frequently changing.

```dockerfile
# Good - dependencies cached
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .

# Avoid - cache invalidated often
COPY . .
RUN pip install -r requirements.txt
```

### 7. Health Checks
```dockerfile
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8080/health || exit 1
```

## Container Registry

### Docker Hub
```bash
# Login
docker login

# Tag image
docker tag myapp:latest username/myapp:latest

# Push image
docker push username/myapp:latest

# Pull image
docker pull username/myapp:latest
```

### Google Container Registry (GCR)
```bash
# Configure Docker for GCR
gcloud auth configure-docker

# Tag image
docker tag myapp gcr.io/project-id/myapp:latest

# Push image
docker push gcr.io/project-id/myapp:latest
```

## Networking

### Bridge Network (Default)
```bash
docker network create my-network
docker run --network my-network myapp
```

### Connect Containers
```bash
# Create network
docker network create app-network

# Run containers on same network
docker run --network app-network --name api myapi
docker run --network app-network --name frontend myfrontend

# Frontend can access API at http://api:8000
```

## Volumes

### Named Volumes
```bash
# Create volume
docker volume create mydata

# Use volume
docker run -v mydata:/app/data myapp

# List volumes
docker volume ls

# Remove volume
docker volume rm mydata
```

### Bind Mounts
```bash
# Mount host directory
docker run -v $(pwd):/app myapp

# Read-only mount
docker run -v $(pwd):/app:ro myapp
```

## Security

### Scan Images
```bash
docker scan myapp:latest
```

### Run with Limited Resources
```bash
docker run --memory="512m" --cpus="1.0" myapp
```

### Use Secrets
```bash
# Docker Compose with secrets
docker-compose --env-file .env.production up
```

## Troubleshooting

### Container Won't Start
```bash
# Check logs
docker logs container_id

# Run with interactive shell
docker run -it myapp /bin/bash
```

### Out of Disk Space
```bash
# Clean up everything
docker system prune -a

# Remove unused volumes
docker volume prune
```

### Network Issues
```bash
# Inspect network
docker network inspect bridge

# Check container IP
docker inspect -f '{{range.NetworkSettings.Networks}}{{.IPAddress}}{{end}}' container_id
```

## Resources
- Official Docs: https://docs.docker.com/
- Best Practices: https://docs.docker.com/develop/dev-best-practices/
- Dockerfile Reference: https://docs.docker.com/engine/reference/builder/
- Docker Hub: https://hub.docker.com/

## Version Used in SeedGPT
```
Docker Engine 20+
Docker Compose 2+
```
