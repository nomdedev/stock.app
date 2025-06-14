-- Script para la base de datos: auditoria
-- Contiene tablas de auditoría y errores del sistema

-- =====================
-- TABLA auditorias_sistema
-- =====================
IF OBJECT_ID('auditorias_sistema', 'U') IS NOT NULL DROP TABLE auditorias_sistema;
CREATE TABLE auditorias_sistema (
    id INT IDENTITY(1,1) PRIMARY KEY,
    origen_evento NVARCHAR(30),
    fecha DATETIME DEFAULT GETDATE(),
    usuario_id INT,
    descripcion NVARCHAR(MAX)
);

-- =====================
-- TABLA errores_sistema
-- =====================
IF OBJECT_ID('errores_sistema', 'U') IS NOT NULL DROP TABLE errores_sistema;
CREATE TABLE errores_sistema (
    id INT IDENTITY(1,1) PRIMARY KEY,
    origen_evento NVARCHAR(30),
    fecha DATETIME DEFAULT GETDATE(),
    descripcion NVARCHAR(MAX)
);

-- =====================
-- TABLA eventos_auditoria
-- =====================
IF OBJECT_ID('eventos_auditoria', 'U') IS NOT NULL DROP TABLE eventos_auditoria;
CREATE TABLE eventos_auditoria (
    id INT IDENTITY(1,1) PRIMARY KEY,
    usuario_id INT,
    modulo NVARCHAR(50),
    accion NVARCHAR(50),
    detalle NVARCHAR(MAX),
    ip_origen NVARCHAR(100),
    fecha_hora DATETIME DEFAULT GETDATE()
);
