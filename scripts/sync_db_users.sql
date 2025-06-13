-- Script de sincronización para la base de datos 'users'
-- Crear tabla faltante
IF NOT EXISTS (SELECT * FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_NAME = 'notificaciones')
BEGIN
    CREATE TABLE notificaciones (
        id INT IDENTITY(1,1) PRIMARY KEY,
        mensaje NVARCHAR(255) NOT NULL,
        fecha DATETIME NOT NULL DEFAULT GETDATE(),
        tipo NVARCHAR(50),
        leido BIT DEFAULT 0,
        usuario_id INT
    );
END
GO

-- Agregar columnas faltantes en 'usuarios'
IF COL_LENGTH('usuarios', 'rowversion') IS NULL
    ALTER TABLE usuarios ADD rowversion ROWVERSION;
IF COL_LENGTH('usuarios', 'ip_ultimo_login') IS NULL
    ALTER TABLE usuarios ADD ip_ultimo_login NVARCHAR(50);
IF COL_LENGTH('usuarios', 'ultimo_login') IS NULL
    ALTER TABLE usuarios ADD ultimo_login DATETIME;
GO

-- Agregar columna faltante en 'permisos_modulos'
IF COL_LENGTH('permisos_modulos', 'usuario_id') IS NULL
    ALTER TABLE permisos_modulos ADD usuario_id INT;
GO

-- Agregar columna faltante en 'logs_usuarios'
IF COL_LENGTH('logs_usuarios', 'fecha') IS NULL
    ALTER TABLE logs_usuarios ADD fecha DATETIME DEFAULT GETDATE();
GO

-- Columnas sobrantes detectadas (revisar antes de eliminar)
-- ALTER TABLE usuarios DROP COLUMN ultima_conexion; -- Revisar si es seguro eliminar
GO
