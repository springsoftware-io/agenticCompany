#!/bin/bash
# Fix the hardcoded token in the cleanup script across all commits

cd /Users/roei/dev_workspace/spring-clients-projects/seedGPT

# Use git filter-branch to rewrite history
git filter-branch --force --tree-filter '
  if [ -f apps/agenticCompany/scripts/cleanup_test_repos.sh ]; then
    sed -i.bak "s/GH_TOKEN=\"ghp_[^\"]*\"/GH_TOKEN=\"\${GITHUB_TOKEN:-}\"/g" apps/agenticCompany/scripts/cleanup_test_repos.sh
    rm -f apps/agenticCompany/scripts/cleanup_test_repos.sh.bak
  fi
' --prune-empty -- 7d1d24a..HEAD

echo "History rewritten successfully"
