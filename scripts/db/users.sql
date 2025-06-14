-- Script para la base de datos: users
-- Contiene tablas de usuarios, permisos y logs de usuarios

-- =====================
-- TABLA usuarios
-- =====================
IF OBJECT_ID('usuarios', 'U') IS NOT NULL DROP TABLE usuarios;
CREATE TABLE usuarios (
    id INT IDENTITY(1,1) PRIMARY KEY,
    nombre NVARCHAR(100),
    apellido NVARCHAR(100),
    email NVARCHAR(100) UNIQUE,
    usuario NVARCHAR(50) UNIQUE,
    password_hash NVARCHAR(255),
    rol NVARCHAR(50),
    estado NVARCHAR(20),
    fecha_creacion DATETIME DEFAULT GETDATE(),
    ultima_conexion DATETIME
);

-- =====================
-- TABLA permisos_modulos
-- =====================
IF OBJECT_ID('permisos_modulos', 'U') IS NOT NULL DROP TABLE permisos_modulos;
CREATE TABLE permisos_modulos (
    id INT IDENTITY(1,1) PRIMARY KEY,
    id_usuario INT,
    modulo VARCHAR(50) NOT NULL,
    puede_ver BIT DEFAULT 1,
    puede_modificar BIT DEFAULT 0,
    puede_aprobar BIT DEFAULT 0,
    fecha_creacion DATETIME DEFAULT GETDATE(),
    creado_por INT
);

-- =====================
-- TABLA logs_usuarios
-- =====================
IF OBJECT_ID('logs_usuarios', 'U') IS NOT NULL DROP TABLE logs_usuarios;
CREATE TABLE logs_usuarios (
    id INT IDENTITY(1,1) PRIMARY KEY,
    usuario_id INT,
    accion NVARCHAR(255),
    modulo NVARCHAR(50),
    fecha_hora DATETIME DEFAULT GETDATE(),
    detalle NVARCHAR(MAX),
    ip_origen NVARCHAR(100)
);

-- =====================
-- TABLA solicitudes_aprobacion
-- =====================
IF OBJECT_ID('solicitudes_aprobacion', 'U') IS NOT NULL DROP TABLE solicitudes_aprobacion;
CREATE TABLE solicitudes_aprobacion (
    id INT IDENTITY(1,1) PRIMARY KEY,
    id_usuario INT,
    modulo NVARCHAR(50),
    tipo_accion NVARCHAR(50),
    datos_json NVARCHAR(MAX),
    estado NVARCHAR(30)
);
