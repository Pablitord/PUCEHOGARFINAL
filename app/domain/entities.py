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
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


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
    # Características especiales
    has_terrace: bool = False
    has_balcony: bool = False
    sea_view: bool = False
    parking: bool = False
    furnished: bool = False
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
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    resolved_by: Optional[str] = None  # ID del admin que resolvió

