import os
from typing import Optional


class Config:
    """Configuración de la aplicación"""
    
    # Flask
    SECRET_KEY: str = os.getenv("SECRET_KEY", "dev-secret-key-change-in-production")
    
    # Supabase
    SUPABASE_URL: str = os.getenv("SUPABASE_URL", "https://ajllimnmijoydpzrrpyn.supabase.co")
    SUPABASE_KEY: str = os.getenv("SUPABASE_KEY", "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImFqbGxpbW5taWpveWRwenJycHluIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NjcxMTkzOTMsImV4cCI6MjA4MjY5NTM5M30.QGsG81mcOaFA9QNrneLb-qaKBekmmTTn8tKa3kvQJyg")
    # Service Role Key (bypasea RLS - solo para operaciones de servidor)
    SUPABASE_SERVICE_ROLE_KEY: str = os.getenv("SUPABASE_SERVICE_ROLE_KEY", "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImFqbGxpbW5taWpveWRwenJycHluIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc2NzExOTM5MywiZXhwIjoyMDgyNjk1MzkzfQ.7vUxg0e6OwXhmeGSecsnI4CzjHm8tRSWA4RgobVSPuU")
    
    # Storage
    STORAGE_BUCKET: str = os.getenv("STORAGE_BUCKET", "comprobantes")
    
    # Debug
    DEBUG: bool = os.getenv("FLASK_DEBUG", "False").lower() == "true"




