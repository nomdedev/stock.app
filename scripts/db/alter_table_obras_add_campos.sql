-- Script para agregar campos modernos a la tabla obras en SQL Server
-- Ejecutar en SSMS o Azure Data Studio conectado a la base correspondiente

ALTER TABLE obras ADD cantidad_aberturas INT NULL;
ALTER TABLE obras ADD fecha_compra DATE NULL;
ALTER TABLE obras ADD pago_completo BIT NULL;
ALTER TABLE obras ADD pago_porcentaje DECIMAL(5,2) NULL;
ALTER TABLE obras ADD monto_usd DECIMAL(18,2) NULL;
ALTER TABLE obras ADD monto_ars DECIMAL(18,2) NULL;
ALTER TABLE obras ADD tipo_obra VARCHAR(30) NULL;
ALTER TABLE obras ADD fecha_entrega DATE NULL;
ALTER TABLE obras ADD usuario_creador INT NULL;
-- Si usuario_creador debe ser FK, ejecutar luego:
-- ALTER TABLE obras ADD CONSTRAINT FK_obras_usuario_creador FOREIGN KEY (usuario_creador) REFERENCES usuarios(id);

-- Agregar fecha_medicion (fecha de medición) y dias_entrega (días de entrega, default 90)
ALTER TABLE obras ADD fecha_medicion DATE NULL;
ALTER TABLE obras ADD dias_entrega INT NOT NULL DEFAULT 90;
-- Si ya existe fecha_entrega, se puede actualizar con: UPDATE obras SET fecha_entrega = DATEADD(DAY, dias_entrega, fecha_medicion) WHERE fecha_medicion IS NOT NULL;
