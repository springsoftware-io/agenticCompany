"""Dashboard API routes for real-time project progress monitoring"""

import logging
from datetime import datetime, timedelta
from typing import Optional, List, Dict, Any
from pathlib import Path

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func, desc

from database import get_db
from db_models import User, UsageMetric, Subscription, Task, TaskProgress
from auth import get_current_active_user
from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/dashboard", tags=["dashboard"])


# ==================== Response Models ====================

class AgentActivityRecord(BaseModel):
    """Individual agent execution record"""
    issue_number: int
    issue_title: str
    issue_type: str
    labels: List[str]
    status: str
    pr_number: Optional[int] = None
    created_at: str
    resolved_at: Optional[str] = None
    merged_at: Optional[str] = None
    time_to_resolve_minutes: Optional[int] = None
    time_to_merge_minutes: Optional[int] = None
    files_changed: int = 0
    error_message: Optional[str] = None


class AgentTypeMetrics(BaseModel):
    """Metrics for a specific agent/issue type"""
    agent_type: str
    total_attempts: int
    resolved_count: int
    merged_count: int
    failed_count: int
    success_rate: float = Field(ge=0.0, le=1.0)
    merge_rate: float = Field(ge=0.0, le=1.0)
    avg_time_to_resolve_minutes: Optional[float] = None
    avg_time_to_merge_minutes: Optional[float] = None


class ProjectHealthMetrics(BaseModel):
    """Overall project health indicators"""
    health_score: float = Field(ge=0.0, le=100.0, description="Overall health score 0-100")
    tasks_completed_today: int
    tasks_completed_this_week: int
    prs_created_today: int
    prs_merged_today: int
    active_issues_count: int
    open_prs_count: int
    deployment_status: str = "unknown"  # healthy, degraded, down, unknown
    last_deployment_at: Optional[str] = None


class CostMetrics(BaseModel):
    """Cost tracking and projections"""
    total_ai_operations: int
    monthly_operations_limit: int
    operations_used_percent: float = Field(ge=0.0, le=100.0)
    estimated_monthly_cost: float = Field(description="Estimated cost in USD")
    cost_per_operation: float = Field(description="Average cost per AI operation")
    projects_created_count: int
    issues_generated_count: int
    prs_created_count: int


class DashboardMetricsResponse(BaseModel):
    """Comprehensive dashboard metrics"""
    user_email: str
    subscription_tier: str
    project_health: ProjectHealthMetrics
    cost_metrics: CostMetrics
    agent_metrics: List[AgentTypeMetrics]
    recent_activity: List[AgentActivityRecord]
    timestamp: datetime


class TimeSeriesDataPoint(BaseModel):
    """Single data point in time series"""
    timestamp: str
    value: float
    label: Optional[str] = None


class TimeSeriesResponse(BaseModel):
    """Time series data for charts"""
    metric_name: str
    data_points: List[TimeSeriesDataPoint]
    unit: str = ""
    period: str = "daily"  # hourly, daily, weekly


class ActiveTaskRecord(BaseModel):
    """Active project creation task"""
    task_id: str
    project_name: str
    status: str
    message: str
    progress_percent: int = Field(ge=0, le=100)
    created_at: str
    updated_at: Optional[str] = None
    org_url: Optional[str] = None
    repo_url: Optional[str] = None
    deployment_url: Optional[str] = None


class ActiveTasksResponse(BaseModel):
    """List of active project creation tasks"""
    active_tasks: List[ActiveTaskRecord]
    total_active: int
    total_completed_today: int
    total_failed_today: int


# ==================== Helper Functions ====================

def calculate_health_score(
    success_rate: float,
    merge_rate: float,
    tasks_completed: int,
    active_issues: int,
    deployment_status: str
) -> float:
    """
    Calculate overall project health score (0-100)

    Factors:
    - Agent success rate (40%)
    - PR merge rate (30%)
    - Activity level (15%)
    - Issue backlog (10%)
    - Deployment status (5%)
    """
    # Success rate component (0-40 points)
    success_component = success_rate * 40

    # Merge rate component (0-30 points)
    merge_component = merge_rate * 30

    # Activity component (0-15 points)
    # Healthy activity = 5-20 tasks per week
    activity_score = min(tasks_completed / 20, 1.0) * 15

    # Backlog component (0-10 points)
    # Healthy backlog = 5-15 open issues
    if 5 <= active_issues <= 15:
        backlog_score = 10
    elif active_issues < 5:
        backlog_score = 5  # Too few issues (might be stagnant)
    else:
        backlog_score = max(0, 10 - (active_issues - 15) / 5)

    # Deployment component (0-5 points)
    deployment_scores = {
        "healthy": 5,
        "degraded": 3,
        "down": 0,
        "unknown": 2
    }
    deployment_score = deployment_scores.get(deployment_status, 2)

    total_score = (
        success_component +
        merge_component +
        activity_score +
        backlog_score +
        deployment_score
    )

    return round(min(100.0, max(0.0, total_score)), 1)


def load_outcome_tracker_data() -> Dict[str, Any]:
    """
    Load data from the outcome tracker SQLite database

    Returns:
        Dictionary with outcomes data or empty dict if not available
    """
    try:
        import sys
        from pathlib import Path

        # Add seedgpt-core to path
        core_path = Path(__file__).parent.parent.parent.parent / "seedgpt-core" / "src"
        if core_path.exists():
            sys.path.insert(0, str(core_path))

        from utils.outcome_tracker import OutcomeTracker

        # Initialize tracker (defaults to .seedgpt/outcomes.db)
        tracker = OutcomeTracker()

        # Get overall stats
        overall_stats = tracker.get_overall_stats()

        # Get type-specific metrics
        type_metrics = tracker.get_type_metrics(days=30)  # Last 30 days

        # Get recent activity
        recent_outcomes = tracker.get_recent_outcomes(limit=20)

        return {
            "overall_stats": overall_stats,
            "type_metrics": type_metrics,
            "recent_outcomes": recent_outcomes
        }
    except Exception as e:
        logger.warning(f"Could not load outcome tracker data: {e}")
        return {
            "overall_stats": {
                "total_attempts": 0,
                "resolved_count": 0,
                "merged_count": 0,
                "failed_count": 0,
                "success_rate": 0.0,
                "merge_rate": 0.0,
                "avg_time_to_resolve_minutes": None,
                "avg_time_to_merge_minutes": None
            },
            "type_metrics": {},
            "recent_outcomes": []
        }


def get_github_stats(user_email: str) -> Dict[str, Any]:
    """
    Fetch GitHub repository stats (issues, PRs, deployments)

    For demo purposes, returns mock data. In production, this would
    call GitHub API to get real-time stats from the user's SeedGPT project.
    """
    # TODO: Implement GitHub API integration
    # This would fetch from the user's planted project repository
    return {
        "active_issues_count": 12,
        "open_prs_count": 3,
        "deployment_status": "healthy",
        "last_deployment_at": datetime.utcnow().isoformat()
    }


# ==================== API Endpoints ====================

@router.get("/metrics", response_model=DashboardMetricsResponse)
async def get_dashboard_metrics(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Get comprehensive dashboard metrics for the current user

    Includes:
    - Project health score
    - Cost and usage metrics
    - Agent performance by type
    - Recent agent activity
    """
    logger.info(f"📊 Dashboard metrics request from: {current_user.email}")

    try:
        # Get user's usage metrics
        usage_metric = db.query(UsageMetric).filter(
            UsageMetric.user_id == current_user.id
        ).first()

        # Get subscription info
        subscription = db.query(Subscription).filter(
            Subscription.user_id == current_user.id
        ).first()

        if not usage_metric:
            raise HTTPException(status_code=404, detail="Usage metrics not found")

        if not subscription:
            raise HTTPException(status_code=404, detail="Subscription not found")

        # Load outcome tracker data
        outcome_data = load_outcome_tracker_data()
        overall_stats = outcome_data["overall_stats"]
        type_metrics = outcome_data["type_metrics"]
        recent_outcomes = outcome_data["recent_outcomes"]

        # Get GitHub stats
        github_stats = get_github_stats(current_user.email)

        # Calculate tasks completed today and this week
        today = datetime.utcnow().date()
        week_start = today - timedelta(days=today.weekday())

        # Get real task data from database
        db_tasks_today = db.query(func.count(Task.id)).filter(
            Task.user_email == current_user.email,
            Task.status == "completed",
            func.date(Task.completed_at) == today
        ).scalar() or 0
        
        db_tasks_week = db.query(func.count(Task.id)).filter(
            Task.user_email == current_user.email,
            Task.status == "completed",
            func.date(Task.completed_at) >= week_start
        ).scalar() or 0

        # Combine with outcome tracker data
        tasks_today = sum(
            1 for outcome in recent_outcomes
            if outcome.get("merged_at") and
            datetime.fromisoformat(outcome["merged_at"]).date() == today
        ) + db_tasks_today

        tasks_this_week = sum(
            1 for outcome in recent_outcomes
            if outcome.get("merged_at") and
            datetime.fromisoformat(outcome["merged_at"]).date() >= week_start
        ) + db_tasks_week

        prs_today = sum(
            1 for outcome in recent_outcomes
            if outcome.get("created_at") and
            datetime.fromisoformat(outcome["created_at"]).date() == today
        )

        prs_merged_today = tasks_today  # Same as tasks completed today

        # Calculate project health score
        health_score = calculate_health_score(
            success_rate=overall_stats["success_rate"],
            merge_rate=overall_stats["merge_rate"],
            tasks_completed=tasks_this_week,
            active_issues=github_stats["active_issues_count"],
            deployment_status=github_stats["deployment_status"]
        )

        # Build project health metrics
        project_health = ProjectHealthMetrics(
            health_score=health_score,
            tasks_completed_today=tasks_today,
            tasks_completed_this_week=tasks_this_week,
            prs_created_today=prs_today,
            prs_merged_today=prs_merged_today,
            active_issues_count=github_stats["active_issues_count"],
            open_prs_count=github_stats["open_prs_count"],
            deployment_status=github_stats["deployment_status"],
            last_deployment_at=github_stats.get("last_deployment_at")
        )

        # Calculate cost metrics
        operations_used = usage_metric.ai_operations_count or 0
        operations_limit = subscription.monthly_ai_ops_limit or 100
        operations_percent = min(100.0, (operations_used / operations_limit * 100))

        # Estimated costs (example rates)
        cost_per_op = 0.05  # $0.05 per AI operation (example)
        estimated_cost = operations_used * cost_per_op

        cost_metrics = CostMetrics(
            total_ai_operations=operations_used,
            monthly_operations_limit=operations_limit,
            operations_used_percent=round(operations_percent, 1),
            estimated_monthly_cost=round(estimated_cost, 2),
            cost_per_operation=cost_per_op,
            projects_created_count=usage_metric.projects_created or 0,
            issues_generated_count=usage_metric.issues_generated or 0,
            prs_created_count=usage_metric.prs_created or 0
        )

        # Build agent type metrics
        agent_metrics = []
        for agent_type, metrics in type_metrics.items():
            agent_metrics.append(AgentTypeMetrics(
                agent_type=agent_type,
                total_attempts=metrics.total_attempts,
                resolved_count=metrics.resolved_count,
                merged_count=metrics.merged_count,
                failed_count=metrics.failed_count,
                success_rate=round(metrics.success_rate, 3),
                merge_rate=round(metrics.merge_rate, 3),
                avg_time_to_resolve_minutes=metrics.avg_time_to_resolve_minutes,
                avg_time_to_merge_minutes=metrics.avg_time_to_merge_minutes
            ))

        # Build recent activity records
        recent_activity = []
        for outcome in recent_outcomes[:10]:  # Last 10 activities
            recent_activity.append(AgentActivityRecord(
                issue_number=outcome["issue_number"],
                issue_title=outcome["issue_title"],
                issue_type=outcome["issue_type"],
                labels=outcome["labels"],
                status=outcome["status"],
                pr_number=outcome.get("pr_number"),
                created_at=outcome["created_at"],
                resolved_at=outcome.get("resolved_at"),
                merged_at=outcome.get("merged_at"),
                time_to_resolve_minutes=outcome.get("time_to_resolve_minutes"),
                time_to_merge_minutes=outcome.get("time_to_merge_minutes"),
                files_changed=outcome.get("files_changed", 0),
                error_message=outcome.get("error_message")
            ))

        response = DashboardMetricsResponse(
            user_email=current_user.email,
            subscription_tier=subscription.tier.value,
            project_health=project_health,
            cost_metrics=cost_metrics,
            agent_metrics=agent_metrics,
            recent_activity=recent_activity,
            timestamp=datetime.utcnow()
        )

        logger.info(f"✅ Dashboard metrics generated for: {current_user.email}")
        logger.info(f"   Health Score: {health_score}")
        logger.info(f"   Tasks Today: {tasks_today}")
        logger.info(f"   Operations Used: {operations_percent:.1f}%")

        return response

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Error generating dashboard metrics: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to generate dashboard metrics: {str(e)}"
        )


@router.get("/activity/recent", response_model=List[AgentActivityRecord])
async def get_recent_activity(
    limit: int = 20,
    current_user: User = Depends(get_current_active_user)
):
    """
    Get recent agent activity records

    Args:
        limit: Maximum number of records to return (default: 20, max: 100)
    """
    limit = min(limit, 100)  # Cap at 100

    logger.info(f"📋 Recent activity request from: {current_user.email} (limit: {limit})")

    try:
        outcome_data = load_outcome_tracker_data()
        recent_outcomes = outcome_data["recent_outcomes"][:limit]

        activity_records = []
        for outcome in recent_outcomes:
            activity_records.append(AgentActivityRecord(
                issue_number=outcome["issue_number"],
                issue_title=outcome["issue_title"],
                issue_type=outcome["issue_type"],
                labels=outcome["labels"],
                status=outcome["status"],
                pr_number=outcome.get("pr_number"),
                created_at=outcome["created_at"],
                resolved_at=outcome.get("resolved_at"),
                merged_at=outcome.get("merged_at"),
                time_to_resolve_minutes=outcome.get("time_to_resolve_minutes"),
                time_to_merge_minutes=outcome.get("time_to_merge_minutes"),
                files_changed=outcome.get("files_changed", 0),
                error_message=outcome.get("error_message")
            ))

        logger.info(f"✅ Returned {len(activity_records)} activity records")
        return activity_records

    except Exception as e:
        logger.error(f"❌ Error fetching recent activity: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to fetch recent activity: {str(e)}"
        )


@router.get("/metrics/timeseries/{metric_name}", response_model=TimeSeriesResponse)
async def get_timeseries_metrics(
    metric_name: str,
    period: str = "daily",
    days: int = 7,
    current_user: User = Depends(get_current_active_user)
):
    """
    Get time series data for dashboard charts

    Args:
        metric_name: Metric to fetch (e.g., 'tasks_completed', 'prs_created', 'success_rate')
        period: Aggregation period ('hourly', 'daily', 'weekly')
        days: Number of days of historical data (max: 90)

    Supported metrics:
    - tasks_completed: Number of tasks completed (merged PRs)
    - prs_created: Number of PRs created
    - success_rate: Agent success rate over time
    - operations_used: AI operations consumed
    """
    days = min(days, 90)  # Cap at 90 days

    logger.info(f"📈 Timeseries request: {metric_name} ({period}, {days} days)")

    # TODO: Implement actual time series aggregation from database
    # For now, generate sample data

    data_points = []
    now = datetime.utcnow()

    for i in range(days):
        date = now - timedelta(days=days - i - 1)
        # Generate sample data (replace with real aggregation)
        value = 5 + (i % 3) * 2  # Sample oscillating values

        data_points.append(TimeSeriesDataPoint(
            timestamp=date.isoformat(),
            value=float(value),
            label=date.strftime("%b %d")
        ))

    return TimeSeriesResponse(
        metric_name=metric_name,
        data_points=data_points,
        unit="count" if "count" in metric_name or "tasks" in metric_name else "percent",
        period=period
    )


@router.get("/active-tasks", response_model=ActiveTasksResponse)
async def get_active_tasks(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Get all active project creation tasks for the current user
    
    Shows real-time progress of ongoing project plantings
    """
    logger.info(f"📋 Active tasks request from: {current_user.email}")
    
    try:
        # Get active tasks (not completed or failed)
        active_tasks = db.query(Task).filter(
            Task.user_email == current_user.email,
            Task.status.in_(["initializing", "in_progress", "creating_org", "forking_repo", "customizing", "deploying"])
        ).order_by(Task.created_at.desc()).all()
        
        # Get today's completed and failed tasks
        today = datetime.utcnow().date()
        completed_today = db.query(func.count(Task.id)).filter(
            Task.user_email == current_user.email,
            Task.status == "completed",
            func.date(Task.completed_at) == today
        ).scalar() or 0
        
        failed_today = db.query(func.count(Task.id)).filter(
            Task.user_email == current_user.email,
            Task.status == "failed",
            func.date(Task.failed_at) == today
        ).scalar() or 0
        
        # Build response
        task_records = []
        for task in active_tasks:
            task_records.append(ActiveTaskRecord(
                task_id=task.task_id,
                project_name=task.project_name or "Unknown",
                status=task.status,
                message=task.message or "Processing...",
                progress_percent=task.progress_percent or 0,
                created_at=task.created_at.isoformat() if task.created_at else datetime.utcnow().isoformat(),
                updated_at=task.updated_at.isoformat() if task.updated_at else None,
                org_url=task.org_url,
                repo_url=task.repo_url,
                deployment_url=task.deployment_url
            ))
        
        response = ActiveTasksResponse(
            active_tasks=task_records,
            total_active=len(task_records),
            total_completed_today=completed_today,
            total_failed_today=failed_today
        )
        
        logger.info(f"✅ Found {len(task_records)} active tasks for {current_user.email}")
        return response
        
    except Exception as e:
        logger.error(f"❌ Error fetching active tasks: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to fetch active tasks: {str(e)}")


@router.get("/health")
async def dashboard_health_check():
    """Health check endpoint for dashboard service"""
    return {
        "status": "healthy",
        "service": "dashboard",
        "timestamp": datetime.utcnow().isoformat()
    }
