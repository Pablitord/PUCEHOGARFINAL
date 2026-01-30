from typing import Optional, List
from datetime import datetime

from supabase import Client

from ...domain.entities import Rating
from .client import SupabaseClient


class SupabaseRatingRepository:
    """Repositorio de calificaciones usando Supabase"""

    def __init__(self, client: Optional[Client] = None):
        self.client = client or SupabaseClient.get_client()
        self.table = "ratings"

    def _row_to_entity(self, row: dict) -> Rating:
        """Convierte una fila de BD a entidad Rating"""
        def _parse_dt(val):
            if not val:
                return None
            if isinstance(val, datetime):
                return val
            try:
                return datetime.fromisoformat(val.replace("Z", "+00:00"))
            except Exception:
                return None
        
        return Rating(
            id=str(row["id"]),
            tenant_id=row["tenant_id"],
            department_id=row["department_id"],
            rating=int(row["rating"]),
            comment=row.get("comment"),
            created_at=_parse_dt(row.get("created_at")),
            updated_at=_parse_dt(row.get("updated_at")),
        )

    def get_by_id(self, rating_id: str) -> Optional[Rating]:
        try:
            result = self.client.table(self.table).select("*").eq("id", rating_id).single().execute()
            if result.data:
                return self._row_to_entity(result.data)
            return None
        except Exception:
            return None

    def get_by_department(self, department_id: str) -> List[Rating]:
        try:
            result = (
                self.client.table(self.table)
                .select("*")
                .eq("department_id", department_id)
                .order("created_at", desc=True)
                .execute()
            )
            return [self._row_to_entity(row) for row in result.data]
        except Exception:
            return []

    def get_by_tenant_and_department(self, tenant_id: str, department_id: str) -> Optional[Rating]:
        try:
            result = (
                self.client.table(self.table)
                .select("*")
                .eq("tenant_id", tenant_id)
                .eq("department_id", department_id)
                .maybe_single()
                .execute()
            )
            if result.data:
                return self._row_to_entity(result.data)
            return None
        except Exception:
            return None

    def get_average_rating(self, department_id: str) -> Optional[float]:
        try:
            result = (
                self.client.table(self.table)
                .select("rating")
                .eq("department_id", department_id)
                .execute()
            )
            if not result.data:
                return None
            ratings = [float(row["rating"]) for row in result.data]
            return sum(ratings) / len(ratings) if ratings else None
        except Exception:
            return None

    def get_rating_count(self, department_id: str) -> int:
        try:
            result = (
                self.client.table(self.table)
                .select("id", count="exact")
                .eq("department_id", department_id)
                .execute()
            )
            return result.count if result.count is not None else 0
        except Exception:
            return 0

    def create(self, rating: Rating) -> Rating:
        data = {
            "tenant_id": rating.tenant_id,
            "department_id": rating.department_id,
            "rating": rating.rating,
            "comment": rating.comment,
        }
        result = self.client.table(self.table).insert(data).execute()
        if result.data:
            return self._row_to_entity(result.data[0])
        raise Exception("Error al crear calificación")

    def update(self, rating: Rating) -> Rating:
        data = {
            "rating": rating.rating,
            "comment": rating.comment,
            "updated_at": datetime.utcnow().isoformat(),
        }
        result = (
            self.client.table(self.table)
            .update(data)
            .eq("id", rating.id)
            .execute()
        )
        if result.data:
            return self._row_to_entity(result.data[0])
        raise Exception("Error al actualizar calificación")

    def delete(self, rating_id: str) -> bool:
        try:
            self.client.table(self.table).delete().eq("id", rating_id).execute()
            return True
        except Exception:
            return False
