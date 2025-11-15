#!/bin/bash

# GitHub Cleanup Script - Delete old test-blog-* repositories
# Keeps only the last 5 repositories by creation time

set -e

# Configuration
GH_TOKEN="${GITHUB_TOKEN:-}"
REPO_PREFIX="test-blog-"
KEEP_COUNT=5

if [ -z "$GH_TOKEN" ]; then
  echo -e "${RED}Error: GITHUB_TOKEN environment variable is not set${NC}"
  exit 1
fi

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${YELLOW}=== GitHub Test Repository Cleanup ===${NC}"
echo "Searching for repositories matching: ${REPO_PREFIX}*"
echo "Will keep the last ${KEEP_COUNT} repositories"
echo ""

# Get authenticated user
USER=$(curl -s -H "Authorization: token ${GH_TOKEN}" \
  https://api.github.com/user | jq -r '.login')

if [ -z "$USER" ] || [ "$USER" == "null" ]; then
  echo -e "${RED}Error: Failed to authenticate with GitHub${NC}"
  exit 1
fi

echo "Authenticated as: ${USER}"
echo ""

# Fetch all repositories matching the prefix, sorted by creation date (newest first)
echo "Fetching repositories..."
REPOS=$(curl -s -H "Authorization: token ${GH_TOKEN}" \
  "https://api.github.com/user/repos?per_page=100&sort=created&direction=desc" | \
  jq -r --arg prefix "$REPO_PREFIX" \
  '[.[] | select(.name | startswith($prefix)) | {name: .name, created: .created_at, full_name: .full_name}] | sort_by(.created) | reverse')

# Count total matching repos
TOTAL_COUNT=$(echo "$REPOS" | jq 'length')

if [ "$TOTAL_COUNT" -eq 0 ]; then
  echo -e "${YELLOW}No repositories found matching ${REPO_PREFIX}*${NC}"
  exit 0
fi

echo "Found ${TOTAL_COUNT} repositories matching ${REPO_PREFIX}*"
echo ""

# Calculate how many to delete
DELETE_COUNT=$((TOTAL_COUNT - KEEP_COUNT))

if [ "$DELETE_COUNT" -le 0 ]; then
  echo -e "${GREEN}Only ${TOTAL_COUNT} repositories found. Nothing to delete.${NC}"
  exit 0
fi

echo -e "${YELLOW}Will delete ${DELETE_COUNT} repositories (keeping the newest ${KEEP_COUNT})${NC}"
echo ""

# Get repositories to delete (skip the first KEEP_COUNT)
REPOS_TO_DELETE=$(echo "$REPOS" | jq -r --argjson keep "$KEEP_COUNT" \
  '.[$keep:] | .[] | .full_name')

if [ -z "$REPOS_TO_DELETE" ]; then
  echo -e "${GREEN}No repositories to delete${NC}"
  exit 0
fi

# Display repositories that will be kept
echo -e "${GREEN}Keeping (newest ${KEEP_COUNT}):${NC}"
echo "$REPOS" | jq -r --argjson keep "$KEEP_COUNT" \
  '.[:$keep] | .[] | "  - \(.name) (created: \(.created))"'
echo ""

# Display repositories that will be deleted
echo -e "${RED}Deleting (oldest ${DELETE_COUNT}):${NC}"
echo "$REPOS" | jq -r --argjson keep "$KEEP_COUNT" \
  '.[$keep:] | .[] | "  - \(.name) (created: \(.created))"'
echo ""

# Confirm deletion
read -p "Do you want to proceed with deletion? (yes/no): " CONFIRM

if [ "$CONFIRM" != "yes" ]; then
  echo -e "${YELLOW}Deletion cancelled${NC}"
  exit 0
fi

echo ""
echo "Starting deletion..."
echo ""

# Delete repositories
DELETED=0
FAILED=0

while IFS= read -r REPO_FULL_NAME; do
  echo -n "Deleting ${REPO_FULL_NAME}... "
  
  RESPONSE=$(curl -s -w "\n%{http_code}" -X DELETE \
    -H "Authorization: token ${GH_TOKEN}" \
    "https://api.github.com/repos/${REPO_FULL_NAME}")
  
  HTTP_CODE=$(echo "$RESPONSE" | tail -n1)
  
  if [ "$HTTP_CODE" -eq 204 ]; then
    echo -e "${GREEN}✓ Deleted${NC}"
    ((DELETED++))
  else
    echo -e "${RED}✗ Failed (HTTP ${HTTP_CODE})${NC}"
    ((FAILED++))
  fi
  
  # Rate limiting: wait a bit between deletions
  sleep 1
done <<< "$REPOS_TO_DELETE"

echo ""
echo -e "${GREEN}=== Cleanup Complete ===${NC}"
echo "Successfully deleted: ${DELETED}"
if [ "$FAILED" -gt 0 ]; then
  echo -e "${RED}Failed: ${FAILED}${NC}"
fi
