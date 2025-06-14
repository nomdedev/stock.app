-- Script unificado para sincronizar tablas y agregar datos de ejemplo

-- Base de datos 'auditoria'
USE auditoria;
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

-- Base de datos 'users'
USE users;
IF NOT EXISTS (SELECT * FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_NAME = 'usuarios')
BEGIN
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
END
GO

-- Base de datos 'inventario'
USE inventario;
IF NOT EXISTS (SELECT * FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_NAME = 'proveedores')
BEGIN
    CREATE TABLE proveedores (
        id INT IDENTITY(1,1) PRIMARY KEY,
        nombre NVARCHAR(100),
        contacto NVARCHAR(100),
        telefono NVARCHAR(50),
        direccion NVARCHAR(255)
    );
END
GO

IF NOT EXISTS (SELECT * FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_NAME = 'categorias')
BEGIN
    CREATE TABLE categorias (
        id INT IDENTITY(1,1) PRIMARY KEY,
        nombre NVARCHAR(100),
        descripcion NVARCHAR(255)
    );
END
GO

IF NOT EXISTS (SELECT * FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_NAME = 'inventario')
BEGIN
    CREATE TABLE inventario (
        id INT IDENTITY(1,1) PRIMARY KEY,
        codigo NVARCHAR(50),
        nombre NVARCHAR(100),
        categoria_id INT FOREIGN KEY REFERENCES categorias(id),
        proveedor_id INT FOREIGN KEY REFERENCES proveedores(id),
        stock_actual DECIMAL(18,2),
        stock_minimo DECIMAL(18,2),
        ubicacion NVARCHAR(100),
        descripcion NVARCHAR(255)
    );
END
GO

-- Agregar datos de ejemplo
INSERT INTO proveedores (nombre, contacto, telefono, direccion) VALUES
('Proveedor A', 'Juan Perez', '123456789', 'Calle Falsa 123'),
('Proveedor B', 'Maria Lopez', '987654321', 'Avenida Siempre Viva 456');

INSERT INTO categorias (nombre, descripcion) VALUES
('Categoría 1', 'Descripción de categoría 1'),
('Categoría 2', 'Descripción de categoría 2');

INSERT INTO inventario (codigo, nombre, categoria_id, proveedor_id, stock_actual, stock_minimo, ubicacion, descripcion) VALUES
('INV001', 'Producto 1', 1, 1, 100, 10, 'Almacén A', 'Descripción del producto 1'),
('INV002', 'Producto 2', 2, 2, 50, 5, 'Almacén B', 'Descripción del producto 2');
