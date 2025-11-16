# GitHub Actions Documentation

**Official Docs:** https://docs.github.com/en/actions

## Overview
GitHub Actions is a CI/CD platform for automating workflows. We use it for testing, building, and deploying SeedGPT components.

## Key Features
- Automated CI/CD pipelines
- Event-driven workflows
- Matrix builds
- Secrets management
- Marketplace with pre-built actions
- Self-hosted runners support

## Workflow Basics

### Workflow File
Located in `.github/workflows/*.yml`

```yaml
name: CI/CD Pipeline

on:
  push:
    branches: [main]
  pull_request:
    branches: [main]
  workflow_dispatch:

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Run tests
        run: npm test
```

## Workflow Syntax

### Triggers (on)
```yaml
on:
  # Push to specific branches
  push:
    branches: [main, develop]
    paths:
      - 'src/**'
      - '!docs/**'
  
  # Pull requests
  pull_request:
    branches: [main]
  
  # Scheduled (cron)
  schedule:
    - cron: '0 */10 * * *'  # Every 10 minutes
  
  # Manual trigger
  workflow_dispatch:
    inputs:
      environment:
        description: 'Environment to deploy'
        required: true
        default: 'staging'
```

### Jobs
```yaml
jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - name: Checkout code
        uses: actions/checkout@v4
      
      - name: Build
        run: npm run build
  
  deploy:
    needs: build  # Wait for build to complete
    runs-on: ubuntu-latest
    steps:
      - name: Deploy
        run: ./deploy.sh
```

### Steps
```yaml
steps:
  # Use an action
  - uses: actions/checkout@v4
  
  # Run command
  - name: Install dependencies
    run: npm install
  
  # Multi-line command
  - name: Build and test
    run: |
      npm run build
      npm test
  
  # With environment variables
  - name: Deploy
    run: ./deploy.sh
    env:
      API_KEY: ${{ secrets.API_KEY }}
```

## Runners

### GitHub-Hosted Runners
```yaml
runs-on: ubuntu-latest  # Ubuntu
runs-on: windows-latest  # Windows
runs-on: macos-latest    # macOS
```

### Matrix Strategy
```yaml
jobs:
  test:
    runs-on: ${{ matrix.os }}
    strategy:
      matrix:
        os: [ubuntu-latest, windows-latest, macos-latest]
        node: [16, 18, 20]
    steps:
      - uses: actions/setup-node@v4
        with:
          node-version: ${{ matrix.node }}
```

## Common Actions

### Checkout Code
```yaml
- uses: actions/checkout@v4
  with:
    fetch-depth: 0  # Fetch all history
```

### Setup Languages
```yaml
# Node.js
- uses: actions/setup-node@v4
  with:
    node-version: '18'
    cache: 'npm'

# Python
- uses: actions/setup-python@v5
  with:
    python-version: '3.11'
    cache: 'pip'

# Go
- uses: actions/setup-go@v5
  with:
    go-version: '1.21'
```

### Cache Dependencies
```yaml
- uses: actions/cache@v4
  with:
    path: ~/.npm
    key: ${{ runner.os }}-node-${{ hashFiles('**/package-lock.json') }}
    restore-keys: |
      ${{ runner.os }}-node-
```

### Upload/Download Artifacts
```yaml
# Upload
- uses: actions/upload-artifact@v4
  with:
    name: build-output
    path: dist/

# Download
- uses: actions/download-artifact@v4
  with:
    name: build-output
    path: dist/
```

## Secrets & Variables

### Using Secrets
```yaml
steps:
  - name: Deploy
    run: ./deploy.sh
    env:
      API_KEY: ${{ secrets.API_KEY }}
      DATABASE_URL: ${{ secrets.DATABASE_URL }}
```

### Setting Secrets
1. Go to repository Settings → Secrets and variables → Actions
2. Click "New repository secret"
3. Add name and value

### Environment Variables
```yaml
env:
  NODE_ENV: production
  API_URL: https://api.example.com

jobs:
  build:
    env:
      BUILD_ENV: staging
    steps:
      - name: Build
        run: npm run build
        env:
          SPECIFIC_VAR: value
```

## Conditional Execution

### If Conditions
```yaml
steps:
  - name: Deploy to production
    if: github.ref == 'refs/heads/main'
    run: ./deploy-prod.sh
  
  - name: Deploy to staging
    if: github.ref == 'refs/heads/develop'
    run: ./deploy-staging.sh
  
  - name: Run on success
    if: success()
    run: echo "Previous steps succeeded"
  
  - name: Run on failure
    if: failure()
    run: echo "Previous steps failed"
```

## Docker in Actions

### Build and Push
```yaml
- name: Build Docker image
  run: docker build -t myapp:${{ github.sha }} .

- name: Push to registry
  run: |
    echo ${{ secrets.DOCKER_PASSWORD }} | docker login -u ${{ secrets.DOCKER_USERNAME }} --password-stdin
    docker push myapp:${{ github.sha }}
```

### Docker Compose
```yaml
- name: Run tests with Docker Compose
  run: |
    docker-compose up -d
    docker-compose exec -T api pytest
    docker-compose down
```

## Google Cloud Deployment

### Authenticate
```yaml
- name: Authenticate to Google Cloud
  uses: google-github-actions/auth@v2
  with:
    credentials_json: ${{ secrets.GCP_CREDENTIALS }}
```

### Deploy to Cloud Run
```yaml
- name: Deploy to Cloud Run
  uses: google-github-actions/deploy-cloudrun@v2
  with:
    service: my-service
    image: gcr.io/project/image:tag
    region: us-central1
```

## Notifications

### Slack Notification
```yaml
- name: Slack Notification
  uses: 8398a7/action-slack@v3
  with:
    status: ${{ job.status }}
    text: 'Deployment completed'
    webhook_url: ${{ secrets.SLACK_WEBHOOK }}
  if: always()
```

## Reusable Workflows

### Define Reusable Workflow
```yaml
# .github/workflows/reusable-deploy.yml
name: Reusable Deploy

on:
  workflow_call:
    inputs:
      environment:
        required: true
        type: string
    secrets:
      api_key:
        required: true

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - name: Deploy to ${{ inputs.environment }}
        run: ./deploy.sh
        env:
          API_KEY: ${{ secrets.api_key }}
```

### Use Reusable Workflow
```yaml
jobs:
  deploy-staging:
    uses: ./.github/workflows/reusable-deploy.yml
    with:
      environment: staging
    secrets:
      api_key: ${{ secrets.STAGING_API_KEY }}
```

## SeedGPT Workflow Examples

### API CI/CD
```yaml
name: Seed Planter API - CI/CD

on:
  push:
    branches: [main]
    paths:
      - 'apps/agenticCompany/**'

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: '3.11'
      - run: pip install -r requirements.txt
      - run: pytest

  deploy:
    needs: test
    runs-on: ubuntu-latest
    steps:
      - uses: google-github-actions/auth@v2
        with:
          credentials_json: ${{ secrets.GCP_CREDENTIALS }}
      - run: gcloud run deploy api --image gcr.io/project/api:latest
```

### Agent Workflow (Scheduled)
```yaml
name: Product Agent

on:
  schedule:
    - cron: '0 */10 * * *'  # Every 10 minutes
  workflow_dispatch:

jobs:
  run-agent:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: '3.11'
      - run: pip install -r requirements.txt
      - name: Run product agent
        run: python -m agents.product_agent
        env:
          ANTHROPIC_API_KEY: ${{ secrets.ANTHROPIC_API_KEY }}
          GITHUB_TOKEN: ${{ secrets.PAT_TOKEN }}
```

## Best Practices

1. **Use specific action versions** (`@v4` not `@main`)
2. **Cache dependencies** to speed up workflows
3. **Use secrets** for sensitive data
4. **Limit workflow permissions** with `permissions:`
5. **Use matrix builds** for testing multiple versions
6. **Set timeouts** to prevent stuck workflows
7. **Use concurrency** to cancel outdated runs
8. **Monitor workflow usage** for billing
9. **Use reusable workflows** for common patterns
10. **Add status badges** to README

## Debugging

### Enable Debug Logging
Set repository secrets:
- `ACTIONS_STEP_DEBUG`: `true`
- `ACTIONS_RUNNER_DEBUG`: `true`

### View Logs
```yaml
- name: Debug
  run: |
    echo "GitHub ref: ${{ github.ref }}"
    echo "GitHub SHA: ${{ github.sha }}"
    echo "Runner OS: ${{ runner.os }}"
    env
```

## Status Badge

```markdown
![CI](https://github.com/username/repo/workflows/CI/badge.svg)
```

## Resources
- Official Docs: https://docs.github.com/en/actions
- Workflow Syntax: https://docs.github.com/en/actions/reference/workflow-syntax-for-github-actions
- Actions Marketplace: https://github.com/marketplace?type=actions
- Examples: https://github.com/actions/starter-workflows

## Version Used in SeedGPT
```
GitHub Actions (latest)
actions/checkout@v4
actions/setup-python@v5
actions/setup-node@v4
google-github-actions/auth@v2
google-github-actions/deploy-cloudrun@v2
```
