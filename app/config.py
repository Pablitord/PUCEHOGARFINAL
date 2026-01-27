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

    # SMTP / Email
    SMTP_HOST: str = os.getenv("SMTP_HOST", "")
    SMTP_PORT: int = int(os.getenv("SMTP_PORT", "587"))
    SMTP_USER: str = os.getenv("SMTP_USER", "")
    SMTP_PASSWORD: str = os.getenv("SMTP_PASSWORD", "")
    SMTP_FROM: str = os.getenv("SMTP_FROM", "")
    SMTP_USE_TLS: bool = os.getenv("SMTP_USE_TLS", "True").lower() == "true"




