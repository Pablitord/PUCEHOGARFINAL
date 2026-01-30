-- ============================================
-- INSERTS DE CALIFICACIONES PARA 4 DEPARTAMENTOS
-- ============================================
-- Ejecuta este script en el SQL Editor de Supabase
-- 
-- Este script inserta calificaciones variadas para cada uno de tus 4 departamentos

-- ============================================
-- DEPARTAMENTO 1 (Primer departamento)
-- ============================================
INSERT INTO ratings (tenant_id, department_id, rating, comment)
SELECT 
    (SELECT id FROM users WHERE role = 'tenant' LIMIT 1),
    (SELECT id FROM departments ORDER BY created_at LIMIT 1 OFFSET 0),
    5,
    'Excelente departamento, muy bien ubicado y con todas las comodidades. La atención fue impecable y el lugar está muy limpio.'
WHERE EXISTS (SELECT 1 FROM users WHERE role = 'tenant')
  AND EXISTS (SELECT 1 FROM departments OFFSET 0)
ON CONFLICT (tenant_id, department_id) DO NOTHING;

INSERT INTO ratings (tenant_id, department_id, rating, comment)
SELECT 
    (SELECT id FROM users WHERE role = 'tenant' LIMIT 1 OFFSET 1),
    (SELECT id FROM departments ORDER BY created_at LIMIT 1 OFFSET 0),
    4,
    'Muy buen departamento, cómodo y limpio. Solo faltaría un poco más de espacio en el baño, pero en general está muy bien.'
WHERE EXISTS (SELECT 1 FROM users WHERE role = 'tenant' OFFSET 1)
  AND EXISTS (SELECT 1 FROM departments OFFSET 0)
ON CONFLICT (tenant_id, department_id) DO NOTHING;

-- ============================================
-- DEPARTAMENTO 2 (Segundo departamento)
-- ============================================
INSERT INTO ratings (tenant_id, department_id, rating, comment)
SELECT 
    (SELECT id FROM users WHERE role = 'tenant' LIMIT 1),
    (SELECT id FROM departments ORDER BY created_at LIMIT 1 OFFSET 1),
    5,
    'Perfecto para vivir. Muy tranquilo y bien mantenido. La ubicación es excelente y tiene todo lo necesario.'
WHERE EXISTS (SELECT 1 FROM users WHERE role = 'tenant')
  AND EXISTS (SELECT 1 FROM departments OFFSET 1)
ON CONFLICT (tenant_id, department_id) DO NOTHING;

INSERT INTO ratings (tenant_id, department_id, rating, comment)
SELECT 
    (SELECT id FROM users WHERE role = 'tenant' LIMIT 1 OFFSET 2),
    (SELECT id FROM departments ORDER BY created_at LIMIT 1 OFFSET 1),
    4,
    'Buen departamento en general. Muy cómodo y bien equipado. Lo recomiendo.'
WHERE EXISTS (SELECT 1 FROM users WHERE role = 'tenant' OFFSET 2)
  AND EXISTS (SELECT 1 FROM departments OFFSET 1)
ON CONFLICT (tenant_id, department_id) DO NOTHING;

-- ============================================
-- DEPARTAMENTO 3 (Tercer departamento)
-- ============================================
INSERT INTO ratings (tenant_id, department_id, rating, comment)
SELECT 
    (SELECT id FROM users WHERE role = 'tenant' LIMIT 1),
    (SELECT id FROM departments ORDER BY created_at LIMIT 1 OFFSET 2),
    4,
    'Muy buen lugar para vivir. El departamento está en excelente estado y la zona es muy segura.'
WHERE EXISTS (SELECT 1 FROM users WHERE role = 'tenant')
  AND EXISTS (SELECT 1 FROM departments OFFSET 2)
ON CONFLICT (tenant_id, department_id) DO NOTHING;

INSERT INTO ratings (tenant_id, department_id, rating, comment)
SELECT 
    (SELECT id FROM users WHERE role = 'tenant' LIMIT 1 OFFSET 3),
    (SELECT id FROM departments ORDER BY created_at LIMIT 1 OFFSET 2),
    3,
    'El departamento está bien, pero necesita algunas mejoras en la iluminación. Por lo demás, todo correcto.'
WHERE EXISTS (SELECT 1 FROM users WHERE role = 'tenant' OFFSET 3)
  AND EXISTS (SELECT 1 FROM departments OFFSET 2)
ON CONFLICT (tenant_id, department_id) DO NOTHING;

-- ============================================
-- DEPARTAMENTO 4 (Cuarto departamento)
-- ============================================
INSERT INTO ratings (tenant_id, department_id, rating, comment)
SELECT 
    (SELECT id FROM users WHERE role = 'tenant' LIMIT 1),
    (SELECT id FROM departments ORDER BY created_at LIMIT 1 OFFSET 3),
    5,
    'Excelente opción. El departamento es amplio, moderno y muy bien cuidado. La mejor experiencia que he tenido.'
WHERE EXISTS (SELECT 1 FROM users WHERE role = 'tenant')
  AND EXISTS (SELECT 1 FROM departments OFFSET 3)
ON CONFLICT (tenant_id, department_id) DO NOTHING;

INSERT INTO ratings (tenant_id, department_id, rating, comment)
SELECT 
    (SELECT id FROM users WHERE role = 'tenant' LIMIT 1 OFFSET 1),
    (SELECT id FROM departments ORDER BY created_at LIMIT 1 OFFSET 3),
    4,
    'Muy satisfecho con el departamento. Todo funciona correctamente y el mantenimiento es excelente.'
WHERE EXISTS (SELECT 1 FROM users WHERE role = 'tenant' OFFSET 1)
  AND EXISTS (SELECT 1 FROM departments OFFSET 3)
ON CONFLICT (tenant_id, department_id) DO NOTHING;

-- ============================================
-- Verificar las calificaciones insertadas
-- ============================================
-- Ejecuta esto para ver las calificaciones creadas por departamento:

SELECT 
    d.title as departamento,
    COUNT(r.id) as total_calificaciones,
    ROUND(AVG(r.rating), 2) as promedio_calificacion,
    MIN(r.rating) as calificacion_minima,
    MAX(r.rating) as calificacion_maxima
FROM departments d
LEFT JOIN ratings r ON d.id = r.department_id
GROUP BY d.id, d.title
ORDER BY d.title;

-- Ver todas las calificaciones con detalles:
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
ORDER BY d.title, r.created_at DESC;
*/
