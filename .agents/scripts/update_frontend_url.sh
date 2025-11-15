#!/bin/bash

# Script to update the frontend URL in docs/index.html with the actual Cloud Run URL

set -e

PROJECT_ID="magic-mirror-427812"
SERVICE_NAME="seed-planter-frontend"
REGION="us-central1"
INDEX_FILE="docs/index.html"

echo "🔍 Getting Cloud Run service URL..."

# Get the actual service URL
SERVICE_URL=$(gcloud run services describe $SERVICE_NAME \
  --platform managed \
  --region $REGION \
  --format 'value(status.url)' \
  --project $PROJECT_ID 2>/dev/null)

if [ -z "$SERVICE_URL" ]; then
  echo "❌ Error: Could not get service URL. Make sure the service is deployed."
  exit 1
fi

echo "✅ Found URL: $SERVICE_URL"

# Update the index.html file
if [ -f "$INDEX_FILE" ]; then
  echo "📝 Updating $INDEX_FILE..."
  
  # Use sed to replace the placeholder URL
  if [[ "$OSTYPE" == "darwin"* ]]; then
    # macOS
    sed -i '' "s|const FRONTEND_APP_URL = '.*';|const FRONTEND_APP_URL = '$SERVICE_URL';|g" "$INDEX_FILE"
  else
    # Linux
    sed -i "s|const FRONTEND_APP_URL = '.*';|const FRONTEND_APP_URL = '$SERVICE_URL';|g" "$INDEX_FILE"
  fi
  
  echo "✅ Updated $INDEX_FILE with URL: $SERVICE_URL"
else
  echo "❌ Error: $INDEX_FILE not found"
  exit 1
fi

echo "🎉 Done! The frontend URL has been updated."
