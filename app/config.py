import os
from typing import Optional

# Cargar variables de entorno desde .env si existe (local)
try:
    from dotenv import load_dotenv
    load_dotenv()
except Exception:
    pass


class Config:
    """Configuración de la aplicación"""
    
    # Flask
    SECRET_KEY: str = os.getenv("SECRET_KEY", "")
    
    # Supabase
    SUPABASE_URL: str = os.getenv("SUPABASE_URL", "")
    SUPABASE_KEY: str = os.getenv("SUPABASE_KEY", "")
    # Service Role Key (bypasa RLS - solo para operaciones de servidor)
    SUPABASE_SERVICE_ROLE_KEY: str = os.getenv("SUPABASE_SERVICE_ROLE_KEY", "")
    
    # Storage
    STORAGE_BUCKET: str = os.getenv("STORAGE_BUCKET", "comprobantes")
    
    # Debug
    DEBUG: bool = os.getenv("FLASK_DEBUG", "False").lower() == "true"




