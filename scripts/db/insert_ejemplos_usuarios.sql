-- Script para insertar datos de ejemplo en la tabla 'usuarios'
INSERT INTO usuarios (id, nombre, email, rol, fecha_creacion, activo) VALUES
(1, 'Admin', 'admin@example.com', 'Administrador', '2025-01-01', 1),
(2, 'Usuario1', 'usuario1@example.com', 'Usuario', '2025-02-01', 1),
(3, 'Usuario2', 'usuario2@example.com', 'Usuario', '2025-03-01', 0),
(4, 'Supervisor', 'supervisor@example.com', 'Supervisor', '2025-04-01', 1),
(5, 'UsuarioComun', 'usuariocomun@example.com', 'Usuario', '2025-05-01', 1);

-- Asegurar que el usuario admin tenga permisos para todos los módulos
INSERT INTO permisos_modulos (id_usuario, modulo, puede_ver, puede_modificar, puede_aprobar) 
SELECT 1, modulo, 1, 1, 1 FROM (
    SELECT 'Obras' AS modulo UNION ALL
    SELECT 'Inventario' UNION ALL
    SELECT 'Herrajes' UNION ALL
    SELECT 'Vidrios' UNION ALL
    SELECT 'Pedidos de Materiales' UNION ALL
    SELECT 'Producción' UNION ALL
    SELECT 'Logística' UNION ALL
    SELECT 'Contabilidad' UNION ALL
    SELECT 'Usuarios y Auditoría' UNION ALL
    SELECT 'Configuración'
) AS modulos;
