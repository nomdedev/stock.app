-- Script para la base de datos: pedidos
-- Contiene tablas de pedidos de compra, detalle, presupuestos

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
    id_item INT,
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
