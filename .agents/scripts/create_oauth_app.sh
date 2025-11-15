#!/bin/bash
# Script to create GitHub OAuth App for SeedGPT Guided Setup

set -e

echo "🔐 Creating GitHub OAuth App for SeedGPT Guided Setup..."

# Configuration
APP_NAME="SeedGPT Guided Setup"
HOMEPAGE_URL="https://roeiba.github.io/SeedGPT"
CALLBACK_URL="https://roeiba.github.io/SeedGPT/oauth-callback.html"
DESCRIPTION="Automated GitHub authentication and fork setup for SeedGPT"

# Get the authenticated user
USER=$(gh api user --jq '.login')
echo "✓ Authenticated as: $USER"

# Create OAuth App using GitHub API
echo "Creating OAuth App..."

RESPONSE=$(gh api \
  --method POST \
  -H "Accept: application/vnd.github+json" \
  -H "X-GitHub-Api-Version: 2022-11-28" \
  /user/applications \
  -f name="$APP_NAME" \
  -f url="$HOMEPAGE_URL" \
  -f callback_url="$CALLBACK_URL" \
  -f description="$DESCRIPTION" 2>&1)

if [ $? -eq 0 ]; then
    echo "✅ OAuth App created successfully!"
    echo ""
    echo "📋 OAuth App Details:"
    echo "$RESPONSE" | jq '{
        name: .name,
        client_id: .client_id,
        url: .url,
        callback_url: .callback_url
    }'
    
    CLIENT_ID=$(echo "$RESPONSE" | jq -r '.client_id')
    
    echo ""
    echo "🔑 Client ID: $CLIENT_ID"
    echo ""
    echo "⚠️  IMPORTANT: You need to generate a Client Secret manually:"
    echo "   1. Go to: https://github.com/settings/developers"
    echo "   2. Click on '$APP_NAME'"
    echo "   3. Click 'Generate a new client secret'"
    echo "   4. Save the secret securely (you won't be able to see it again)"
    echo ""
    echo "📝 Next Steps:"
    echo "   1. Update CLIENT_ID in docs/guided-setup.html (line 280)"
    echo "   2. Update CLIENT_ID in docs/oauth-callback.html (line 95)"
    echo "   3. Set up OAuth proxy with Client Secret"
    echo ""
    
    # Offer to update the files automatically
    read -p "Would you like to update the CLIENT_ID in the HTML files now? (y/n) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        # Update guided-setup.html
        sed -i.bak "s/const GITHUB_CLIENT_ID = '[^']*'/const GITHUB_CLIENT_ID = '$CLIENT_ID'/" docs/guided-setup.html
        echo "✓ Updated docs/guided-setup.html"
        
        # Update oauth-callback.html
        sed -i.bak "s/const GITHUB_CLIENT_ID = '[^']*'/const GITHUB_CLIENT_ID = '$CLIENT_ID'/" docs/oauth-callback.html
        echo "✓ Updated docs/oauth-callback.html"
        
        # Remove backup files
        rm -f docs/guided-setup.html.bak docs/oauth-callback.html.bak
        
        echo ""
        echo "✅ Files updated! Don't forget to commit the changes."
    fi
else
    echo "❌ Failed to create OAuth App"
    echo "$RESPONSE"
    exit 1
fi
