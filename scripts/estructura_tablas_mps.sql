-- Script UNIFICADO para crear o migrar la estructura de todas las tablas críticas del sistema MPS
-- Ejecutar en SQL Server Management Studio o similar, adaptando tipos si usas PostgreSQL

-- =====================
-- TABLA inventario_perfiles (INVENTARIO)
-- =====================
IF OBJECT_ID('inventario_perfiles', 'U') IS NOT NULL DROP TABLE inventario_perfiles;
CREATE TABLE inventario_perfiles (
    id INT IDENTITY(1,1) PRIMARY KEY,
    codigo VARCHAR(100) UNIQUE NOT NULL,
    descripcion VARCHAR(255),
    tipo VARCHAR(50),
    acabado VARCHAR(50),
    numero VARCHAR(50),
    vs VARCHAR(50),
    proveedor VARCHAR(100),
    longitud DECIMAL(18,2),
    ancho DECIMAL(18,2),
    alto DECIMAL(18,2),
    necesarias DECIMAL(18,2),
    stock DECIMAL(18,2),
    faltan DECIMAL(18,2),
    ped_min DECIMAL(18,2),
    emba VARCHAR(50),
    pedido VARCHAR(100),
    importe DECIMAL(18,2)
);

-- =====================
-- TABLA usuarios (USERS)
-- =====================
IF OBJECT_ID('usuarios', 'U') IS NOT NULL DROP TABLE usuarios;
CREATE TABLE usuarios (
    id INT IDENTITY(1,1) PRIMARY KEY,
    nombre VARCHAR(100),
    apellido VARCHAR(100),
    email VARCHAR(100) UNIQUE,
    usuario VARCHAR(50) UNIQUE,
    password_hash TEXT,
    rol VARCHAR(50),
    estado VARCHAR(20),
    fecha_creacion DATETIME DEFAULT GETDATE(),
    ultima_conexion DATETIME
);

-- =====================
-- TABLA roles_permisos (USERS)
-- =====================
IF OBJECT_ID('roles_permisos', 'U') IS NOT NULL DROP TABLE roles_permisos;
CREATE TABLE roles_permisos (
    id INT IDENTITY(1,1) PRIMARY KEY,
    rol VARCHAR(50),
    modulo VARCHAR(50),
    permiso_ver BIT DEFAULT 1,
    permiso_editar BIT DEFAULT 0,
    permiso_aprobar BIT DEFAULT 0,
    permiso_eliminar BIT DEFAULT 0
);

-- =====================
-- TABLA logs_usuarios (USERS)
-- =====================
IF OBJECT_ID('logs_usuarios', 'U') IS NOT NULL DROP TABLE logs_usuarios;
CREATE TABLE logs_usuarios (
    id INT IDENTITY(1,1) PRIMARY KEY,
    usuario_id INT,
    accion TEXT,
    modulo VARCHAR(50),
    fecha_hora DATETIME DEFAULT GETDATE(),
    detalle TEXT,
    ip_origen VARCHAR(100)
);

-- =====================
-- TABLA obras (OBRAS)
-- =====================
IF OBJECT_ID('obras', 'U') IS NOT NULL DROP TABLE obras;
CREATE TABLE obras (
    id INT IDENTITY(1,1) PRIMARY KEY,
    nombre VARCHAR(100),
    cliente VARCHAR(100),
    estado VARCHAR(50),
    fecha_compra DATE,
    cantidad_aberturas INT,
    pago_completo BIT,
    pago_porcentaje DECIMAL(5,2),
    monto_usd DECIMAL(18,2),
    monto_ars DECIMAL(18,2),
    fecha_medicion DATE,
    dias_entrega INT DEFAULT 90,
    fecha_entrega DATE,
    usuario_creador INT
);

-- =====================
-- TABLA materiales_por_obra (OBRAS)
-- =====================
IF OBJECT_ID('materiales_por_obra', 'U') IS NOT NULL DROP TABLE materiales_por_obra;
CREATE TABLE materiales_por_obra (
    id INT IDENTITY(1,1) PRIMARY KEY,
    id_obra INT,
    id_item INT,
    cantidad_necesaria DECIMAL(18,2),
    cantidad_reservada DECIMAL(18,2),
    estado VARCHAR(30)
);

-- =====================
-- TABLA cronograma_obras (OBRAS)
-- =====================
IF OBJECT_ID('cronograma_obras', 'U') IS NOT NULL DROP TABLE cronograma_obras;
CREATE TABLE cronograma_obras (
    id INT IDENTITY(1,1) PRIMARY KEY,
    id_obra INT,
    etapa VARCHAR(50),
    fecha_programada DATE,
    fecha_realizada DATE,
    observaciones TEXT,
    responsable INT,
    estado VARCHAR(30)
);

-- =====================
-- TABLA auditorias_sistema (AUDITORIA)
-- =====================
IF OBJECT_ID('auditorias_sistema', 'U') IS NOT NULL DROP TABLE auditorias_sistema;
CREATE TABLE auditorias_sistema (
    id INT IDENTITY(1,1) PRIMARY KEY,
    fecha_hora DATETIME DEFAULT GETDATE(),
    usuario_id INT,
    modulo_afectado VARCHAR(50),
    tipo_evento VARCHAR(30),
    detalle TEXT,
    ip_origen VARCHAR(50),
    device_info TEXT,
    origen_evento VARCHAR(30)
);

-- =====================
-- TABLA errores_sistema (AUDITORIA)
-- =====================
IF OBJECT_ID('errores_sistema', 'U') IS NOT NULL DROP TABLE errores_sistema;
CREATE TABLE errores_sistema (
    id INT IDENTITY(1,1) PRIMARY KEY,
    fecha_hora DATETIME DEFAULT GETDATE(),
    usuario_id INT,
    modulo VARCHAR(50),
    descripcion_error TEXT,
    stack_trace TEXT,
    ip_origen VARCHAR(50),
    origen_evento VARCHAR(30)
);

-- =====================
-- TABLA permisos_modulos (USERS)
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
-- TABLA solicitudes_aprobacion (USERS/AUDITORIA)
-- =====================
IF OBJECT_ID('solicitudes_aprobacion', 'U') IS NOT NULL DROP TABLE solicitudes_aprobacion;
CREATE TABLE solicitudes_aprobacion (
    id INT IDENTITY(1,1) PRIMARY KEY,
    id_usuario INT,
    modulo VARCHAR(50) NOT NULL,
    tipo_accion VARCHAR(30) NOT NULL,
    datos_json TEXT NOT NULL,
    estado VARCHAR(20) DEFAULT 'pendiente',
    fecha_solicitud DATETIME DEFAULT GETDATE(),
    fecha_resolucion DATETIME,
    resuelto_por INT,
    observaciones TEXT
);

-- =====================
-- (Agrega aquí otras tablas críticas siguiendo el mismo patrón si es necesario)

-- FIN DEL SCRIPT UNIFICADO
