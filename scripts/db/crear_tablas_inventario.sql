-- Crear tabla inventario_items
CREATE TABLE IF NOT EXISTS inventario_items (
    id SERIAL PRIMARY KEY,
    codigo VARCHAR(20) UNIQUE NOT NULL, -- Código único del ítem
    nombre VARCHAR(100) NOT NULL,       -- Nombre o descripción del ítem
    tipo_material VARCHAR(50),          -- Tipo de material (PVC, aluminio, etc.)
    unidad VARCHAR(20),                 -- Unidad de medida (m, unidad, kg, etc.)
    stock_actual DECIMAL DEFAULT 0,     -- Cantidad actual en stock
    stock_minimo DECIMAL DEFAULT 0,     -- Stock mínimo recomendado
    ubicacion TEXT,                     -- Ubicación física del ítem
    descripcion TEXT,                   -- Descripción o detalles técnicos
    qr_code TEXT,                       -- Código QR generado automáticamente
    imagen_referencia TEXT              -- Ruta o URL de la imagen del ítem
);

ALTER TABLE inventario_items
ADD COLUMN qr TEXT; -- Código QR basado en el código del ítem

-- Crear tabla movimientos_stock
CREATE TABLE IF NOT EXISTS movimientos_stock (
    id SERIAL PRIMARY KEY,
    id_item INT REFERENCES inventario_items(id) ON DELETE CASCADE, -- Relación con inventario_items
    fecha TIMESTAMP DEFAULT CURRENT_TIMESTAMP,                     -- Fecha y hora del movimiento
    tipo_movimiento VARCHAR(20) NOT NULL,                          -- Tipo de movimiento (ingreso, egreso, ajuste, etc.)
    cantidad DECIMAL NOT NULL,                                     -- Cantidad movida
    realizado_por INT,                                             -- Usuario que realizó el movimiento
    observaciones TEXT,                                            -- Detalles o motivo del movimiento
    referencia TEXT                                                -- Referencia a obra, pedido u otro módulo
);

-- Crear tabla reservas_stock
CREATE TABLE IF NOT EXISTS reservas_stock (
    id SERIAL PRIMARY KEY,
    id_item INT REFERENCES inventario_items(id) ON DELETE CASCADE, -- Relación con inventario_items
    fecha_reserva TIMESTAMP DEFAULT CURRENT_TIMESTAMP,             -- Fecha de la reserva
    cantidad_reservada DECIMAL NOT NULL,                           -- Cantidad reservada
    referencia_obra INT,                                           -- Relación con una obra (si aplica)
    estado VARCHAR(20) DEFAULT 'activa'                           -- Estado de la reserva (activa, utilizada, cancelada)
);
