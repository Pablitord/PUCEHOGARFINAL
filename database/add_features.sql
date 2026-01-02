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
ADD COLUMN IF NOT EXISTS furnished BOOLEAN DEFAULT FALSE;

