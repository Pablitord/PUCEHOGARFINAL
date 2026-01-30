-- ============================================
-- INSERTS DE EJEMPLO PARA CALIFICACIONES
-- ============================================
-- Ejecuta este script en el SQL Editor de Supabase
-- 
-- IMPORTANTE: Asegúrate de que existan:
-- 1. Al menos un usuario con role='tenant'
-- 2. Al menos un departamento
-- 3. Que el tenant tenga un pago aprobado para el departamento (opcional, pero recomendado)

-- ============================================
-- OPCIÓN 1: Usando subconsultas (automático)
-- ============================================
-- Esta versión obtiene automáticamente los primeros tenants y departamentos disponibles

-- Calificación 1: Excelente (5 estrellas)
INSERT INTO ratings (tenant_id, department_id, rating, comment)
SELECT 
    (SELECT id FROM users WHERE role = 'tenant' LIMIT 1),
    (SELECT id FROM departments LIMIT 1),
    5,
    'Excelente departamento, muy bien ubicado y con todas las comodidades. La atención fue impecable.'
WHERE EXISTS (SELECT 1 FROM users WHERE role = 'tenant')
  AND EXISTS (SELECT 1 FROM departments)
ON CONFLICT (tenant_id, department_id) DO NOTHING;

-- Calificación 2: Muy bueno (4 estrellas)
INSERT INTO ratings (tenant_id, department_id, rating, comment)
SELECT 
    (SELECT id FROM users WHERE role = 'tenant' LIMIT 1 OFFSET 1),
    (SELECT id FROM departments LIMIT 1),
    4,
    'Muy buen departamento, cómodo y limpio. Solo faltaría un poco más de espacio en el baño.'
WHERE EXISTS (SELECT 1 FROM users WHERE role = 'tenant' OFFSET 1)
  AND EXISTS (SELECT 1 FROM departments)
ON CONFLICT (tenant_id, department_id) DO NOTHING;

-- Calificación 3: Bueno (4 estrellas) - Sin comentario
INSERT INTO ratings (tenant_id, department_id, rating, comment)
SELECT 
    (SELECT id FROM users WHERE role = 'tenant' LIMIT 1),
    (SELECT id FROM departments LIMIT 1 OFFSET 1),
    4,
    NULL
WHERE EXISTS (SELECT 1 FROM users WHERE role = 'tenant')
  AND EXISTS (SELECT 1 FROM departments OFFSET 1)
ON CONFLICT (tenant_id, department_id) DO NOTHING;

-- Calificación 4: Regular (3 estrellas)
INSERT INTO ratings (tenant_id, department_id, rating, comment)
SELECT 
    (SELECT id FROM users WHERE role = 'tenant' LIMIT 1 OFFSET 2),
    (SELECT id FROM departments LIMIT 1),
    3,
    'El departamento está bien, pero necesita algunas mejoras en la iluminación.'
WHERE EXISTS (SELECT 1 FROM users WHERE role = 'tenant' OFFSET 2)
  AND EXISTS (SELECT 1 FROM departments)
ON CONFLICT (tenant_id, department_id) DO NOTHING;

-- Calificación 5: Excelente (5 estrellas) - Para otro departamento
INSERT INTO ratings (tenant_id, department_id, rating, comment)
SELECT 
    (SELECT id FROM users WHERE role = 'tenant' LIMIT 1),
    (SELECT id FROM departments LIMIT 1 OFFSET 2),
    5,
    'Perfecto para vivir. Muy tranquilo y bien mantenido. Lo recomiendo totalmente.'
WHERE EXISTS (SELECT 1 FROM users WHERE role = 'tenant')
  AND EXISTS (SELECT 1 FROM departments OFFSET 2)
ON CONFLICT (tenant_id, department_id) DO NOTHING;

-- ============================================
-- OPCIÓN 2: Con IDs específicos (manual)
-- ============================================
-- Reemplaza los UUIDs con los IDs reales de tus usuarios y departamentos
-- Puedes obtenerlos ejecutando:
-- SELECT id, email, role FROM users WHERE role = 'tenant';
-- SELECT id, title, address FROM departments;

/*
-- Ejemplo con IDs específicos (descomenta y reemplaza los UUIDs):

INSERT INTO ratings (tenant_id, department_id, rating, comment)
VALUES 
    ('TU_USER_ID_1', 'TU_DEPARTMENT_ID_1', 5, 'Excelente departamento, muy recomendado.'),
    ('TU_USER_ID_2', 'TU_DEPARTMENT_ID_1', 4, 'Muy bueno, solo faltaría más espacio.'),
    ('TU_USER_ID_1', 'TU_DEPARTMENT_ID_2', 5, 'Perfecto para vivir, muy tranquilo.')
ON CONFLICT (tenant_id, department_id) DO NOTHING;
*/

-- ============================================
-- OPCIÓN 3: Para un departamento específico
-- ============================================
-- Si quieres agregar varias calificaciones para un departamento específico,
-- reemplaza 'TU_DEPARTMENT_ID' con el ID real del departamento

/*
INSERT INTO ratings (tenant_id, department_id, rating, comment)
SELECT 
    u.id,
    'TU_DEPARTMENT_ID'::UUID,
    CASE (ROW_NUMBER() OVER ()) % 5 + 1
        WHEN 1 THEN 5
        WHEN 2 THEN 4
        WHEN 3 THEN 4
        WHEN 4 THEN 3
        ELSE 5
    END,
    CASE (ROW_NUMBER() OVER ()) % 5 + 1
        WHEN 1 THEN 'Excelente departamento, muy bien ubicado.'
        WHEN 2 THEN 'Muy bueno, cómodo y limpio.'
        WHEN 3 THEN 'Buen departamento en general.'
        WHEN 4 THEN 'Regular, necesita algunas mejoras.'
        ELSE 'Perfecto para vivir, lo recomiendo.'
    END
FROM users u
WHERE u.role = 'tenant'
LIMIT 5
ON CONFLICT (tenant_id, department_id) DO NOTHING;
*/

-- ============================================
-- Verificar las calificaciones insertadas
-- ============================================
-- Ejecuta esto para ver las calificaciones creadas:

/*
SELECT 
    r.id,
    u.email as tenant_email,
    d.title as department_title,
    r.rating,
    r.comment,
    r.created_at
FROM ratings r
JOIN users u ON r.tenant_id = u.id
JOIN departments d ON r.department_id = d.id
ORDER BY r.created_at DESC;
*/
