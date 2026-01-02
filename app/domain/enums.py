from enum import Enum


class PaymentStatus(str, Enum):
    """Estados de un pago"""
    PENDING = "pending"  # Pendiente de revisión
    APPROVED = "approved"  # Aprobado
    REJECTED = "rejected"  # Rechazado


class ReportStatus(str, Enum):
    """Estados de un reporte"""
    OPEN = "open"  # Abierto
    IN_PROGRESS = "in_progress"  # En progreso
    RESOLVED = "resolved"  # Resuelto
    CLOSED = "closed"  # Cerrado


class DepartmentStatus(str, Enum):
    """Estados de un departamento"""
    AVAILABLE = "available"  # Disponible
    OCCUPIED = "occupied"  # Ocupado
    MAINTENANCE = "maintenance"  # En mantenimiento


class UserRole(str, Enum):
    """Roles de usuario"""
    ADMIN = "admin"  # Administrador
    TENANT = "tenant"  # Inquilino
    VISITOR = "visitor"  # Visitante (sin autenticación)

