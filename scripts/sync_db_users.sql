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
        usuario_id INT -- FK to usuarios.id presumably
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

-- Asegurar columnas canónicas y eliminar duplicados/obsoletos

-- Para la tabla 'permisos_modulos':
-- Asegurar que 'id_usuario' (columna canónica) exista.
IF COL_LENGTH('permisos_modulos', 'id_usuario') IS NULL
    ALTER TABLE permisos_modulos ADD id_usuario INT;
GO
-- Eliminar 'usuario_id' (columna duplicada) si existe y 'id_usuario' también.
-- La línea original "IF COL_LENGTH('permisos_modulos', 'usuario_id') IS NULL ALTER TABLE permisos_modulos ADD usuario_id INT;" fue eliminada para evitar crear el duplicado.
IF COL_LENGTH('permisos_modulos', 'usuario_id') IS NOT NULL AND COL_LENGTH('permisos_modulos', 'id_usuario') IS NOT NULL AND 'usuario_id' <> 'id_usuario'
BEGIN
    PRINT 'Revisar: Posible columna duplicada permisos_modulos.usuario_id. Considere ejecutar: ALTER TABLE permisos_modulos DROP COLUMN usuario_id;';
    -- ALTER TABLE permisos_modulos DROP COLUMN usuario_id; -- DESCOMENTAR TRAS REVISIÓN Y MIGRACIÓN DE DATOS SI ES NECESARIO
END
GO


-- Para la tabla 'logs_usuarios':
-- Asegurar que 'fecha_hora' (columna canónica) exista.
IF COL_LENGTH('logs_usuarios', 'fecha_hora') IS NULL
BEGIN
    -- Si 'fecha_hora' no existe pero 'fecha' sí, y son equivalentes, podría renombrarse 'fecha'.
    -- Por ahora, simplemente se asegura que 'fecha_hora' exista.
    ALTER TABLE logs_usuarios ADD fecha_hora DATETIME DEFAULT GETDATE();
END
GO
-- Eliminar 'fecha' (columna duplicada) si existe y 'fecha_hora' también.
-- La línea original "IF COL_LENGTH('logs_usuarios', 'fecha') IS NULL ALTER TABLE logs_usuarios ADD fecha DATETIME DEFAULT GETDATE();" fue eliminada.
IF COL_LENGTH('logs_usuarios', 'fecha') IS NOT NULL AND COL_LENGTH('logs_usuarios', 'fecha_hora') IS NOT NULL AND 'fecha' <> 'fecha_hora'
BEGIN
    PRINT 'Revisar: Posible columna duplicada logs_usuarios.fecha. Considere ejecutar: ALTER TABLE logs_usuarios DROP COLUMN fecha;';
    -- ALTER TABLE logs_usuarios DROP COLUMN fecha; -- DESCOMENTAR TRAS REVISIÓN Y MIGRACIÓN DE DATOS SI ES NECESARIO
END
GO

-- Para la tabla 'usuarios':
-- Eliminar columna obsoleta 'ultima_conexion' si 'ultimo_login' la reemplaza.
-- La línea original "-- ALTER TABLE usuarios DROP COLUMN ultima_conexion;" se actualiza para ser condicional.
IF COL_LENGTH('usuarios', 'ultima_conexion') IS NOT NULL AND COL_LENGTH('usuarios', 'ultimo_login') IS NOT NULL
BEGIN
    PRINT 'Revisar: Posible columna obsoleta usuarios.ultima_conexion. Considere ejecutar: ALTER TABLE usuarios DROP COLUMN ultima_conexion;';
    -- ALTER TABLE usuarios DROP COLUMN ultima_conexion; -- DESCOMENTAR TRAS REVISIÓN
END
GO
