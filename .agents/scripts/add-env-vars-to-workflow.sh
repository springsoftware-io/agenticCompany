#!/bin/bash
# Script to add environment variables section to a workflow file
# Usage: ./add-env-vars-to-workflow.sh <workflow-file>

set -e

if [ $# -eq 0 ]; then
    echo "Usage: $0 <workflow-file>"
    echo "Example: $0 .github/workflows/test-agents.yml"
    exit 1
fi

WORKFLOW_FILE="$1"

if [ ! -f "$WORKFLOW_FILE" ]; then
    echo "Error: File not found: $WORKFLOW_FILE"
    exit 1
fi

# Check if env section already exists
if grep -q "^env:" "$WORKFLOW_FILE"; then
    echo "⚠️  Warning: 'env:' section already exists in $WORKFLOW_FILE"
    echo "Please add variables manually or remove existing env section first"
    exit 1
fi

# Create backup
BACKUP_FILE="${WORKFLOW_FILE}.backup"
cp "$WORKFLOW_FILE" "$BACKUP_FILE"
echo "✅ Created backup: $BACKUP_FILE"

# Environment variables to add
ENV_VARS='
# Centralized path configuration
env:
  # Core paths
  CORE_DIR: autogrow-core
  SRC_DIR: autogrow-core/src
  TESTS_DIR: autogrow-core/tests
  SCRIPTS_DIR: autogrow-core/scripts
  
  # Key files
  REQUIREMENTS_FILE: autogrow-core/src/requirements.txt
  
  # Test paths
  TESTS_CACHE: autogrow-core/tests/.pytest_cache
  COVERAGE_DIR: autogrow-core/tests/htmlcov
  COVERAGE_XML: autogrow-core/tests/htmlcov/coverage.xml
  
  # Agent paths
  CLAUDE_AGENT_DIR: autogrow-core/src/claude-agent
  GEMINI_AGENT_DIR: autogrow-core/src/gemini-agent
  CLAUDE_SCRIPTS: autogrow-core/src/claude-agent/scripts
  GEMINI_SCRIPTS: autogrow-core/src/gemini-agent/scripts
'

# Find the line number where "jobs:" starts
JOBS_LINE=$(grep -n "^jobs:" "$WORKFLOW_FILE" | head -1 | cut -d: -f1)

if [ -z "$JOBS_LINE" ]; then
    echo "Error: Could not find 'jobs:' section in $WORKFLOW_FILE"
    exit 1
fi

# Insert env section before jobs
{
    head -n $((JOBS_LINE - 1)) "$WORKFLOW_FILE"
    echo "$ENV_VARS"
    tail -n +$JOBS_LINE "$WORKFLOW_FILE"
} > "${WORKFLOW_FILE}.tmp"

mv "${WORKFLOW_FILE}.tmp" "$WORKFLOW_FILE"

echo "✅ Added environment variables to $WORKFLOW_FILE"
echo ""
echo "Next steps:"
echo "1. Review the changes: git diff $WORKFLOW_FILE"
echo "2. Replace hardcoded paths with env vars manually"
echo "3. Test the workflow"
echo "4. Remove backup if satisfied: rm $BACKUP_FILE"
echo ""
echo "Common replacements:"
echo "  autogrow-core/src/requirements.txt  →  \${{ env.REQUIREMENTS_FILE }}"
echo "  autogrow-core/tests/htmlcov/        →  \${{ env.COVERAGE_DIR }}"
echo "  cd autogrow-core                    →  cd \${{ env.CORE_DIR }}"
