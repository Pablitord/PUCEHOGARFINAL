from typing import Protocol, Optional, List
from datetime import datetime

from ..domain.entities import Department, Payment, Report, User, Notification
from ..domain.enums import DepartmentStatus, PaymentStatus, ReportStatus


class UserRepository(Protocol):
    """Interface para repositorio de usuarios"""
    
    def get_by_id(self, user_id: str) -> Optional[User]:
        """Obtiene un usuario por ID"""
        ...
    
    def get_by_email(self, email: str) -> Optional[User]:
        """Obtiene un usuario por email"""
        ...
    
    def create(self, user: User) -> User:
        """Crea un nuevo usuario"""
        ...
    
    def update(self, user: User) -> User:
        """Actualiza un usuario"""
        ...
    
    def get_tenants_by_department(self, department_id: str) -> List[User]:
        """Obtiene inquilinos de un departamento"""
        ...

    def get_admins(self) -> List[User]:
        """Obtiene todos los administradores"""
        ...

    def has_admins(self) -> bool:
        """Retorna True si existe al menos un admin"""
        ...


class DepartmentRepository(Protocol):
    """Interface para repositorio de departamentos"""
    
    def get_by_id(self, department_id: str) -> Optional[Department]:
        """Obtiene un departamento por ID"""
        ...
    
    def get_all(
        self,
        status: Optional[DepartmentStatus] = None,
        filters: Optional[dict] = None
    ) -> List[Department]:
        """Obtiene todos los departamentos, con filtros opcionales (características, rangos)"""
        ...
    
    def create(self, department: Department) -> Department:
        """Crea un nuevo departamento"""
        ...
    
    def update(self, department: Department) -> Department:
        """Actualiza un departamento"""
        ...
    
    def delete(self, department_id: str) -> bool:
        """Elimina un departamento"""
        ...


class PaymentRepository(Protocol):
    """Interface para repositorio de pagos"""
    
    def get_by_id(self, payment_id: str) -> Optional[Payment]:
        """Obtiene un pago por ID"""
        ...
    
    def get_by_tenant(self, tenant_id: str) -> List[Payment]:
        """Obtiene pagos de un inquilino"""
        ...
    
    def get_by_status(self, status: PaymentStatus) -> List[Payment]:
        """Obtiene pagos por estado"""
        ...
    
    def create(self, payment: Payment) -> Payment:
        """Crea un nuevo pago"""
        ...
    
    def update(self, payment: Payment) -> Payment:
        """Actualiza un pago"""
        ...
    
    def update_status(
        self,
        payment_id: str,
        status: PaymentStatus,
        reviewed_by: Optional[str] = None
    ) -> Optional[Payment]:
        """Actualiza el estado de un pago"""
        ...


class ReportRepository(Protocol):
    """Interface para repositorio de reportes"""
    
    def get_by_id(self, report_id: str) -> Optional[Report]:
        """Obtiene un reporte por ID"""
        ...
    
    def get_by_tenant(self, tenant_id: str) -> List[Report]:
        """Obtiene reportes de un inquilino"""
        ...
    
    def get_by_status(self, status: ReportStatus) -> List[Report]:
        """Obtiene reportes por estado"""
        ...
    
    def get_all(self) -> List[Report]:
        """Obtiene todos los reportes"""
        ...
    
    def create(self, report: Report) -> Report:
        """Crea un nuevo reporte"""
        ...
    
    def update(self, report: Report) -> Report:
        """Actualiza un reporte"""
        ...
    
    def update_status(
        self,
        report_id: str,
        status: ReportStatus,
        resolved_by: Optional[str] = None
    ) -> Optional[Report]:
        """Actualiza el estado de un reporte"""
        ...

    def update_notes(self, report_id: str, notes: Optional[str]) -> Optional[Report]:
        """Actualiza notas del reporte"""
        ...


class NotificationRepository(Protocol):
    """Interface para repositorio de notificaciones"""

    def create(self, notification: Notification) -> Notification:
        """Crea una notificación"""
        ...

    def get_unread_by_user(self, user_id: str, limit: int = 10) -> List[Notification]:
        """Obtiene notificaciones no leídas de un usuario"""
        ...

    def mark_as_read(self, notification_id: str, user_id: str) -> bool:
        """Marca como leída una notificación si pertenece al usuario"""
        ...

    def mark_all_as_read(self, user_id: str) -> bool:
        """Marca todas las notificaciones del usuario como leídas"""
        ...


class StorageRepository(Protocol):
    """Interface para repositorio de almacenamiento"""
    
    def upload_file(
        self,
        file_content: bytes,
        file_name: str,
        content_type: str = "application/octet-stream"
    ) -> str:
        """Sube un archivo y retorna la URL"""
        ...
    
    def delete_file(self, file_path: str) -> bool:
        """Elimina un archivo"""
        ...

