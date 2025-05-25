-- Base de datos: usuarios
CREATE DATABASE IF NOT EXISTS users;
\c usuarios;

CREATE TABLE usuarios (
    id SERIAL PRIMARY KEY,
    nombre VARCHAR(100),
    apellido VARCHAR(100),
    email VARCHAR(100) UNIQUE,
    usuario VARCHAR(50) UNIQUE,
    password_hash TEXT,
    rol VARCHAR(50),
    estado VARCHAR(20),
    fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    ultima_conexion TIMESTAMP
);

CREATE TABLE roles_permisos (
    id SERIAL PRIMARY KEY,
    rol VARCHAR(50),
    modulo VARCHAR(50),
    permiso_ver BOOLEAN,
    permiso_editar BOOLEAN,
    permiso_aprobar BOOLEAN,
    permiso_eliminar BOOLEAN
);

CREATE TABLE logs_usuarios (
    id SERIAL PRIMARY KEY,
    usuario_id INT REFERENCES usuarios(id),
    accion TEXT,
    modulo VARCHAR(50),
    fecha_hora TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    detalle TEXT,
    ip_origen VARCHAR(100)
);

-- Base de datos: inventario
CREATE DATABASE IF NOT EXISTS inventario;
\c inventario;

CREATE TABLE inventario_items (
    id SERIAL PRIMARY KEY,
    codigo VARCHAR(20) UNIQUE,
    nombre VARCHAR(100),
    tipo_material VARCHAR(50),
    unidad VARCHAR(20),
    stock_actual DECIMAL,
    stock_minimo DECIMAL,
    ubicacion TEXT,
    descripcion TEXT,
    qr_code TEXT,
    imagen_referencia TEXT
);

CREATE TABLE movimientos_stock (
    id SERIAL PRIMARY KEY,
    id_item INT REFERENCES inventario_items(id),
    fecha TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    tipo_movimiento VARCHAR(20),
    cantidad DECIMAL,
    realizado_por INT,
    observaciones TEXT,
    referencia TEXT
);

CREATE TABLE reservas_stock (
    id SERIAL PRIMARY KEY,
    id_item INT REFERENCES inventario_items(id),
    fecha_reserva TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    cantidad_reservada DECIMAL,
    referencia_obra INT,
    estado VARCHAR(20)
);

-- Base de datos: obras
CREATE DATABASE IF NOT EXISTS obras;
\c obras;

CREATE TABLE obras (
    id SERIAL PRIMARY KEY,
    nombre_cliente VARCHAR(100),
    apellido_cliente VARCHAR(100),
    telefono VARCHAR(50),
    email VARCHAR(100),
    direccion TEXT,
    fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    estado_general VARCHAR(50),
    observaciones TEXT,
    nombre VARCHAR(100),
    cliente VARCHAR(100),
    estado VARCHAR(50),
    fecha DATE
);

CREATE TABLE cronograma_obras (
    id SERIAL PRIMARY KEY,
    id_obra INT REFERENCES obras(id),
    etapa VARCHAR(50),
    fecha_programada DATE,
    fecha_realizada DATE,
    observaciones TEXT,
    responsable INT,
    estado VARCHAR(30)
);

CREATE TABLE materiales_por_obra (
    id SERIAL PRIMARY KEY,
    id_obra INT REFERENCES obras(id),
    id_item INT,
    cantidad_necesaria DECIMAL,
    cantidad_reservada DECIMAL,
    estado VARCHAR(30)
);


-- Base de datos: compras
CREATE DATABASE IF NOT EXISTS compras;
\c compras;

CREATE TABLE pedidos_compra (
    id SERIAL PRIMARY KEY,
    fecha_creacion TIMESTAMP,
    solicitado_por INT,
    estado VARCHAR(30),
    observaciones TEXT,
    prioridad VARCHAR(20)
);

CREATE TABLE detalle_pedido (
    id SERIAL PRIMARY KEY,
    id_pedido INT REFERENCES pedidos_compra(id),
    id_item INT,
    cantidad_solicitada DECIMAL,
    unidad VARCHAR(20),
    justificacion TEXT
);

CREATE TABLE presupuestos (
    id SERIAL PRIMARY KEY,
    id_pedido INT REFERENCES pedidos_compra(id),
    proveedor VARCHAR(100),
    fecha_recepcion DATE,
    archivo_adjunto TEXT,
    comentarios TEXT,
    precio_total DECIMAL,
    seleccionado BOOLEAN
);

-- Base de datos: produccion
CREATE DATABASE IF NOT EXISTS produccion;
\c produccion;

CREATE TABLE aberturas (
    id SERIAL PRIMARY KEY,
    id_obra INT,
    codigo VARCHAR(100),
    tipo_abertura VARCHAR(50),
    descripcion TEXT,
    estado_general VARCHAR(50),
    fecha_inicio DATE,
    fecha_entrega_estimada DATE
);

CREATE TABLE etapas_fabricacion (
    id SERIAL PRIMARY KEY,
    id_abertura INT REFERENCES aberturas(id),
    etapa VARCHAR(50),
    fecha_inicio DATE,
    fecha_fin DATE,
    realizado_por INT,
    estado VARCHAR(30),
    tiempo_estimado INTERVAL,
    tiempo_real INTERVAL,
    observaciones TEXT
);

-- Base de datos: logistica
CREATE DATABASE IF NOT EXISTS logistica;
\c logistica;

CREATE TABLE entregas_obras (
    id SERIAL PRIMARY KEY,
    id_obra INT,
    fecha_programada DATE,
    fecha_realizada DATE,
    estado VARCHAR(30),
    vehiculo_asignado INT,
    chofer_asignado INT,
    observaciones TEXT,
    firma_receptor TEXT
);

CREATE TABLE checklist_entrega (
    id SERIAL PRIMARY KEY,
    id_entrega INT REFERENCES entregas_obras(id),
    item TEXT,
    estado_item VARCHAR(20),
    observaciones TEXT
);

-- Base de datos: auditoria
CREATE DATABASE IF NOT EXISTS auditoria;
\c auditoria;

CREATE TABLE auditorias_sistema (
    id SERIAL PRIMARY KEY,
    fecha_hora TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    usuario_id INT,
    modulo_afectado VARCHAR(50),
    tipo_evento VARCHAR(30),
    detalle TEXT,
    ip_origen VARCHAR(50),
    device_info TEXT,
    origen_evento VARCHAR(30)
);

CREATE TABLE errores_sistema (
    id SERIAL PRIMARY KEY,
    fecha_hora TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    usuario_id INT,
    modulo VARCHAR(50),
    descripcion_error TEXT,
    stack_trace TEXT,
    ip_origen VARCHAR(50),
    origen_evento VARCHAR(30)
);


-- Base de datos: mantenimiento
CREATE DATABASE IF NOT EXISTS mantenimiento;
\c mantenimiento;

CREATE TABLE herramientas (
    id SERIAL PRIMARY KEY,
    nombre VARCHAR(100),
    descripcion TEXT,
    codigo_interno VARCHAR(50),
    ubicacion TEXT,
    estado VARCHAR(30),
    imagen TEXT
);

CREATE TABLE vehiculos (
    id SERIAL PRIMARY KEY,
    patente VARCHAR(20),
    marca VARCHAR(50),
    modelo VARCHAR(50),
    estado_operativo VARCHAR(30),
    ubicacion_actual TEXT
);

CREATE TABLE mantenimientos (
    id SERIAL PRIMARY KEY,
    tipo_objeto VARCHAR(20),
    id_objeto INT,
    tipo_mantenimiento VARCHAR(50),
    fecha_realizacion DATE,
    realizado_por INT,
    observaciones TEXT,
    firma_digital TEXT
);

CREATE TABLE checklists_mantenimiento (
    id SERIAL PRIMARY KEY,
    id_mantenimiento INT REFERENCES mantenimientos(id),
    item TEXT,
    estado VARCHAR(20),
    observaciones TEXT
);

CREATE TABLE repuestos_usados (
    id SERIAL PRIMARY KEY,
    id_mantenimiento INT REFERENCES mantenimientos(id),
    id_item INT,
    cantidad_utilizada DECIMAL
);

CREATE TABLE tareas_recurrentes (
    id SERIAL PRIMARY KEY,
    tipo_objeto VARCHAR(20),
    id_objeto INT,
    descripcion TEXT,
    frecuencia_dias INT,
    proxima_fecha DATE,
    responsable INT
);

-- Base de datos: contabilidad
CREATE DATABASE IF NOT EXISTS contabilidad;
\c contabilidad;

CREATE TABLE recibos (
    id SERIAL PRIMARY KEY,
    fecha_emision DATE,
    obra_id INT,
    monto_total DECIMAL,
    concepto TEXT,
    destinatario TEXT,
    firma_digital TEXT,
    usuario_emisor INT,
    estado VARCHAR(30),
    archivo_pdf TEXT
);

CREATE TABLE movimientos_contables (
    id SERIAL PRIMARY KEY,
    fecha DATE,
    tipo_movimiento VARCHAR(20),
    monto DECIMAL,
    concepto TEXT,
    referencia_recibo INT,
    observaciones TEXT
);

-- Base de datos: config
CREATE DATABASE IF NOT EXISTS config;
\c config;

CREATE TABLE configuracion_sistema (
    id SERIAL PRIMARY KEY,
    clave VARCHAR(100) UNIQUE,
    valor TEXT,
    descripcion TEXT,
    ultima_modificacion TIMESTAMP,
    modificado_por INT
);

CREATE TABLE apariencia_usuario (
    id SERIAL PRIMARY KEY,
    usuario_id INT,
    modo_color VARCHAR(20),
    idioma_preferido VARCHAR(10),
    mostrar_notificaciones BOOLEAN,
    tamaño_fuente VARCHAR(10)
);
