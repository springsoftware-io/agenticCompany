# Test Fix Summary - API Response Schema Mismatch

## Issue
GitHub Actions CI/CD test failure in `test_projects_api.py::TestProjectsAPI::test_create_project_has_required_fields`

**Error:**
```
AssertionError: Missing required field: project_id
assert 'project_id' in {'task_id': 'a5d99c58-ebff-4302-9a68-f4273fc9c2ad', ...}
```

## Root Cause
The tests were written for an older synchronous API design, but the implementation was updated to use an **async task-based architecture**. The mismatch:

### Old Design (What Tests Expected)
```json
POST /api/v1/projects
Response: {
  "project_id": "uuid",
  "status": "initializing",
  "websocket_url": "ws://...",
  "created_at": "...",
  "estimated_completion_time": 120
}
```

### New Design (Current Implementation)
```json
POST /api/v1/projects
Response: {
  "task_id": "uuid",
  "status": "initializing",
  "message": "Project creation started...",
  "created_at": "...",
  "estimated_completion_time": 120
}
```

## Architecture Change
The API now uses a **task-based async pattern**:

1. **POST /api/v1/projects** - Returns immediately with `task_id`
2. **GET /api/v1/tasks/{task_id}** - Poll for progress and results
3. **WebSocket /api/v1/projects/{project_id}/ws** - Real-time updates (after project_id is available)

This allows:
- Immediate response (no blocking)
- Long-running operations in background
- Progress tracking via polling or WebSocket
- Better scalability

## Changes Made

### Updated Tests
Fixed 5 test cases in `test_projects_api.py`:

1. **test_create_project_has_required_fields**
   - Changed expected fields from `["project_id", "websocket_url", ...]` to `["task_id", "message", ...]`

2. **test_create_project_id_is_uuid** → **test_create_project_task_id_is_uuid**
   - Now validates `task_id` instead of `project_id`

3. **test_create_project_websocket_url_format** → **test_create_project_message_exists**
   - Validates status message instead of WebSocket URL (not in initial response)

4. **test_create_project_with_minimal_data**
   - Checks for `task_id` instead of `project_id`

5. **test_create_multiple_projects_returns_unique_ids**
   - Validates unique `task_id` values

### Response Models (No Changes Needed)
The implementation already uses correct models:
- `PlantSeedResponse` - Initial response with task_id
- `TaskStatusResponse` - Progress polling response with project_id (when available)

## Testing
All tests should now pass. The workflow will:
1. Create project → Get task_id
2. Poll task status → Get progress updates
3. Eventually get project_id, org_url, repo_url, deployment_url

## Next Steps
Consider adding tests for:
- Task status polling endpoint (`GET /api/v1/tasks/{task_id}`)
- WebSocket connection after project creation
- Task completion flow
- Error handling for failed tasks

## Related Files
- `/apps/seed-planter-api/src/main.py` - Endpoint implementation
- `/apps/seed-planter-api/src/models.py` - Response models
- `/apps/seed-planter-api/tests/test_projects_api.py` - Fixed tests
