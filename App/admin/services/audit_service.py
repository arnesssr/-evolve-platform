from typing import Optional, Dict, Any
from App.admin.models.audit_log import AuditLog

class AuditService:
    """Write admin audit log entries."""

    def log(self, *, action: str, actor_id: Optional[int], target_type: str = "", target_id: str = "", target_display: str = "", details: Optional[Dict[str, Any]] = None, ip_address: Optional[str] = None, user_agent: str = "") -> AuditLog:
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

