from typing import Optional
import uuid
from datetime import datetime
import mimetypes

from supabase import Client

from ...config import Config
from .client import SupabaseClient


class SupabaseStorageRepository:
    """Implementación de StorageRepository usando Supabase Storage"""
    
    def __init__(self, client: Optional[Client] = None, use_service_role: bool = True):
        """
        Inicializa el repositorio de storage.
        
        Args:
            client: Cliente de Supabase (opcional)
            use_service_role: Si True, usa Service Role Key para bypasear RLS (recomendado)
        """
        if use_service_role:
            self.client = client or SupabaseClient.get_service_role_client()
        else:
            self.client = client or SupabaseClient.get_client()
        self.bucket = Config.STORAGE_BUCKET
    
    def _detect_content_type(self, file_name: str) -> str:
        """Detecta el tipo MIME del archivo"""
        mime_type, _ = mimetypes.guess_type(file_name)
        if mime_type:
            return mime_type
        
        # Fallback según extensión
        extension = file_name.lower().split('.')[-1] if '.' in file_name else ''
        mime_map = {
            'jpg': 'image/jpeg',
            'jpeg': 'image/jpeg',
            'png': 'image/png',
            'gif': 'image/gif',
            'pdf': 'application/pdf',
            'webp': 'image/webp'
        }
        return mime_map.get(extension, 'application/octet-stream')
    
    def upload_file(
        self,
        file_content: bytes,
        file_name: str,
        content_type: Optional[str] = None
    ) -> str:
        """Sube un archivo y retorna la URL pública"""
        try:
            # Detectar content type si no se proporciona
            if not content_type:
                content_type = self._detect_content_type(file_name)
            
            # Generar nombre único para evitar colisiones
            timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
            unique_id = str(uuid.uuid4())[:8]
            file_extension = file_name.split('.')[-1].lower() if '.' in file_name else ''
            safe_file_name = f"{timestamp}_{unique_id}.{file_extension}" if file_extension else f"{timestamp}_{unique_id}"
            
            # Subir archivo
            result = self.client.storage.from_(self.bucket).upload(
                path=safe_file_name,
                file=file_content,
                file_options={
                    "content-type": content_type,
                    "upsert": "false"  # No sobrescribir si existe
                }
            )
            
            # Verificar que se subió correctamente
            if result:
                # Obtener URL pública
                url_result = self.client.storage.from_(self.bucket).get_public_url(safe_file_name)
                return url_result
            else:
                raise Exception("No se recibió respuesta del servidor al subir el archivo")
                
        except Exception as e:
            error_msg = str(e)
            # Mejorar mensaje de error
            if "Bucket not found" in error_msg or "does not exist" in error_msg:
                raise Exception(f"El bucket '{self.bucket}' no existe en Supabase. Crea el bucket en Storage primero.")
            elif "new row violates row-level security" in error_msg.lower():
                raise Exception("Error de permisos. Verifica las políticas RLS del bucket en Supabase.")
            elif "duplicate" in error_msg.lower():
                raise Exception("Ya existe un archivo con ese nombre. Intenta de nuevo.")
            else:
                raise Exception(f"Error al subir archivo: {error_msg}")
    
    def delete_file(self, file_path: str) -> bool:
        """Elimina un archivo"""
        try:
            # Extraer el nombre del archivo de la URL si es necesario
            if "/" in file_path:
                file_name = file_path.split("/")[-1]
            else:
                file_name = file_path
            
            self.client.storage.from_(self.bucket).remove([file_name])
            return True
        except Exception:
            return False

