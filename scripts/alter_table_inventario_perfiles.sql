-- Script para adaptar la tabla inventario_perfiles a la estructura esperada por el código y los tests
-- Ejecutar en SQL Server Management Studio o similar

-- Agregar columnas si no existen
IF COL_LENGTH('inventario_perfiles', 'nombre') IS NULL
    ALTER TABLE inventario_perfiles ADD nombre VARCHAR(100);
IF COL_LENGTH('inventario_perfiles', 'tipo_material') IS NULL
    ALTER TABLE inventario_perfiles ADD tipo_material VARCHAR(50);
IF COL_LENGTH('inventario_perfiles', 'unidad') IS NULL
    ALTER TABLE inventario_perfiles ADD unidad VARCHAR(20);
IF COL_LENGTH('inventario_perfiles', 'stock_actual') IS NULL
    ALTER TABLE inventario_perfiles ADD stock_actual DECIMAL(18,2) DEFAULT 0;
IF COL_LENGTH('inventario_perfiles', 'stock_minimo') IS NULL
    ALTER TABLE inventario_perfiles ADD stock_minimo DECIMAL(18,2) DEFAULT 0;
IF COL_LENGTH('inventario_perfiles', 'ubicacion') IS NULL
    ALTER TABLE inventario_perfiles ADD ubicacion VARCHAR(100);
IF COL_LENGTH('inventario_perfiles', 'descripcion') IS NULL
    ALTER TABLE inventario_perfiles ADD descripcion VARCHAR(255);
IF COL_LENGTH('inventario_perfiles', 'qr') IS NULL
    ALTER TABLE inventario_perfiles ADD qr VARCHAR(100);
IF COL_LENGTH('inventario_perfiles', 'imagen_referencia') IS NULL
    ALTER TABLE inventario_perfiles ADD imagen_referencia VARCHAR(255);

-- Opcional: poblar columnas nuevas con datos existentes si corresponde
-- UPDATE inventario_perfiles SET nombre = descripcion WHERE nombre IS NULL AND descripcion IS NOT NULL;

-- NOTA: Si alguna columna ya existe pero con otro tipo, deberás ajustarla manualmente.

-- Verifica la estructura final
SELECT * FROM INFORMATION_SCHEMA.COLUMNS WHERE TABLE_NAME = 'inventario_perfiles';
