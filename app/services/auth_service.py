from typing import Optional

from ..domain.entities import User
from ..domain.enums import UserRole
from ..repositories.interfaces import UserRepository
from ..factories.user_factory import UserFactory


class AuthService:
    """Servicio de autenticación y gestión de usuarios"""
    
    def __init__(self, user_repo: UserRepository):
        self.user_repo = user_repo
    
    def register(
        self,
        email: str,
        password: str,
        full_name: Optional[str] = None,
        role: UserRole = UserRole.TENANT
    ) -> User:
        """Registra un nuevo usuario"""
        # Verificar si el email ya existe
        existing_user = self.user_repo.get_by_email(email)
        if existing_user:
            raise ValueError("El email ya está registrado")
        
        # Crear usuario usando factory
        if role == UserRole.TENANT:
            user = UserFactory.create_tenant(email, full_name)
        elif role == UserRole.ADMIN:
            user = UserFactory.create_admin(email, full_name)
        else:
            raise ValueError(f"Rol no válido para registro: {role}")
        
        # TODO: En producción, aquí deberías usar Supabase Auth para crear el usuario
        # y luego guardar los datos adicionales en la tabla users
        
        # Guardar en BD
        user = self.user_repo.create(user)
        return user
    
    def login(self, email: str, password: str) -> Optional[User]:
        """
        Autentica un usuario.
        
        Nota: En producción, esto debería usar Supabase Auth.
        Por ahora, solo verifica que el usuario exista.
        """
        user = self.user_repo.get_by_email(email)
        if not user:
            return None
        
        # TODO: Integrar con Supabase Auth para validar password
        # Por ahora, solo retornamos el usuario si existe
        return user
    
    def get_user_by_id(self, user_id: str) -> Optional[User]:
        """Obtiene un usuario por ID"""
        return self.user_repo.get_by_id(user_id)
    
    def get_user_by_email(self, email: str) -> Optional[User]:
        """Obtiene un usuario por email"""
        return self.user_repo.get_by_email(email)
    
    def is_admin(self, user: User) -> bool:
        """Verifica si un usuario es administrador"""
        return user.role == UserRole.ADMIN
    
    def is_tenant(self, user: User) -> bool:
        """Verifica si un usuario es inquilino"""
        return user.role == UserRole.TENANT
    
    def can_access_department(self, user: User, department_id: str) -> bool:
        """Verifica si un usuario puede acceder a un departamento"""
        if self.is_admin(user):
            return True
        if self.is_tenant(user):
            return user.department_id == department_id
        return False

