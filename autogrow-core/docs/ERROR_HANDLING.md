# Error Handling Guide

## Overview

This project implements comprehensive error handling for all API interactions, with specific support for:

- **Claude CLI errors** (credit balance, authentication, etc.)
- **Anthropic API errors** (rate limits, authentication, etc.)
- **GitHub API errors** (rate limits, permissions, etc.)
- **Git operations** (merge conflicts, push failures, etc.)

## Exception Hierarchy

```
AutoGrowException (base)
├── ConfigurationError
│   ├── MissingEnvironmentVariableError
│   └── InvalidConfigurationError
├── APIError
│   ├── GitHubAPIError
│   ├── AnthropicAPIError
│   ├── RateLimitError
│   ├── AuthenticationError
│   └── CreditBalanceError (NEW)
├── GitError
│   ├── BranchError
│   ├── CommitError
│   ├── PushError
│   ├── MergeConflictError
│   └── DirtyWorkingTreeError
├── IssueError
│   ├── IssueNotFoundError
│   ├── InvalidIssueFormatError
│   └── DuplicateIssueError
├── AgentError
│   ├── AgentResponseError
│   ├── AgentTimeoutError
│   └── JSONParseError
└── ValidationError
    ├── ProjectBriefValidationError
    └── InvalidLabelError
```

## Common Error Scenarios

### 1. Credit Balance Too Low

**Error Message**:
```
❌ Claude CLI credit balance is too low. Please add credits to your Claude account.
```

**Solution**:
1. Visit https://claude.ai/settings/billing
2. Add credits to your account
3. Re-run the workflow

**Exception Type**: `CreditBalanceError`

### 2. API Rate Limit Exceeded

**Error Message**:
```
❌ Anthropic API rate limit exceeded.
Please retry after: 1731585600
```

**Solution**:
1. Wait for the specified time
2. Consider implementing rate limiting in your code
3. Upgrade your API plan if needed

**Exception Type**: `RateLimitError`

### 3. Authentication Failed

**Error Message**:
```
❌ Authentication failed. Please check your API credentials.
```

**Solution**:
1. Verify `ANTHROPIC_API_KEY` is set correctly
2. Check if the API key is valid and not expired
3. Ensure the key has proper permissions

**Exception Type**: `AuthenticationError`

### 4. GitHub API Errors

**Error Message**:
```
❌ GitHub API error occurred.
```

**Solution**:
1. Check `GITHUB_TOKEN` is valid
2. Verify repository permissions
3. Check GitHub API status: https://www.githubstatus.com/

**Exception Type**: `GitHubAPIError`

## Error Handling Best Practices

### 1. Always Use Specific Exceptions

❌ **Bad**:
```python
try:
    result = call_api()
except Exception as e:
    print(f"Error: {e}")
```

✅ **Good**:
```python
try:
    result = call_api()
except CreditBalanceError as e:
    logger.error("Credit balance too low. Please add credits.")
    sys.exit(1)
except RateLimitError as e:
    logger.error(f"Rate limit exceeded. Retry after: {e.retry_after}")
    sys.exit(1)
except AnthropicAPIError as e:
    logger.error(f"API error: {e}")
    sys.exit(1)
```

### 2. Include Error Details in Logs

```python
except CreditBalanceError as e:
    logger.error(
        "Credit balance error",
        extra={
            "service": e.service,
            "error_details": e.details
        }
    )
```

### 3. Provide Actionable Error Messages

Include:
- What went wrong
- Why it happened (if known)
- How to fix it
- Where to get help

### 4. Use Error Converters

```python
from utils.exceptions import get_exception_for_anthropic_error

try:
    result = agent.query(prompt)
except Exception as e:
    # Convert to appropriate exception type
    raise get_exception_for_anthropic_error(e, "Failed to call Claude API")
```

## Monitoring and Debugging

### Checking Logs

All errors are logged with structured data:

```bash
# View recent errors
grep "ERROR" logs/agent.log | tail -20

# View specific error type
grep "CreditBalanceError" logs/agent.log

# View error details
grep -A 5 "ERROR" logs/agent.log
```

### Error Metrics

Track error rates in your monitoring system:

- `credit_balance_errors_total`
- `rate_limit_errors_total`
- `authentication_errors_total`
- `api_errors_total`

## Testing Error Handling

```bash
# Test credit balance error detection
python3 .agents/scripts/test_credit_error.py

# Test with dry mode to avoid actual API calls
DRY_MODE=true python3 .github/scripts/issue_generator.py
```

## Related Documentation

- [Exception Classes](../src/utils/exceptions.py) - Full exception definitions
- [Error Handling Improvements](./.agents/ERROR_HANDLING_IMPROVEMENTS.md) - Recent changes
- [Claude CLI Documentation](https://code.claude.com/docs/en/headless) - Official docs
- [Anthropic API Errors](https://docs.anthropic.com/claude/reference/errors) - API error reference

## Support

If you encounter an error not covered here:

1. Check the logs for detailed error information
2. Review the exception type and details
3. Consult the related documentation
4. Open an issue with the error details and logs
