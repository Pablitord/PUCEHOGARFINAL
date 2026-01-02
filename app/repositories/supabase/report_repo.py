from typing import Optional, List
from datetime import datetime

from supabase import Client

from ...domain.entities import Report
from ...domain.enums import ReportStatus
from .client import SupabaseClient


class SupabaseReportRepository:
    """Implementación de ReportRepository usando Supabase"""
    
    def __init__(self, client: Optional[Client] = None):
        self.client = client or SupabaseClient.get_client()
        self.table = "reports"
    
    def _row_to_entity(self, row: dict) -> Report:
        """Convierte una fila de BD a entidad Report"""
        return Report(
            id=str(row["id"]),
            tenant_id=str(row["tenant_id"]),
            department_id=str(row["department_id"]),
            title=row["title"],
            description=row["description"],
            status=ReportStatus(row["status"]),
            created_at=row.get("created_at"),
            updated_at=row.get("updated_at"),
            resolved_by=row.get("resolved_by")
        )
    
    def get_by_id(self, report_id: str) -> Optional[Report]:
        """Obtiene un reporte por ID"""
        try:
            result = self.client.table(self.table).select("*").eq("id", report_id).single().execute()
            if result.data:
                return self._row_to_entity(result.data)
            return None
        except Exception:
            return None
    
    def get_by_tenant(self, tenant_id: str) -> List[Report]:
        """Obtiene reportes de un inquilino"""
        try:
            result = self.client.table(self.table).select("*").eq("tenant_id", tenant_id).order("created_at", desc=True).execute()
            return [self._row_to_entity(row) for row in result.data]
        except Exception:
            return []
    
    def get_by_status(self, status: ReportStatus) -> List[Report]:
        """Obtiene reportes por estado"""
        try:
            result = self.client.table(self.table).select("*").eq("status", status.value).order("created_at", desc=True).execute()
            return [self._row_to_entity(row) for row in result.data]
        except Exception:
            return []
    
    def get_all(self) -> List[Report]:
        """Obtiene todos los reportes"""
        try:
            result = self.client.table(self.table).select("*").order("created_at", desc=True).execute()
            return [self._row_to_entity(row) for row in result.data]
        except Exception:
            return []
    
    def create(self, report: Report) -> Report:
        """Crea un nuevo reporte"""
        data = {
            "tenant_id": report.tenant_id,
            "department_id": report.department_id,
            "title": report.title,
            "description": report.description,
            "status": report.status.value
        }
        result = self.client.table(self.table).insert(data).execute()
        return self._row_to_entity(result.data[0])
    
    def update(self, report: Report) -> Report:
        """Actualiza un reporte"""
        data = {
            "tenant_id": report.tenant_id,
            "department_id": report.department_id,
            "title": report.title,
            "description": report.description,
            "status": report.status.value,
            "resolved_by": report.resolved_by,
            "updated_at": datetime.utcnow().isoformat()
        }
        result = self.client.table(self.table).update(data).eq("id", report.id).execute()
        return self._row_to_entity(result.data[0])
    
    def update_status(
        self,
        report_id: str,
        status: ReportStatus,
        resolved_by: Optional[str] = None
    ) -> Optional[Report]:
        """Actualiza el estado de un reporte"""
        try:
            data = {
                "status": status.value,
                "updated_at": datetime.utcnow().isoformat()
            }
            if resolved_by:
                data["resolved_by"] = resolved_by
            
            result = self.client.table(self.table).update(data).eq("id", report_id).execute()
            if result.data:
                return self._row_to_entity(result.data[0])
            return None
        except Exception:
            return None

