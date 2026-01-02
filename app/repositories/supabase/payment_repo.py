from typing import Optional, List
from datetime import datetime

from supabase import Client

from ...domain.entities import Payment
from ...domain.enums import PaymentStatus
from .client import SupabaseClient


class SupabasePaymentRepository:
    """Implementación de PaymentRepository usando Supabase"""
    
    def __init__(self, client: Optional[Client] = None):
        self.client = client or SupabaseClient.get_client()
        self.table = "payments"
    
    def _row_to_entity(self, row: dict) -> Payment:
        """Convierte una fila de BD a entidad Payment"""
        def _parse_dt(val):
            if not val:
                return None
            if isinstance(val, datetime):
                return val
            try:
                return datetime.fromisoformat(val.replace("Z", "+00:00"))
            except Exception:
                return None
        return Payment(
            id=str(row["id"]),
            tenant_id=str(row["tenant_id"]),
            department_id=str(row["department_id"]),
            amount=float(row["amount"]),
            status=PaymentStatus(row["status"]),
            month=row["month"],
            receipt_url=row.get("receipt_url"),
            notes=row.get("notes"),
            created_at=_parse_dt(row.get("created_at")),
            updated_at=_parse_dt(row.get("updated_at")),
            reviewed_by=row.get("reviewed_by")
        )
    
    def get_by_id(self, payment_id: str) -> Optional[Payment]:
        """Obtiene un pago por ID"""
        try:
            result = self.client.table(self.table).select("*").eq("id", payment_id).single().execute()
            if result.data:
                return self._row_to_entity(result.data)
            return None
        except Exception:
            return None
    
    def get_by_tenant(self, tenant_id: str) -> List[Payment]:
        """Obtiene pagos de un inquilino"""
        try:
            result = self.client.table(self.table).select("*").eq("tenant_id", tenant_id).order("month", desc=True).execute()
            return [self._row_to_entity(row) for row in result.data]
        except Exception:
            return []
    
    def get_by_status(self, status: PaymentStatus) -> List[Payment]:
        """Obtiene pagos por estado"""
        try:
            result = self.client.table(self.table).select("*").eq("status", status.value).order("created_at", desc=True).execute()
            return [self._row_to_entity(row) for row in result.data]
        except Exception:
            return []
    
    def create(self, payment: Payment) -> Payment:
        """Crea un nuevo pago"""
        data = {
            "tenant_id": payment.tenant_id,
            "department_id": payment.department_id,
            "amount": payment.amount,
            "status": payment.status.value,
            "month": payment.month,
            "receipt_url": payment.receipt_url,
            "notes": payment.notes
        }
        result = self.client.table(self.table).insert(data).execute()
        return self._row_to_entity(result.data[0])
    
    def update(self, payment: Payment) -> Payment:
        """Actualiza un pago"""
        data = {
            "tenant_id": payment.tenant_id,
            "department_id": payment.department_id,
            "amount": payment.amount,
            "status": payment.status.value,
            "month": payment.month,
            "receipt_url": payment.receipt_url,
            "notes": payment.notes,
            "reviewed_by": payment.reviewed_by,
            "updated_at": datetime.utcnow().isoformat()
        }
        result = self.client.table(self.table).update(data).eq("id", payment.id).execute()
        return self._row_to_entity(result.data[0])
    
    def update_status(
        self,
        payment_id: str,
        status: PaymentStatus,
        reviewed_by: Optional[str] = None
    ) -> Optional[Payment]:
        """Actualiza el estado de un pago"""
        try:
            data = {
                "status": status.value,
                "updated_at": datetime.utcnow().isoformat()
            }
            if reviewed_by:
                data["reviewed_by"] = reviewed_by
            
            result = self.client.table(self.table).update(data).eq("id", payment_id).execute()
            if result.data:
                return self._row_to_entity(result.data[0])
            return None
        except Exception:
            return None

