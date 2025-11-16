# Dashboard API Documentation

## Overview

The Dashboard API provides real-time insights into project progress, agent activity, cost metrics, and overall project health for SeedGPT users.

**Base URL:** `/api/v1/dashboard`

**Authentication:** All dashboard endpoints require a valid JWT token in the Authorization header.

```
Authorization: Bearer <your_jwt_token>
```

---

## Endpoints

### 1. Get Dashboard Metrics

**`GET /api/v1/dashboard/metrics`**

Retrieves comprehensive dashboard metrics including project health, cost tracking, agent performance, and recent activity.

#### Request

```bash
curl -X GET "https://api.seedgpt.com/api/v1/dashboard/metrics" \
  -H "Authorization: Bearer <your_token>"
```

#### Response

```json
{
  "user_email": "user@example.com",
  "subscription_tier": "pro",
  "project_health": {
    "health_score": 85.5,
    "tasks_completed_today": 3,
    "tasks_completed_this_week": 15,
    "prs_created_today": 4,
    "prs_merged_today": 3,
    "active_issues_count": 12,
    "open_prs_count": 3,
    "deployment_status": "healthy",
    "last_deployment_at": "2025-11-16T14:30:00Z"
  },
  "cost_metrics": {
    "total_ai_operations": 450,
    "monthly_operations_limit": 1000,
    "operations_used_percent": 45.0,
    "estimated_monthly_cost": 22.50,
    "cost_per_operation": 0.05,
    "projects_created_count": 2,
    "issues_generated_count": 48,
    "prs_created_count": 36
  },
  "agent_metrics": [
    {
      "agent_type": "feature",
      "total_attempts": 25,
      "resolved_count": 22,
      "merged_count": 20,
      "failed_count": 3,
      "success_rate": 0.88,
      "merge_rate": 0.80,
      "avg_time_to_resolve_minutes": 45.5,
      "avg_time_to_merge_minutes": 180.2
    },
    {
      "agent_type": "bug",
      "total_attempts": 15,
      "resolved_count": 14,
      "merged_count": 13,
      "failed_count": 1,
      "success_rate": 0.93,
      "merge_rate": 0.87,
      "avg_time_to_resolve_minutes": 30.0,
      "avg_time_to_merge_minutes": 90.5
    }
  ],
  "recent_activity": [
    {
      "issue_number": 42,
      "issue_title": "Add user authentication system",
      "issue_type": "feature",
      "labels": ["feature", "backend"],
      "status": "merged",
      "pr_number": 45,
      "created_at": "2025-11-16T10:00:00Z",
      "resolved_at": "2025-11-16T10:45:00Z",
      "merged_at": "2025-11-16T13:20:00Z",
      "time_to_resolve_minutes": 45,
      "time_to_merge_minutes": 200,
      "files_changed": 8,
      "error_message": null
    }
  ],
  "timestamp": "2025-11-16T15:00:00Z"
}
```

#### Response Fields

| Field | Type | Description |
|-------|------|-------------|
| `user_email` | string | Current user's email |
| `subscription_tier` | string | User's subscription tier (free, basic, pro, business) |
| `project_health` | object | Project health indicators |
| `project_health.health_score` | float | Overall health score (0-100) |
| `project_health.tasks_completed_today` | int | Tasks completed today |
| `project_health.tasks_completed_this_week` | int | Tasks completed this week |
| `project_health.prs_created_today` | int | PRs created today |
| `project_health.prs_merged_today` | int | PRs merged today |
| `project_health.active_issues_count` | int | Open issues in backlog |
| `project_health.open_prs_count` | int | Open pull requests |
| `project_health.deployment_status` | string | Deployment health (healthy, degraded, down, unknown) |
| `project_health.last_deployment_at` | string | ISO timestamp of last deployment |
| `cost_metrics` | object | Usage and cost tracking |
| `cost_metrics.total_ai_operations` | int | Total AI operations used |
| `cost_metrics.monthly_operations_limit` | int | Monthly operation quota |
| `cost_metrics.operations_used_percent` | float | Percentage of quota used (0-100) |
| `cost_metrics.estimated_monthly_cost` | float | Estimated cost in USD |
| `cost_metrics.cost_per_operation` | float | Average cost per operation |
| `cost_metrics.projects_created_count` | int | Total projects created |
| `cost_metrics.issues_generated_count` | int | Total issues generated |
| `cost_metrics.prs_created_count` | int | Total PRs created |
| `agent_metrics` | array | Performance metrics by agent type |
| `agent_metrics[].agent_type` | string | Type of agent (feature, bug, documentation, etc.) |
| `agent_metrics[].total_attempts` | int | Total resolution attempts |
| `agent_metrics[].resolved_count` | int | Successfully resolved issues |
| `agent_metrics[].merged_count` | int | Successfully merged PRs |
| `agent_metrics[].failed_count` | int | Failed attempts |
| `agent_metrics[].success_rate` | float | Success rate (0.0-1.0) |
| `agent_metrics[].merge_rate` | float | Merge rate (0.0-1.0) |
| `agent_metrics[].avg_time_to_resolve_minutes` | float | Average resolution time in minutes |
| `agent_metrics[].avg_time_to_merge_minutes` | float | Average merge time in minutes |
| `recent_activity` | array | Recent agent activity records |
| `timestamp` | string | Response generation timestamp |

---

### 2. Get Recent Activity

**`GET /api/v1/dashboard/activity/recent`**

Retrieves recent agent activity records with detailed execution information.

#### Query Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `limit` | int | 20 | Maximum number of records (max: 100) |

#### Request

```bash
curl -X GET "https://api.seedgpt.com/api/v1/dashboard/activity/recent?limit=50" \
  -H "Authorization: Bearer <your_token>"
```

#### Response

```json
[
  {
    "issue_number": 42,
    "issue_title": "Add user authentication system",
    "issue_type": "feature",
    "labels": ["feature", "backend"],
    "status": "merged",
    "pr_number": 45,
    "created_at": "2025-11-16T10:00:00Z",
    "resolved_at": "2025-11-16T10:45:00Z",
    "merged_at": "2025-11-16T13:20:00Z",
    "time_to_resolve_minutes": 45,
    "time_to_merge_minutes": 200,
    "files_changed": 8,
    "error_message": null
  },
  {
    "issue_number": 38,
    "issue_title": "Fix memory leak in data processor",
    "issue_type": "bug",
    "labels": ["bug", "performance"],
    "status": "failed",
    "pr_number": null,
    "created_at": "2025-11-16T09:00:00Z",
    "resolved_at": null,
    "merged_at": null,
    "time_to_resolve_minutes": null,
    "time_to_merge_minutes": null,
    "files_changed": 0,
    "error_message": "Build failed: Tests did not pass"
  }
]
```

#### Activity Status Values

| Status | Description |
|--------|-------------|
| `pending` | Issue resolution in progress |
| `resolved` | PR created successfully |
| `merged` | PR merged into main branch |
| `closed` | PR closed without merging |
| `failed` | Resolution attempt failed |

---

### 3. Get Time Series Metrics

**`GET /api/v1/dashboard/metrics/timeseries/{metric_name}`**

Retrieves time series data for dashboard charts and trend visualization.

#### Path Parameters

| Parameter | Type | Description |
|-----------|------|-------------|
| `metric_name` | string | Metric to fetch (see supported metrics below) |

#### Query Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `period` | string | daily | Aggregation period: hourly, daily, weekly |
| `days` | int | 7 | Number of days of historical data (max: 90) |

#### Supported Metrics

- `tasks_completed` - Number of tasks completed (merged PRs)
- `prs_created` - Number of PRs created
- `success_rate` - Agent success rate over time
- `operations_used` - AI operations consumed

#### Request

```bash
curl -X GET "https://api.seedgpt.com/api/v1/dashboard/metrics/timeseries/tasks_completed?period=daily&days=7" \
  -H "Authorization: Bearer <your_token>"
```

#### Response

```json
{
  "metric_name": "tasks_completed",
  "data_points": [
    {
      "timestamp": "2025-11-10T00:00:00Z",
      "value": 5.0,
      "label": "Nov 10"
    },
    {
      "timestamp": "2025-11-11T00:00:00Z",
      "value": 7.0,
      "label": "Nov 11"
    },
    {
      "timestamp": "2025-11-12T00:00:00Z",
      "value": 3.0,
      "label": "Nov 12"
    }
  ],
  "unit": "count",
  "period": "daily"
}
```

---

### 4. Health Check

**`GET /api/v1/dashboard/health`**

Simple health check endpoint for the dashboard service.

#### Request

```bash
curl -X GET "https://api.seedgpt.com/api/v1/dashboard/health"
```

#### Response

```json
{
  "status": "healthy",
  "service": "dashboard",
  "timestamp": "2025-11-16T15:00:00Z"
}
```

---

## Health Score Calculation

The project health score (0-100) is calculated using the following weighted components:

| Component | Weight | Description |
|-----------|--------|-------------|
| Agent Success Rate | 40% | Percentage of successful agent executions |
| PR Merge Rate | 30% | Percentage of PRs that get merged |
| Activity Level | 15% | Task completion frequency (5-20 tasks/week = optimal) |
| Issue Backlog | 10% | Healthy range: 5-15 open issues |
| Deployment Status | 5% | Current deployment health |

### Health Score Ranges

- **80-100**: Excellent - Project is thriving
- **60-79**: Good - Project is progressing well
- **40-59**: Fair - Some issues need attention
- **0-39**: Poor - Project needs immediate attention

---

## Agent Types

The system tracks performance for the following agent types:

| Type | Description |
|------|-------------|
| `feature` | New feature implementation |
| `bug` | Bug fixes |
| `documentation` | Documentation updates |
| `refactor` | Code refactoring |
| `test` | Test additions/fixes |
| `performance` | Performance improvements |
| `security` | Security fixes |
| `ci/cd` | CI/CD pipeline updates |
| `other` | Miscellaneous changes |

---

## Error Responses

### 401 Unauthorized

```json
{
  "detail": "Authentication required"
}
```

### 404 Not Found

```json
{
  "detail": "Usage metrics not found"
}
```

### 500 Internal Server Error

```json
{
  "error": "Internal server error",
  "detail": "Failed to generate dashboard metrics: <error_message>",
  "timestamp": "2025-11-16T15:00:00Z"
}
```

---

## Rate Limits

Dashboard API endpoints follow the standard rate limits:

- **Free Tier**: 60 requests/hour
- **Basic Tier**: 300 requests/hour
- **Pro Tier**: 1,000 requests/hour
- **Business Tier**: 5,000 requests/hour

---

## WebSocket Support (Coming Soon)

Real-time dashboard updates via WebSocket:

```
WS /api/v1/dashboard/live?token=<your_jwt_token>
```

### Message Types

- `metrics_update` - Partial metrics update
- `activity_update` - New activity record
- `full_refresh` - Full dashboard refresh needed

---

## Usage Example

### Python

```python
import requests

# Get dashboard metrics
response = requests.get(
    "https://api.seedgpt.com/api/v1/dashboard/metrics",
    headers={"Authorization": f"Bearer {token}"}
)

metrics = response.json()
print(f"Health Score: {metrics['project_health']['health_score']}")
print(f"Tasks Today: {metrics['project_health']['tasks_completed_today']}")
```

### JavaScript

```javascript
// Fetch dashboard metrics
const response = await fetch(
  'https://api.seedgpt.com/api/v1/dashboard/metrics',
  {
    headers: {
      'Authorization': `Bearer ${token}`,
      'Content-Type': 'application/json'
    }
  }
);

const metrics = await response.json();
console.log('Health Score:', metrics.project_health.health_score);
console.log('Operations Used:', metrics.cost_metrics.operations_used_percent);
```

### cURL

```bash
# Get comprehensive metrics
curl -X GET "https://api.seedgpt.com/api/v1/dashboard/metrics" \
  -H "Authorization: Bearer ${TOKEN}"

# Get recent activity
curl -X GET "https://api.seedgpt.com/api/v1/dashboard/activity/recent?limit=10" \
  -H "Authorization: Bearer ${TOKEN}"

# Get time series data
curl -X GET "https://api.seedgpt.com/api/v1/dashboard/metrics/timeseries/tasks_completed?period=daily&days=7" \
  -H "Authorization: Bearer ${TOKEN}"
```

---

## Notes

1. **Data Freshness**: Metrics are aggregated from the outcome tracker database and user metrics. Recent activity reflects the last 30 days by default.

2. **Time Zones**: All timestamps are in UTC (ISO 8601 format).

3. **Caching**: Dashboard metrics are not cached to ensure real-time accuracy. Consider client-side caching for performance.

4. **Authentication**: JWT tokens expire after 24 hours. Refresh tokens as needed.

5. **Future Enhancements**:
   - WebSocket support for live updates
   - GitHub API integration for real-time repository stats
   - Custom date range filters
   - Export functionality (CSV, JSON)
   - Webhook notifications for critical events

---

## Support

For questions or issues with the Dashboard API:

- Documentation: https://docs.seedgpt.com
- GitHub Issues: https://github.com/roeiba/SeedGPT/issues
- Email: support@seedgpt.com
