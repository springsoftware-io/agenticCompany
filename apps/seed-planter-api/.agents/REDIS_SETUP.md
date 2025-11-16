# Redis Setup for Task Polling

## Current Status
The application now works **without Redis** by gracefully degrading functionality:
- Task polling endpoints return 404 when Redis is unavailable
- Project creation still works but without real-time status updates
- Logs warnings instead of crashing

## Production Setup (Recommended)

To enable full task polling functionality in production, set up Redis:

### Option 1: Google Cloud Memorystore (Recommended for GCP)

```bash
# Create Redis instance
gcloud redis instances create seedgpt-redis \
    --size=1 \
    --region=us-central1 \
    --redis-version=redis_7_0 \
    --tier=basic

# Get connection info
gcloud redis instances describe seedgpt-redis \
    --region=us-central1 \
    --format="get(host,port)"
```

### Option 2: External Redis Provider

Use a managed Redis service like:
- **Redis Cloud** (redis.com)
- **Upstash** (upstash.com)
- **AWS ElastiCache**

### Configure Cloud Run

Update the deployment to include Redis URL:

```yaml
# In .github/workflows/apps-seed-planter-api.yml
--set-env-vars "REDIS_URL=redis://[REDIS_HOST]:6379"
```

Or add as a secret:

```bash
# Create secret
gcloud secrets create REDIS_URL --data-file=- <<< "redis://[REDIS_HOST]:6379"

# Update deployment
--update-secrets "REDIS_URL=REDIS_URL:latest"
```

## Environment Variables

```bash
# Default (localhost)
REDIS_URL=redis://localhost:6379

# Cloud Memorystore (internal IP)
REDIS_URL=redis://10.0.0.3:6379

# External provider with auth
REDIS_URL=redis://username:password@host:port
```

## Testing Locally

```bash
# Start Redis with Docker
docker run -d -p 6379:6379 redis:7-alpine

# Or with docker-compose
docker-compose up -d redis
```

## Monitoring

When Redis is available, you'll see:
```
✅ Redis connected - task polling enabled
```

When Redis is unavailable:
```
⚠️ Redis not available - task polling disabled
```

## Future Improvements

1. **Implement fallback storage** - Use database for task status when Redis unavailable
2. **Add Redis health check** - Monitor Redis availability
3. **Configure connection pooling** - Optimize Redis connections
4. **Set up Redis persistence** - Enable RDB or AOF for data durability
