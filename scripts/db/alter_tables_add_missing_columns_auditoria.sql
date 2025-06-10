-- =====================
-- DB AUDITORIA
-- =====================
-- auditorias_sistema
IF COL_LENGTH('auditorias_sistema', 'fecha_hora') IS NULL ALTER TABLE auditorias_sistema ADD fecha_hora DATETIME DEFAULT GETDATE();
IF COL_LENGTH('auditorias_sistema', 'usuario_id') IS NULL ALTER TABLE auditorias_sistema ADD usuario_id INT;
IF COL_LENGTH('auditorias_sistema', 'modulo_afectado') IS NULL ALTER TABLE auditorias_sistema ADD modulo_afectado VARCHAR(50);
IF COL_LENGTH('auditorias_sistema', 'tipo_evento') IS NULL ALTER TABLE auditorias_sistema ADD tipo_evento VARCHAR(30);
IF COL_LENGTH('auditorias_sistema', 'detalle') IS NULL ALTER TABLE auditorias_sistema ADD detalle TEXT;
IF COL_LENGTH('auditorias_sistema', 'ip_origen') IS NULL ALTER TABLE auditorias_sistema ADD ip_origen VARCHAR(50);
IF COL_LENGTH('auditorias_sistema', 'device_info') IS NULL ALTER TABLE auditorias_sistema ADD device_info TEXT;
IF COL_LENGTH('auditorias_sistema', 'origen_evento') IS NULL ALTER TABLE auditorias_sistema ADD origen_evento VARCHAR(30);

-- errores_sistema
IF COL_LENGTH('errores_sistema', 'fecha_hora') IS NULL ALTER TABLE errores_sistema ADD fecha_hora DATETIME DEFAULT GETDATE();
IF COL_LENGTH('errores_sistema', 'usuario_id') IS NULL ALTER TABLE errores_sistema ADD usuario_id INT;
IF COL_LENGTH('errores_sistema', 'modulo') IS NULL ALTER TABLE errores_sistema ADD modulo VARCHAR(50);
IF COL_LENGTH('errores_sistema', 'descripcion_error') IS NULL ALTER TABLE errores_sistema ADD descripcion_error TEXT;
IF COL_LENGTH('errores_sistema', 'stack_trace') IS NULL ALTER TABLE errores_sistema ADD stack_trace TEXT;
IF COL_LENGTH('errores_sistema', 'ip_origen') IS NULL ALTER TABLE errores_sistema ADD ip_origen VARCHAR(50);
IF COL_LENGTH('errores_sistema', 'origen_evento') IS NULL ALTER TABLE errores_sistema ADD origen_evento VARCHAR(30);
