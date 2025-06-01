-- SQL Server: Asegurar columna fecha_entrega y cargar datos de ejemplo para el módulo Obras

-- 1. Agregar columna fecha_entrega si no existe
IF COL_LENGTH('obras', 'fecha_entrega') IS NULL
BEGIN
    ALTER TABLE obras ADD fecha_entrega DATE NULL;
END
GO

-- 2. Eliminar datos actuales (opcional, solo si quieres limpiar la tabla)
-- DELETE FROM obras;

-- 3. Insertar datos de ejemplo compatibles con el Gantt
INSERT INTO obras (nombre, cliente, estado, fecha, fecha_entrega) VALUES
('Edificio Central', 'Constructora Sur', 'Medición', DATEADD(DAY, -10, CAST(GETDATE() AS DATE)), DATEADD(DAY, 30, CAST(GETDATE() AS DATE))),
('Torre Norte', 'Desarrollos Río', 'Fabricación', DATEADD(DAY, -20, CAST(GETDATE() AS DATE)), DATEADD(DAY, 15, CAST(GETDATE() AS DATE))),
('Residencial Sur', 'Grupo Delta', 'Entrega', DATEADD(DAY, -40, CAST(GETDATE() AS DATE)), DATEADD(DAY, 5, CAST(GETDATE() AS DATE)));
GO

-- Si la tabla tiene un campo IDENTITY obligatorio, omite la columna id en el insert.
-- Si la tabla ya tiene datos, los inserts pueden fallar por duplicidad de nombre/cliente.
