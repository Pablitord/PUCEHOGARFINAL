import re
from typing import Optional

from ..domain.entities import User
from ..domain.enums import UserRole


class UserFactory:
    """Factory para crear usuarios siguiendo el patrón Factory"""
    
    @staticmethod
    def validate_email(email: str) -> bool:
        """Valida formato de email"""
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return bool(re.match(pattern, email))
    
    @staticmethod
    def create_tenant(
        email: str,
        full_name: Optional[str] = None,
        department_id: Optional[str] = None
    ) -> User:
        """Crea un usuario con rol TENANT"""
        if not UserFactory.validate_email(email):
            raise ValueError("Email inválido")
        
        return User(
            id="",  # Se asignará al guardar en BD
            email=email.lower().strip(),
            role=UserRole.TENANT,
            full_name=full_name,
            department_id=department_id
        )
    
    @staticmethod
    def create_admin(
        email: str,
        full_name: Optional[str] = None
    ) -> User:
        """Crea un usuario con rol ADMIN"""
        if not UserFactory.validate_email(email):
            raise ValueError("Email inválido")
        
        return User(
            id="",
            email=email.lower().strip(),
            role=UserRole.ADMIN,
            full_name=full_name
        )
    
    @staticmethod
    def create_user(
        email: str,
        role: UserRole,
        full_name: Optional[str] = None,
        department_id: Optional[str] = None
    ) -> User:
        """Crea un usuario con el rol especificado"""
        if not UserFactory.validate_email(email):
            raise ValueError("Email inválido")
        
        if role == UserRole.TENANT:
            return UserFactory.create_tenant(email, full_name, department_id)
        elif role == UserRole.ADMIN:
            return UserFactory.create_admin(email, full_name)
        else:
            raise ValueError(f"Rol no válido para creación: {role}")

