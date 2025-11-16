#!/bin/bash

# Setup Auth0 secrets in Google Cloud Secret Manager
# Usage: ./setup_auth0_secrets.sh

set -e

PROJECT_ID="magic-mirror-427812"
REGION="us-central1"

echo "🔐 Setting up Auth0 secrets for project: $PROJECT_ID"
echo ""

# Check if secrets already exist
check_secret() {
    local secret_name=$1
    if gcloud secrets describe "$secret_name" --project="$PROJECT_ID" &>/dev/null; then
        echo "✅ Secret $secret_name already exists"
        return 0
    else
        echo "❌ Secret $secret_name does not exist"
        return 1
    fi
}

# Create or update secret
create_or_update_secret() {
    local secret_name=$1
    local secret_value=$2
    
    if check_secret "$secret_name"; then
        echo "   Updating $secret_name..."
        echo -n "$secret_value" | gcloud secrets versions add "$secret_name" \
            --data-file=- \
            --project="$PROJECT_ID"
    else
        echo "   Creating $secret_name..."
        echo -n "$secret_value" | gcloud secrets create "$secret_name" \
            --data-file=- \
            --replication-policy="automatic" \
            --project="$PROJECT_ID"
    fi
}

# Prompt for Auth0 credentials
echo "📝 Please provide your Auth0 credentials:"
echo ""

read -p "Auth0 Domain (e.g., dev-xxx.us.auth0.com): " AUTH0_DOMAIN
read -p "Auth0 Client ID: " AUTH0_CLIENT_ID
read -sp "Auth0 Client Secret: " AUTH0_CLIENT_SECRET
echo ""
read -p "Auth0 Audience (e.g., https://dev-xxx.us.auth0.com/api/v2/): " AUTH0_AUDIENCE
echo ""

# Validate inputs
if [ -z "$AUTH0_DOMAIN" ] || [ -z "$AUTH0_CLIENT_ID" ] || [ -z "$AUTH0_CLIENT_SECRET" ] || [ -z "$AUTH0_AUDIENCE" ]; then
    echo "❌ Error: All Auth0 credentials are required"
    exit 1
fi

echo ""
echo "🚀 Creating/updating secrets..."
echo ""

# Create secrets
create_or_update_secret "AUTH0_DOMAIN" "$AUTH0_DOMAIN"
create_or_update_secret "AUTH0_CLIENT_ID" "$AUTH0_CLIENT_ID"
create_or_update_secret "AUTH0_CLIENT_SECRET" "$AUTH0_CLIENT_SECRET"
create_or_update_secret "AUTH0_AUDIENCE" "$AUTH0_AUDIENCE"

echo ""
echo "✅ Auth0 secrets created successfully!"
echo ""
echo "📋 Next steps:"
echo "1. Update Cloud Run service to use these secrets"
echo "2. Run: gcloud run services update agenticCompany \\"
echo "     --update-secrets=AUTH0_DOMAIN=AUTH0_DOMAIN:latest,AUTH0_CLIENT_ID=AUTH0_CLIENT_ID:latest,AUTH0_CLIENT_SECRET=AUTH0_CLIENT_SECRET:latest,AUTH0_AUDIENCE=AUTH0_AUDIENCE:latest \\"
echo "     --region=$REGION \\"
echo "     --project=$PROJECT_ID"
echo ""
