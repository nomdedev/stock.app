-- =====================
-- DB USERS
-- =====================
-- usuarios
IF COL_LENGTH('usuarios', 'nombre') IS NULL ALTER TABLE usuarios ADD nombre VARCHAR(100);
IF COL_LENGTH('usuarios', 'apellido') IS NULL ALTER TABLE usuarios ADD apellido VARCHAR(100);
IF COL_LENGTH('usuarios', 'email') IS NULL ALTER TABLE usuarios ADD email VARCHAR(100);
IF COL_LENGTH('usuarios', 'usuario') IS NULL ALTER TABLE usuarios ADD usuario VARCHAR(50);
IF COL_LENGTH('usuarios', 'password_hash') IS NULL ALTER TABLE usuarios ADD password_hash TEXT;
IF COL_LENGTH('usuarios', 'rol') IS NULL ALTER TABLE usuarios ADD rol VARCHAR(50);
IF COL_LENGTH('usuarios', 'estado') IS NULL ALTER TABLE usuarios ADD estado VARCHAR(20);
IF COL_LENGTH('usuarios', 'fecha_creacion') IS NULL ALTER TABLE usuarios ADD fecha_creacion DATETIME DEFAULT GETDATE();
IF COL_LENGTH('usuarios', 'ultima_conexion') IS NULL ALTER TABLE usuarios ADD ultima_conexion DATETIME;

-- logs_usuarios
IF COL_LENGTH('logs_usuarios', 'usuario_id') IS NULL ALTER TABLE logs_usuarios ADD usuario_id INT;
IF COL_LENGTH('logs_usuarios', 'accion') IS NULL ALTER TABLE logs_usuarios ADD accion TEXT;
IF COL_LENGTH('logs_usuarios', 'modulo') IS NULL ALTER TABLE logs_usuarios ADD modulo VARCHAR(50);
IF COL_LENGTH('logs_usuarios', 'fecha_hora') IS NULL ALTER TABLE logs_usuarios ADD fecha_hora DATETIME DEFAULT GETDATE();
IF COL_LENGTH('logs_usuarios', 'detalle') IS NULL ALTER TABLE logs_usuarios ADD detalle TEXT;
IF COL_LENGTH('logs_usuarios', 'ip_origen') IS NULL ALTER TABLE logs_usuarios ADD ip_origen VARCHAR(100);

-- permisos_modulos
IF COL_LENGTH('permisos_modulos', 'id_usuario') IS NULL ALTER TABLE permisos_modulos ADD id_usuario INT;
IF COL_LENGTH('permisos_modulos', 'modulo') IS NULL ALTER TABLE permisos_modulos ADD modulo VARCHAR(50);
IF COL_LENGTH('permisos_modulos', 'puede_ver') IS NULL ALTER TABLE permisos_modulos ADD puede_ver BIT DEFAULT 1;
IF COL_LENGTH('permisos_modulos', 'puede_modificar') IS NULL ALTER TABLE permisos_modulos ADD puede_modificar BIT DEFAULT 0;
IF COL_LENGTH('permisos_modulos', 'puede_aprobar') IS NULL ALTER TABLE permisos_modulos ADD puede_aprobar BIT DEFAULT 0;
IF COL_LENGTH('permisos_modulos', 'fecha_creacion') IS NULL ALTER TABLE permisos_modulos ADD fecha_creacion DATETIME DEFAULT GETDATE();
IF COL_LENGTH('permisos_modulos', 'creado_por') IS NULL ALTER TABLE permisos_modulos ADD creado_por INT;

-- solicitudes_aprobacion
IF COL_LENGTH('solicitudes_aprobacion', 'id_usuario') IS NULL ALTER TABLE solicitudes_aprobacion ADD id_usuario INT;
IF COL_LENGTH('solicitudes_aprobacion', 'modulo') IS NULL ALTER TABLE solicitudes_aprobacion ADD modulo VARCHAR(50);
IF COL_LENGTH('solicitudes_aprobacion', 'tipo_accion') IS NULL ALTER TABLE solicitudes_aprobacion ADD tipo_accion VARCHAR(30);
IF COL_LENGTH('solicitudes_aprobacion', 'datos_json') IS NULL ALTER TABLE solicitudes_aprobacion ADD datos_json TEXT;
IF COL_LENGTH('solicitudes_aprobacion', 'estado') IS NULL ALTER TABLE solicitudes_aprobacion ADD estado VARCHAR(20) DEFAULT 'pendiente';
IF COL_LENGTH('solicitudes_aprobacion', 'fecha_solicitud') IS NULL ALTER TABLE solicitudes_aprobacion ADD fecha_solicitud DATETIME DEFAULT GETDATE();
IF COL_LENGTH('solicitudes_aprobacion', 'fecha_resolucion') IS NULL ALTER TABLE solicitudes_aprobacion ADD fecha_resolucion DATETIME;
IF COL_LENGTH('solicitudes_aprobacion', 'resuelto_por') IS NULL ALTER TABLE solicitudes_aprobacion ADD resuelto_por INT;
IF COL_LENGTH('solicitudes_aprobacion', 'observaciones') IS NULL ALTER TABLE solicitudes_aprobacion ADD observaciones TEXT;
