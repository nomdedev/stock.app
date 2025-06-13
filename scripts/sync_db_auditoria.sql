-- Script de sincronización para la base de datos 'auditoria'

-- Crear tablas faltantes
IF NOT EXISTS (SELECT * FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_NAME = 'auditorias_sistema')
BEGIN
    CREATE TABLE auditorias_sistema (
        id INT IDENTITY(1,1) PRIMARY KEY,
        usuario NVARCHAR(100),
        modulo NVARCHAR(100),
        accion NVARCHAR(100),
        fecha DATETIME DEFAULT GETDATE(),
        detalle NVARCHAR(255),
        ip_origen NVARCHAR(50),
        modulo_afectado NVARCHAR(100),
        tipo_evento NVARCHAR(50)
    );
END
GO

IF NOT EXISTS (SELECT * FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_NAME = 'errores_sistema')
BEGIN
    CREATE TABLE errores_sistema (
        id INT IDENTITY(1,1) PRIMARY KEY,
        fecha DATETIME DEFAULT GETDATE(),
        modulo NVARCHAR(100),
        detalle NVARCHAR(255),
        usuario NVARCHAR(100),
        ip_origen NVARCHAR(50)
    );
END
GO

-- Agregar columnas faltantes
IF COL_LENGTH('auditorias_sistema', 'usuario') IS NULL
    ALTER TABLE auditorias_sistema ADD usuario NVARCHAR(100);
IF COL_LENGTH('errores_sistema', 'fecha') IS NULL
    ALTER TABLE errores_sistema ADD fecha DATETIME DEFAULT GETDATE();
GO
