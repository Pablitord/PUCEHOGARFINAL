-- ============================================
-- AGREGAR CAMPOS DE CARACTERÍSTICAS A DEPARTAMENTOS
-- ============================================
-- Ejecuta este script en el SQL Editor de Supabase
-- para agregar campos de filtros (terraza, balcón, vista al mar, etc.)

ALTER TABLE departments
ADD COLUMN IF NOT EXISTS has_terrace BOOLEAN DEFAULT FALSE,
ADD COLUMN IF NOT EXISTS has_balcony BOOLEAN DEFAULT FALSE,
ADD COLUMN IF NOT EXISTS sea_view BOOLEAN DEFAULT FALSE,
ADD COLUMN IF NOT EXISTS parking BOOLEAN DEFAULT FALSE,
ADD COLUMN IF NOT EXISTS furnished BOOLEAN DEFAULT FALSE,
ADD COLUMN IF NOT EXISTS allow_pets BOOLEAN DEFAULT FALSE,
ADD COLUMN IF NOT EXISTS image_url_2 TEXT,
ADD COLUMN IF NOT EXISTS image_url_3 TEXT;

-- ============================================
-- AGREGAR CAMPOS A REPORTES
-- ============================================
ALTER TABLE reports
ADD COLUMN IF NOT EXISTS notes TEXT,
ADD COLUMN IF NOT EXISTS attachment_url TEXT;
