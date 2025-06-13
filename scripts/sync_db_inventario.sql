-- Script de sincronización para la base de datos 'inventario'

-- Crear tablas faltantes (estructura básica, ajustar tipos según modelo si es necesario)
IF NOT EXISTS (SELECT * FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_NAME = 'inventario_items')
BEGIN
    CREATE TABLE inventario_items (
        id INT IDENTITY(1,1) PRIMARY KEY,
        codigo NVARCHAR(50),
        nombre NVARCHAR(100),
        tipo NVARCHAR(50),
        stock_actual INT,
        stock_minimo INT,
        ubicacion NVARCHAR(100),
        descripcion NVARCHAR(255),
        qr NVARCHAR(100),
        imagen_referencia NVARCHAR(255),
        rowversion ROWVERSION
    );
END
GO

IF NOT EXISTS (SELECT * FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_NAME = 'detalle_pedido')
BEGIN
    CREATE TABLE detalle_pedido (
        id INT IDENTITY(1,1) PRIMARY KEY,
        id_pedido INT,
        id_item INT,
        cantidad INT,
        precio_unitario DECIMAL(18,2),
        subtotal DECIMAL(18,2),
        estado NVARCHAR(50)
    );
END
GO

IF NOT EXISTS (SELECT * FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_NAME = 'inventario_perfiles')
BEGIN
    CREATE TABLE inventario_perfiles (
        id INT IDENTITY(1,1) PRIMARY KEY,
        codigo NVARCHAR(50),
        nombre NVARCHAR(100),
        tipo_material NVARCHAR(50),
        unidad NVARCHAR(20),
        stock_actual INT,
        stock_minimo INT,
        ubicacion NVARCHAR(100),
        descripcion NVARCHAR(255),
        qr NVARCHAR(100),
        imagen_referencia NVARCHAR(255),
        rowversion ROWVERSION
    );
END
GO

IF NOT EXISTS (SELECT * FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_NAME = 'movimientos_stock')
BEGIN
    CREATE TABLE movimientos_stock (
        id INT IDENTITY(1,1) PRIMARY KEY,
        id_item INT,
        tipo_movimiento NVARCHAR(50),
        cantidad INT,
        fecha DATETIME DEFAULT GETDATE(),
        usuario NVARCHAR(100),
        detalle NVARCHAR(255)
    );
END
GO

IF NOT EXISTS (SELECT * FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_NAME = 'reservas_stock')
BEGIN
    CREATE TABLE reservas_stock (
        id INT IDENTITY(1,1) PRIMARY KEY,
        id_item INT,
        id_obra INT,
        cantidad_reservada INT,
        fecha DATETIME DEFAULT GETDATE(),
        estado NVARCHAR(50)
    );
END
GO

IF NOT EXISTS (SELECT * FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_NAME = 'reservas_materiales')
BEGIN
    CREATE TABLE reservas_materiales (
        id INT IDENTITY(1,1) PRIMARY KEY,
        id_item INT,
        cantidad_reservada INT,
        referencia_obra NVARCHAR(100),
        estado NVARCHAR(50)
    );
END
GO

IF NOT EXISTS (SELECT * FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_NAME = 'perfiles_por_obra')
BEGIN
    CREATE TABLE perfiles_por_obra (
        id INT IDENTITY(1,1) PRIMARY KEY,
        id_obra INT,
        id_perfil INT,
        cantidad_reservada INT,
        estado NVARCHAR(50)
    );
END
GO

IF NOT EXISTS (SELECT * FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_NAME = 'materiales')
BEGIN
    CREATE TABLE materiales (
        id INT IDENTITY(1,1) PRIMARY KEY,
        codigo NVARCHAR(50),
        descripcion NVARCHAR(255),
        cantidad INT,
        ubicacion NVARCHAR(100),
        observaciones NVARCHAR(255),
        rowversion ROWVERSION
    );
END
GO

IF NOT EXISTS (SELECT * FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_NAME = 'obras')
BEGIN
    CREATE TABLE obras (
        id INT IDENTITY(1,1) PRIMARY KEY,
        nombre NVARCHAR(100),
        cliente NVARCHAR(100),
        estado NVARCHAR(50),
        fecha DATETIME,
        cantidad_aberturas INT,
        pago_completo BIT,
        pago_porcentaje DECIMAL(5,2),
        monto_usd DECIMAL(18,2),
        monto_ars DECIMAL(18,2),
        fecha_medicion DATETIME,
        dias_entrega INT,
        fecha_entrega DATETIME,
        usuario_creador NVARCHAR(100),
        rowversion ROWVERSION
    );
END
GO

IF NOT EXISTS (SELECT * FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_NAME = 'cronograma_obras')
BEGIN
    CREATE TABLE cronograma_obras (
        id INT IDENTITY(1,1) PRIMARY KEY,
        id_obra INT,
        etapa NVARCHAR(100),
        fecha_inicio DATETIME,
        fecha_fin DATETIME,
        estado NVARCHAR(50),
        fecha_programada DATETIME,
        fecha_realizada DATETIME,
        observaciones NVARCHAR(255),
        responsable NVARCHAR(100)
    );
END
GO

IF NOT EXISTS (SELECT * FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_NAME = 'materiales_por_obra')
BEGIN
    CREATE TABLE materiales_por_obra (
        id INT IDENTITY(1,1) PRIMARY KEY,
        id_obra INT,
        id_item INT,
        cantidad_necesaria INT,
        cantidad_reservada INT,
        estado NVARCHAR(50)
    );
END
GO

IF NOT EXISTS (SELECT * FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_NAME = 'pedidos')
BEGIN
    CREATE TABLE pedidos (
        id INT IDENTITY(1,1) PRIMARY KEY,
        id_obra INT,
        fecha_emision DATETIME DEFAULT GETDATE(),
        estado NVARCHAR(50),
        total_estimado DECIMAL(18,2),
        usuario NVARCHAR(100),
        rowversion ROWVERSION
    );
END
GO

IF NOT EXISTS (SELECT * FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_NAME = 'pedidos_compra')
BEGIN
    CREATE TABLE pedidos_compra (
        id INT IDENTITY(1,1) PRIMARY KEY,
        id_obra INT,
        fecha DATETIME DEFAULT GETDATE(),
        estado NVARCHAR(50),
        usuario NVARCHAR(100),
        total_usd DECIMAL(18,2),
        total_ars DECIMAL(18,2),
        rowversion ROWVERSION
    );
END
GO

IF NOT EXISTS (SELECT * FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_NAME = 'pedidos_por_obra')
BEGIN
    CREATE TABLE pedidos_por_obra (
        id INT IDENTITY(1,1) PRIMARY KEY,
        id_pedido INT,
        id_obra INT,
        id_item INT,
        tipo_item NVARCHAR(50),
        cantidad_requerida INT
    );
END
GO

-- Agregar columnas faltantes a tablas existentes
IF COL_LENGTH('inventario_perfiles', 'rowversion') IS NULL
    ALTER TABLE inventario_perfiles ADD rowversion ROWVERSION;
IF COL_LENGTH('movimientos_stock', 'usuario') IS NULL
    ALTER TABLE movimientos_stock ADD usuario NVARCHAR(100);
IF COL_LENGTH('reservas_stock', 'id_obra') IS NULL
    ALTER TABLE reservas_stock ADD id_obra INT;
IF COL_LENGTH('perfiles_por_obra', 'id_obra') IS NULL
    ALTER TABLE perfiles_por_obra ADD id_obra INT;
IF COL_LENGTH('materiales', 'cantidad') IS NULL
    ALTER TABLE materiales ADD cantidad INT;
IF COL_LENGTH('cronograma_obras', 'fecha_inicio') IS NULL
    ALTER TABLE cronograma_obras ADD fecha_inicio DATETIME;
IF COL_LENGTH('pedidos', 'id_obra') IS NULL
    ALTER TABLE pedidos ADD id_obra INT;
IF COL_LENGTH('pedidos_por_obra', 'id_pedido') IS NULL
    ALTER TABLE pedidos_por_obra ADD id_pedido INT;
GO
