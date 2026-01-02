from typing import Optional, List
from datetime import datetime

from supabase import Client

from ...domain.entities import User
from ...domain.enums import UserRole
from .client import SupabaseClient


class SupabaseUserRepository:
    """Implementación de UserRepository usando Supabase"""
    
    def __init__(self, client: Optional[Client] = None):
        self.client = client or SupabaseClient.get_client()
        self.table = "users"
    
    def _row_to_entity(self, row: dict) -> User:
        """Convierte una fila de BD a entidad User"""
        return User(
            id=str(row["id"]),
            email=row["email"],
            role=UserRole(row["role"]),
            full_name=row.get("full_name"),
            department_id=row.get("department_id"),
            created_at=row.get("created_at"),
            updated_at=row.get("updated_at")
        )
    
    def get_by_id(self, user_id: str) -> Optional[User]:
        """Obtiene un usuario por ID"""
        try:
            result = self.client.table(self.table).select("*").eq("id", user_id).single().execute()
            if result.data:
                return self._row_to_entity(result.data)
            return None
        except Exception:
            return None
    
    def get_by_email(self, email: str) -> Optional[User]:
        """Obtiene un usuario por email"""
        try:
            result = self.client.table(self.table).select("*").eq("email", email.lower().strip()).single().execute()
            if result.data:
                return self._row_to_entity(result.data)
            return None
        except Exception:
            return None
    
    def create(self, user: User) -> User:
        """Crea un nuevo usuario"""
        data = {
            "email": user.email,
            "role": user.role.value,
            "full_name": user.full_name,
            "department_id": user.department_id
        }
        result = self.client.table(self.table).insert(data).execute()
        return self._row_to_entity(result.data[0])
    
    def update(self, user: User) -> User:
        """Actualiza un usuario"""
        data = {
            "email": user.email,
            "role": user.role.value,
            "full_name": user.full_name,
            "department_id": user.department_id,
            "updated_at": datetime.utcnow().isoformat()
        }
        result = self.client.table(self.table).update(data).eq("id", user.id).execute()
        return self._row_to_entity(result.data[0])
    
    def get_tenants_by_department(self, department_id: str) -> List[User]:
        """Obtiene inquilinos de un departamento"""
        try:
            result = self.client.table(self.table).select("*").eq("department_id", department_id).eq("role", UserRole.TENANT.value).execute()
            return [self._row_to_entity(row) for row in result.data]
        except Exception:
            return []

