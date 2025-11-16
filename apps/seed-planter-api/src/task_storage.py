"""Task storage service using database for tracking async operations"""

import logging
from typing import Optional, Dict, Any
from datetime import datetime, timedelta
from sqlalchemy.orm import Session

from database import SessionLocal
from db_models import Task, TaskProgress
from models import ProjectStatus, ProjectDetails, ProjectProgress as ProjectProgressModel

logger = logging.getLogger(__name__)


class TaskStorage:
    """Manages task state in database"""
    
    def __init__(self):
        self.task_ttl = 3600  # Tasks expire after 1 hour
    
    async def connect(self):
        """Connect to database (no-op for compatibility)"""
        logger.info("Task storage using database")
    
    async def disconnect(self):
        """Disconnect from database (no-op for compatibility)"""
        logger.info("Task storage cleanup complete")
    
    def _get_db(self) -> Session:
        """Get database session"""
        return SessionLocal()
    
    async def create_task(self, task_id: str, initial_data: Dict[str, Any]) -> None:
        """Create a new task"""
        db = self._get_db()
        try:
            task = Task(
                task_id=task_id,
                status=ProjectStatus.INITIALIZING.value,
                project_name=initial_data.get("project_name"),
                project_description=initial_data.get("project_description"),
                user_email=initial_data.get("user_email"),
                mode=initial_data.get("mode"),
                message=initial_data.get("message", "Initializing..."),
                progress_percent=initial_data.get("progress_percent", 0),
                created_at=datetime.utcnow(),
                expires_at=datetime.utcnow() + timedelta(seconds=self.task_ttl),
                extra_data=initial_data.get("extra_data")
            )
            db.add(task)
            db.commit()
            logger.info(f"Created task {task_id}")
        except Exception as e:
            db.rollback()
            logger.error(f"Failed to create task {task_id}: {e}")
            raise
        finally:
            db.close()
    
    async def update_task_status(
        self, 
        task_id: str, 
        status: ProjectStatus,
        **kwargs
    ) -> None:
        """Update task status and additional fields"""
        db = self._get_db()
        try:
            task = db.query(Task).filter(Task.task_id == task_id).first()
            
            if not task:
                logger.warning(f"Task {task_id} not found")
                return
            
            task.status = status.value
            task.updated_at = datetime.utcnow()
            
            # Update additional fields
            for key, value in kwargs.items():
                if hasattr(task, key):
                    setattr(task, key, value)
            
            db.commit()
            logger.debug(f"Updated task {task_id} status to {status.value}")
        except Exception as e:
            db.rollback()
            logger.error(f"Failed to update task {task_id}: {e}")
        finally:
            db.close()
    
    async def update_progress(
        self,
        task_id: str,
        progress: ProjectProgressModel
    ) -> None:
        """Update task progress"""
        db = self._get_db()
        try:
            # Create progress record
            progress_record = TaskProgress(
                task_id=task_id,
                status=progress.status.value,
                message=progress.message,
                progress_percent=progress.progress_percent,
                org_url=progress.org_url,
                repo_url=progress.repo_url,
                deployment_url=progress.deployment_url,
                gcp_project_id=progress.gcp_project_id,
                timestamp=progress.timestamp
            )
            db.add(progress_record)
            
            # Also update main task status
            task = db.query(Task).filter(Task.task_id == task_id).first()
            if task:
                task.status = progress.status.value
                task.message = progress.message
                task.progress_percent = progress.progress_percent
                task.org_url = progress.org_url or task.org_url
                task.repo_url = progress.repo_url or task.repo_url
                task.deployment_url = progress.deployment_url or task.deployment_url
                task.gcp_project_id = progress.gcp_project_id or task.gcp_project_id
                task.updated_at = datetime.utcnow()
            
            db.commit()
        except Exception as e:
            db.rollback()
            logger.error(f"Failed to update progress for task {task_id}: {e}")
        finally:
            db.close()
    
    async def get_task(self, task_id: str) -> Optional[Dict[str, Any]]:
        """Get task data"""
        db = self._get_db()
        try:
            task = db.query(Task).filter(Task.task_id == task_id).first()
            
            if not task:
                return None
            
            return {
                "task_id": task.task_id,
                "status": task.status,
                "project_name": task.project_name,
                "project_description": task.project_description,
                "user_email": task.user_email,
                "mode": task.mode,
                "message": task.message,
                "progress_percent": task.progress_percent,
                "project_id": task.project_id,
                "org_url": task.org_url,
                "repo_url": task.repo_url,
                "deployment_url": task.deployment_url,
                "gcp_project_id": task.gcp_project_id,
                "error_message": task.error_message,
                "created_at": task.created_at.isoformat() if task.created_at else None,
                "updated_at": task.updated_at.isoformat() if task.updated_at else None,
                "completed_at": task.completed_at.isoformat() if task.completed_at else None,
                "failed_at": task.failed_at.isoformat() if task.failed_at else None,
                "extra_data": task.extra_data
            }
        finally:
            db.close()
    
    async def get_progress(self, task_id: str) -> Optional[Dict[str, Any]]:
        """Get latest progress for a task"""
        db = self._get_db()
        try:
            # Get the most recent progress record
            progress = db.query(TaskProgress).filter(
                TaskProgress.task_id == task_id
            ).order_by(TaskProgress.timestamp.desc()).first()
            
            if not progress:
                return None
            
            return {
                "task_id": progress.task_id,
                "status": progress.status,
                "message": progress.message,
                "progress_percent": progress.progress_percent,
                "org_url": progress.org_url,
                "repo_url": progress.repo_url,
                "deployment_url": progress.deployment_url,
                "gcp_project_id": progress.gcp_project_id,
                "timestamp": progress.timestamp.isoformat() if progress.timestamp else None,
                "extra_data": progress.extra_data
            }
        finally:
            db.close()
    
    async def complete_task(
        self,
        task_id: str,
        result: ProjectDetails
    ) -> None:
        """Mark task as completed with result"""
        await self.update_task_status(
            task_id,
            ProjectStatus.COMPLETED,
            project_id=result.project_id,
            project_name=result.project_name,
            org_url=result.org_url,
            repo_url=result.repo_url,
            deployment_url=result.deployment_url,
            gcp_project_id=result.gcp_project_id,
            completed_at=datetime.utcnow()
        )
        
        logger.info(f"Task {task_id} completed successfully")
    
    async def fail_task(
        self,
        task_id: str,
        error_message: str
    ) -> None:
        """Mark task as failed"""
        await self.update_task_status(
            task_id,
            ProjectStatus.FAILED,
            error_message=error_message,
            failed_at=datetime.utcnow()
        )
        
        logger.error(f"Task {task_id} failed: {error_message}")


# Global instance
task_storage = TaskStorage()
