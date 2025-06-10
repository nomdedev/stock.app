-- =====================
-- DB OBRAS
-- =====================
-- obras
IF COL_LENGTH('obras', 'nombre') IS NULL ALTER TABLE obras ADD nombre VARCHAR(100);
IF COL_LENGTH('obras', 'cliente') IS NULL ALTER TABLE obras ADD cliente VARCHAR(100);
IF COL_LENGTH('obras', 'estado') IS NULL ALTER TABLE obras ADD estado VARCHAR(50);
IF COL_LENGTH('obras', 'fecha_compra') IS NULL ALTER TABLE obras ADD fecha_compra DATE;
IF COL_LENGTH('obras', 'cantidad_aberturas') IS NULL ALTER TABLE obras ADD cantidad_aberturas INT;
IF COL_LENGTH('obras', 'pago_completo') IS NULL ALTER TABLE obras ADD pago_completo BIT;
IF COL_LENGTH('obras', 'pago_porcentaje') IS NULL ALTER TABLE obras ADD pago_porcentaje DECIMAL(5,2);
IF COL_LENGTH('obras', 'monto_usd') IS NULL ALTER TABLE obras ADD monto_usd DECIMAL(18,2);
IF COL_LENGTH('obras', 'monto_ars') IS NULL ALTER TABLE obras ADD monto_ars DECIMAL(18,2);
IF COL_LENGTH('obras', 'fecha_medicion') IS NULL ALTER TABLE obras ADD fecha_medicion DATE;
IF COL_LENGTH('obras', 'dias_entrega') IS NULL ALTER TABLE obras ADD dias_entrega INT DEFAULT 90;
IF COL_LENGTH('obras', 'fecha_entrega') IS NULL ALTER TABLE obras ADD fecha_entrega DATE;
IF COL_LENGTH('obras', 'usuario_creador') IS NULL ALTER TABLE obras ADD usuario_creador INT;
IF COL_LENGTH('obras', 'rowversion') IS NULL ALTER TABLE obras ADD rowversion ROWVERSION NOT NULL;

-- cronograma_obras
IF COL_LENGTH('cronograma_obras', 'id_obra') IS NULL ALTER TABLE cronograma_obras ADD id_obra INT;
IF COL_LENGTH('cronograma_obras', 'etapa') IS NULL ALTER TABLE cronograma_obras ADD etapa VARCHAR(50);
IF COL_LENGTH('cronograma_obras', 'fecha_programada') IS NULL ALTER TABLE cronograma_obras ADD fecha_programada DATE;
IF COL_LENGTH('cronograma_obras', 'fecha_realizada') IS NULL ALTER TABLE cronograma_obras ADD fecha_realizada DATE;
IF COL_LENGTH('cronograma_obras', 'observaciones') IS NULL ALTER TABLE cronograma_obras ADD observaciones TEXT;
IF COL_LENGTH('cronograma_obras', 'responsable') IS NULL ALTER TABLE cronograma_obras ADD responsable INT;
IF COL_LENGTH('cronograma_obras', 'estado') IS NULL ALTER TABLE cronograma_obras ADD estado VARCHAR(30);
