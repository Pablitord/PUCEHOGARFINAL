from dataclasses import dataclass
from datetime import datetime
from typing import Optional

from .enums import DepartmentStatus, PaymentStatus, ReportStatus, UserRole


@dataclass
class User:
    """Entidad Usuario"""
    id: str
    email: str
    role: UserRole
    full_name: Optional[str] = None
    department_id: Optional[str] = None
    password_hash: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


@dataclass
class Notification:
    """Entidad Notificación"""
    id: str
    user_id: str
    title: str
    message: str
    link: Optional[str]
    type: Optional[str]
    is_read: bool
    created_at: Optional[datetime] = None


@dataclass
class Department:
    """Entidad Departamento"""
    id: str
    title: str
    address: str
    price: float
    status: DepartmentStatus
    description: Optional[str] = None
    rooms: Optional[int] = None
    bathrooms: Optional[int] = None
    area: Optional[float] = None
    image_url: Optional[str] = None
    image_url_2: Optional[str] = None
    image_url_3: Optional[str] = None
    # Características especiales
    has_terrace: bool = False
    has_balcony: bool = False
    sea_view: bool = False
    parking: bool = False
    furnished: bool = False
    allow_pets: bool = False
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


@dataclass
class Payment:
    """Entidad Pago"""
    id: str
    tenant_id: str
    department_id: str
    amount: float
    status: PaymentStatus
    month: str  # Formato: "YYYY-MM"
    receipt_url: Optional[str] = None
    notes: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    reviewed_by: Optional[str] = None  # ID del admin que revisó


@dataclass
class Report:
    """Entidad Reporte"""
    id: str
    tenant_id: str
    department_id: str
    title: str
    description: str
    status: ReportStatus
    notes: Optional[str] = None
    attachment_url: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    resolved_by: Optional[str] = None  # ID del admin que resolvió


@dataclass
class Rating:
    """Entidad Calificación"""
    id: str
    tenant_id: str
    department_id: str
    rating: int  # 1-5 estrellas
    comment: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

