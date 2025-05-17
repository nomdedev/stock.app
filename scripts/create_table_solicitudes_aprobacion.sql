-- Tabla para registrar solicitudes de acciones que requieren aprobación de supervisor
CREATE TABLE solicitudes_aprobacion (
    id SERIAL PRIMARY KEY,
    id_usuario INT REFERENCES usuarios(id),
    modulo VARCHAR(50) NOT NULL,
    tipo_accion VARCHAR(30) NOT NULL, -- agregar, editar, eliminar
    datos_json TEXT NOT NULL,         -- datos de la acción en formato JSON
    estado VARCHAR(20) DEFAULT 'pendiente', -- pendiente, aprobada, rechazada
    fecha_solicitud TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    fecha_resolucion TIMESTAMP,
    resuelto_por INT REFERENCES usuarios(id),
    observaciones TEXT
);

-- Ejemplo de inserción de solicitud:
-- INSERT INTO solicitudes_aprobacion (id_usuario, modulo, tipo_accion, datos_json)
-- VALUES (?, 'inventario', 'editar', '{...}');
