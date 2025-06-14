-- =====================
-- DATOS DE EJEMPLO PARA FLUJO COMPLETO DE OBRAS Y PEDIDOS
-- =====================
-- NOTA: Ajusta los IDs de obra y usuario según tu base si es necesario.

-- CREACIÓN CONDICIONAL DE TABLAS DE EJEMPLO SI NO EXISTEN
IF OBJECT_ID('inventario.dbo.vidrios_por_obra', 'U') IS NULL
CREATE TABLE inventario.dbo.vidrios_por_obra (
    id INT IDENTITY(1,1) PRIMARY KEY,
    id_obra INT,
    id_vidrio INT,
    cantidad_necesaria DECIMAL(18,2),
    cantidad_reservada DECIMAL(18,2),
    estado VARCHAR(30)
);

IF OBJECT_ID('inventario.dbo.herrajes_por_obra', 'U') IS NULL
CREATE TABLE inventario.dbo.herrajes_por_obra (
    id INT IDENTITY(1,1) PRIMARY KEY,
    id_obra INT,
    id_herraje INT,
    cantidad_necesaria DECIMAL(18,2),
    cantidad_reservada DECIMAL(18,2),
    estado VARCHAR(30)
);

IF OBJECT_ID('inventario.dbo.pagos_por_obra', 'U') IS NULL
CREATE TABLE inventario.dbo.pagos_por_obra (
    id INT IDENTITY(1,1) PRIMARY KEY,
    id_obra INT,
    monto DECIMAL(18,2),
    moneda VARCHAR(10),
    fecha_pago DATE,
    metodo VARCHAR(50),
    estado VARCHAR(30)
);

IF OBJECT_ID('inventario.dbo.logistica_por_obra', 'U') IS NULL
CREATE TABLE inventario.dbo.logistica_por_obra (
    id INT IDENTITY(1,1) PRIMARY KEY,
    id_obra INT,
    estado_envio VARCHAR(30),
    fecha_envio DATE,
    transportista VARCHAR(100),
    observaciones TEXT
);

-- 1. USUARIOS (en base users)
INSERT INTO users.dbo.usuarios (nombre, apellido, email, usuario, password_hash, rol, estado)
VALUES
('Admin', 'Principal', 'admin@empresa.com', 'admin', 'hash1', 'admin', 'activo'),
('Juan', 'Pérez', 'juan@empresa.com', 'jperez', 'hash2', 'operador', 'activo'),
('Ana', 'García', 'ana@empresa.com', 'agarcia', 'hash3', 'logistica', 'activo');

-- 2. PERMISOS DE USUARIOS
INSERT INTO users.dbo.permisos_modulos (id_usuario, modulo, puede_ver, puede_modificar, puede_aprobar)
VALUES
(1, 'Obras', 1, 1, 1),
(2, 'Obras', 1, 1, 0),
(3, 'Logistica', 1, 0, 0);

-- 3. MATERIALES POR OBRA (en base inventario)
INSERT INTO inventario.dbo.materiales_por_obra (id_obra, id_item, cantidad_necesaria, cantidad_reservada, estado)
VALUES
(1, 101, 10, 10, 'reservado'),
(1, 102, 5, 5, 'reservado'),
(2, 103, 8, 8, 'reservado'),
(3, 104, 12, 12, 'reservado');

-- 4. CRONOGRAMA DE OBRAS (en base inventario)
INSERT INTO inventario.dbo.cronograma_obras (id_obra, etapa, fecha_programada, fecha_realizada, observaciones, responsable, estado)
VALUES
(1, 'Medición', '2025-05-01', '2025-05-02', 'Medición realizada', 1, 'completado'),
(1, 'Fabricación', '2025-05-10', NULL, 'En espera de materiales', 2, 'pendiente'),
(2, 'Medición', '2025-04-20', '2025-04-21', 'Medición ok', 1, 'completado'),
(2, 'Fabricación', '2025-04-25', NULL, '', 2, 'pendiente'),
(3, 'Medición', '2025-03-15', '2025-03-16', '', 1, 'completado'),
(3, 'Entrega', '2025-06-10', NULL, '', 3, 'pendiente');

-- 5. LOGS DE USUARIOS (opcional, para auditoría)
INSERT INTO users.dbo.logs_usuarios (usuario_id, accion, modulo, fecha_hora, detalle, ip_origen)
VALUES
(1, 'login', 'Obras', GETDATE(), 'Ingreso correcto', '127.0.0.1'),
(2, 'alta_obra', 'Obras', GETDATE(), 'Creó obra Torre Norte', '127.0.0.1'),
(3, 'ver_cronograma', 'Obras', GETDATE(), 'Consultó cronograma', '127.0.0.1');

-- 6. SOLICITUDES DE APROBACION (opcional)
INSERT INTO users.dbo.solicitudes_aprobacion (id_usuario, modulo, tipo_accion, datos_json, estado)
VALUES
(2, 'Obras', 'alta', '{"obra":"Residencial Sur"}', 'pendiente');

-- 7. VIDRIOS POR OBRA (en base inventario)
INSERT INTO inventario.dbo.vidrios_por_obra (id_obra, id_vidrio, cantidad_necesaria, cantidad_reservada, estado)
VALUES
(1, 201, 6, 6, 'reservado'),
(2, 202, 4, 4, 'reservado'),
(3, 203, 8, 8, 'reservado');

-- 8. HERRAJES POR OBRA (en base inventario)
INSERT INTO inventario.dbo.herrajes_por_obra (id_obra, id_herraje, cantidad_necesaria, cantidad_reservada, estado)
VALUES
(1, 301, 12, 12, 'reservado'),
(2, 302, 7, 7, 'reservado'),
(3, 303, 10, 10, 'reservado');

-- 9. PAGOS POR OBRA (en base inventario)
INSERT INTO inventario.dbo.pagos_por_obra (id_obra, monto, moneda, fecha_pago, metodo, estado)
VALUES
(1, 1000, 'USD', '2025-05-05', 'transferencia', 'completado'),
(2, 800, 'USD', '2025-04-28', 'efectivo', 'pendiente'),
(3, 1200, 'USD', '2025-06-01', 'tarjeta', 'completado');

-- 10. AUDITORÍA DE OBRAS (en base auditoria)
INSERT INTO auditoria.dbo.eventos_auditoria (usuario_id, modulo, accion, detalle, ip_origen, fecha_hora)
VALUES
(1, 'Obras', 'alta', 'Alta de obra Edificio Central', '127.0.0.1', GETDATE()),
(2, 'Obras', 'modificacion', 'Modificación de obra Torre Norte', '127.0.0.1', GETDATE()),
(3, 'Obras', 'consulta', 'Consulta de obra Residencial Sur', '127.0.0.1', GETDATE());

-- 11. LOGÍSTICA POR OBRA (en base inventario)
INSERT INTO inventario.dbo.logistica_por_obra (id_obra, estado_envio, fecha_envio, transportista, observaciones)
VALUES
(1, 'en tránsito', '2025-05-20', 'Transporte Sur', 'Sin novedades'),
(2, 'pendiente', NULL, NULL, 'Esperando confirmación'),
(3, 'entregado', '2025-06-12', 'Logística Delta', 'Entregado sin inconvenientes');

-- Agregar columnas faltantes en la tabla `obras`
IF COL_LENGTH('inventario.dbo.obras', 'estado_actual') IS NULL
ALTER TABLE inventario.dbo.obras ADD estado_actual NVARCHAR(50), ultima_actualizacion DATETIME DEFAULT GETDATE();

-- Crear tabla `historial_estados`
IF OBJECT_ID('inventario.dbo.historial_estados', 'U') IS NULL
CREATE TABLE inventario.dbo.historial_estados (
    id INT IDENTITY(1,1) PRIMARY KEY,
    id_obra INT FOREIGN KEY REFERENCES inventario.dbo.obras(id),
    estado NVARCHAR(50),
    fecha_cambio DATETIME DEFAULT GETDATE(),
    detalles NVARCHAR(255)
);

-- Ajustar tablas relacionadas con pedidos para incluir seguimiento detallado
IF COL_LENGTH('inventario.dbo.vidrios_por_obra', 'fecha_actualizacion') IS NULL
ALTER TABLE inventario.dbo.vidrios_por_obra ADD fecha_actualizacion DATETIME DEFAULT GETDATE();

IF COL_LENGTH('inventario.dbo.herrajes_por_obra', 'fecha_actualizacion') IS NULL
ALTER TABLE inventario.dbo.herrajes_por_obra ADD fecha_actualizacion DATETIME DEFAULT GETDATE();

-- Insertar datos de ejemplo en `historial_estados`
INSERT INTO inventario.dbo.historial_estados (id_obra, estado, detalles)
VALUES
(1, 'En progreso', 'Inicio de obra'),
(1, 'Pendiente', 'Esperando materiales'),
(2, 'Completado', 'Obra finalizada'),
(3, 'En progreso', 'Instalación de vidrios en curso');

-- Puedes agregar más ejemplos para otros módulos según tus tablas y relaciones.
