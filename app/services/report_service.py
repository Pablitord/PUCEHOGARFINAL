from typing import List, Optional

from ..domain.entities import Report
from ..domain.enums import ReportStatus
from ..repositories.interfaces import ReportRepository


class ReportService:
    """Servicio de gestión de reportes"""
    
    def __init__(self, report_repo: ReportRepository):
        self.report_repo = report_repo
    
    def get_reports_by_tenant(self, tenant_id: str) -> List[Report]:
        """Obtiene todos los reportes de un inquilino"""
        return self.report_repo.get_by_tenant(tenant_id)
    
    def get_report_by_id(self, report_id: str) -> Optional[Report]:
        """Obtiene un reporte por ID"""
        return self.report_repo.get_by_id(report_id)
    
    def get_all_reports(self) -> List[Report]:
        """Obtiene todos los reportes (para admin)"""
        return self.report_repo.get_all()
    
    def get_open_reports(self) -> List[Report]:
        """Obtiene reportes abiertos (para admin)"""
        return self.report_repo.get_by_status(ReportStatus.OPEN)
    
    def create_report(
        self,
        tenant_id: str,
        department_id: str,
        title: str,
        description: str
    ) -> Report:
        """Crea un nuevo reporte"""
        # Validaciones
        if not title or not title.strip():
            raise ValueError("El título es obligatorio")
        if not description or not description.strip():
            raise ValueError("La descripción es obligatoria")
        
        report = Report(
            id="",
            tenant_id=tenant_id,
            department_id=department_id,
            title=title.strip(),
            description=description.strip(),
            status=ReportStatus.OPEN
        )
        
        return self.report_repo.create(report)
    
    def update_report_status(
        self,
        report_id: str,
        status: ReportStatus,
        resolved_by: Optional[str] = None
    ) -> Optional[Report]:
        """Actualiza el estado de un reporte"""
        return self.report_repo.update_status(
            report_id=report_id,
            status=status,
            resolved_by=resolved_by
        )
    
    def mark_as_in_progress(
        self,
        report_id: str,
        resolved_by: str
    ) -> Optional[Report]:
        """Marca un reporte como en progreso"""
        return self.update_report_status(
            report_id=report_id,
            status=ReportStatus.IN_PROGRESS,
            resolved_by=resolved_by
        )
    
    def resolve_report(
        self,
        report_id: str,
        resolved_by: str
    ) -> Optional[Report]:
        """Resuelve un reporte"""
        return self.update_report_status(
            report_id=report_id,
            status=ReportStatus.RESOLVED,
            resolved_by=resolved_by
        )
    
    def close_report(
        self,
        report_id: str,
        resolved_by: str
    ) -> Optional[Report]:
        """Cierra un reporte"""
        return self.update_report_status(
            report_id=report_id,
            status=ReportStatus.CLOSED,
            resolved_by=resolved_by
        )

