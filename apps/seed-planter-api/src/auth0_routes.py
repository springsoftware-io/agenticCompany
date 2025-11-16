"""Auth0 authentication routes for FastAPI"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from datetime import datetime

from database import get_db
from db_models import User
from auth0_service import get_current_user_auth0

router = APIRouter(prefix="/api/v1/auth", tags=["auth"])


@router.get("/me")
async def get_current_user(
    user: User = Depends(get_current_user_auth0),
    db: Session = Depends(get_db)
):
    """Get current authenticated user information"""
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Get subscription info if exists
    subscription_tier = None
    if user.subscription:
        subscription_tier = user.subscription.tier.value
    
    return {
        "id": user.id,
        "email": user.email,
        "full_name": user.full_name,
        "is_active": user.is_active,
        "subscription_tier": subscription_tier,
        "created_at": user.created_at.isoformat() if user.created_at else None,
        "oauth_provider": user.oauth_provider
    }


@router.get("/usage")
async def get_usage_stats(
    user: User = Depends(get_current_user_auth0),
    db: Session = Depends(get_db)
):
    """Get user usage statistics"""
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Get current month's usage
    from db_models import UsageMetric
    from datetime import datetime, timedelta
    
    # Get start of current month
    now = datetime.utcnow()
    month_start = datetime(now.year, now.month, 1)
    
    current_usage = db.query(UsageMetric).filter(
        UsageMetric.user_id == user.id,
        UsageMetric.period_start >= month_start
    ).first()
    
    # Get subscription limits
    monthly_limit = None
    if user.subscription:
        monthly_limit = user.subscription.monthly_ai_ops_limit
    
    return {
        "ai_operations_count": current_usage.ai_operations_count if current_usage else 0,
        "projects_created": current_usage.projects_created if current_usage else 0,
        "monthly_limit": monthly_limit,
        "subscription_tier": user.subscription.tier.value if user.subscription else "free"
    }
