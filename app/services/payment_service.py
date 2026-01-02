from typing import List, Optional
from datetime import datetime

from ..domain.entities import Payment
from ..domain.enums import PaymentStatus
from ..repositories.interfaces import PaymentRepository, StorageRepository


class PaymentService:
    """Servicio de gestión de pagos"""
    
    def __init__(
        self,
        payment_repo: PaymentRepository,
        storage_repo: StorageRepository
    ):
        self.payment_repo = payment_repo
        self.storage_repo = storage_repo
    
    def get_payments_by_tenant(self, tenant_id: str) -> List[Payment]:
        """Obtiene todos los pagos de un inquilino"""
        return self.payment_repo.get_by_tenant(tenant_id)
    
    def get_payment_by_id(self, payment_id: str) -> Optional[Payment]:
        """Obtiene un pago por ID"""
        return self.payment_repo.get_by_id(payment_id)
    
    def get_pending_payments(self) -> List[Payment]:
        """Obtiene todos los pagos pendientes (para admin)"""
        return self.payment_repo.get_by_status(PaymentStatus.PENDING)
    
    def get_payments_by_status(self, status: PaymentStatus) -> List[Payment]:
        """Obtiene pagos por estado"""
        return self.payment_repo.get_by_status(status)
    
    def create_payment(
        self,
        tenant_id: str,
        department_id: str,
        amount: float,
        month: str,
        notes: Optional[str] = None
    ) -> Payment:
        """Crea un nuevo pago"""
        # Validaciones
        if amount <= 0:
            raise ValueError("El monto debe ser mayor a 0")
        
        # Validar formato de mes (YYYY-MM)
        try:
            datetime.strptime(month, "%Y-%m")
        except ValueError:
            raise ValueError("El formato del mes debe ser YYYY-MM")
        
        payment = Payment(
            id="",
            tenant_id=tenant_id,
            department_id=department_id,
            amount=amount,
            status=PaymentStatus.PENDING,
            month=month,
            notes=notes
        )
        
        return self.payment_repo.create(payment)
    
    def create_payment_with_receipt(
        self,
        tenant_id: str,
        department_id: str,
        amount: float,
        month: str,
        file_content: bytes,
        file_name: str,
        notes: Optional[str] = None
    ) -> Optional[Payment]:
        """Crea un pago y sube el comprobante en un solo paso"""
        try:
            # Crear el pago
            payment = self.create_payment(
                tenant_id=tenant_id,
                department_id=department_id,
                amount=amount,
                month=month,
                notes=notes
            )
            
            # Subir comprobante
            updated_payment = self.upload_receipt(
                payment_id=payment.id,
                file_content=file_content,
                file_name=file_name
            )
            
            return updated_payment
        except Exception as e:
            raise Exception(f"Error al crear pago con comprobante: {str(e)}")
    
    def upload_receipt(
        self,
        payment_id: str,
        file_content: bytes,
        file_name: str
    ) -> Optional[Payment]:
        """Sube un comprobante y lo asocia a un pago"""
        payment = self.payment_repo.get_by_id(payment_id)
        if not payment:
            return None
        
        try:
            # Subir archivo (el storage_repo detectará automáticamente el content_type)
            receipt_url = self.storage_repo.upload_file(
                file_content=file_content,
                file_name=file_name
            )
            
            # Actualizar pago con URL del comprobante
            payment.receipt_url = receipt_url
            return self.payment_repo.update(payment)
        except Exception as e:
            # Re-lanzar la excepción con el mensaje mejorado
            raise Exception(str(e))
    
    def approve_payment(
        self,
        payment_id: str,
        reviewed_by: str
    ) -> Optional[Payment]:
        """Aprueba un pago (solo admin)"""
        return self.payment_repo.update_status(
            payment_id=payment_id,
            status=PaymentStatus.APPROVED,
            reviewed_by=reviewed_by
        )
    
    def reject_payment(
        self,
        payment_id: str,
        reviewed_by: str,
        notes: Optional[str] = None
    ) -> Optional[Payment]:
        """Rechaza un pago (solo admin)"""
        payment = self.payment_repo.get_by_id(payment_id)
        if not payment:
            return None
        
        payment.status = PaymentStatus.REJECTED
        payment.reviewed_by = reviewed_by
        if notes:
            payment.notes = notes
        
        return self.payment_repo.update(payment)

