# Secrets Reference Card

## Google Cloud Secret Manager - Project: magic-mirror-427812

### Current Secrets

| Secret Name | Purpose | Used By | Status |
|------------|---------|---------|--------|
| `AUTH0_DOMAIN` | Auth0 tenant domain | agenticCompany | ✅ Configured (placeholder) |
| `AUTH0_CLIENT_ID` | Auth0 application client ID | agenticCompany | ✅ Configured (placeholder) |
| `AUTH0_CLIENT_SECRET` | Auth0 application client secret | agenticCompany | ✅ Configured (placeholder) |
| `AUTH0_AUDIENCE` | Auth0 API audience | agenticCompany | ✅ Configured (placeholder) |
| `DATABASE_URL` | PostgreSQL connection string | agenticCompany | ✅ Configured |
| `GCP_CREDENTIALS` | GCP service account JSON | agenticCompany | ✅ Configured |
| `GITHUB_OAUTH_CLIENT_SECRET` | GitHub OAuth app secret | agenticCompany | ✅ Configured |

### Quick Commands

#### List all secrets
```bash
gcloud secrets list --project=magic-mirror-427812
```

#### View secret versions
```bash
gcloud secrets versions list SECRET_NAME --project=magic-mirror-427812
```

#### Update a secret
```bash
echo -n "new_value" | gcloud secrets versions add SECRET_NAME \
  --data-file=- \
  --project=magic-mirror-427812
```

#### View Cloud Run secrets configuration
```bash
gcloud run services describe agenticCompany \
  --region=us-central1 \
  --project=magic-mirror-427812 \
  --format="yaml(spec.template.spec.containers[0].env)"
```

### Update Auth0 Secrets

Use the helper script:
```bash
./.agents/scripts/setup_auth0_secrets.sh
```

Or manually:
```bash
# From asset-gold-volatility project
AUTH0_DOMAIN="dev-qi4l073sys2rptlp.us.auth0.com"
AUTH0_CLIENT_ID="Nihe1fJY996ZV8XouX5G8msQNtHSJu7S"
AUTH0_CLIENT_SECRET="Aig9bKzjRTgnNjhxczeliKPDngT37M6IK4fgTpnK6b07d2QNkG35hrTk2s0EBVyj"
AUTH0_AUDIENCE="https://dev-qi4l073sys2rptlp.us.auth0.com/api/v2/"

# Update secrets
echo -n "$AUTH0_DOMAIN" | gcloud secrets versions add AUTH0_DOMAIN --data-file=- --project=magic-mirror-427812
echo -n "$AUTH0_CLIENT_ID" | gcloud secrets versions add AUTH0_CLIENT_ID --data-file=- --project=magic-mirror-427812
echo -n "$AUTH0_CLIENT_SECRET" | gcloud secrets versions add AUTH0_CLIENT_SECRET --data-file=- --project=magic-mirror-427812
echo -n "$AUTH0_AUDIENCE" | gcloud secrets versions add AUTH0_AUDIENCE --data-file=- --project=magic-mirror-427812
```

### Deployment

Secrets are automatically injected during deployment via GitHub Actions workflow:
- File: `.github/workflows/apps-agenticCompany.yml`
- Line: `--update-secrets` parameter includes all Auth0 secrets

Manual deployment with secrets:
```bash
gcloud run deploy agenticCompany \
  --image gcr.io/magic-mirror-427812/agenticCompany:latest \
  --region us-central1 \
  --project magic-mirror-427812 \
  --update-secrets="AUTH0_DOMAIN=AUTH0_DOMAIN:latest,AUTH0_CLIENT_ID=AUTH0_CLIENT_ID:latest,AUTH0_CLIENT_SECRET=AUTH0_CLIENT_SECRET:latest,AUTH0_AUDIENCE=AUTH0_AUDIENCE:latest"
```

### Security Best Practices

- ✅ Secrets stored in Secret Manager (not in code)
- ✅ Automatic replication for high availability
- ✅ Version history maintained
- ✅ IAM-controlled access
- ⚠️ Update placeholder values with real Auth0 credentials
- ⚠️ Rotate secrets regularly
- ⚠️ Use different Auth0 tenants for dev/prod

### Monitoring

Check if secrets are loaded correctly:
```bash
# View Cloud Run logs
gcloud run services logs read agenticCompany \
  --region=us-central1 \
  --project=magic-mirror-427812 \
  --limit=50

# Check for Auth0 configuration errors
gcloud run services logs read agenticCompany \
  --region=us-central1 \
  --project=magic-mirror-427812 \
  --limit=50 | grep -i auth0
```

### Troubleshooting

**Problem**: Secrets not loading
```bash
# Check IAM permissions
gcloud projects get-iam-policy magic-mirror-427812 \
  --flatten="bindings[].members" \
  --filter="bindings.role:roles/secretmanager.secretAccessor"
```

**Problem**: Auth0 authentication failing
```bash
# Check secret values (first few characters only)
gcloud secrets versions access latest --secret=AUTH0_DOMAIN --project=magic-mirror-427812 | head -c 20
```

**Problem**: Need to rollback a secret
```bash
# List versions
gcloud secrets versions list AUTH0_DOMAIN --project=magic-mirror-427812

# Access specific version
gcloud secrets versions access VERSION_NUMBER --secret=AUTH0_DOMAIN --project=magic-mirror-427812
```
