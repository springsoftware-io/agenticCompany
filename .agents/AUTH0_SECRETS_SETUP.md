# Auth0 Secrets Setup Guide

## Secrets Created in Google Cloud Secret Manager

The following secrets have been created in project `magic-mirror-427812`:

1. **AUTH0_DOMAIN** - Auth0 tenant domain
2. **AUTH0_CLIENT_ID** - Auth0 application client ID
3. **AUTH0_CLIENT_SECRET** - Auth0 application client secret
4. **AUTH0_AUDIENCE** - Auth0 API audience/identifier

## Current Status

✅ Secrets created with placeholder values
✅ GitHub Actions workflow updated to inject secrets
✅ Cloud Run service configured to use secrets

## Update Secrets with Real Values

### Option 1: Using the Setup Script

```bash
cd /Users/roei/dev_workspace/spring-clients-projects/seedGPT
./.agents/scripts/setup_auth0_secrets.sh
```

This script will prompt you for your Auth0 credentials and update all secrets.

### Option 2: Manually Update Individual Secrets

```bash
# Update AUTH0_DOMAIN
echo -n "your-tenant.us.auth0.com" | gcloud secrets versions add AUTH0_DOMAIN \
  --data-file=- \
  --project=magic-mirror-427812

# Update AUTH0_CLIENT_ID
echo -n "your_client_id" | gcloud secrets versions add AUTH0_CLIENT_ID \
  --data-file=- \
  --project=magic-mirror-427812

# Update AUTH0_CLIENT_SECRET
echo -n "your_client_secret" | gcloud secrets versions add AUTH0_CLIENT_SECRET \
  --data-file=- \
  --project=magic-mirror-427812

# Update AUTH0_AUDIENCE
echo -n "https://your-tenant.us.auth0.com/api/v2/" | gcloud secrets versions add AUTH0_AUDIENCE \
  --data-file=- \
  --project=magic-mirror-427812
```

### Option 3: Using Google Cloud Console

1. Go to [Secret Manager](https://console.cloud.google.com/security/secret-manager?project=magic-mirror-427812)
2. Click on each secret (AUTH0_DOMAIN, AUTH0_CLIENT_ID, etc.)
3. Click "New Version"
4. Paste the secret value
5. Click "Add New Version"

## Verify Secrets are Loaded

After updating secrets, the Cloud Run service will automatically pick them up on the next deployment or restart.

To verify:

```bash
# Check secret versions
gcloud secrets versions list AUTH0_DOMAIN --project=magic-mirror-427812
gcloud secrets versions list AUTH0_CLIENT_ID --project=magic-mirror-427812
gcloud secrets versions list AUTH0_CLIENT_SECRET --project=magic-mirror-427812
gcloud secrets versions list AUTH0_AUDIENCE --project=magic-mirror-427812

# Check Cloud Run service configuration
gcloud run services describe agenticCompany \
  --region=us-central1 \
  --project=magic-mirror-427812 \
  --format="value(spec.template.spec.containers[0].env)"
```

## Auth0 Application Setup

If you haven't set up your Auth0 application yet:

1. **Create Auth0 Account**: Go to [auth0.com](https://auth0.com) and sign up
2. **Create Application**: 
   - Go to Applications → Create Application
   - Choose "Single Page Web Application"
   - Name it "SeedGPT"
3. **Configure Application**:
   - Allowed Callback URLs: `https://your-frontend-url.com/callback`
   - Allowed Logout URLs: `https://your-frontend-url.com`
   - Allowed Web Origins: `https://your-frontend-url.com`
4. **Get Credentials**:
   - Domain: Found in application settings (e.g., `dev-xxx.us.auth0.com`)
   - Client ID: Found in application settings
   - Client Secret: Found in application settings
5. **Create API**:
   - Go to Applications → APIs → Create API
   - Name: "SeedGPT API"
   - Identifier: `https://your-domain.us.auth0.com/api/v2/` (this is your audience)

## Testing

After updating secrets, test the authentication:

```bash
# Get a test token from Auth0 (you'll need to implement OAuth flow in frontend)
# Then test with the API:

curl -X GET https://agenticCompany-1068119864554.us-central1.run.app/api/v1/auth/me \
  -H "Authorization: Bearer YOUR_AUTH0_JWT_TOKEN"
```

## Troubleshooting

### Secrets not loading
- Check Cloud Run logs: `gcloud run services logs read agenticCompany --region=us-central1 --project=magic-mirror-427812`
- Verify secrets exist: `gcloud secrets list --project=magic-mirror-427812`
- Check IAM permissions: Cloud Run service account needs `roles/secretmanager.secretAccessor`

### Authentication failing
- Verify Auth0 domain matches exactly (no https://, no trailing slash)
- Check audience URL matches your Auth0 API identifier
- Ensure JWT token is valid and not expired
- Check Cloud Run logs for detailed error messages

## Security Notes

- ⚠️ Never commit Auth0 credentials to git
- ⚠️ Rotate secrets regularly
- ⚠️ Use different Auth0 tenants for dev/staging/production
- ⚠️ Monitor secret access in Google Cloud Console
- ⚠️ Enable Auth0 anomaly detection and brute force protection

## Next Steps

1. ✅ Update secrets with real Auth0 credentials
2. ✅ Deploy the updated code (already committed)
3. ✅ Test authentication with a real Auth0 token
4. ✅ Update frontend to use Auth0 authentication
5. ✅ Run database migration to add OAuth fields
