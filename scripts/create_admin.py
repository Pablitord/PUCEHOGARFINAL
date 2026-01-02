"""
Script para crear un usuario administrador

Uso:
    python scripts/create_admin.py

El script te pedirá interactivamente:
    - Nombre completo
    - Email
    - Contraseña
"""

import sys
import os
import getpass

# Agregar el directorio raíz al path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import create_app
from app.deps import build_dependencies
from app.domain.enums import UserRole
from app.factories.user_factory import UserFactory


def create_admin():
    """Crea un usuario administrador de forma interactiva"""
    app = create_app()
    
    print("=" * 60)
    print("  CREAR USUARIO ADMINISTRADOR")
    print("=" * 60)
    print()
    
    # Solicitar datos
    full_name = input("Nombre completo: ").strip()
    if not full_name:
        print("❌ El nombre completo es requerido")
        sys.exit(1)
    
    email = input("Email: ").strip().lower()
    if not email:
        print("❌ El email es requerido")
        sys.exit(1)
    
    password = getpass.getpass("Contraseña (mínimo 6 caracteres): ")
    if len(password) < 6:
        print("❌ La contraseña debe tener al menos 6 caracteres")
        sys.exit(1)
    
    password_confirm = getpass.getpass("Confirmar contraseña: ")
    if password != password_confirm:
        print("❌ Las contraseñas no coinciden")
        sys.exit(1)
    
    print()
    print("Creando usuario administrador...")
    print()
    
    with app.app_context():
        deps = build_dependencies()
        auth_service = deps.get('auth_service')
        user_repo = auth_service.user_repo
        
        # Verificar si el usuario ya existe
        existing_user = user_repo.get_by_email(email)
        if existing_user:
            print(f"❌ El usuario con email {email} ya existe.")
            print(f"   Rol actual: {existing_user.role.value}")
            
            response = input("¿Deseas cambiar el rol a ADMIN? (s/n): ").lower()
            if response == 's':
                existing_user.role = UserRole.ADMIN
                existing_user.full_name = full_name
                user_repo.update(existing_user)
                print(f"✅ Usuario {email} actualizado a ADMIN")
            else:
                print("Operación cancelada.")
            return
        
        # Crear usuario admin usando factory
        try:
            user = UserFactory.create_admin(email, full_name)
            user = user_repo.create(user)
            print("=" * 60)
            print("✅ USUARIO ADMINISTRADOR CREADO EXITOSAMENTE!")
            print("=" * 60)
            print(f"   Nombre: {user.full_name}")
            print(f"   Email: {user.email}")
            print(f"   Rol: {user.role.value}")
            print(f"   ID: {user.id}")
            print()
            print("⚠️  NOTA: Este script solo crea el usuario en la BD.")
            print("   Para autenticación completa, deberías integrar Supabase Auth.")
            print("   Por ahora, el login funciona verificando que el usuario exista.")
        except ValueError as e:
            print(f"❌ Error de validación: {e}")
            sys.exit(1)
        except Exception as e:
            print(f"❌ Error al crear usuario: {e}")
            sys.exit(1)


if __name__ == "__main__":
    try:
        create_admin()
    except KeyboardInterrupt:
        print("\n\nOperación cancelada por el usuario.")
        sys.exit(0)

