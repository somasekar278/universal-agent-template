#!/usr/bin/env python3
"""
SOTA Agent Framework - Deployment CLI

Helps users deploy their agent solutions to various platforms.

Usage:
    sota-deploy init [--platform docker|k8s|databricks|aws|gcp]
    sota-deploy build [--tag TAG]
    sota-deploy push [--registry REGISTRY]
    sota-deploy apply [--environment ENV]
    sota-deploy status
"""

import os
import sys
import argparse
import subprocess
from pathlib import Path
from typing import Optional, Dict, Any
import yaml


class DeploymentManager:
    """Manages deployment of agent solutions."""
    
    PLATFORMS = ["docker", "kubernetes", "databricks", "aws-lambda", "gcp-functions", "all"]
    
    def __init__(self, project_dir: Path = Path(".")):
        self.project_dir = project_dir
        self.deploy_dir = project_dir / "deployment"
    
    def init(self, platform: str = "all"):
        """Initialize deployment configuration for specified platform."""
        
        print(f"\n🚀 Initializing deployment configuration for: {platform}\n")
        
        self.deploy_dir.mkdir(exist_ok=True)
        
        if platform in ["docker", "all"]:
            self._generate_dockerfile()
            self._generate_docker_compose()
        
        if platform in ["kubernetes", "all"]:
            self._generate_k8s_manifests()
        
        if platform in ["databricks", "all"]:
            self._generate_databricks_config()
        
        if platform in ["aws-lambda", "all"]:
            self._generate_serverless_config("aws")
        
        if platform in ["gcp-functions", "all"]:
            self._generate_serverless_config("gcp")
        
        self._generate_github_actions()
        self._generate_deployment_readme()
        
        print(f"✅ Deployment configuration created in: {self.deploy_dir}")
        print(f"\n📖 Next steps:")
        print(f"   1. Review and customize configs in {self.deploy_dir}/")
        print(f"   2. Build: sota-deploy build")
        print(f"   3. Deploy: sota-deploy apply --environment production")
    
    def _generate_dockerfile(self):
        """Generate production-ready Dockerfile."""
        
        dockerfile_content = """# Production Dockerfile for SOTA Agent Solution
FROM python:3.11-slim as builder

WORKDIR /build

# Install build dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \\
    build-essential \\
    && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY requirements.txt .

# Install Python dependencies
RUN pip install --user --no-cache-dir -r requirements.txt

# Runtime stage
FROM python:3.11-slim

WORKDIR /app

# Copy dependencies from builder
COPY --from=builder /root/.local /root/.local

# Make sure scripts in .local are usable
ENV PATH=/root/.local/bin:$PATH

# Install runtime dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \\
    curl \\
    && rm -rf /var/lib/apt/lists/*

# Copy application code
COPY . .

# Install agent solution
RUN pip install --no-cache-dir -e .

# Create non-root user
RUN useradd -m -u 1000 agentuser && \\
    chown -R agentuser:agentuser /app

USER agentuser

# Expose ports
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \\
    CMD curl -f http://localhost:8000/health || exit 1

# Run application
CMD ["python", "-m", "uvicorn", "services.api:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "4"]
"""
        
        dockerfile_path = self.project_dir / "Dockerfile"
        dockerfile_path.write_text(dockerfile_content)
        print(f"   ✅ Created Dockerfile")
    
    def _generate_docker_compose(self):
        """Generate docker-compose.yml for local testing."""
        
        compose_content = """version: '3.8'

services:
  api:
    build: .
    ports:
      - "8000:8000"
    environment:
      - ENVIRONMENT=development
      - DATABRICKS_HOST=${DATABRICKS_HOST}
      - DATABRICKS_TOKEN=${DATABRICKS_TOKEN}
    volumes:
      - ./config:/app/config:ro
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 40s
    restart: unless-stopped
  
  worker:
    build: .
    command: python -m services.worker
    environment:
      - ENVIRONMENT=development
      - DATABRICKS_HOST=${DATABRICKS_HOST}
      - DATABRICKS_TOKEN=${DATABRICKS_TOKEN}
    volumes:
      - ./config:/app/config:ro
    depends_on:
      api:
        condition: service_healthy
    restart: unless-stopped
  
  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"
    restart: unless-stopped
"""
        
        compose_path = self.deploy_dir / "docker-compose.yml"
        compose_path.write_text(compose_content)
        print(f"   ✅ Created docker-compose.yml")
    
    def _generate_k8s_manifests(self):
        """Generate Kubernetes manifests."""
        
        k8s_dir = self.deploy_dir / "kubernetes"
        k8s_dir.mkdir(exist_ok=True)
        
        # Deployment
        deployment = """apiVersion: apps/v1
kind: Deployment
metadata:
  name: agent-api
  labels:
    app: agent-api
spec:
  replicas: 3
  selector:
    matchLabels:
      app: agent-api
  template:
    metadata:
      labels:
        app: agent-api
    spec:
      containers:
      - name: agent-api
        image: ${IMAGE_REGISTRY}/agent-solution:${IMAGE_TAG}
        ports:
        - containerPort: 8000
        env:
        - name: ENVIRONMENT
          value: "production"
        - name: DATABRICKS_TOKEN
          valueFrom:
            secretKeyRef:
              name: databricks-secret
              key: token
        - name: DATABRICKS_HOST
          valueFrom:
            configMapKeyRef:
              name: databricks-config
              key: host
        resources:
          requests:
            memory: "512Mi"
            cpu: "500m"
          limits:
            memory: "2Gi"
            cpu: "2000m"
        livenessProbe:
          httpGet:
            path: /health
            port: 8000
          initialDelaySeconds: 30
          periodSeconds: 10
        readinessProbe:
          httpGet:
            path: /health
            port: 8000
          initialDelaySeconds: 5
          periodSeconds: 5
"""
        
        # Service
        service = """apiVersion: v1
kind: Service
metadata:
  name: agent-api-service
spec:
  selector:
    app: agent-api
  ports:
  - protocol: TCP
    port: 80
    targetPort: 8000
  type: LoadBalancer
"""
        
        # HPA
        hpa = """apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: agent-api-hpa
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: agent-api
  minReplicas: 3
  maxReplicas: 20
  metrics:
  - type: Resource
    resource:
      name: cpu
      target:
        type: Utilization
        averageUtilization: 70
  - type: Resource
    resource:
      name: memory
      target:
        type: Utilization
        averageUtilization: 80
"""
        
        (k8s_dir / "deployment.yaml").write_text(deployment)
        (k8s_dir / "service.yaml").write_text(service)
        (k8s_dir / "hpa.yaml").write_text(hpa)
        print(f"   ✅ Created Kubernetes manifests in deployment/kubernetes/")
    
    def _generate_databricks_config(self):
        """Generate Databricks deployment config."""
        
        databricks_dir = self.deploy_dir / "databricks"
        databricks_dir.mkdir(exist_ok=True)
        
        job_config = """# Databricks Job Configuration
# Deploy with: databricks jobs create --json-file deployment/databricks/job.json

{
  "name": "agent-batch-processing",
  "tasks": [
    {
      "task_key": "process_batch",
      "description": "Process data with agents",
      "new_cluster": {
        "spark_version": "13.3.x-scala2.12",
        "node_type_id": "i3.xlarge",
        "num_workers": 4,
        "spark_conf": {
          "spark.databricks.delta.preview.enabled": "true"
        }
      },
      "python_wheel_task": {
        "package_name": "agent_solution",
        "entry_point": "main",
        "parameters": ["--date", "{{job.start_time}}"]
      },
      "libraries": [
        {"pypi": {"package": "sota-agent-framework[databricks]"}},
        {"whl": "dbfs:/wheels/agent_solution-1.0.0-py3-none-any.whl"}
      ],
      "timeout_seconds": 3600
    }
  ],
  "schedule": {
    "quartz_cron_expression": "0 0 * * * ?",
    "timezone_id": "America/Los_Angeles"
  },
  "email_notifications": {
    "on_failure": ["alerts@company.com"]
  },
  "max_concurrent_runs": 1
}
"""
        
        (databricks_dir / "job.json").write_text(job_config)
        print(f"   ✅ Created Databricks job config")
    
    def _generate_serverless_config(self, provider: str):
        """Generate serverless configuration."""
        
        serverless_dir = self.deploy_dir / "serverless"
        serverless_dir.mkdir(exist_ok=True)
        
        if provider == "aws":
            config = """# Serverless Framework Configuration for AWS Lambda
service: agent-solution

provider:
  name: aws
  runtime: python3.11
  region: us-west-2
  memorySize: 1024
  timeout: 300
  environment:
    DATABRICKS_TOKEN: ${env:DATABRICKS_TOKEN}
    DATABRICKS_HOST: ${env:DATABRICKS_HOST}
  
  iamRoleStatements:
    - Effect: Allow
      Action:
        - logs:CreateLogGroup
        - logs:CreateLogStream
        - logs:PutLogEvents
      Resource: '*'

functions:
  executeAgent:
    handler: handler.execute_agent
    events:
      - http:
          path: /execute
          method: post
          cors: true
    reservedConcurrency: 100

package:
  patterns:
    - '!tests/**'
    - '!docs/**'
    - '!.git/**'
    - '!deployment/**'

plugins:
  - serverless-python-requirements

custom:
  pythonRequirements:
    dockerizePip: true
    slim: true
"""
            (serverless_dir / "serverless.yml").write_text(config)
            
            # Lambda handler
            handler = """import json
from agents import AgentRouter
from shared.schemas import AgentInput

# Initialize once (cold start optimization)
router = AgentRouter.from_yaml("config/agents.yaml")

def execute_agent(event, context):
    '''AWS Lambda handler for agent execution.'''
    
    try:
        # Parse request
        body = json.loads(event['body'])
        
        # Execute agent (sync wrapper for async)
        import asyncio
        request = AgentInput(**body)
        result = asyncio.run(
            router.route(body['agent_name'], request)
        )
        
        return {
            'statusCode': 200,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            'body': json.dumps(result.dict())
        }
    
    except Exception as e:
        return {
            'statusCode': 500,
            'body': json.dumps({'error': str(e)})
        }
"""
            (serverless_dir / "handler.py").write_text(handler)
            print(f"   ✅ Created AWS Lambda/Serverless config")
        
        elif provider == "gcp":
            main_py = """import functions_framework
from agents import AgentRouter
from shared.schemas import AgentInput

router = AgentRouter.from_yaml("config/agents.yaml")

@functions_framework.http
def execute_agent(request):
    '''Google Cloud Function entry point.'''
    
    request_json = request.get_json()
    
    import asyncio
    result = asyncio.run(
        router.route(
            request_json['agent_name'],
            AgentInput(**request_json)
        )
    )
    
    return result.dict()
"""
            (serverless_dir / "main.py").write_text(main_py)
            print(f"   ✅ Created GCP Cloud Functions config")
    
    def _generate_github_actions(self):
        """Generate GitHub Actions workflow."""
        
        github_dir = self.project_dir / ".github" / "workflows"
        github_dir.mkdir(parents=True, exist_ok=True)
        
        workflow = """name: Deploy Agent Solution

on:
  push:
    branches: [main]
    tags: ['v*']

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      
      - name: Install dependencies
        run: |
          pip install -r requirements.txt
          pip install pytest pytest-asyncio
      
      - name: Run tests
        run: pytest tests/ -v
  
  build-and-push:
    needs: test
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Set up Docker Buildx
        uses: docker/setup-buildx-action@v2
      
      - name: Login to Container Registry
        uses: docker/login-action@v2
        with:
          registry: ghcr.io
          username: ${{ github.actor }}
          password: ${{ secrets.GITHUB_TOKEN }}
      
      - name: Build and push
        uses: docker/build-push-action@v4
        with:
          context: .
          push: true
          tags: |
            ghcr.io/${{ github.repository }}:latest
            ghcr.io/${{ github.repository }}:${{ github.sha }}
  
  deploy:
    needs: build-and-push
    runs-on: ubuntu-latest
    if: startsWith(github.ref, 'refs/tags/v')
    steps:
      - uses: actions/checkout@v3
      
      - name: Deploy to production
        run: |
          echo "Deploy to your platform here"
          # kubectl apply -f deployment/kubernetes/
          # databricks jobs run-now --job-id ${{ secrets.JOB_ID }}
          # serverless deploy --stage production
"""
        
        (github_dir / "deploy.yml").write_text(workflow)
        print(f"   ✅ Created GitHub Actions workflow")
    
    def _generate_deployment_readme(self):
        """Generate deployment README."""
        
        readme = """# Deployment Guide

This directory contains deployment configurations for your agent solution.

## Quick Start

```bash
# Docker local testing
docker-compose -f deployment/docker-compose.yml up

# Build for production
sota-deploy build --tag v1.0.0

# Deploy to Kubernetes
kubectl apply -f deployment/kubernetes/

# Deploy to Databricks
databricks jobs create --json-file deployment/databricks/job.json

# Deploy to AWS Lambda
cd deployment/serverless && serverless deploy --stage production
```

## Files

- `Dockerfile` - Production Docker image
- `docker-compose.yml` - Local multi-service testing
- `kubernetes/` - Kubernetes manifests (deployment, service, HPA)
- `databricks/` - Databricks job configurations
- `serverless/` - AWS Lambda / GCP Functions configs
- `.github/workflows/` - CI/CD pipelines

## Configuration

Set these environment variables before deploying:

```bash
export DATABRICKS_HOST=https://your-workspace.databricks.com
export DATABRICKS_TOKEN=your-token
export IMAGE_REGISTRY=ghcr.io/yourorg
export IMAGE_TAG=v1.0.0
```

## See Also

- [Complete Deployment Guide](../docs/DEPLOYMENT.md)
- [Framework Documentation](../docs/)
"""
        
        (self.deploy_dir / "README.md").write_text(readme)
        print(f"   ✅ Created deployment README")
    
    def build(self, tag: Optional[str] = None):
        """Build Docker image."""
        
        if not (self.project_dir / "Dockerfile").exists():
            print("❌ Dockerfile not found. Run 'sota-deploy init' first.")
            return False
        
        tag = tag or "latest"
        image_name = f"{self.project_dir.name}:{tag}"
        
        print(f"\n🔨 Building Docker image: {image_name}\n")
        
        cmd = ["docker", "build", "-t", image_name, str(self.project_dir)]
        
        result = subprocess.run(cmd)
        
        if result.returncode == 0:
            print(f"\n✅ Image built successfully: {image_name}")
            return True
        else:
            print(f"\n❌ Build failed")
            return False
    
    def status(self):
        """Show deployment status."""
        
        print("\n📊 Deployment Status\n")
        
        # Check Docker
        if (self.project_dir / "Dockerfile").exists():
            print("✅ Docker configuration ready")
        else:
            print("❌ Docker not configured")
        
        # Check K8s
        if (self.deploy_dir / "kubernetes").exists():
            print("✅ Kubernetes manifests ready")
        else:
            print("❌ Kubernetes not configured")
        
        # Check Databricks
        if (self.deploy_dir / "databricks").exists():
            print("✅ Databricks configuration ready")
        else:
            print("❌ Databricks not configured")
        
        # Check serverless
        if (self.deploy_dir / "serverless").exists():
            print("✅ Serverless configuration ready")
        else:
            print("❌ Serverless not configured")
        
        print()


def main():
    """Main CLI entry point."""
    
    parser = argparse.ArgumentParser(
        description="SOTA Agent Framework - Deployment CLI",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    subparsers = parser.add_subparsers(dest="command", help="Commands")
    
    # Init command
    init_parser = subparsers.add_parser("init", help="Initialize deployment configuration")
    init_parser.add_argument(
        "--platform",
        choices=DeploymentManager.PLATFORMS,
        default="all",
        help="Target deployment platform"
    )
    
    # Build command
    build_parser = subparsers.add_parser("build", help="Build Docker image")
    build_parser.add_argument(
        "--tag",
        default="latest",
        help="Image tag"
    )
    
    # Status command
    status_parser = subparsers.add_parser("status", help="Show deployment status")
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    manager = DeploymentManager()
    
    if args.command == "init":
        manager.init(args.platform)
    elif args.command == "build":
        manager.build(args.tag)
    elif args.command == "status":
        manager.status()


if __name__ == "__main__":
    main()

