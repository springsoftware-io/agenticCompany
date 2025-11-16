# Google Cloud Platform Documentation

**Official Docs:** https://cloud.google.com/docs

## Overview
We use Google Cloud Platform (GCP) for hosting and infrastructure, primarily Cloud Run for serverless container deployment.

## Services Used

### Cloud Run
Fully managed serverless platform for containerized applications.

**Key Features:**
- Auto-scaling (0 to N instances)
- Pay per use (only when serving requests)
- Built-in HTTPS
- Container-based deployment
- Supports any language/framework

**Deployment:**
```bash
gcloud run deploy SERVICE_NAME \
  --image gcr.io/PROJECT_ID/IMAGE_NAME \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated \
  --memory 512Mi \
  --cpu 1 \
  --min-instances 0 \
  --max-instances 10 \
  --timeout 300 \
  --port 8080
```

**Environment Variables:**
```bash
gcloud run services update SERVICE_NAME \
  --set-env-vars "KEY1=value1,KEY2=value2"
```

**Secrets:**
```bash
gcloud run services update SERVICE_NAME \
  --update-secrets "SECRET_NAME=SECRET_NAME:latest"
```

### Cloud SQL
Managed PostgreSQL database.

**Connection:**
- Use Cloud SQL Proxy for local development
- Use Unix socket in production: `/cloudsql/PROJECT:REGION:INSTANCE`

```python
# SQLAlchemy connection string
DATABASE_URL = "postgresql+psycopg2://user:pass@/dbname?host=/cloudsql/PROJECT:REGION:INSTANCE"
```

### Container Registry (GCR)
Docker image storage.

**Push Image:**
```bash
docker tag IMAGE_NAME gcr.io/PROJECT_ID/IMAGE_NAME:TAG
docker push gcr.io/PROJECT_ID/IMAGE_NAME:TAG
```

### Secret Manager
Secure storage for API keys and credentials.

**Create Secret:**
```bash
echo -n "secret-value" | gcloud secrets create SECRET_NAME --data-file=-
```

**Access in Cloud Run:**
```bash
--update-secrets "ENV_VAR=SECRET_NAME:latest"
```

### Resource Manager
Manage GCP projects and resources programmatically.

```python
from google.cloud import resourcemanager_v3

client = resourcemanager_v3.ProjectsClient()
project = client.get_project(name="projects/PROJECT_ID")
```

## Authentication

### Service Account
```bash
# Create service account
gcloud iam service-accounts create SA_NAME

# Grant permissions
gcloud projects add-iam-policy-binding PROJECT_ID \
  --member="serviceAccount:SA_NAME@PROJECT_ID.iam.gserviceaccount.com" \
  --role="roles/run.admin"

# Create key
gcloud iam service-accounts keys create key.json \
  --iam-account=SA_NAME@PROJECT_ID.iam.gserviceaccount.com
```

### Application Default Credentials
```python
from google.auth import default

credentials, project = default()
```

## Cloud Run Configuration

### CPU & Memory
- **CPU:** 1, 2, 4, 6, 8
- **Memory:** 128Mi to 32Gi
- **CPU Boost:** `--cpu-boost` for faster cold starts
- **No CPU Throttling:** `--no-cpu-throttling` for always-on CPU

### Scaling
- **Min instances:** Keep warm instances (costs more)
- **Max instances:** Limit concurrent scaling
- **Concurrency:** Requests per instance (default: 80)

### Timeouts
- **Request timeout:** Max 3600s (1 hour)
- **Default:** 300s (5 minutes)

## Monitoring & Logging

### Cloud Logging
```python
import logging
from google.cloud import logging as cloud_logging

client = cloud_logging.Client()
client.setup_logging()

logging.info("Log message")  # Appears in Cloud Logging
```

### View Logs
```bash
gcloud run services logs read SERVICE_NAME --limit 50
```

## CI/CD with GitHub Actions

```yaml
- name: Deploy to Cloud Run
  uses: google-github-actions/deploy-cloudrun@v2
  with:
    service: service-name
    image: gcr.io/project/image:tag
    region: us-central1
```

## Best Practices
1. **Use secrets** for sensitive data (never env vars)
2. **Set min-instances=0** for cost savings (unless you need low latency)
3. **Enable Cloud Logging** for debugging
4. **Use health checks** for reliability
5. **Set appropriate timeouts** for long-running tasks
6. **Use Cloud SQL Proxy** for secure database connections
7. **Tag images** with git commit SHA for traceability

## Environment Variables Used in SeedGPT
```bash
GCP_PROJECT_ID=magic-mirror-427812
REGION=us-central1
SERVICE_NAME=agenticCompany
REGISTRY=gcr.io
```

## Resources
- Cloud Run Docs: https://cloud.google.com/run/docs
- Cloud SQL Docs: https://cloud.google.com/sql/docs
- Secret Manager: https://cloud.google.com/secret-manager/docs
- Pricing Calculator: https://cloud.google.com/products/calculator

## Python Libraries Used
```
google-cloud-resource-manager==1.12.5
google-cloud-run==0.10.7
google-auth==2.35.0
```
