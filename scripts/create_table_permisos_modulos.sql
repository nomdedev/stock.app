-- Tabla de permisos por usuario y módulo (flexible y escalable)
CREATE TABLE permisos_modulos (
    id SERIAL PRIMARY KEY,
    id_usuario INT REFERENCES usuarios(id),
    modulo VARCHAR(50) NOT NULL,
    puede_ver BOOLEAN DEFAULT TRUE,
    puede_modificar BOOLEAN DEFAULT FALSE,
    puede_aprobar BOOLEAN DEFAULT FALSE,
    fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    creado_por INT REFERENCES usuarios(id)
);

-- Ejemplo de consulta para obtener los permisos de un usuario:
-- SELECT modulo, puede_ver, puede_modificar, puede_aprobar FROM permisos_modulos WHERE id_usuario = ?;

-- Si se desea manejar permisos por rol, se recomienda:
-- 1. Crear tabla roles (id, nombre)
-- 2. Crear tabla roles_permisos (id, id_rol, modulo, puede_ver, puede_modificar, puede_aprobar)
-- 3. Relacionar usuarios con roles (columna id_rol en usuarios)
-- 4. Al consultar permisos, combinar los de usuario y rol (el de usuario tiene prioridad)
