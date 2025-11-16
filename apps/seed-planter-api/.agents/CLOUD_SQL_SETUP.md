# Google Cloud SQL Setup Guide

## Database Instance
- **Instance Name**: seedgpt-db
- **Project**: magic-mirror-427812
- **Region**: us-central1
- **Connection Name**: `magic-mirror-427812:us-central1:seedgpt-db`
- **Database**: seedgpt
- **User**: seedgpt_user
- **IP Address**: 34.56.111.107

## Configuration

### Production (Cloud Run)
Cloud Run automatically connects via Unix socket. The DATABASE_URL is stored in Secret Manager and automatically injected:
```
DATABASE_URL=postgresql+psycopg2://seedgpt_user:uj71RVRWZPckYucBYCK7edfyQ@/seedgpt?host=/cloudsql/magic-mirror-427812:us-central1:seedgpt-db
```

### Local Development with Cloud SQL Proxy

1. **Install Cloud SQL Proxy**:
   ```bash
   curl -o cloud-sql-proxy https://storage.googleapis.com/cloud-sql-connectors/cloud-sql-proxy/v2.8.0/cloud-sql-proxy.darwin.amd64
   chmod +x cloud-sql-proxy
   ```

2. **Start the proxy**:
   ```bash
   ./cloud-sql-proxy magic-mirror-427812:us-central1:seedgpt-db
   ```

3. **Use this DATABASE_URL in your local .env**:
   ```
   DATABASE_URL=postgresql://seedgpt_user:uj71RVRWZPckYucBYCK7edfyQ@localhost:5432/seedgpt
   ```

## Database Migrations

Run migrations to create the new Task and TaskProgress tables:
```bash
cd apps/seed-planter-api
alembic revision --autogenerate -m "Add Task and TaskProgress tables"
alembic upgrade head
```

## What Changed

### Removed
- Redis dependency and configuration
- `redis==5.2.0` from requirements.txt
- `REDIS_URL` from config

### Added
- `Task` table for tracking async operations
- `TaskProgress` table for detailed progress history
- Database-based task storage in `task_storage.py`
- PostgreSQL connection via Cloud SQL

### Benefits
- Single database for all data (no Redis needed)
- Persistent task history
- Better integration with existing database infrastructure
- Simplified deployment (one less service to manage)
