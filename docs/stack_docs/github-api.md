# GitHub API Documentation (PyGithub)

**Official Docs:** https://pygithub.readthedocs.io/

## Overview
PyGithub is a Python library to access the GitHub API v3. We use it for automated repository management, issue creation, and pull request handling.

## Authentication

### Personal Access Token (PAT)
```python
from github import Github

g = Github("your-personal-access-token")
```

### GitHub App
```python
from github import GithubIntegration

integration = GithubIntegration(app_id, private_key)
```

## Core Operations

### Repository Access
```python
# Get repository
repo = g.get_repo("owner/repo-name")

# Repository info
print(repo.name)
print(repo.description)
print(repo.stargazers_count)
```

### Issues

**Create Issue:**
```python
issue = repo.create_issue(
    title="Bug: Something is broken",
    body="Detailed description of the issue",
    labels=["bug", "priority-high"],
    assignees=["username"]
)
```

**List Issues:**
```python
# Open issues
open_issues = repo.get_issues(state='open')
for issue in open_issues:
    print(f"#{issue.number}: {issue.title}")

# Filter by label
bugs = repo.get_issues(labels=["bug"])
```

**Update Issue:**
```python
issue.edit(
    title="Updated title",
    body="Updated body",
    state="closed"
)
```

**Add Comment:**
```python
issue.create_comment("This is a comment")
```

### Pull Requests

**Create PR:**
```python
pr = repo.create_pull(
    title="Feature: Add new functionality",
    body="Description of changes",
    head="feature-branch",
    base="main"
)
```

**List PRs:**
```python
pulls = repo.get_pulls(state='open')
for pr in pulls:
    print(f"#{pr.number}: {pr.title}")
```

**Merge PR:**
```python
pr.merge(
    commit_message="Merge pull request",
    merge_method="squash"  # or "merge", "rebase"
)
```

**Review PR:**
```python
pr.create_review(
    body="Looks good!",
    event="APPROVE"  # or "REQUEST_CHANGES", "COMMENT"
)
```

### Branches

**Create Branch:**
```python
source = repo.get_branch("main")
repo.create_git_ref(
    ref=f"refs/heads/new-branch",
    sha=source.commit.sha
)
```

**List Branches:**
```python
branches = repo.get_branches()
for branch in branches:
    print(branch.name)
```

### Files

**Get File Content:**
```python
file = repo.get_contents("path/to/file.py")
content = file.decoded_content.decode('utf-8')
```

**Create/Update File:**
```python
repo.create_file(
    path="path/to/new-file.py",
    message="Add new file",
    content="file content",
    branch="main"
)

# Update existing file
repo.update_file(
    path="path/to/file.py",
    message="Update file",
    content="new content",
    sha=file.sha,  # Required for updates
    branch="main"
)
```

**Delete File:**
```python
repo.delete_file(
    path="path/to/file.py",
    message="Delete file",
    sha=file.sha,
    branch="main"
)
```

### Commits

**Get Commits:**
```python
commits = repo.get_commits()
for commit in commits:
    print(f"{commit.sha[:7]}: {commit.commit.message}")
```

**Create Commit:**
```python
# Low-level API for multiple file changes
from github import InputGitTreeElement

# Get base tree
base_tree = repo.get_git_tree(repo.get_branch("main").commit.sha)

# Create tree elements
elements = [
    InputGitTreeElement("file1.py", "100644", "blob", content="content1"),
    InputGitTreeElement("file2.py", "100644", "blob", content="content2")
]

# Create tree and commit
tree = repo.create_git_tree(elements, base_tree)
parent = repo.get_git_commit(repo.get_branch("main").commit.sha)
commit = repo.create_git_commit("Commit message", tree, [parent])

# Update branch reference
ref = repo.get_git_ref("heads/main")
ref.edit(commit.sha)
```

### Labels

**Create Label:**
```python
repo.create_label(
    name="bug",
    color="d73a4a",
    description="Something isn't working"
)
```

**Add Label to Issue:**
```python
issue.add_to_labels("bug", "priority-high")
```

### Webhooks

**Create Webhook:**
```python
config = {
    "url": "https://example.com/webhook",
    "content_type": "json"
}

repo.create_hook(
    name="web",
    config=config,
    events=["push", "pull_request"],
    active=True
)
```

## Rate Limiting

```python
# Check rate limit
rate_limit = g.get_rate_limit()
print(f"Core: {rate_limit.core.remaining}/{rate_limit.core.limit}")
print(f"Search: {rate_limit.search.remaining}/{rate_limit.search.limit}")
```

**Limits:**
- Authenticated: 5,000 requests/hour
- Search: 30 requests/minute
- GraphQL: 5,000 points/hour

## Error Handling

```python
from github import GithubException, RateLimitExceededException

try:
    repo = g.get_repo("owner/repo")
except GithubException as e:
    print(f"Error {e.status}: {e.data}")
except RateLimitExceededException:
    print("Rate limit exceeded")
```

## Best Practices

1. **Use fine-grained PATs** with minimal permissions
2. **Handle rate limits** gracefully
3. **Cache data** when possible
4. **Use conditional requests** to save quota
5. **Paginate results** for large datasets
6. **Use webhooks** instead of polling
7. **Store commit SHAs** for file operations

## Pagination

```python
# Auto-pagination
for issue in repo.get_issues():
    print(issue.title)

# Manual pagination
issues = repo.get_issues()
for page in range(0, 3):
    page_issues = issues.get_page(page)
    for issue in page_issues:
        print(issue.title)
```

## Environment Variables

```bash
GITHUB_TOKEN=ghp_your_personal_access_token
GITHUB_USERNAME=your-username
```

## Resources
- PyGithub Docs: https://pygithub.readthedocs.io/
- GitHub API Docs: https://docs.github.com/en/rest
- GitHub API Reference: https://docs.github.com/en/rest/reference

## Version Used in SeedGPT
```
PyGithub==2.5.0
GitPython==3.1.43
```
