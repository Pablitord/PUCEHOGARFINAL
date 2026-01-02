-- ============================================
-- DATOS DE EJEMPLO PARA DEPARTAMENTOS
-- ============================================
-- Ejecuta este script en el SQL Editor de Supabase
-- para poblar la tabla departments con datos de prueba

INSERT INTO departments (
  title, address, price, status, description, rooms, bathrooms, area, image_url,
  has_terrace, has_balcony, sea_view, parking, furnished
) VALUES
('Departamento Moderno Centro', 'Av. Principal 123, Centro', 450.00, 'available', 'Hermoso departamento en el corazón de la ciudad, cerca de todo. Ideal para profesionales.', 2, 1, 65.5, NULL, FALSE, TRUE, FALSE, FALSE, FALSE),
('Loft Espacioso', 'Calle Comercial 456, Centro', 550.00, 'available', 'Loft amplio con diseño moderno, perfecto para parejas jóvenes.', 1, 1, 75.0, NULL, FALSE, TRUE, FALSE, TRUE, FALSE),
('Apartamento Familiar', 'Av. Residencial 789, Zona Norte', 650.00, 'available', 'Departamento espacioso ideal para familias, con excelente iluminación natural.', 3, 2, 95.0, NULL, FALSE, FALSE, FALSE, TRUE, FALSE),
('Casa en Condominio', 'Condominio Los Pinos, Mz 5 Lt 12', 750.00, 'available', 'Casa independiente en condominio cerrado, con jardín y estacionamiento.', 3, 2, 120.0, NULL, TRUE, FALSE, FALSE, TRUE, FALSE),
('Departamento Vista al Mar', 'Av. Costera 234, Zona Este', 850.00, 'available', 'Departamento con vista al mar, balcón amplio y acabados de lujo.', 2, 2, 85.0, NULL, FALSE, TRUE, TRUE, TRUE, TRUE),
('Estudio Compacto', 'Calle Peatonal 567, Centro', 350.00, 'available', 'Estudio funcional y moderno, perfecto para estudiantes o profesionales solteros.', 1, 1, 40.0, NULL, FALSE, FALSE, FALSE, FALSE, FALSE),
('Penthouse de Lujo', 'Torre Residencial, Piso 15, Av. Principal', 1200.00, 'available', 'Penthouse exclusivo con terraza privada, vista panorámica y acabados premium.', 4, 3, 180.0, NULL, TRUE, TRUE, FALSE, TRUE, TRUE),
('Departamento Económico', 'Barrio Popular, Calle 10 #25-30', 280.00, 'available', 'Departamento económico, ideal para empezar. Bien ubicado y con servicios básicos.', 1, 1, 35.0, NULL, FALSE, FALSE, FALSE, FALSE, FALSE),
('Casa con Patio', 'Sector Residencial, Calle 45 #12-34', 600.00, 'available', 'Casa con patio trasero, perfecta para mascotas. Zona tranquila y segura.', 2, 2, 100.0, NULL, TRUE, FALSE, FALSE, TRUE, FALSE),
('Departamento Amueblado', 'Av. Universitaria 890, Zona Sur', 500.00, 'available', 'Departamento completamente amueblado, listo para habitar. Ideal para estudiantes universitarios.', 2, 1, 60.0, NULL, FALSE, FALSE, FALSE, FALSE, TRUE),
('Loft Industrial', 'Zona Industrial Renovada, Calle 20 #5-10', 480.00, 'available', 'Loft con estilo industrial, techos altos y espacios abiertos. Zona en desarrollo.', 1, 1, 70.0, NULL, FALSE, TRUE, FALSE, TRUE, FALSE),
('Apartamento con Balcón', 'Torre Verde, Piso 8, Av. Ecológica', 580.00, 'available', 'Apartamento con balcón amplio, vista a parque y excelente iluminación.', 2, 2, 80.0, NULL, FALSE, TRUE, FALSE, FALSE, FALSE),
('Casa de Dos Pisos', 'Sector Residencial Alto, Calle 30 #15-20', 900.00, 'available', 'Casa de dos pisos con garaje, ideal para familias grandes. Zona exclusiva.', 4, 3, 150.0, NULL, TRUE, FALSE, FALSE, TRUE, TRUE),
('Departamento Minimalista', 'Av. Moderna 345, Zona Nueva', 420.00, 'available', 'Departamento con diseño minimalista, espacios optimizados y acabados modernos.', 2, 1, 55.0, NULL, FALSE, FALSE, FALSE, FALSE, FALSE),
('Estudio con Terraza', 'Edificio Panorámico, Piso 5, Av. Vista', 380.00, 'available', 'Estudio con terraza privada, perfecto para disfrutar del aire libre.', 1, 1, 45.0, NULL, TRUE, FALSE, FALSE, FALSE, FALSE);

