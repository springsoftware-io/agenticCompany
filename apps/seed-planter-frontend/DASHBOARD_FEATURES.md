# Dashboard Features

## Overview

The SeedGPT Dashboard provides real-time visibility into your autonomous project's progress, AI agent activity, cost tracking, and overall project health.

![Dashboard Preview](https://via.placeholder.com/800x400?text=Dashboard+Preview)

---

## Key Features

### 1. Project Health Score (0-100)

Visual indicator of overall project health based on:

- **Agent Success Rate** (40%) - How often agents successfully complete tasks
- **PR Merge Rate** (30%) - Percentage of PRs that get merged
- **Activity Level** (15%) - Task completion frequency
- **Issue Backlog** (10%) - Healthy issue count (5-15 optimal)
- **Deployment Status** (5%) - Current deployment health

**Health Ranges:**
- 🟢 80-100: Excellent
- 🟡 60-79: Good
- 🟠 40-59: Fair
- 🔴 0-39: Poor

### 2. Real-Time Metrics Cards

#### Today's Activity
- Tasks completed today
- Tasks completed this week
- PRs created and merged
- Active issues in backlog

#### Usage & Cost Tracking
- AI operations used vs. quota
- Estimated monthly cost
- Cost per operation
- Projects created count

#### Subscription Info
- Current tier (Free, Basic, Pro, Business)
- Monthly operation limits
- Usage percentage with visual progress bar
- Upgrade prompts at 80% capacity

### 3. Agent Performance Table

Track performance by agent type:

| Metric | Description |
|--------|-------------|
| **Agent Type** | feature, bug, documentation, etc. |
| **Attempts** | Total resolution attempts |
| **Success Rate** | Percentage of successful executions |
| **Merge Rate** | Percentage of merged PRs |
| **Avg Time** | Average resolution time in minutes |

**Visual Indicators:**
- 🟢 Green: 80%+ success rate
- 🟡 Yellow: 60-79% success rate
- 🔴 Red: <60% success rate

### 4. Activity Timeline

Real-time feed of agent actions showing:

- Issue title and number
- PR number and status
- Files changed
- Resolution time
- Labels and categorization
- Error messages (if failed)
- Timestamp and time ago

**Status Types:**
- ✅ Merged - PR successfully merged
- 🔵 Resolved - PR created and pending
- ❌ Failed - Resolution attempt failed
- ⭕ Closed - PR closed without merge
- 🕐 Pending - In progress

### 5. Auto-Refresh & Live Updates

- **Auto-refresh toggle** - Enable/disable automatic updates
- **Manual refresh button** - Refresh on demand
- **30-second interval** - Configurable refresh rate
- **WebSocket support** - Ready for real-time streaming (coming soon)
- **Live status indicator** - Shows connection status

---

## Technical Architecture

### Frontend Components

```
src/
├── components/
│   └── Dashboard.jsx          # Main dashboard component
├── hooks/
│   ├── useDashboard.js        # Dashboard data hook
│   └── useTimeSeriesMetrics.js # Chart data hook
└── utils/
    └── logger.js              # Structured logging
```

### Backend Endpoints

```
GET /api/v1/dashboard/metrics
GET /api/v1/dashboard/activity/recent
GET /api/v1/dashboard/metrics/timeseries/{metric_name}
GET /api/v1/dashboard/health
```

See [DASHBOARD_API.md](../../seed-planter-api/DASHBOARD_API.md) for full API documentation.

### Data Sources

1. **PostgreSQL Database**
   - User usage metrics
   - Subscription information
   - Billing data

2. **SQLite Outcome Tracker**
   - Agent execution history
   - Issue resolution outcomes
   - PR merge statistics
   - Performance metrics by type

3. **GitHub API** (Coming Soon)
   - Real-time repository stats
   - Open issues count
   - PR status
   - Deployment information

4. **Redis**
   - Task status caching
   - Real-time progress updates

---

## Usage

### Accessing the Dashboard

1. **Authentication Required**
   - Login with your SeedGPT account
   - Dashboard requires a valid JWT token

2. **Navigation**
   - Click "Dashboard" in the top navigation
   - Available after authentication

3. **View Options**
   - Desktop: Full multi-column layout
   - Tablet: Responsive 2-column grid
   - Mobile: Single column stack

### Understanding Your Metrics

#### Health Score Interpretation

**80-100 (Excellent)**
- Agents performing consistently well
- High PR merge rate
- Active development pace
- Healthy issue backlog

**60-79 (Good)**
- Generally positive progress
- Minor issues to address
- Consider reviewing failed tasks

**40-59 (Fair)**
- Success rate needs improvement
- Check agent error messages
- May need prompt tuning

**0-39 (Poor)**
- Critical attention needed
- Review agent configurations
- Check for blocking issues

#### Cost Optimization Tips

1. **Monitor Operation Usage**
   - Track daily/weekly patterns
   - Set alerts at 80% capacity
   - Plan upgrades before limits

2. **Analyze Cost per Operation**
   - Compare across agent types
   - Identify expensive operations
   - Optimize frequently-run tasks

3. **Review Agent Efficiency**
   - High success rate = better ROI
   - Failed attempts still count
   - Improve prompts to reduce retries

---

## Customization

### Refresh Interval

Change the auto-refresh rate in `useDashboard` hook:

```javascript
const { metrics } = useDashboard({
  autoRefresh: true,
  refreshInterval: 30000, // 30 seconds (default)
  enableWebSocket: false  // Enable for real-time updates
});
```

### Data Retention

Historical data is available for:
- **Recent Activity**: Last 30 days
- **Time Series**: Up to 90 days
- **Agent Metrics**: Lifetime aggregate

### Custom Filtering

Filter activity by agent type or status:

```javascript
const filteredActivity = recentActivity.filter(
  activity => activity.issue_type === 'feature'
);
```

---

## Performance Considerations

### API Call Optimization

- **Batch Requests**: Single `/metrics` call fetches all data
- **Conditional Refresh**: Only refresh when tab is active
- **Smart Polling**: Increase interval when idle
- **Client Caching**: Cache non-critical data

### Frontend Optimization

- **Lazy Loading**: Dashboard loads on-demand
- **Code Splitting**: Separate bundle from main app
- **Memoization**: React components use `useMemo`
- **Virtual Scrolling**: For long activity lists (coming soon)

---

## Troubleshooting

### Common Issues

#### "Authentication Required" Error

**Cause**: JWT token expired or missing

**Solution**:
1. Log out and log back in
2. Check localStorage for 'auth_token'
3. Verify token not expired (24h lifetime)

#### "Dashboard Unavailable" Error

**Cause**: Backend service or database issue

**Solution**:
1. Check API health: `GET /api/v1/dashboard/health`
2. Verify outcome tracker database exists
3. Check backend logs for errors

#### No Recent Activity Showing

**Cause**: No agent executions yet or data not recorded

**Solution**:
1. Wait for agents to run (check cron schedules)
2. Verify outcome tracker is recording data
3. Check `.seedgpt/outcomes.db` exists

#### Metrics Loading Slowly

**Cause**: Large dataset or database query performance

**Solution**:
1. Reduce activity limit parameter
2. Add database indexes (already configured)
3. Enable caching layer (Redis)

---

## Future Enhancements

### Phase 1 (Current)
- ✅ Basic metrics dashboard
- ✅ Agent performance tracking
- ✅ Cost monitoring
- ✅ Activity timeline
- ✅ Health score calculation

### Phase 2 (Next Release)
- 🔄 WebSocket real-time updates
- 🔄 GitHub API integration
- 🔄 Time series charts
- 🔄 Custom date range filters
- 🔄 Export to CSV/JSON

### Phase 3 (Future)
- 📋 Predictive analytics
- 📋 AI-powered insights
- 📋 Anomaly detection
- 📋 Performance recommendations
- 📋 Cost optimization suggestions
- 📋 Custom dashboards
- 📋 Team collaboration features
- 📋 Webhook notifications

---

## Security

### Authentication

- JWT-based authentication
- Token expiration after 24 hours
- Secure token storage (localStorage)
- HTTPS-only in production

### Authorization

- User can only see their own data
- Admin roles for multi-user projects
- API rate limiting by tier

### Data Privacy

- Metrics aggregated per user
- No sharing between users
- GDPR-compliant data handling
- Optional data retention controls

---

## Analytics & Monitoring

### Tracked Events

- Dashboard page views
- Refresh button clicks
- Auto-refresh toggles
- Metric API calls
- Error occurrences

### Performance Metrics

- API response times
- Frontend render times
- Data freshness
- Cache hit rates

---

## Support

### Documentation

- [API Documentation](../../seed-planter-api/DASHBOARD_API.md)
- [Main README](../../../README.md)
- [Architecture Guide](../../seed-planter-api/ARCHITECTURE.md)

### Getting Help

- GitHub Issues: https://github.com/roeiba/SeedGPT/issues
- Discussions: https://github.com/roeiba/SeedGPT/discussions
- Email: support@seedgpt.com

### Contributing

Contributions welcome! See:
- Feature requests: Create GitHub issue with `feature` label
- Bug reports: Create GitHub issue with `bug` label
- Pull requests: Follow contribution guidelines

---

## Changelog

### v1.0.0 (2025-11-16)

**Added:**
- Initial dashboard release
- Project health score calculation
- Agent performance metrics
- Cost tracking
- Activity timeline
- Auto-refresh functionality
- Responsive design
- API documentation

**Known Issues:**
- WebSocket not yet implemented
- GitHub stats are mocked
- Time series charts show sample data
- No export functionality

---

## License

MIT License - See [LICENSE](../../../LICENSE) for details
