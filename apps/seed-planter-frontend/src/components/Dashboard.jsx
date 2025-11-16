import { useState } from 'react'
import {
  Activity,
  TrendingUp,
  GitPullRequest,
  CheckCircle,
  XCircle,
  Clock,
  DollarSign,
  Zap,
  AlertCircle,
  RefreshCw,
  Loader2,
  Heart,
  Code,
  FileText,
  Eye
} from 'lucide-react'
import { useDashboard } from '../hooks/useDashboard'

/**
 * Dashboard Component
 *
 * Real-time project progress dashboard showing:
 * - Project health score
 * - Agent activity and performance
 * - Cost metrics and usage
 * - Recent activity timeline
 */
export function Dashboard() {
  const [autoRefresh, setAutoRefresh] = useState(true)
  const {
    metrics,
    recentActivity,
    loading,
    error,
    connected,
    refresh
  } = useDashboard({
    autoRefresh,
    refreshInterval: 30000,
    enableWebSocket: false // Enable when WebSocket endpoint is ready
  })

  const [refreshing, setRefreshing] = useState(false)

  const handleRefresh = async () => {
    setRefreshing(true)
    await refresh()
    setTimeout(() => setRefreshing(false), 500)
  }

  if (loading && !metrics) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-primary-50 via-white to-purple-50 flex items-center justify-center">
        <div className="text-center">
          <Loader2 className="w-12 h-12 text-primary-600 animate-spin mx-auto mb-4" />
          <p className="text-gray-600">Loading dashboard...</p>
        </div>
      </div>
    )
  }

  if (error && !metrics) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-primary-50 via-white to-purple-50 flex items-center justify-center">
        <div className="card max-w-md text-center">
          <AlertCircle className="w-12 h-12 text-red-500 mx-auto mb-4" />
          <h2 className="text-xl font-semibold mb-2">Dashboard Unavailable</h2>
          <p className="text-gray-600 mb-4">{error}</p>
          <button onClick={handleRefresh} className="btn-primary">
            Try Again
          </button>
        </div>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-primary-50 via-white to-purple-50">
      {/* Header */}
      <header className="bg-white border-b border-gray-200 sticky top-0 z-10">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              <Activity className="w-8 h-8 text-primary-600" />
              <div>
                <h1 className="text-2xl font-bold text-gray-900">Project Dashboard</h1>
                <p className="text-sm text-gray-600">{metrics?.user_email}</p>
              </div>
            </div>

            <div className="flex items-center gap-4">
              {/* Connection Status */}
              {connected && (
                <div className="flex items-center gap-2 text-sm text-green-600">
                  <div className="w-2 h-2 bg-green-500 rounded-full animate-pulse"></div>
                  Live
                </div>
              )}

              {/* Auto-refresh Toggle */}
              <label className="flex items-center gap-2 text-sm cursor-pointer">
                <input
                  type="checkbox"
                  checked={autoRefresh}
                  onChange={(e) => setAutoRefresh(e.target.checked)}
                  className="rounded text-primary-600"
                />
                Auto-refresh
              </label>

              {/* Manual Refresh */}
              <button
                onClick={handleRefresh}
                disabled={refreshing}
                className="btn-secondary flex items-center gap-2"
              >
                <RefreshCw className={`w-4 h-4 ${refreshing ? 'animate-spin' : ''}`} />
                Refresh
              </button>
            </div>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="space-y-8">
          {/* Project Health & Overview */}
          <section>
            <h2 className="text-lg font-semibold mb-4">Project Health</h2>
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
              <HealthScoreCard health={metrics?.project_health} />
              <MetricCard
                title="Tasks Today"
                value={metrics?.project_health?.tasks_completed_today || 0}
                subtitle={`${metrics?.project_health?.tasks_completed_this_week || 0} this week`}
                icon={CheckCircle}
                color="green"
              />
              <MetricCard
                title="PRs Created"
                value={metrics?.project_health?.prs_created_today || 0}
                subtitle={`${metrics?.project_health?.open_prs_count || 0} open`}
                icon={GitPullRequest}
                color="blue"
              />
              <MetricCard
                title="Active Issues"
                value={metrics?.project_health?.active_issues_count || 0}
                subtitle="In backlog"
                icon={FileText}
                color="purple"
              />
            </div>
          </section>

          {/* Cost & Usage Metrics */}
          <section>
            <h2 className="text-lg font-semibold mb-4">Usage & Costs</h2>
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
              <UsageCard costMetrics={metrics?.cost_metrics} />
              <MetricCard
                title="Estimated Cost"
                value={`$${metrics?.cost_metrics?.estimated_monthly_cost?.toFixed(2) || '0.00'}`}
                subtitle={`$${metrics?.cost_metrics?.cost_per_operation?.toFixed(3) || '0.000'} per operation`}
                icon={DollarSign}
                color="green"
              />
              <MetricCard
                title="Projects Created"
                value={metrics?.cost_metrics?.projects_created_count || 0}
                subtitle="Total projects"
                icon={Code}
                color="indigo"
              />
              <MetricCard
                title="Subscription"
                value={metrics?.subscription_tier || 'Free'}
                subtitle={`${metrics?.cost_metrics?.monthly_operations_limit || 0} ops/month`}
                icon={Zap}
                color="yellow"
              />
            </div>
          </section>

          {/* Agent Performance */}
          <section>
            <h2 className="text-lg font-semibold mb-4">Agent Performance</h2>
            <div className="card">
              <AgentMetricsTable agentMetrics={metrics?.agent_metrics || []} />
            </div>
          </section>

          {/* Recent Activity Timeline */}
          <section>
            <h2 className="text-lg font-semibold mb-4">Recent Activity</h2>
            <div className="card">
              <ActivityTimeline activities={recentActivity} />
            </div>
          </section>
        </div>
      </main>
    </div>
  )
}

/**
 * Health Score Card with visual indicator
 */
function HealthScoreCard({ health }) {
  const score = health?.health_score || 0
  const getScoreColor = (score) => {
    if (score >= 80) return 'text-green-600'
    if (score >= 60) return 'text-yellow-600'
    return 'text-red-600'
  }

  const getScoreBgColor = (score) => {
    if (score >= 80) return 'bg-green-100'
    if (score >= 60) return 'bg-yellow-100'
    return 'bg-red-100'
  }

  return (
    <div className="card">
      <div className="flex items-start justify-between mb-3">
        <div>
          <p className="text-sm text-gray-600">Health Score</p>
          <div className="flex items-baseline gap-2">
            <p className={`text-3xl font-bold ${getScoreColor(score)}`}>
              {score.toFixed(0)}
            </p>
            <span className="text-gray-500">/100</span>
          </div>
        </div>
        <div className={`p-2 rounded-lg ${getScoreBgColor(score)}`}>
          <Heart className={`w-6 h-6 ${getScoreColor(score)}`} />
        </div>
      </div>

      {/* Progress Bar */}
      <div className="w-full bg-gray-200 rounded-full h-2 mb-2">
        <div
          className={`h-2 rounded-full transition-all duration-500 ${
            score >= 80 ? 'bg-green-500' :
            score >= 60 ? 'bg-yellow-500' :
            'bg-red-500'
          }`}
          style={{ width: `${score}%` }}
        />
      </div>

      <p className="text-xs text-gray-500">
        Deployment: {health?.deployment_status || 'unknown'}
      </p>
    </div>
  )
}

/**
 * Usage Card with progress bar
 */
function UsageCard({ costMetrics }) {
  const used = costMetrics?.total_ai_operations || 0
  const limit = costMetrics?.monthly_operations_limit || 100
  const percent = costMetrics?.operations_used_percent || 0

  const getUsageColor = (percent) => {
    if (percent >= 90) return 'text-red-600'
    if (percent >= 70) return 'text-yellow-600'
    return 'text-green-600'
  }

  const getUsageBgColor = (percent) => {
    if (percent >= 90) return 'bg-red-500'
    if (percent >= 70) return 'bg-yellow-500'
    return 'bg-green-500'
  }

  return (
    <div className="card">
      <div className="flex items-start justify-between mb-3">
        <div>
          <p className="text-sm text-gray-600">AI Operations</p>
          <div className="flex items-baseline gap-2">
            <p className={`text-2xl font-bold ${getUsageColor(percent)}`}>
              {used}
            </p>
            <span className="text-gray-500">/ {limit}</span>
          </div>
        </div>
        <div className="p-2 rounded-lg bg-primary-100">
          <Zap className="w-6 h-6 text-primary-600" />
        </div>
      </div>

      {/* Progress Bar */}
      <div className="w-full bg-gray-200 rounded-full h-2 mb-2">
        <div
          className={`h-2 rounded-full transition-all duration-500 ${getUsageBgColor(percent)}`}
          style={{ width: `${Math.min(100, percent)}%` }}
        />
      </div>

      <p className="text-xs text-gray-500">
        {percent.toFixed(1)}% used this month
      </p>
    </div>
  )
}

/**
 * Generic Metric Card
 */
function MetricCard({ title, value, subtitle, icon: Icon, color = 'primary' }) {
  const colorClasses = {
    primary: 'bg-primary-100 text-primary-600',
    green: 'bg-green-100 text-green-600',
    blue: 'bg-blue-100 text-blue-600',
    purple: 'bg-purple-100 text-purple-600',
    yellow: 'bg-yellow-100 text-yellow-600',
    red: 'bg-red-100 text-red-600',
    indigo: 'bg-indigo-100 text-indigo-600',
  }

  return (
    <div className="card">
      <div className="flex items-start justify-between">
        <div>
          <p className="text-sm text-gray-600 mb-1">{title}</p>
          <p className="text-3xl font-bold text-gray-900 mb-1">{value}</p>
          <p className="text-xs text-gray-500">{subtitle}</p>
        </div>
        <div className={`p-2 rounded-lg ${colorClasses[color] || colorClasses.primary}`}>
          <Icon className="w-6 h-6" />
        </div>
      </div>
    </div>
  )
}

/**
 * Agent Metrics Table
 */
function AgentMetricsTable({ agentMetrics }) {
  if (!agentMetrics || agentMetrics.length === 0) {
    return (
      <div className="text-center py-8 text-gray-500">
        <Activity className="w-12 h-12 mx-auto mb-2 opacity-50" />
        <p>No agent activity yet</p>
      </div>
    )
  }

  return (
    <div className="overflow-x-auto">
      <table className="w-full">
        <thead>
          <tr className="border-b border-gray-200">
            <th className="text-left py-3 px-4 text-sm font-semibold text-gray-700">Agent Type</th>
            <th className="text-center py-3 px-4 text-sm font-semibold text-gray-700">Attempts</th>
            <th className="text-center py-3 px-4 text-sm font-semibold text-gray-700">Success Rate</th>
            <th className="text-center py-3 px-4 text-sm font-semibold text-gray-700">Merge Rate</th>
            <th className="text-center py-3 px-4 text-sm font-semibold text-gray-700">Avg Time</th>
          </tr>
        </thead>
        <tbody>
          {agentMetrics.map((agent, idx) => (
            <tr key={idx} className="border-b border-gray-100 hover:bg-gray-50">
              <td className="py-3 px-4">
                <div className="flex items-center gap-2">
                  <Code className="w-4 h-4 text-gray-400" />
                  <span className="font-medium capitalize">{agent.agent_type}</span>
                </div>
              </td>
              <td className="text-center py-3 px-4">
                <span className="text-gray-600">{agent.total_attempts}</span>
              </td>
              <td className="text-center py-3 px-4">
                <SuccessRateBadge rate={agent.success_rate} />
              </td>
              <td className="text-center py-3 px-4">
                <SuccessRateBadge rate={agent.merge_rate} />
              </td>
              <td className="text-center py-3 px-4 text-gray-600 text-sm">
                {agent.avg_time_to_resolve_minutes
                  ? `${Math.round(agent.avg_time_to_resolve_minutes)}m`
                  : '-'
                }
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  )
}

/**
 * Success Rate Badge
 */
function SuccessRateBadge({ rate }) {
  const percentage = (rate * 100).toFixed(0)
  const getBadgeColor = (rate) => {
    if (rate >= 0.8) return 'bg-green-100 text-green-700'
    if (rate >= 0.6) return 'bg-yellow-100 text-yellow-700'
    return 'bg-red-100 text-red-700'
  }

  return (
    <span className={`px-2 py-1 rounded-full text-xs font-medium ${getBadgeColor(rate)}`}>
      {percentage}%
    </span>
  )
}

/**
 * Activity Timeline Component
 */
function ActivityTimeline({ activities }) {
  if (!activities || activities.length === 0) {
    return (
      <div className="text-center py-8 text-gray-500">
        <Clock className="w-12 h-12 mx-auto mb-2 opacity-50" />
        <p>No recent activity</p>
      </div>
    )
  }

  return (
    <div className="space-y-4">
      {activities.map((activity, idx) => (
        <ActivityItem key={idx} activity={activity} />
      ))}
    </div>
  )
}

/**
 * Individual Activity Item
 */
function ActivityItem({ activity }) {
  const getStatusIcon = (status) => {
    switch (status) {
      case 'merged':
        return <CheckCircle className="w-5 h-5 text-green-500" />
      case 'resolved':
        return <GitPullRequest className="w-5 h-5 text-blue-500" />
      case 'failed':
        return <XCircle className="w-5 h-5 text-red-500" />
      case 'closed':
        return <XCircle className="w-5 h-5 text-gray-500" />
      default:
        return <Clock className="w-5 h-5 text-yellow-500" />
    }
  }

  const getStatusBadge = (status) => {
    const classes = {
      merged: 'bg-green-100 text-green-700',
      resolved: 'bg-blue-100 text-blue-700',
      failed: 'bg-red-100 text-red-700',
      closed: 'bg-gray-100 text-gray-700',
      pending: 'bg-yellow-100 text-yellow-700',
    }
    return (
      <span className={`px-2 py-1 rounded-full text-xs font-medium ${classes[status] || classes.pending}`}>
        {status}
      </span>
    )
  }

  const formatTimeAgo = (isoString) => {
    const date = new Date(isoString)
    const now = new Date()
    const diffMs = now - date
    const diffMins = Math.floor(diffMs / 60000)
    const diffHours = Math.floor(diffMins / 60)
    const diffDays = Math.floor(diffHours / 24)

    if (diffDays > 0) return `${diffDays}d ago`
    if (diffHours > 0) return `${diffHours}h ago`
    if (diffMins > 0) return `${diffMins}m ago`
    return 'Just now'
  }

  return (
    <div className="flex items-start gap-4 p-4 bg-gray-50 rounded-lg hover:bg-gray-100 transition-colors">
      <div className="mt-1">
        {getStatusIcon(activity.status)}
      </div>

      <div className="flex-1 min-w-0">
        <div className="flex items-start justify-between gap-2 mb-1">
          <h4 className="font-medium text-gray-900 truncate">
            {activity.issue_title}
          </h4>
          {getStatusBadge(activity.status)}
        </div>

        <div className="flex items-center gap-4 text-sm text-gray-600">
          <span className="flex items-center gap-1">
            <FileText className="w-3 h-3" />
            Issue #{activity.issue_number}
          </span>

          {activity.pr_number && (
            <span className="flex items-center gap-1">
              <GitPullRequest className="w-3 h-3" />
              PR #{activity.pr_number}
            </span>
          )}

          <span className="flex items-center gap-1">
            <Code className="w-3 h-3" />
            {activity.files_changed} files
          </span>

          {activity.time_to_resolve_minutes && (
            <span className="flex items-center gap-1">
              <Clock className="w-3 h-3" />
              {Math.round(activity.time_to_resolve_minutes)}m
            </span>
          )}

          <span className="flex items-center gap-1">
            <Clock className="w-3 h-3" />
            {formatTimeAgo(activity.created_at)}
          </span>
        </div>

        {activity.labels && activity.labels.length > 0 && (
          <div className="flex gap-2 mt-2">
            {activity.labels.slice(0, 3).map((label, idx) => (
              <span
                key={idx}
                className="px-2 py-0.5 bg-white border border-gray-200 rounded text-xs text-gray-600"
              >
                {label}
              </span>
            ))}
          </div>
        )}

        {activity.error_message && (
          <div className="mt-2 p-2 bg-red-50 border border-red-100 rounded text-xs text-red-700">
            <AlertCircle className="w-3 h-3 inline mr-1" />
            {activity.error_message}
          </div>
        )}
      </div>
    </div>
  )
}

export default Dashboard
