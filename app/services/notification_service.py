from typing import List, Optional
from datetime import datetime

from ..domain.entities import Notification
from ..repositories.interfaces import NotificationRepository


class NotificationService:
    """Servicio para gestionar notificaciones"""

    def __init__(self, repo: NotificationRepository):
        self.repo = repo

    def create(
        self,
        user_id: str,
        title: str,
        message: str,
        link: Optional[str] = None,
        type: Optional[str] = None,
    ) -> Notification:
        notif = Notification(
            id="",
            user_id=user_id,
            title=title,
            message=message,
            link=link,
            type=type,
            is_read=False,
            created_at=datetime.utcnow().isoformat(),
        )
        return self.repo.create(notif)

    def get_unread(self, user_id: str, limit: int = 10) -> List[Notification]:
        return self.repo.get_unread_by_user(user_id, limit=limit)

    def mark_as_read(self, notification_id: str, user_id: str) -> bool:
        return self.repo.mark_as_read(notification_id, user_id)

