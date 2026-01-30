from typing import List, Optional

from ..domain.entities import Rating
from ..repositories.interfaces import RatingRepository


class RatingService:
    """Servicio de gestión de calificaciones"""
    
    def __init__(self, rating_repo: RatingRepository):
        self.rating_repo = rating_repo
    
    def get_department_ratings(self, department_id: str) -> List[Rating]:
        """Obtiene todas las calificaciones de un departamento"""
        return self.rating_repo.get_by_department(department_id)
    
    def get_user_rating(self, tenant_id: str, department_id: str) -> Optional[Rating]:
        """Obtiene la calificación de un usuario para un departamento específico"""
        return self.rating_repo.get_by_tenant_and_department(tenant_id, department_id)
    
    def get_average_rating(self, department_id: str) -> Optional[float]:
        """Obtiene el promedio de calificaciones de un departamento"""
        return self.rating_repo.get_average_rating(department_id)
    
    def get_rating_count(self, department_id: str) -> int:
        """Obtiene el número de calificaciones de un departamento"""
        return self.rating_repo.get_rating_count(department_id)
    
    def create_rating(
        self,
        tenant_id: str,
        department_id: str,
        rating: int,
        comment: Optional[str] = None
    ) -> Rating:
        """Crea una nueva calificación"""
        # Validar que la calificación esté entre 1 y 5
        if rating < 1 or rating > 5:
            raise ValueError("La calificación debe estar entre 1 y 5")
        
        # Verificar si ya existe una calificación del usuario para este departamento
        existing = self.rating_repo.get_by_tenant_and_department(tenant_id, department_id)
        if existing:
            # Actualizar la calificación existente
            existing.rating = rating
            existing.comment = comment
            return self.rating_repo.update(existing)
        
        # Crear nueva calificación
        new_rating = Rating(
            id="",  # Se generará en el repositorio
            tenant_id=tenant_id,
            department_id=department_id,
            rating=rating,
            comment=comment
        )
        return self.rating_repo.create(new_rating)
    
    def update_rating(
        self,
        rating_id: str,
        rating: int,
        comment: Optional[str] = None
    ) -> Optional[Rating]:
        """Actualiza una calificación existente"""
        if rating < 1 or rating > 5:
            raise ValueError("La calificación debe estar entre 1 y 5")
        
        existing = self.rating_repo.get_by_id(rating_id)
        if not existing:
            return None
        
        existing.rating = rating
        existing.comment = comment
        return self.rating_repo.update(existing)
    
    def delete_rating(self, rating_id: str) -> bool:
        """Elimina una calificación"""
        return self.rating_repo.delete(rating_id)
