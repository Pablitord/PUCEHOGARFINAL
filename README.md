# PUCEHOGAR

Sistema de gestión de departamentos desarrollado con Flask y Supabase, siguiendo principios SOLID y patrones de diseño Repository y Factory.

## 🏗️ Arquitectura

El proyecto sigue una arquitectura en capas con separación de responsabilidades:

- **Domain**: Entidades y enums del dominio (sin dependencias externas)
- **Repositories**: Interfaces y implementaciones para acceso a datos
- **Services**: Lógica de negocio
- **Routes**: Controladores que manejan requests HTTP
- **Templates**: Vistas HTML con Jinja2

## 📋 Requisitos

- Python 3.8+
- Cuenta de Supabase (gratuita)

## 🚀 Instalación

1. Clonar el repositorio
2. Crear un entorno virtual:
```bash
python -m venv venv
```

3. Activar el entorno virtual:
```bash
# Windows
venv\Scripts\activate

# Linux/Mac
source venv/bin/activate
```

4. Instalar dependencias:
```bash
pip install -r requirements.txt
```

5. Configurar variables de entorno:

Crea un archivo `.env` en la raíz del proyecto o configura las variables directamente:

```env
SECRET_KEY=tu-clave-secreta-super-segura
SUPABASE_URL=https://tu-proyecto.supabase.co
SUPABASE_KEY=tu-anon-key-de-supabase
STORAGE_BUCKET=comprobantes
FLASK_DEBUG=True
```

O crea `app/config_local.py`:

```python
import os

class Config:
    SECRET_KEY = "tu-clave-secreta"
    SUPABASE_URL = "https://tu-proyecto.supabase.co"
    SUPABASE_KEY = "tu-anon-key"
    STORAGE_BUCKET = "comprobantes"
    DEBUG = True
```

## 🗄️ Configuración de Supabase

### 1. Crear las tablas

Ejecuta estos SQL en el SQL Editor de Supabase:

```sql
-- Tabla de usuarios
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email TEXT UNIQUE NOT NULL,
    role TEXT NOT NULL CHECK (role IN ('admin', 'tenant', 'visitor')),
    full_name TEXT,
    department_id UUID REFERENCES departments(id),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Tabla de departamentos
CREATE TABLE departments (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    title TEXT NOT NULL,
    address TEXT NOT NULL,
    price DECIMAL(10, 2) NOT NULL,
    status TEXT NOT NULL CHECK (status IN ('available', 'occupied', 'maintenance')),
    description TEXT,
    rooms INTEGER,
    bathrooms INTEGER,
    area DECIMAL(10, 2),
    image_url TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Tabla de pagos
CREATE TABLE payments (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id UUID NOT NULL REFERENCES users(id),
    department_id UUID NOT NULL REFERENCES departments(id),
    amount DECIMAL(10, 2) NOT NULL,
    status TEXT NOT NULL CHECK (status IN ('pending', 'approved', 'rejected')),
    month TEXT NOT NULL,
    receipt_url TEXT,
    notes TEXT,
    reviewed_by UUID REFERENCES users(id),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Tabla de reportes
CREATE TABLE reports (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id UUID NOT NULL REFERENCES users(id),
    department_id UUID NOT NULL REFERENCES departments(id),
    title TEXT NOT NULL,
    description TEXT NOT NULL,
    status TEXT NOT NULL CHECK (status IN ('open', 'in_progress', 'resolved', 'closed')),
    resolved_by UUID REFERENCES users(id),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Índices para mejorar rendimiento
CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_users_department ON users(department_id);
CREATE INDEX idx_payments_tenant ON payments(tenant_id);
CREATE INDEX idx_payments_status ON payments(status);
CREATE INDEX idx_reports_tenant ON reports(tenant_id);
CREATE INDEX idx_reports_status ON reports(status);
```

### 2. Crear el bucket de Storage

**⚠️ IMPORTANTE**: Lee la guía completa en `docs/SETUP_SUPABASE_STORAGE.md`

Resumen rápido:
1. Ve a Storage en el panel de Supabase
2. Crea un nuevo bucket llamado `comprobantes` (exactamente este nombre)
3. **Marca como "Public bucket"** ✅
4. Configura políticas RLS:
   - INSERT: Para usuarios autenticados
   - SELECT: Público (para poder ver los comprobantes)

Ver `docs/SETUP_SUPABASE_STORAGE.md` para instrucciones detalladas y solución de problemas.

### 3. Configurar políticas RLS (Row Level Security)

Si quieres habilitar RLS, puedes configurar políticas personalizadas. Por ahora, el proyecto asume que las políticas están configuradas para permitir acceso según roles.

## 🏃 Ejecutar la aplicación

```bash
python run.py
```

La aplicación estará disponible en `http://localhost:5000`

## 👥 Roles de Usuario

- **VISITOR**: Usuario no autenticado, puede ver departamentos disponibles
- **TENANT**: Inquilino, puede gestionar pagos y crear reportes
- **ADMIN**: Administrador, puede gestionar todo el sistema

## 📁 Estructura del Proyecto

```
PUCEHOGAR/
├── app/
│   ├── __init__.py          # Factory de Flask app
│   ├── config.py            # Configuración
│   ├── deps.py              # Inyección de dependencias
│   ├── domain/              # Capa de dominio
│   │   ├── entities.py      # Entidades del dominio
│   │   └── enums.py         # Enumeraciones
│   ├── factories/           # Patrón Factory
│   │   └── user_factory.py
│   ├── repositories/        # Patrón Repository
│   │   ├── interfaces.py    # Interfaces (Protocol)
│   │   └── supabase/        # Implementaciones
│   ├── routes/              # Controladores
│   ├── services/            # Lógica de negocio
│   ├── static/              # CSS/JS
│   └── templates/           # Vistas HTML
├── run.py                   # Punto de entrada
└── requirements.txt         # Dependencias
```

## 🎯 Principios SOLID Aplicados

- **S**ingle Responsibility: Cada clase tiene una única responsabilidad
- **O**pen/Closed: Extensible mediante interfaces
- **L**iskov Substitution: Repositorios intercambiables
- **I**nterface Segregation: Interfaces específicas por repositorio
- **D**ependency Inversion: Dependencias inyectadas, no hardcodeadas

## 🏭 Patrones de Diseño

- **Repository Pattern**: Abstracción del acceso a datos
- **Factory Pattern**: Creación de usuarios con validación

## 📝 Notas

- El sistema de autenticación actual es básico. En producción, deberías integrar Supabase Auth completo.
- Las imágenes de departamentos pueden ser URLs externas o subidas a Supabase Storage.
- Los comprobantes de pago se almacenan en Supabase Storage.

## 🔒 Seguridad

- Usa variables de entorno para credenciales sensibles
- Cambia `SECRET_KEY` en producción
- Configura RLS en Supabase según tus necesidades
- Valida todas las entradas del usuario

## 📄 Licencia

Este proyecto es privado.
