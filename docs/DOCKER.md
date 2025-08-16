# 🐳 Docker Setup & Usage

This document explains how to run Evolve Payments Platform using Docker for development and production environments.

## 📋 Prerequisites

- [Docker](https://docs.docker.com/get-docker/) (20.10+)
- [Docker Compose](https://docs.docker.com/compose/install/) (2.0+)

## 🚀 Quick Start

### Option 1: Using Pre-built Images (Recommended)

```bash
# Pull the latest image from GitHub Container Registry
docker pull ghcr.io/joynyayieka/evolve-payments-platform:latest

# Run with basic setup
docker run -p 8000:8000 ghcr.io/joynyayieka/evolve-payments-platform:latest
```

### Option 2: Build Locally

```bash
# Clone the repository
git clone https://github.com/JoyNyayieka/evolve-payments-platform.git
cd evolve-payments-platform

# Build and run with Docker Compose (includes database)
docker-compose up --build
```

## 🛠️ Development Setup

### Full Development Environment
```bash
# Start all services (web, database, redis)
docker-compose up -d

# View logs
docker-compose logs -f web

# Access the application
# http://localhost:8000

# Stop services
docker-compose down
```

### Development with Live Reload
The development setup mounts your local code into the container, so changes are reflected immediately without rebuilding.

```bash
# Make code changes locally
# The container automatically picks up changes

# If you add new dependencies, rebuild:
docker-compose up --build
```

## 🏗️ Available Images

### Image Tags
- `latest` - Latest stable release
- `dev` - Development branch
- `v0.1.1` - Specific version tags
- `main` - Main branch builds

### Multi-Architecture Support
Images are built for:
- `linux/amd64` (Intel/AMD 64-bit)
- `linux/arm64` (Apple Silicon, ARM servers)

## 🔧 Configuration

### Environment Variables
```bash
# Required for production
DATABASE_URL=postgresql://user:pass@host:5432/dbname
SECRET_KEY=your-secret-key
DEBUG=False

# Optional
REDIS_URL=redis://localhost:6379/0
ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com
```

### Using Environment Files
```bash
# Create .env file
cp .env.example .env

# Edit configuration
nano .env

# Run with environment file
docker-compose --env-file .env up
```

## 🐘 Database Setup

### PostgreSQL (Recommended for Production)
```yaml
# docker-compose.yml
services:
  db:
    image: postgres:15-alpine
    environment:
      POSTGRES_DB: evolve_payments
      POSTGRES_USER: postgres
      POSTGRES_PASSWORD: secure_password
```

### SQLite (Development Only)
The default setup uses SQLite for simplicity in development.

## 🔐 Security Considerations

### Production Deployment
```bash
# Use specific version tags, not 'latest'
docker pull ghcr.io/joynyayieka/evolve-payments-platform:v0.1.1

# Run with limited privileges
docker run --user 1000:1000 \
  -p 8000:8000 \
  --read-only \
  --tmpfs /tmp \
  ghcr.io/joynyayieka/evolve-payments-platform:v0.1.1
```

### Health Checks
```bash
# Check container health
docker ps
# Look for "healthy" status

# Manual health check
curl http://localhost:8000/
```

## 🚀 CI/CD Integration

### GitHub Actions
The repository includes automated Docker builds:
- **On Push**: Builds and pushes images to registry
- **On Release**: Creates tagged, security-scanned images
- **On PR**: Tests Docker build without pushing

### Security Scanning
Images are automatically scanned for vulnerabilities using Trivy.

## 📊 Monitoring & Logs

### View Logs
```bash
# All services
docker-compose logs

# Specific service
docker-compose logs web

# Follow logs in real-time
docker-compose logs -f web
```

### Container Stats
```bash
# Resource usage
docker stats

# Detailed container info
docker inspect <container_name>
```

## 🛠️ Troubleshooting

### Common Issues

**Port Already in Use:**
```bash
# Find what's using port 8000
lsof -i :8000

# Use different port
docker run -p 8080:8000 ghcr.io/joynyayieka/evolve-payments-platform:latest
```

**Database Connection Issues:**
```bash
# Check if database container is running
docker-compose ps

# Reset database
docker-compose down -v
docker-compose up -d
```

**Permission Issues:**
```bash
# Fix file permissions
sudo chown -R $USER:$USER .
```

### Debugging
```bash
# Access running container shell
docker exec -it evolve-web bash

# Run Django commands
docker-compose exec web python manage.py migrate
docker-compose exec web python manage.py createsuperuser
```

## 📝 Development Workflow

### Making Changes
1. Edit code locally
2. Test with `docker-compose up`
3. Commit changes
4. GitHub Actions automatically builds new image

### Database Migrations
```bash
# Create migrations
docker-compose exec web python manage.py makemigrations

# Apply migrations
docker-compose exec web python manage.py migrate
```

### Static Files
```bash
# Collect static files
docker-compose exec web python manage.py collectstatic
```

## 🌐 Production Deployment

### Cloud Platforms

**AWS ECS/Fargate:**
```bash
aws ecs run-task --task-definition evolve-payments-task
```

**Google Cloud Run:**
```bash
gcloud run deploy evolve-payments \
  --image ghcr.io/joynyayieka/evolve-payments-platform:latest \
  --platform managed
```

**DigitalOcean App Platform:**
```yaml
# .do/app.yaml
services:
- name: web
  source_dir: /
  github:
    repo: JoyNyayieka/evolve-payments-platform
    branch: main
  run_command: python manage.py runserver 0.0.0.0:8000
```

### Load Balancing
For production, run multiple containers behind a load balancer:
```bash
# Scale to 3 instances
docker-compose up --scale web=3
```

## 🆘 Support

If you encounter issues:
1. Check the logs first
2. Verify your environment configuration
3. Open an issue on GitHub with:
   - Docker version
   - Error logs
   - Steps to reproduce

---

**Note:** This is a development release (v0.1.1). Not recommended for production use without proper security hardening and testing.
