import { useState, useEffect, useCallback, useRef } from 'react'
import Logger from '../utils/logger'

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000'
const logger = new Logger('Dashboard')

/**
 * Custom hook for real-time dashboard data
 *
 * Features:
 * - Fetches comprehensive dashboard metrics
 * - WebSocket support for live updates (optional)
 * - Auto-refresh with configurable interval
 * - Error handling and retry logic
 */
export function useDashboard(options = {}) {
  const {
    autoRefresh = true,
    refreshInterval = 30000, // 30 seconds
    enableWebSocket = false,
  } = options

  const [metrics, setMetrics] = useState(null)
  const [recentActivity, setRecentActivity] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)
  const [connected, setConnected] = useState(false)

  const wsRef = useRef(null)
  const intervalRef = useRef(null)
  const authTokenRef = useRef(null)

  // Get auth token from localStorage
  const getAuthToken = useCallback(() => {
    const token = localStorage.getItem('auth_token')
    authTokenRef.current = token
    return token
  }, [])

  // Fetch dashboard metrics
  const fetchMetrics = useCallback(async () => {
    const token = getAuthToken()

    if (!token) {
      logger.warn('No authentication token found')
      setError('Authentication required')
      setLoading(false)
      return null
    }

    try {
      logger.api(`GET ${API_BASE_URL}/api/v1/dashboard/metrics`)

      const response = await fetch(`${API_BASE_URL}/api/v1/dashboard/metrics`, {
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json',
        },
      })

      if (response.status === 401) {
        logger.error('Authentication failed - token may be expired')
        setError('Authentication expired. Please log in again.')
        setLoading(false)
        return null
      }

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}))
        logger.error('Failed to fetch dashboard metrics:', errorData)
        throw new Error(errorData.detail || 'Failed to fetch dashboard metrics')
      }

      const data = await response.json()
      logger.info('Dashboard metrics loaded successfully', {
        healthScore: data.project_health?.health_score,
        tasksToday: data.project_health?.tasks_completed_today,
        agentTypes: data.agent_metrics?.length || 0,
      })

      setMetrics(data)
      setError(null)
      return data

    } catch (err) {
      logger.error('Error fetching dashboard metrics:', err.message)
      setError(err.message)
      return null
    } finally {
      setLoading(false)
    }
  }, [getAuthToken])

  // Fetch recent activity
  const fetchRecentActivity = useCallback(async (limit = 20) => {
    const token = getAuthToken()

    if (!token) {
      return []
    }

    try {
      logger.api(`GET ${API_BASE_URL}/api/v1/dashboard/activity/recent?limit=${limit}`)

      const response = await fetch(
        `${API_BASE_URL}/api/v1/dashboard/activity/recent?limit=${limit}`,
        {
          headers: {
            'Authorization': `Bearer ${token}`,
            'Content-Type': 'application/json',
          },
        }
      )

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}))
        logger.error('Failed to fetch recent activity:', errorData)
        return []
      }

      const data = await response.json()
      logger.info(`Loaded ${data.length} recent activity records`)

      setRecentActivity(data)
      return data

    } catch (err) {
      logger.error('Error fetching recent activity:', err.message)
      return []
    }
  }, [getAuthToken])

  // Refresh all dashboard data
  const refresh = useCallback(async () => {
    logger.info('Refreshing dashboard data...')
    setLoading(true)
    const [metricsData, activityData] = await Promise.all([
      fetchMetrics(),
      fetchRecentActivity(),
    ])
    setLoading(false)
    return { metrics: metricsData, activity: activityData }
  }, [fetchMetrics, fetchRecentActivity])

  // WebSocket connection for real-time updates
  const connectWebSocket = useCallback(() => {
    if (!enableWebSocket) return

    const token = getAuthToken()
    if (!token) {
      logger.warn('Cannot connect WebSocket: No auth token')
      return
    }

    // Close existing connection if any
    if (wsRef.current) {
      wsRef.current.close()
    }

    // Construct WebSocket URL
    const wsUrl = API_BASE_URL.replace('http', 'ws')
    const ws = new WebSocket(`${wsUrl}/api/v1/dashboard/live?token=${token}`)

    ws.onopen = () => {
      logger.websocket('Connected to dashboard WebSocket')
      setConnected(true)
      setError(null)
    }

    ws.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data)
        logger.websocket('Received real-time update:', data)

        // Handle different message types
        if (data.type === 'metrics_update') {
          setMetrics(prev => ({ ...prev, ...data.payload }))
        } else if (data.type === 'activity_update') {
          setRecentActivity(prev => [data.payload, ...prev.slice(0, 19)])
        } else if (data.type === 'full_refresh') {
          refresh()
        }
      } catch (err) {
        logger.error('Error parsing WebSocket message:', err.message)
      }
    }

    ws.onerror = (error) => {
      logger.error('WebSocket error:', error)
      setError('Real-time connection error')
      setConnected(false)
    }

    ws.onclose = () => {
      logger.websocket('Disconnected from dashboard WebSocket')
      setConnected(false)

      // Attempt reconnection after 5 seconds
      setTimeout(() => {
        if (enableWebSocket && authTokenRef.current) {
          logger.info('Attempting WebSocket reconnection...')
          connectWebSocket()
        }
      }, 5000)
    }

    wsRef.current = ws
  }, [enableWebSocket, getAuthToken, refresh])

  // Disconnect WebSocket
  const disconnectWebSocket = useCallback(() => {
    if (wsRef.current) {
      logger.websocket('Closing WebSocket connection')
      wsRef.current.close()
      wsRef.current = null
      setConnected(false)
    }
  }, [])

  // Initial load
  useEffect(() => {
    logger.info('Initializing dashboard...', { autoRefresh, refreshInterval, enableWebSocket })
    refresh()

    // Setup WebSocket if enabled
    if (enableWebSocket) {
      connectWebSocket()
    }

    // Setup auto-refresh
    if (autoRefresh && !enableWebSocket) {
      logger.info(`Setting up auto-refresh every ${refreshInterval}ms`)
      intervalRef.current = setInterval(refresh, refreshInterval)
    }

    // Cleanup
    return () => {
      if (intervalRef.current) {
        clearInterval(intervalRef.current)
      }
      disconnectWebSocket()
    }
  }, [autoRefresh, refreshInterval, enableWebSocket, refresh, connectWebSocket, disconnectWebSocket])

  return {
    // Data
    metrics,
    recentActivity,

    // State
    loading,
    error,
    connected,

    // Actions
    refresh,
    fetchMetrics,
    fetchRecentActivity,
    connectWebSocket,
    disconnectWebSocket,
  }
}

/**
 * Hook for fetching time series metrics for charts
 */
export function useTimeSeriesMetrics(metricName, period = 'daily', days = 7) {
  const [data, setData] = useState(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)

  const getAuthToken = useCallback(() => {
    return localStorage.getItem('auth_token')
  }, [])

  const fetchTimeSeries = useCallback(async () => {
    const token = getAuthToken()

    if (!token) {
      setError('Authentication required')
      setLoading(false)
      return
    }

    try {
      logger.api(`GET ${API_BASE_URL}/api/v1/dashboard/metrics/timeseries/${metricName}`)

      const response = await fetch(
        `${API_BASE_URL}/api/v1/dashboard/metrics/timeseries/${metricName}?period=${period}&days=${days}`,
        {
          headers: {
            'Authorization': `Bearer ${token}`,
            'Content-Type': 'application/json',
          },
        }
      )

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}))
        throw new Error(errorData.detail || 'Failed to fetch time series data')
      }

      const timeSeriesData = await response.json()
      logger.info(`Loaded time series data for ${metricName}`, {
        dataPoints: timeSeriesData.data_points?.length || 0,
      })

      setData(timeSeriesData)
      setError(null)

    } catch (err) {
      logger.error(`Error fetching time series for ${metricName}:`, err.message)
      setError(err.message)
    } finally {
      setLoading(false)
    }
  }, [metricName, period, days, getAuthToken])

  useEffect(() => {
    fetchTimeSeries()
  }, [fetchTimeSeries])

  return {
    data,
    loading,
    error,
    refetch: fetchTimeSeries,
  }
}
