from supabase import create_client, Client
from typing import Optional

from ...config import Config


class SupabaseClient:
    """Cliente singleton para Supabase"""
    
    _instance: Optional[Client] = None
    _service_role_instance: Optional[Client] = None
    
    @classmethod
    def get_client(cls) -> Client:
        """Obtiene o crea el cliente de Supabase (anon key)"""
        if cls._instance is None:
            if not Config.SUPABASE_URL or not Config.SUPABASE_KEY:
                raise ValueError(
                    "SUPABASE_URL y SUPABASE_KEY deben estar configurados. "
                    "Configúralos en variables de entorno o config_local.py"
                )
            cls._instance = create_client(Config.SUPABASE_URL, Config.SUPABASE_KEY)
        return cls._instance
    
    @classmethod
    def get_service_role_client(cls) -> Client:
        """Obtiene o crea el cliente de Supabase con Service Role Key (bypasea RLS)"""
        if cls._service_role_instance is None:
            if not Config.SUPABASE_URL:
                raise ValueError("SUPABASE_URL debe estar configurado")
            
            # Si no hay SERVICE_ROLE_KEY, usar la anon key (con advertencia)
            service_key = Config.SUPABASE_SERVICE_ROLE_KEY or Config.SUPABASE_KEY
            if not Config.SUPABASE_SERVICE_ROLE_KEY:
                print("⚠️  ADVERTENCIA: No se configuró SUPABASE_SERVICE_ROLE_KEY. Usando anon key.")
                print("   Para operaciones de Storage, configura SUPABASE_SERVICE_ROLE_KEY en config_local.py")
            
            cls._service_role_instance = create_client(Config.SUPABASE_URL, service_key)
        return cls._service_role_instance

