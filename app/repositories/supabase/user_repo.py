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
            password_hash=row.get("password_hash"),
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
            "department_id": user.department_id,
            "password_hash": user.password_hash
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
            "password_hash": user.password_hash,
            "updated_at": datetime.utcnow().isoformat()
        }
        result = self.client.table(self.table).update(data).eq("id", user.id).execute()
        return self._row_to_entity(result.data[0])
    
    def has_admins(self) -> bool:
        """Retorna True si existe al menos un admin"""
        try:
            result = (
                self.client.table(self.table)
                .select("id", count="exact")
                .eq("role", UserRole.ADMIN.value)
                .limit(1)
                .execute()
            )
            total = 0
            # Supabase python: result.count si está disponible
            if hasattr(result, "count") and result.count is not None:
                total = result.count
            elif result.data:
                total = len(result.data)
            return total > 0
        except Exception:
            return False

    def get_tenants_by_department(self, department_id: str) -> List[User]:
        """Obtiene inquilinos de un departamento"""
        try:
            result = self.client.table(self.table).select("*").eq("department_id", department_id).eq("role", UserRole.TENANT.value).execute()
            return [self._row_to_entity(row) for row in result.data]
        except Exception:
            return []

    def get_admins(self) -> List[User]:
        """Obtiene todos los administradores"""
        try:
            result = self.client.table(self.table).select("*").eq("role", UserRole.ADMIN.value).execute()
            return [self._row_to_entity(row) for row in result.data]
        except Exception:
            return []
    
    def unassign_department(self, department_id: str) -> int:
        """Desasigna un departamento de todos los usuarios que lo tengan asignado. Retorna el número de usuarios desasignados."""
        try:
            # Obtener todos los usuarios con este departamento asignado
            result = self.client.table(self.table).select("id").eq("department_id", department_id).execute()
            user_ids = [row["id"] for row in result.data]
            
            if not user_ids:
                return 0
            
            # Actualizar todos los usuarios para desasignar el departamento
            self.client.table(self.table).update({"department_id": None}).in_("id", user_ids).execute()
            return len(user_ids)
        except Exception:
            return 0

