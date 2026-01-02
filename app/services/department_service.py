from typing import List, Optional

from ..domain.entities import Department
from ..domain.enums import DepartmentStatus
from ..repositories.interfaces import DepartmentRepository, StorageRepository


class DepartmentService:
    """Servicio de gestión de departamentos"""
    
    def __init__(
        self,
        department_repo: DepartmentRepository,
        storage_repo: Optional[StorageRepository] = None
    ):
        self.department_repo = department_repo
        self.storage_repo = storage_repo
    
    def get_all_departments(
        self,
        status: Optional[DepartmentStatus] = None,
        available_only: bool = False,
        filters: Optional[dict] = None
    ) -> List[Department]:
        """
        Obtiene todos los departamentos.
        
        Args:
            status: Filtrar por estado específico
            available_only: Si True, solo retorna departamentos disponibles
            filters: Filtros opcionales (características, precio, rooms)
        """
        if available_only:
            return self.department_repo.get_all(DepartmentStatus.AVAILABLE, filters)
        return self.department_repo.get_all(status, filters)
    
    def get_department_by_id(self, department_id: str) -> Optional[Department]:
        """Obtiene un departamento por ID"""
        return self.department_repo.get_by_id(department_id)
    
    def create_department(self, department: Department) -> Department:
        """Crea un nuevo departamento (solo admin)"""
        # Validaciones de negocio
        if department.price <= 0:
            raise ValueError("El precio debe ser mayor a 0")
        if not department.title or not department.address:
            raise ValueError("Título y dirección son obligatorios")
        
        return self.department_repo.create(department)
    
    def update_department(self, department: Department) -> Department:
        """Actualiza un departamento (solo admin)"""
        if department.price <= 0:
            raise ValueError("El precio debe ser mayor a 0")
        if not department.title or not department.address:
            raise ValueError("Título y dirección son obligatorios")
        
        return self.department_repo.update(department)
    
    def delete_department(self, department_id: str) -> bool:
        """Elimina un departamento (solo admin)"""
        # Verificar que no esté ocupado
        dept = self.department_repo.get_by_id(department_id)
        if dept and dept.status == DepartmentStatus.OCCUPIED:
            raise ValueError("No se puede eliminar un departamento ocupado")
        
        return self.department_repo.delete(department_id)
    
    def mark_as_occupied(self, department_id: str) -> Optional[Department]:
        """Marca un departamento como ocupado"""
        dept = self.department_repo.get_by_id(department_id)
        if not dept:
            return None
        
        dept.status = DepartmentStatus.OCCUPIED
        return self.department_repo.update(dept)
    
    def mark_as_available(self, department_id: str) -> Optional[Department]:
        """Marca un departamento como disponible"""
        dept = self.department_repo.get_by_id(department_id)
        if not dept:
            return None
        
        dept.status = DepartmentStatus.AVAILABLE
        return self.department_repo.update(dept)
    
    def upload_department_image(
        self,
        department_id: str,
        file_content: bytes,
        file_name: str
    ) -> Optional[Department]:
        """Sube una imagen para un departamento"""
        if not self.storage_repo:
            raise ValueError("Storage repository no configurado")
        
        dept = self.department_repo.get_by_id(department_id)
        if not dept:
            return None
        
        try:
            # Subir imagen
            image_url = self.storage_repo.upload_file(
                file_content=file_content,
                file_name=file_name
            )
            
            # Actualizar departamento con URL de la imagen
            dept.image_url = image_url
            return self.department_repo.update(dept)
        except Exception as e:
            raise Exception(f"Error al subir imagen: {str(e)}")

