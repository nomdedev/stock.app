-- =====================
-- DB INVENTARIO (incluye obras)
-- =====================
-- inventario_perfiles
IF COL_LENGTH('inventario_perfiles', 'codigo') IS NULL ALTER TABLE inventario_perfiles ADD codigo VARCHAR(100);
IF COL_LENGTH('inventario_perfiles', 'descripcion') IS NULL ALTER TABLE inventario_perfiles ADD descripcion VARCHAR(255);
IF COL_LENGTH('inventario_perfiles', 'tipo') IS NULL ALTER TABLE inventario_perfiles ADD tipo VARCHAR(50);
IF COL_LENGTH('inventario_perfiles', 'acabado') IS NULL ALTER TABLE inventario_perfiles ADD acabado VARCHAR(50);
IF COL_LENGTH('inventario_perfiles', 'numero') IS NULL ALTER TABLE inventario_perfiles ADD numero VARCHAR(50);
IF COL_LENGTH('inventario_perfiles', 'vs') IS NULL ALTER TABLE inventario_perfiles ADD vs VARCHAR(50);
IF COL_LENGTH('inventario_perfiles', 'proveedor') IS NULL ALTER TABLE inventario_perfiles ADD proveedor VARCHAR(100);
IF COL_LENGTH('inventario_perfiles', 'longitud') IS NULL ALTER TABLE inventario_perfiles ADD longitud DECIMAL(18,2);
IF COL_LENGTH('inventario_perfiles', 'ancho') IS NULL ALTER TABLE inventario_perfiles ADD ancho DECIMAL(18,2);
IF COL_LENGTH('inventario_perfiles', 'alto') IS NULL ALTER TABLE inventario_perfiles ADD alto DECIMAL(18,2);
IF COL_LENGTH('inventario_perfiles', 'necesarias') IS NULL ALTER TABLE inventario_perfiles ADD necesarias DECIMAL(18,2);
IF COL_LENGTH('inventario_perfiles', 'stock') IS NULL ALTER TABLE inventario_perfiles ADD stock DECIMAL(18,2);
IF COL_LENGTH('inventario_perfiles', 'faltan') IS NULL ALTER TABLE inventario_perfiles ADD faltan DECIMAL(18,2);
IF COL_LENGTH('inventario_perfiles', 'ped_min') IS NULL ALTER TABLE inventario_perfiles ADD ped_min DECIMAL(18,2);
IF COL_LENGTH('inventario_perfiles', 'emba') IS NULL ALTER TABLE inventario_perfiles ADD emba VARCHAR(50);
IF COL_LENGTH('inventario_perfiles', 'pedido') IS NULL ALTER TABLE inventario_perfiles ADD pedido VARCHAR(100);
IF COL_LENGTH('inventario_perfiles', 'importe') IS NULL ALTER TABLE inventario_perfiles ADD importe DECIMAL(18,2);

-- materiales_por_obra
IF COL_LENGTH('materiales_por_obra', 'id_obra') IS NULL ALTER TABLE materiales_por_obra ADD id_obra INT;
IF COL_LENGTH('materiales_por_obra', 'id_item') IS NULL ALTER TABLE materiales_por_obra ADD id_item INT;
IF COL_LENGTH('materiales_por_obra', 'cantidad_necesaria') IS NULL ALTER TABLE materiales_por_obra ADD cantidad_necesaria DECIMAL(18,2);
IF COL_LENGTH('materiales_por_obra', 'cantidad_reservada') IS NULL ALTER TABLE materiales_por_obra ADD cantidad_reservada DECIMAL(18,2);
IF COL_LENGTH('materiales_por_obra', 'estado') IS NULL ALTER TABLE materiales_por_obra ADD estado VARCHAR(30);

-- obras (debe estar en inventario)
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
