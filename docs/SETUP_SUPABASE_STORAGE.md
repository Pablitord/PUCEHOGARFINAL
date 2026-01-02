# Guía: Configuración del Bucket de Storage en Supabase

Esta guía te ayudará a crear y configurar correctamente el bucket `comprobantes` en Supabase Storage para que puedas subir y visualizar los comprobantes de pago.

## 📋 Paso 1: Crear el Bucket

1. **Accede a tu proyecto de Supabase**
   - Ve a [https://supabase.com](https://supabase.com)
   - Inicia sesión y selecciona tu proyecto

2. **Navega a Storage**
   - En el menú lateral izquierdo, haz clic en **"Storage"**
   - Verás una lista de buckets (si ya tienes alguno)

3. **Crear nuevo bucket**
   - Haz clic en el botón **"New bucket"** o **"Crear bucket"**
   - Nombre del bucket: `comprobantes` (debe ser exactamente este nombre)
   - **IMPORTANTE**: Marca la opción **"Public bucket"** ✅
     - Esto permite que los archivos sean accesibles públicamente mediante URL
   - Haz clic en **"Create bucket"**

## 🔒 Paso 2: Configurar Políticas RLS (Row Level Security)

Para que los usuarios puedan subir archivos, necesitas configurar las políticas de seguridad:

### Opción A: Política Pública (Más Simple - Para Desarrollo)

1. **Ve a Storage → Policies**
   - Haz clic en el bucket `comprobantes`
   - Ve a la pestaña **"Policies"**

2. **Crear política para INSERT (Subir archivos)**
   - Haz clic en **"New Policy"**
   - Selecciona **"For full customization"**
   - Nombre: `Allow authenticated uploads`
   - Política:
   ```sql
   (bucket_id = 'comprobantes'::text) AND (auth.role() = 'authenticated'::text)
   ```
   - Operaciones: Marca solo **INSERT**
   - Haz clic en **"Review"** y luego **"Save policy"**

3. **Crear política para SELECT (Leer archivos)**
   - Haz clic en **"New Policy"** nuevamente
   - Nombre: `Allow public read`
   - Política:
   ```sql
   bucket_id = 'comprobantes'::text
   ```
   - Operaciones: Marca solo **SELECT**
   - Haz clic en **"Review"** y luego **"Save policy"**

### Opción B: Política más restrictiva (Para Producción)

Si quieres más control, puedes usar estas políticas:

**Para INSERT (Subir):**
```sql
(bucket_id = 'comprobantes'::text) AND (auth.role() = 'authenticated'::text)
```

**Para SELECT (Leer):**
```sql
(bucket_id = 'comprobantes'::text) AND (auth.role() = 'authenticated'::text)
```

**Para DELETE (Eliminar - solo admin):**
```sql
(bucket_id = 'comprobantes'::text) AND (auth.role() = 'service_role'::text)
```

## 🔧 Paso 3: Verificar Configuración

1. **Verifica que el bucket existe**
   - Deberías ver `comprobantes` en la lista de buckets
   - Debe estar marcado como **Public**

2. **Prueba subir un archivo manualmente**
   - Haz clic en el bucket `comprobantes`
   - Haz clic en **"Upload file"**
   - Sube una imagen de prueba
   - Verifica que puedas ver la URL pública del archivo

## 🔑 Configuración de Service Role Key (Recomendado)

Para evitar problemas con RLS al subir archivos desde el servidor, es recomendable usar la **Service Role Key**:

1. **Obtén tu Service Role Key**:
   - Ve a Supabase → Settings → API
   - Copia la **`service_role` key** (⚠️ NUNCA la expongas en el frontend)

2. **Configúrala en tu aplicación**:
   
   En `app/config_local.py`:
   ```python
   SUPABASE_SERVICE_ROLE_KEY = "tu-service-role-key-aqui"
   ```
   
   O como variable de entorno:
   ```env
   SUPABASE_SERVICE_ROLE_KEY=tu-service-role-key-aqui
   ```

3. **¿Por qué Service Role Key?**
   - Bypasea las políticas RLS (perfecto para operaciones del servidor)
   - Permite subir archivos sin problemas de autenticación
   - Más seguro que exponerla en el frontend

## 🐛 Solución de Problemas

### Error: "Bucket not found"

**Causa**: El bucket no existe o tiene un nombre diferente.

**Solución**:
1. Verifica que el bucket se llame exactamente `comprobantes` (sin mayúsculas, sin espacios)
2. Verifica en `app/config.py` que `STORAGE_BUCKET = "comprobantes"`
3. Si el bucket tiene otro nombre, cambia el nombre en la configuración o crea uno nuevo con el nombre correcto

### Error: "new row violates row-level security" o "Error de permisos"

**Causa**: Las políticas RLS están bloqueando la operación o no estás usando Service Role Key.

**Solución 1 (Recomendado)**: Usa Service Role Key
1. Obtén tu Service Role Key de Supabase → Settings → API
2. Configúrala en `app/config_local.py` como `SUPABASE_SERVICE_ROLE_KEY`
3. El código automáticamente usará esta key para operaciones de Storage

**Solución 2**: Configura políticas RLS más permisivas
1. Ve a Storage → Policies → comprobantes
2. Crea una política de INSERT que permita acceso anónimo:
   ```sql
   bucket_id = 'comprobantes'::text
   ```
   - Operaciones: Marca **INSERT**
   - Esto permite que cualquiera suba archivos (menos seguro)

### Error: "Permission denied"

**Causa**: El bucket no es público o las políticas no permiten acceso.

**Solución**:
1. Verifica que el bucket esté marcado como **Public**
2. Verifica que exista una política de SELECT que permita acceso público o autenticado

### Los archivos se suben pero no se pueden ver

**Causa**: El bucket no es público o falta la política de SELECT.

**Solución**:
1. Asegúrate de que el bucket sea **Public**
2. Crea una política de SELECT que permita acceso público:
   ```sql
   bucket_id = 'comprobantes'::text
   ```

## 📝 Configuración SQL (Alternativa)

Si prefieres configurar todo desde SQL, puedes ejecutar esto en el SQL Editor de Supabase:

```sql
-- Crear el bucket (si no existe)
INSERT INTO storage.buckets (id, name, public)
VALUES ('comprobantes', 'comprobantes', true)
ON CONFLICT (id) DO NOTHING;

-- Opción 1: Política permisiva (si usas Service Role Key, no necesitas esto)
-- Política para permitir subir archivos (público - menos seguro)
CREATE POLICY "Allow public uploads"
ON storage.objects
FOR INSERT
TO public
WITH CHECK (bucket_id = 'comprobantes');

-- Política para permitir leer archivos (público)
CREATE POLICY "Allow public read"
ON storage.objects
FOR SELECT
TO public
USING (bucket_id = 'comprobantes');

-- Opción 2: Política más restrictiva (si usas autenticación real)
-- Política para permitir subir archivos (autenticados)
CREATE POLICY "Allow authenticated uploads"
ON storage.objects
FOR INSERT
TO authenticated
WITH CHECK (bucket_id = 'comprobantes');

-- Política para permitir leer archivos (público)
CREATE POLICY "Allow public read"
ON storage.objects
FOR SELECT
TO public
USING (bucket_id = 'comprobantes');
```

**Nota**: Si usas Service Role Key (recomendado), las políticas de INSERT no son necesarias porque el Service Role Key bypasea RLS.

## ✅ Verificación Final

Después de configurar todo, prueba:

1. **Subir un comprobante desde la aplicación**
   - Ve a un departamento
   - Realiza un pago
   - Sube un comprobante

2. **Verificar que se puede acceder**
   - El admin debería poder ver el comprobante
   - La URL debería ser accesible públicamente

3. **Verificar en Supabase**
   - Ve a Storage → comprobantes
   - Deberías ver el archivo subido
   - Haz clic en el archivo y verifica que la URL pública funcione

## 🎯 Resumen de Configuración

- ✅ Bucket creado: `comprobantes`
- ✅ Bucket marcado como **Public**
- ✅ Política INSERT para usuarios autenticados
- ✅ Política SELECT para acceso público
- ✅ Configuración en `app/config.py` correcta

¡Listo! Ahora deberías poder subir y ver comprobantes sin problemas.

