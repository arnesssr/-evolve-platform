from typing import Optional, Dict, Any
from django.contrib.auth import get_user_model
from ..models.audit_log import AuditLog

User = get_user_model()


class AuditService:
    """Write admin audit log entries."""

    def log(self, *, action: str, actor_id: Optional[int], target_type: str = "", target_id: str = "", target_display: str = "", details: Optional[Dict[str, Any]] = None, ip_address: Optional[str] = None, user_agent: str = "") -> 'AuditLog':
        """Legacy log method for backward compatibility"""
        entry = AuditLog.objects.create(
            action=action,
            actor_id=actor_id,
            target_type=target_type,
            target_id=str(target_id or ""),
            target_display=target_display or "",
            details=details or {},
            ip_address=ip_address,
            user_agent=user_agent or "",
        )
        return entry
    
    def log_action(self, admin_user, action, target_model, target_id=None, description="", ip_address=None):
        """Log admin action with standardized parameters"""
        entry = AuditLog.objects.create(
            action=action,
            actor=admin_user,
            target_type=target_model,
            target_id=str(target_id or ""),
            target_display=description,
            ip_address=ip_address,
        )
        return entry
    
    def get_user_activities(self, user_id, limit=50):
        """Get activities for a specific admin user"""
        return AuditLog.objects.filter(
            actor_id=user_id
        ).order_by('-created_at')[:limit]

