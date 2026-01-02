"""
Módulo de inyección de dependencias (DIP - Dependency Inversion Principle)

Aquí se conectan todas las piezas:
- Cliente Supabase
- Repositorios
- Servicios

Retorna un diccionario con todos los servicios listos para usar en las rutas.
"""

from typing import Dict, Any

from .repositories.supabase.client import SupabaseClient
from .repositories.supabase.user_repo import SupabaseUserRepository
from .repositories.supabase.department_repo import SupabaseDepartmentRepository
from .repositories.supabase.payment_repo import SupabasePaymentRepository
from .repositories.supabase.report_repo import SupabaseReportRepository
from .repositories.supabase.storage_repo import SupabaseStorageRepository

from .services.auth_service import AuthService
from .services.department_service import DepartmentService
from .services.payment_service import PaymentService
from .services.report_service import ReportService


def build_dependencies() -> Dict[str, Any]:
    """
    Construye todas las dependencias y retorna un diccionario con los servicios.
    
    Returns:
        Dict con las siguientes claves:
        - auth_service: AuthService
        - department_service: DepartmentService
        - payment_service: PaymentService
        - report_service: ReportService
    """
    # Cliente Supabase
    client = SupabaseClient.get_client()
    
    # Repositorios
    user_repo = SupabaseUserRepository(client)
    department_repo = SupabaseDepartmentRepository(client)
    payment_repo = SupabasePaymentRepository(client)
    report_repo = SupabaseReportRepository(client)
    storage_repo = SupabaseStorageRepository(client)
    
    # Servicios (inyección de dependencias)
    auth_service = AuthService(user_repo)
    department_service = DepartmentService(department_repo, storage_repo)
    payment_service = PaymentService(payment_repo, storage_repo)
    report_service = ReportService(report_repo)
    
    return {
        "auth_service": auth_service,
        "department_service": department_service,
        "payment_service": payment_service,
        "report_service": report_service
    }

