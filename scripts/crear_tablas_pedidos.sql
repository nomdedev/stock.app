-- Crear tabla pedidos
CREATE TABLE IF NOT EXISTS pedidos (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    obra VARCHAR(100) NOT NULL, -- Obra asociada al pedido
    fecha DATE NOT NULL, -- Fecha del pedido
    materiales TEXT NOT NULL, -- Lista de materiales solicitados
    observaciones TEXT, -- Observaciones adicionales
    estado VARCHAR(20) DEFAULT 'Pendiente' -- Estado del pedido (Pendiente, Aprobado, Rechazado)
);

-- Crear tabla auditoria_pedidos
CREATE TABLE IF NOT EXISTS auditoria_pedidos (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    pedido_id INTEGER NOT NULL, -- ID del pedido asociado
    accion VARCHAR(50) NOT NULL, -- Acción realizada (Aprobado, Rechazado, Creado, etc.)
    usuario VARCHAR(100) NOT NULL, -- Usuario que realizó la acción
    fecha TIMESTAMP DEFAULT CURRENT_TIMESTAMP, -- Fecha y hora de la acción
    FOREIGN KEY (pedido_id) REFERENCES pedidos(id) ON DELETE CASCADE
);
