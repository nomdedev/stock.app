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
DECLARE @estado_activo NVARCHAR(10) = 'activo';

INSERT INTO users.dbo.usuarios (nombre, apellido, email, usuario, password_hash, rol, estado)
VALUES
('Admin', 'Principal', 'admin@empresa.com', 'admin', 'hash1', 'admin', @estado_activo),
('Juan', 'Pérez', 'juan@empresa.com', 'jperez', 'hash2', 'operador', @estado_activo),
('Ana', 'García', 'ana@empresa.com', 'agarcia', 'hash3', 'logistica', @estado_activo);

-- 2. PERMISOS DE USUARIOS
DECLARE @ID_ADMIN INT = 1;
DECLARE @ID_OPERADOR INT = 2;
DECLARE @ID_LOGISTICA INT = 3;
DECLARE @PERMISO_VER BIT = 1;
DECLARE @PERMISO_MODIFICAR BIT = 1;
DECLARE @PERMISO_APROBAR BIT = 1;
DECLARE @PERMISO_NO_APROBAR BIT = 0;
DECLARE @PERMISO_NO_MODIFICAR BIT = 0;

INSERT INTO users.dbo.permisos_modulos (id_usuario, modulo, puede_ver, puede_modificar, puede_aprobar)
VALUES
(@ID_ADMIN, 'Obras', @PERMISO_VER, @PERMISO_MODIFICAR, @PERMISO_APROBAR),
(@ID_OPERADOR, 'Obras', @PERMISO_VER, @PERMISO_MODIFICAR, @PERMISO_NO_APROBAR),
(@ID_LOGISTICA, 'Logistica', @PERMISO_VER, @PERMISO_NO_MODIFICAR, @PERMISO_NO_APROBAR);

-- 3. MATERIALES POR OBRA (en base inventario)
DECLARE @CANTIDAD_RESERVADA_DEFAULT DECIMAL(18,2) = 10;
DECLARE @CANTIDAD_MATERIAL_5 DECIMAL(18,2) = 5;
DECLARE @CANTIDAD_MATERIAL_8 DECIMAL(18,2) = 8;
DECLARE @CANTIDAD_MATERIAL_12 DECIMAL(18,2) = 12;
INSERT INTO inventario.dbo.materiales_por_obra (id_obra, id_item, cantidad_necesaria, cantidad_reservada, estado)
VALUES
(1, 101, @CANTIDAD_RESERVADA_DEFAULT, @CANTIDAD_RESERVADA_DEFAULT, 'reservado'),
(1, 102, @CANTIDAD_MATERIAL_5, @CANTIDAD_MATERIAL_5, 'reservado'),
(2, 103, @CANTIDAD_MATERIAL_8, @CANTIDAD_MATERIAL_8, 'reservado'),
(3, 104, @CANTIDAD_MATERIAL_12, @CANTIDAD_MATERIAL_12, 'reservado');

-- 4. CRONOGRAMA DE OBRAS (en base inventario)
DECLARE @ETAPA_MEDICION NVARCHAR(20) = 'Medición';
DECLARE @ETAPA_FABRICACION NVARCHAR(20) = 'Fabricación';
DECLARE @ETAPA_ENTREGA NVARCHAR(20) = 'Entrega';

INSERT INTO inventario.dbo.cronograma_obras (id_obra, etapa, fecha_programada, fecha_realizada, observaciones, responsable, estado)
VALUES
(1, @ETAPA_MEDICION, '2025-05-01', '2025-05-02', 'Medición realizada', 1, 'completado'),
(1, @ETAPA_FABRICACION, '2025-05-10', NULL, 'En espera de materiales', 2, 'pendiente'),
(2, @ETAPA_MEDICION, '2025-04-20', '2025-04-21', 'Medición ok', 1, 'completado'),
(2, @ETAPA_FABRICACION, '2025-04-25', NULL, '', 2, 'pendiente'),
(3, @ETAPA_ENTREGA, '2025-06-10', NULL, '', 3, 'pendiente');

-- 5. LOGS DE USUARIOS (opcional, para auditoría)
DECLARE @IP_LOCAL NVARCHAR(15) = '127.0.0.1';
INSERT INTO users.dbo.logs_usuarios (usuario_id, accion, modulo, fecha_hora, detalle, ip_origen)
VALUES
(1, 'login', 'Obras', GETDATE(), 'Ingreso correcto', @IP_LOCAL),
(2, 'alta_obra', 'Obras', GETDATE(), 'Creó obra Torre Norte', @IP_LOCAL),
(3, 'ver_cronograma', 'Obras', GETDATE(), 'Consultó cronograma', @IP_LOCAL);

-- 6. SOLICITUDES DE APROBACION (opcional)
INSERT INTO users.dbo.solicitudes_aprobacion (id_usuario, modulo, tipo_accion, datos_json, estado)
VALUES
(2, 'Obras', 'alta', '{"obra":"Residencial Sur"}', 'pendiente');
-- 7. VIDRIOS POR OBRA (en base inventario)
DECLARE @CANTIDAD_VIDRIO_DEFAULT DECIMAL(18,2) = 8;
INSERT INTO inventario.dbo.vidrios_por_obra (id_obra, id_vidrio, cantidad_necesaria, cantidad_reservada, estado)
VALUES
(1, 201, 6, 6, 'reservado'),
(2, 202, 4, 4, 'reservado'),
(3, 203, @CANTIDAD_VIDRIO_DEFAULT, @CANTIDAD_VIDRIO_DEFAULT, 'reservado');
-- 8. HERRAJES POR OBRA (en base inventario)
DECLARE @CANTIDAD_HERRAJE_DEFAULT DECIMAL(18,2) = 9;
INSERT INTO inventario.dbo.herrajes_por_obra (id_obra, id_herraje, cantidad_necesaria, cantidad_reservada, estado)
VALUES
(1, 301, @CANTIDAD_MATERIAL_12, @CANTIDAD_MATERIAL_12, 'reservado'),
(2, 302, 7, 7, 'reservado'),
(3, 303, @CANTIDAD_HERRAJE_DEFAULT, @CANTIDAD_HERRAJE_DEFAULT, 'reservado');

-- 9. PAGOS POR OBRA (en base inventario)
INSERT INTO inventario.dbo.pagos_por_obra (id_obra, monto, moneda, fecha_pago, metodo, estado)
VALUES
(1, 1000, 'USD', '2025-05-05', 'transferencia', 'completado'),
(2, 800, 'USD', '2025-04-28', 'efectivo', 'pendiente'),
(3, 1200, 'USD', '2025-06-01', 'tarjeta', 'completado');
-- 10. AUDITORÍA DE OBRAS (en base auditoria)
INSERT INTO auditoria.dbo.eventos_auditoria (usuario_id, modulo, accion, detalle, ip_origen, fecha_hora)
VALUES
(1, 'Obras', 'alta', 'Alta de obra Edificio Central', @IP_LOCAL, GETDATE()),
(2, 'Obras', 'modificacion', 'Modificación de obra Torre Norte', @IP_LOCAL, GETDATE()),
(3, 'Obras', 'consulta', 'Consulta de obra Residencial Sur', @IP_LOCAL, GETDATE());

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
