-- Script actualizado para la base de datos: inventario
-- Estructura real según uso en todos los módulos y tests

-- =====================
-- TABLA inventario_perfiles
-- =====================
IF OBJECT_ID('inventario_perfiles', 'U') IS NOT NULL DROP TABLE inventario_perfiles;
CREATE TABLE inventario_perfiles (
    id INT IDENTITY(1,1) PRIMARY KEY,
    codigo NVARCHAR(100) UNIQUE NOT NULL,
    tipo_material NVARCHAR(50),
    unidad NVARCHAR(20),
    stock_actual DECIMAL(18,2) DEFAULT 0,
    stock_minimo DECIMAL(18,2) DEFAULT 0,
    ubicacion NVARCHAR(255),
    descripcion NVARCHAR(MAX),
    qr NVARCHAR(255),
    imagen_referencia NVARCHAR(255),
    tipo NVARCHAR(50),
    acabado NVARCHAR(50),
    numero NVARCHAR(50),
    vs NVARCHAR(50),
    proveedor NVARCHAR(100),
    longitud NVARCHAR(20),
    ancho NVARCHAR(20),
    alto NVARCHAR(20),
    necesarias DECIMAL(18,2),
    stock DECIMAL(18,2),
    faltan DECIMAL(18,2),
    ped_min DECIMAL(18,2),
    emba NVARCHAR(50),
    pedido NVARCHAR(50),
    importe DECIMAL(18,2),
    fecha_creacion DATETIME DEFAULT GETDATE(),
    fecha_actualizacion DATETIME DEFAULT GETDATE()
);

-- =====================
-- TABLA perfiles_por_obra
-- =====================
IF OBJECT_ID('perfiles_por_obra', 'U') IS NOT NULL DROP TABLE perfiles_por_obra;
CREATE TABLE perfiles_por_obra (
    id INT IDENTITY(1,1) PRIMARY KEY,
    id_obra INT NOT NULL,
    id_perfil INT FOREIGN KEY REFERENCES inventario_perfiles(id) ON DELETE CASCADE,
    cantidad_reservada DECIMAL(18,2) NOT NULL,
    estado NVARCHAR(30) DEFAULT 'Reservado'
);

-- =====================
-- TABLA reservas_materiales
-- =====================
IF OBJECT_ID('reservas_materiales', 'U') IS NOT NULL DROP TABLE reservas_materiales;
CREATE TABLE reservas_materiales (
    id INT IDENTITY(1,1) PRIMARY KEY,
    id_item INT FOREIGN KEY REFERENCES inventario_perfiles(id) ON DELETE CASCADE,
    cantidad_reservada DECIMAL(18,2) NOT NULL,
    referencia_obra NVARCHAR(100),
    estado NVARCHAR(20) DEFAULT 'activa',
    codigo_reserva NVARCHAR(100),
    fecha_reserva DATETIME DEFAULT GETDATE()
);

-- =====================
-- TABLA movimientos_stock
-- =====================
IF OBJECT_ID('movimientos_stock', 'U') IS NOT NULL DROP TABLE movimientos_stock;
CREATE TABLE movimientos_stock (
    id INT IDENTITY(1,1) PRIMARY KEY,
    id_perfil INT FOREIGN KEY REFERENCES inventario_perfiles(id) ON DELETE CASCADE,
    tipo_movimiento NVARCHAR(20) NOT NULL,
    cantidad DECIMAL(18,2) NOT NULL,
    fecha DATETIME DEFAULT GETDATE(),
    usuario NVARCHAR(100),
    referencia NVARCHAR(255)
);

-- =====================
-- TABLA pedidos_material
-- =====================
IF OBJECT_ID('pedidos_material', 'U') IS NOT NULL DROP TABLE pedidos_material;
CREATE TABLE pedidos_material (
    id INT IDENTITY(1,1) PRIMARY KEY,
    id_obra INT NOT NULL,
    id_item INT FOREIGN KEY REFERENCES inventario_perfiles(id) ON DELETE CASCADE,
    cantidad DECIMAL(18,2) NOT NULL,
    estado NVARCHAR(30),
    fecha DATETIME DEFAULT GETDATE(),
    usuario NVARCHAR(100)
);

-- =====================
-- TABLA herrajes
-- =====================
IF OBJECT_ID('herrajes', 'U') IS NOT NULL DROP TABLE herrajes;
CREATE TABLE herrajes (
    id INT IDENTITY(1,1) PRIMARY KEY,
    codigo NVARCHAR(100) UNIQUE NOT NULL,
    descripcion NVARCHAR(255),
    stock_actual DECIMAL(18,2) DEFAULT 0,
    stock_minimo DECIMAL(18,2) DEFAULT 0,
    ubicacion NVARCHAR(255),
    proveedor NVARCHAR(100),
    imagen_referencia NVARCHAR(255)
);

-- =====================
-- TABLA herrajes_por_obra (ajustada)
-- =====================
IF OBJECT_ID('herrajes_por_obra', 'U') IS NOT NULL DROP TABLE herrajes_por_obra;
CREATE TABLE herrajes_por_obra (
    id INT IDENTITY(1,1) PRIMARY KEY,
    id_obra INT NOT NULL,
    id_herraje INT FOREIGN KEY REFERENCES herrajes(id) ON DELETE CASCADE,
    cantidad_necesaria DECIMAL(18,2) NOT NULL,
    cantidad_reservada DECIMAL(18,2) NOT NULL,
    estado NVARCHAR(30) DEFAULT 'Reservado'
);

-- =====================
-- TABLA materiales
-- =====================
IF OBJECT_ID('materiales', 'U') IS NOT NULL DROP TABLE materiales;
CREATE TABLE materiales (
    id INT IDENTITY(1,1) PRIMARY KEY,
    codigo NVARCHAR(100) UNIQUE NOT NULL,
    descripcion NVARCHAR(255),
    cantidad DECIMAL(18,2) DEFAULT 0,
    ubicacion NVARCHAR(100),
    fecha_ingreso DATETIME DEFAULT GETDATE(),
    observaciones NVARCHAR(MAX)
);

-- =====================
-- TABLA pagos_por_obra
-- =====================
IF OBJECT_ID('pagos_por_obra', 'U') IS NOT NULL DROP TABLE pagos_por_obra;
CREATE TABLE pagos_por_obra (
    id INT IDENTITY(1,1) PRIMARY KEY,
    id_obra INT NOT NULL,
    monto DECIMAL(18,2),
    moneda NVARCHAR(10),
    fecha_pago DATE,
    metodo NVARCHAR(50),
    estado NVARCHAR(30)
);

-- =====================
-- TABLA logistica_por_obra
-- =====================
IF OBJECT_ID('logistica_por_obra', 'U') IS NOT NULL DROP TABLE logistica_por_obra;
CREATE TABLE logistica_por_obra (
    id INT IDENTITY(1,1) PRIMARY KEY,
    id_obra INT NOT NULL,
    estado_envio NVARCHAR(30),
    fecha_envio DATE,
    transportista NVARCHAR(100),
    observaciones NVARCHAR(MAX)
);

-- =====================
-- TABLA vidrios_por_obra
-- =====================
IF OBJECT_ID('vidrios_por_obra', 'U') IS NOT NULL DROP TABLE vidrios_por_obra;
CREATE TABLE vidrios_por_obra (
    id INT IDENTITY(1,1) PRIMARY KEY,
    id_obra INT NOT NULL,
    id_vidrio INT,
    cantidad_necesaria DECIMAL(18,2),
    cantidad_reservada DECIMAL(18,2),
    estado NVARCHAR(30)
);

-- =====================
-- TABLA materiales_por_obra
-- =====================
IF OBJECT_ID('materiales_por_obra', 'U') IS NOT NULL DROP TABLE materiales_por_obra;
CREATE TABLE materiales_por_obra (
    id INT IDENTITY(1,1) PRIMARY KEY,
    id_obra INT NOT NULL,
    id_item INT NOT NULL,
    cantidad_necesaria DECIMAL(18,2) NOT NULL,
    cantidad_reservada DECIMAL(18,2) NOT NULL,
    estado NVARCHAR(30) DEFAULT 'Reservado'
);

-- =====================
-- DATOS DE EJEMPLO MÍNIMOS
-- =====================
INSERT INTO inventario_perfiles (codigo, descripcion, tipo_material, unidad, stock_actual, stock_minimo, ubicacion, descripcion) VALUES ('PERF001', 'Perfil A', 'PVC', 'm', 100, 10, 'Depósito', 'Perfil estándar');
INSERT INTO herrajes (codigo, descripcion, stock_actual, stock_minimo, ubicacion) VALUES ('HERR001', 'Herraje A', 50, 5, 'Depósito');
INSERT INTO materiales (codigo, descripcion, cantidad, ubicacion) VALUES ('MAT001', 'Material A', 200, 'Depósito');
INSERT INTO perfiles_por_obra (id_obra, id_perfil, cantidad_reservada) VALUES (1, 1, 10);
INSERT INTO reservas_materiales (id_item, cantidad_reservada, referencia_obra, estado) VALUES (1, 5, 'OBRA1', 'activa');
INSERT INTO movimientos_stock (id_perfil, tipo_movimiento, cantidad, usuario) VALUES (1, 'Ingreso', 100, 'admin');
INSERT INTO pedidos_material (id_obra, id_item, cantidad, estado, usuario) VALUES (1, 1, 5, 'pendiente', 'admin');
INSERT INTO herrajes_por_obra (id_obra, id_herraje, cantidad_reservada) VALUES (1, 1, 2);
INSERT INTO materiales_por_obra (id_obra, id_item, cantidad_necesaria, cantidad_reservada) VALUES (1, 1, 4, 2);
INSERT INTO pagos_por_obra (id_obra, monto, moneda, estado) VALUES (1, 1000, 'ARS', 'pendiente');
INSERT INTO logistica_por_obra (id_obra, estado_envio, transportista) VALUES (1, 'pendiente', 'Transporte X');
INSERT INTO vidrios_por_obra (id_obra, id_vidrio, cantidad_necesaria, cantidad_reservada, estado) VALUES (1, 1, 4, 2, 'pendiente');
