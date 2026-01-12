from typing import Optional, List
from datetime import datetime

from supabase import Client

from ...domain.entities import Notification
from .client import SupabaseClient


class SupabaseNotificationRepository:
    """Repositorio de notificaciones usando Supabase"""

    def __init__(self, client: Optional[Client] = None):
        self.client = client or SupabaseClient.get_client()
        self.table = "notifications"

    def _row_to_entity(self, row: dict) -> Notification:
        return Notification(
            id=str(row["id"]),
            user_id=row["user_id"],
            title=row["title"],
            message=row["message"],
            link=row.get("link"),
            type=row.get("type"),
            is_read=bool(row.get("is_read", False)),
            created_at=row.get("created_at"),
        )

    def create(self, notification: Notification) -> Notification:
        data = {
            "user_id": notification.user_id,
            "title": notification.title,
            "message": notification.message,
            "link": notification.link,
            "type": notification.type,
            "is_read": notification.is_read,
            "created_at": notification.created_at or datetime.utcnow().isoformat(),
        }
        result = self.client.table(self.table).insert(data).execute()
        return self._row_to_entity(result.data[0])

    def get_unread_by_user(self, user_id: str, limit: int = 10) -> List[Notification]:
        try:
            result = (
                self.client.table(self.table)
                .select("*")
                .eq("user_id", user_id)
                .eq("is_read", False)
                .order("created_at", desc=True)
                .limit(limit)
                .execute()
            )
            return [self._row_to_entity(row) for row in result.data]
        except Exception:
            return []

    def mark_as_read(self, notification_id: str, user_id: str) -> bool:
        try:
            res = (
                self.client.table(self.table)
                .update({"is_read": True, "updated_at": datetime.utcnow().isoformat()})
                .eq("id", notification_id)
                .eq("user_id", user_id)
                .execute()
            )
            return bool(res.data)
        except Exception:
            return False

    def mark_all_as_read(self, user_id: str) -> bool:
        try:
            res = (
                self.client.table(self.table)
                .update({"is_read": True, "updated_at": datetime.utcnow().isoformat()})
                .eq("user_id", user_id)
                .execute()
            )
            return bool(res.data)
        except Exception:
            return False

