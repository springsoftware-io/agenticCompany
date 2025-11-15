#!/bin/bash
# Script to guide OAuth App creation for SeedGPT Guided Setup

set -e

echo "🔐 GitHub OAuth App Setup for SeedGPT Guided Setup"
echo "=================================================="
echo ""

# Configuration
APP_NAME="SeedGPT Guided Setup"
HOMEPAGE_URL="https://roeiba.github.io/SeedGPT"
CALLBACK_URL="https://roeiba.github.io/SeedGPT/oauth-callback.html"
DESCRIPTION="Automated GitHub authentication and fork setup for SeedGPT"

echo "📋 OAuth App Configuration:"
echo "   Application name: $APP_NAME"
echo "   Homepage URL: $HOMEPAGE_URL"
echo "   Authorization callback URL: $CALLBACK_URL"
echo "   Description: $DESCRIPTION"
echo ""

# Build the pre-filled URL
ENCODED_NAME=$(echo "$APP_NAME" | jq -sRr @uri)
ENCODED_URL=$(echo "$HOMEPAGE_URL" | jq -sRr @uri)
ENCODED_CALLBACK=$(echo "$CALLBACK_URL" | jq -sRr @uri)
ENCODED_DESC=$(echo "$DESCRIPTION" | jq -sRr @uri)

OAUTH_URL="https://github.com/settings/applications/new"

echo "🌐 Opening GitHub OAuth App creation page..."
echo ""
echo "Please follow these steps:"
echo "   1. Fill in the form with the details above"
echo "   2. Click 'Register application'"
echo "   3. Copy the Client ID"
echo "   4. Generate a new client secret and copy it"
echo "   5. Return here and paste the Client ID"
echo ""

# Open the browser
if command -v open &> /dev/null; then
    open "$OAUTH_URL"
elif command -v xdg-open &> /dev/null; then
    xdg-open "$OAUTH_URL"
else
    echo "Please open this URL in your browser:"
    echo "$OAUTH_URL"
fi

echo ""
read -p "Press Enter after you've created the OAuth App..."
echo ""

# Ask for Client ID
read -p "Enter the Client ID: " CLIENT_ID

if [ -z "$CLIENT_ID" ]; then
    echo "❌ Client ID is required"
    exit 1
fi

echo ""
echo "✅ Client ID received: $CLIENT_ID"
echo ""

# Update the HTML files
echo "📝 Updating HTML files with Client ID..."

# Update guided-setup.html
if [ -f "docs/guided-setup.html" ]; then
    # Use perl for cross-platform compatibility
    perl -i -pe "s/const GITHUB_CLIENT_ID = '[^']*'/const GITHUB_CLIENT_ID = '$CLIENT_ID'/" docs/guided-setup.html
    echo "✓ Updated docs/guided-setup.html"
else
    echo "⚠️  docs/guided-setup.html not found"
fi

# Update oauth-callback.html
if [ -f "docs/oauth-callback.html" ]; then
    perl -i -pe "s/const GITHUB_CLIENT_ID = '[^']*'/const GITHUB_CLIENT_ID = '$CLIENT_ID'/" docs/oauth-callback.html
    echo "✓ Updated docs/oauth-callback.html"
else
    echo "⚠️  docs/oauth-callback.html not found"
fi

echo ""
echo "✅ Setup complete!"
echo ""
echo "📝 Next Steps:"
echo "   1. ✓ Client ID updated in HTML files"
echo "   2. Store the Client Secret securely (you'll need it for the OAuth proxy)"
echo "   3. Deploy an OAuth proxy service (see .agents/GUIDED_SETUP_IMPLEMENTATION.md)"
echo "   4. Update OAUTH_PROXY_URL in docs/oauth-callback.html"
echo "   5. Commit and push the changes"
echo ""
echo "💡 Tip: The Token-based authentication method works immediately without OAuth proxy!"
echo ""

# Show git status
if git diff --quiet docs/guided-setup.html docs/oauth-callback.html 2>/dev/null; then
    echo "⚠️  No changes detected. Make sure the Client ID was entered correctly."
else
    echo "📊 Git status:"
    git status --short docs/guided-setup.html docs/oauth-callback.html
    echo ""
    read -p "Would you like to commit these changes? (y/n) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        git add docs/guided-setup.html docs/oauth-callback.html
        git commit -m "Configure GitHub OAuth Client ID for guided setup"
        echo "✓ Changes committed"
        echo ""
        read -p "Would you like to push to remote? (y/n) " -n 1 -r
        echo
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            git push
            echo "✓ Changes pushed"
        fi
    fi
fi

echo ""
echo "🎉 All done! Your OAuth App is ready."
echo "   View your app at: https://github.com/settings/developers"
