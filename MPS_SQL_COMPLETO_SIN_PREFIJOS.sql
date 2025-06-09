-- Script corregido y adaptado para SQL Server (idempotente, sin creación de bases de datos)
-- Ejecutar en la base de datos correspondiente antes de cada bloque

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
-- TABLA inventario_items
-- =====================
IF OBJECT_ID('inventario_items', 'U') IS NOT NULL DROP TABLE inventario_items;
CREATE TABLE inventario_items (
    id INT IDENTITY(1,1) PRIMARY KEY,
    codigo NVARCHAR(100) UNIQUE NOT NULL,
    nombre NVARCHAR(100),
    tipo_material NVARCHAR(50),
    unidad NVARCHAR(20),
    stock_actual DECIMAL(18,2) DEFAULT 0,
    stock_minimo DECIMAL(18,2) DEFAULT 0,
    ubicacion NVARCHAR(255),
    descripcion NVARCHAR(MAX),
    qr_code NVARCHAR(255),
    imagen_referencia NVARCHAR(255)
);

-- =====================
-- TABLA movimientos_stock
-- =====================
IF OBJECT_ID('movimientos_stock', 'U') IS NOT NULL DROP TABLE movimientos_stock;
CREATE TABLE movimientos_stock (
    id INT IDENTITY(1,1) PRIMARY KEY,
    id_item INT FOREIGN KEY REFERENCES inventario_items(id) ON DELETE CASCADE,
    fecha DATETIME DEFAULT GETDATE(),
    tipo_movimiento NVARCHAR(20) NOT NULL,
    cantidad DECIMAL(18,2) NOT NULL,
    realizado_por INT,
    observaciones NVARCHAR(MAX),
    referencia NVARCHAR(255)
);

-- =====================
-- TABLA reservas_stock
-- =====================
IF OBJECT_ID('reservas_stock', 'U') IS NOT NULL DROP TABLE reservas_stock;
CREATE TABLE reservas_stock (
    id INT IDENTITY(1,1) PRIMARY KEY,
    id_item INT FOREIGN KEY REFERENCES inventario_items(id) ON DELETE CASCADE,
    fecha_reserva DATETIME DEFAULT GETDATE(),
    cantidad_reservada DECIMAL(18,2) NOT NULL,
    referencia_obra INT,
    estado NVARCHAR(20) DEFAULT 'activa'
);

-- =====================
-- TABLA obras
-- =====================
IF OBJECT_ID('obras', 'U') IS NOT NULL DROP TABLE obras;
CREATE TABLE obras (
    id INT IDENTITY(1,1) PRIMARY KEY,
    nombre NVARCHAR(100),
    usuario_creador INT,
    cliente NVARCHAR(100),
    estado NVARCHAR(30),
    fecha_medicion DATETIME,
    fecha_entrega DATETIME
);

-- =====================
-- TABLA cronograma_obras
-- =====================
IF OBJECT_ID('cronograma_obras', 'U') IS NOT NULL DROP TABLE cronograma_obras;
CREATE TABLE cronograma_obras (
    id INT IDENTITY(1,1) PRIMARY KEY,
    id_obra INT FOREIGN KEY REFERENCES obras(id) ON DELETE CASCADE,
    fecha DATETIME,
    estado NVARCHAR(30)
);

-- =====================
-- TABLA materiales_por_obra
-- =====================
IF OBJECT_ID('materiales_por_obra', 'U') IS NOT NULL DROP TABLE materiales_por_obra;
CREATE TABLE materiales_por_obra (
    id INT IDENTITY(1,1) PRIMARY KEY,
    id_obra INT FOREIGN KEY REFERENCES obras(id) ON DELETE CASCADE,
    id_item INT FOREIGN KEY REFERENCES inventario_items(id) ON DELETE CASCADE,
    cantidad DECIMAL(18,2),
    estado NVARCHAR(30)
);

-- =====================
-- TABLA pedidos_compra
-- =====================
IF OBJECT_ID('pedidos_compra', 'U') IS NOT NULL DROP TABLE pedidos_compra;
CREATE TABLE pedidos_compra (
    id INT IDENTITY(1,1) PRIMARY KEY,
    prioridad NVARCHAR(20),
    fecha DATE,
    estado NVARCHAR(20)
);

-- =====================
-- TABLA detalle_pedido
-- =====================
IF OBJECT_ID('detalle_pedido', 'U') IS NOT NULL DROP TABLE detalle_pedido;
CREATE TABLE detalle_pedido (
    id INT IDENTITY(1,1) PRIMARY KEY,
    pedido_id INT FOREIGN KEY REFERENCES pedidos_compra(id) ON DELETE CASCADE,
    id_item INT FOREIGN KEY REFERENCES inventario_items(id),
    cantidad DECIMAL(18,2),
    justificacion NVARCHAR(MAX)
);

-- =====================
-- TABLA presupuestos
-- =====================
IF OBJECT_ID('presupuestos', 'U') IS NOT NULL DROP TABLE presupuestos;
CREATE TABLE presupuestos (
    id INT IDENTITY(1,1) PRIMARY KEY,
    pedido_id INT FOREIGN KEY REFERENCES pedidos_compra(id) ON DELETE CASCADE,
    seleccionado BIT DEFAULT 0,
    monto DECIMAL(18,2)
);

-- =====================
-- TABLA aberturas
-- =====================
IF OBJECT_ID('aberturas', 'U') IS NOT NULL DROP TABLE aberturas;
CREATE TABLE aberturas (
    id INT IDENTITY(1,1) PRIMARY KEY,
    fecha_entrega_estimada DATE,
    id_obra INT FOREIGN KEY REFERENCES obras(id)
);

-- =====================
-- TABLA etapas_fabricacion
-- =====================
IF OBJECT_ID('etapas_fabricacion', 'U') IS NOT NULL DROP TABLE etapas_fabricacion;
CREATE TABLE etapas_fabricacion (
    id INT IDENTITY(1,1) PRIMARY KEY,
    id_abertura INT FOREIGN KEY REFERENCES aberturas(id) ON DELETE CASCADE,
    observaciones NVARCHAR(MAX)
);

-- =====================
-- TABLA entregas_obras
-- =====================
IF OBJECT_ID('entregas_obras', 'U') IS NOT NULL DROP TABLE entregas_obras;
CREATE TABLE entregas_obras (
    id INT IDENTITY(1,1) PRIMARY KEY,
    id_obra INT FOREIGN KEY REFERENCES obras(id) ON DELETE CASCADE,
    fecha_entrega DATETIME,
    firma_receptor NVARCHAR(255)
);

-- =====================
-- TABLA checklist_entrega
-- =====================
IF OBJECT_ID('checklist_entrega', 'U') IS NOT NULL DROP TABLE checklist_entrega;
CREATE TABLE checklist_entrega (
    id INT IDENTITY(1,1) PRIMARY KEY,
    id_entrega INT FOREIGN KEY REFERENCES entregas_obras(id) ON DELETE CASCADE,
    observaciones NVARCHAR(MAX)
);

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

-- Fin del script
