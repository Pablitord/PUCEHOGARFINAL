from typing import Optional, List
from datetime import datetime

from supabase import Client

from ...domain.entities import Department
from ...domain.enums import DepartmentStatus
from .client import SupabaseClient


class SupabaseDepartmentRepository:
    """Implementación de DepartmentRepository usando Supabase"""
    
    def __init__(self, client: Optional[Client] = None):
        self.client = client or SupabaseClient.get_client()
        self.table = "departments"
    
    def _row_to_entity(self, row: dict) -> Department:
        """Convierte una fila de BD a entidad Department"""
        return Department(
            id=str(row["id"]),
            title=row["title"],
            address=row["address"],
            price=float(row["price"]),
            status=DepartmentStatus(row["status"]),
            description=row.get("description"),
            rooms=row.get("rooms"),
            bathrooms=row.get("bathrooms"),
            area=float(row["area"]) if row.get("area") else None,
            image_url=row.get("image_url"),
            has_terrace=row.get("has_terrace", False) or False,
            has_balcony=row.get("has_balcony", False) or False,
            sea_view=row.get("sea_view", False) or False,
            parking=row.get("parking", False) or False,
            furnished=row.get("furnished", False) or False,
            created_at=row.get("created_at"),
            updated_at=row.get("updated_at")
        )
    
    def get_by_id(self, department_id: str) -> Optional[Department]:
        """Obtiene un departamento por ID"""
        try:
            result = self.client.table(self.table).select("*").eq("id", department_id).single().execute()
            if result.data:
                return self._row_to_entity(result.data)
            return None
        except Exception:
            return None
    
    def get_all(
        self,
        status: Optional[DepartmentStatus] = None,
        filters: Optional[dict] = None
    ) -> List[Department]:
        """Obtiene todos los departamentos con filtros opcionales"""
        try:
            query = self.client.table(self.table).select("*")

            if status:
                query = query.eq("status", status.value)

            if filters:
                if filters.get("has_terrace") is True:
                    query = query.eq("has_terrace", True)
                if filters.get("has_balcony") is True:
                    query = query.eq("has_balcony", True)
                if filters.get("sea_view") is True:
                    query = query.eq("sea_view", True)
                if filters.get("parking") is True:
                    query = query.eq("parking", True)
                if filters.get("furnished") is True:
                    query = query.eq("furnished", True)
                if filters.get("min_price") is not None:
                    query = query.gte("price", filters["min_price"])
                if filters.get("max_price") is not None:
                    query = query.lte("price", filters["max_price"])
                if filters.get("min_rooms") is not None:
                    query = query.gte("rooms", filters["min_rooms"])
                if filters.get("max_rooms") is not None:
                    query = query.lte("rooms", filters["max_rooms"])

            result = query.order("created_at", desc=True).execute()
            return [self._row_to_entity(row) for row in result.data]
        except Exception:
            return []
    
    def create(self, department: Department) -> Department:
        """Crea un nuevo departamento"""
        data = {
            "title": department.title,
            "address": department.address,
            "price": department.price,
            "status": department.status.value,
            "description": department.description,
            "rooms": department.rooms,
            "bathrooms": department.bathrooms,
            "area": department.area,
            "image_url": department.image_url,
            "has_terrace": department.has_terrace,
            "has_balcony": department.has_balcony,
            "sea_view": department.sea_view,
            "parking": department.parking,
            "furnished": department.furnished
        }
        result = self.client.table(self.table).insert(data).execute()
        return self._row_to_entity(result.data[0])
    
    def update(self, department: Department) -> Department:
        """Actualiza un departamento"""
        data = {
            "title": department.title,
            "address": department.address,
            "price": department.price,
            "status": department.status.value,
            "description": department.description,
            "rooms": department.rooms,
            "bathrooms": department.bathrooms,
            "area": department.area,
            "image_url": department.image_url,
            "has_terrace": department.has_terrace,
            "has_balcony": department.has_balcony,
            "sea_view": department.sea_view,
            "parking": department.parking,
            "furnished": department.furnished,
            "updated_at": datetime.utcnow().isoformat()
        }
        result = self.client.table(self.table).update(data).eq("id", department.id).execute()
        return self._row_to_entity(result.data[0])
    
    def delete(self, department_id: str) -> bool:
        """Elimina un departamento"""
        try:
            self.client.table(self.table).delete().eq("id", department_id).execute()
            return True
        except Exception:
            return False

