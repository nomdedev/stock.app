-- Script de sincronización para la base de datos 'inventario'

-- Crear tablas faltantes (estructura básica, ajustar tipos según modelo si es necesario)
IF NOT EXISTS (SELECT * FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_NAME = 'inventario_items')
BEGIN
    CREATE TABLE inventario_items (
        id INT IDENTITY(1,1) PRIMARY KEY,
        codigo NVARCHAR(50),
        nombre NVARCHAR(100),
        tipo NVARCHAR(50),
        stock_actual DECIMAL(18,2), -- Unificado a DECIMAL
        stock_minimo DECIMAL(18,2), -- Unificado a DECIMAL
        ubicacion NVARCHAR(100),
        descripcion NVARCHAR(255),
        qr NVARCHAR(100),
        imagen_referencia NVARCHAR(255),
        rowversion ROWVERSION
    );
END
GO

-- Sincronizar tabla detalle_pedido
IF OBJECT_ID('detalle_pedido', 'U') IS NULL
BEGIN
    CREATE TABLE detalle_pedido (
        id INT PRIMARY KEY IDENTITY(1,1),
        id_pedido INT, -- FK a pedidos.id
        id_perfil INT, -- FK a inventario_perfiles.id
        cantidad DECIMAL(10, 2) NOT NULL,
        precio_unitario DECIMAL(10, 2) NOT NULL,
        subtotal DECIMAL(10, 2),
        CONSTRAINT FK_detalle_pedido_pedido FOREIGN KEY (id_pedido) REFERENCES pedidos(id) ON DELETE CASCADE,
        CONSTRAINT FK_detalle_pedido_perfil FOREIGN KEY (id_perfil) REFERENCES inventario_perfiles(id) ON DELETE CASCADE
    );
    PRINT 'Tabla detalle_pedido creada.';
END
ELSE
BEGIN
    PRINT 'Tabla detalle_pedido ya existe. Verificando columnas...';
    IF COL_LENGTH('detalle_pedido', 'id_item') IS NOT NULL AND COL_LENGTH('detalle_pedido', 'id_perfil') IS NULL
    BEGIN
        EXEC sp_rename 'detalle_pedido.id_item', 'id_perfil', 'COLUMN';
        PRINT 'Columna id_item renombrada a id_perfil en detalle_pedido.';
    END
    ELSE IF COL_LENGTH('detalle_pedido', 'id_perfil') IS NULL
    BEGIN
        ALTER TABLE detalle_pedido ADD id_perfil INT;
        PRINT 'Columna id_perfil añadida a detalle_pedido.';
    END
    IF NOT EXISTS (SELECT * FROM sys.foreign_keys WHERE name = 'FK_detalle_pedido_perfil' AND parent_object_id = OBJECT_ID('detalle_pedido'))
    BEGIN
        ALTER TABLE detalle_pedido ADD CONSTRAINT FK_detalle_pedido_perfil FOREIGN KEY (id_perfil) REFERENCES inventario_perfiles(id) ON DELETE CASCADE;
        PRINT 'FK FK_detalle_pedido_perfil creada en detalle_pedido.';
    END
END
GO

IF NOT EXISTS (SELECT * FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_NAME = 'inventario_perfiles')
BEGIN
    CREATE TABLE inventario_perfiles (
        id INT IDENTITY(1,1) PRIMARY KEY,
        codigo NVARCHAR(50),
        nombre NVARCHAR(100),
        tipo_material NVARCHAR(50),
        unidad NVARCHAR(20),
        stock_actual DECIMAL(18,2), -- Unificado a DECIMAL
        stock_minimo DECIMAL(18,2), -- Unificado a DECIMAL
        ubicacion NVARCHAR(100),
        descripcion NVARCHAR(255),
        qr NVARCHAR(100),
        imagen_referencia NVARCHAR(255),
        -- Columnas adicionales de la importación y uso
        tipo NVARCHAR(100),
        acabado NVARCHAR(100),
        numero NVARCHAR(50),
        vs NVARCHAR(50),
        proveedor NVARCHAR(100),
        longitud NVARCHAR(50), -- Podría ser DECIMAL si se usa para cálculos
        ancho NVARCHAR(50),   -- Podría ser DECIMAL
        alto NVARCHAR(50),    -- Podría ser DECIMAL
        necesarias DECIMAL(18,2),
        stock DECIMAL(18,2), -- Parece redundante con stock_actual
        faltan DECIMAL(18,2),
        ped_min DECIMAL(18,2),
        emba NVARCHAR(50),
        pedido NVARCHAR(100),
        importe DECIMAL(18,2),
        fecha_creacion DATETIME DEFAULT GETDATE(),
        fecha_actualizacion DATETIME DEFAULT GETDATE(),
        rowversion ROWVERSION
    );
END
GO

IF NOT EXISTS (SELECT * FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_NAME = 'movimientos_stock')
BEGIN
    CREATE TABLE movimientos_stock (
        id INT IDENTITY(1,1) PRIMARY KEY,
        id_perfil INT, -- Corregido a id_perfil (asumiendo que referencia a inventario_perfiles)
        tipo_movimiento NVARCHAR(50),
        cantidad DECIMAL(18,2), -- Unificado a DECIMAL
        fecha DATETIME DEFAULT GETDATE(),
        usuario NVARCHAR(100),
        referencia NVARCHAR(255), -- Aumentado tamaño para detalle/referencia
        detalle NVARCHAR(255) -- Mantenido por si se usa, aunque 'referencia' podría ser suficiente
    );
END
GO

IF NOT EXISTS (SELECT * FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_NAME = 'reservas_materiales')
BEGIN
    CREATE TABLE reservas_materiales (
        id INT PRIMARY KEY IDENTITY(1,1),
        id_perfil INT, -- FK a inventario_perfiles.id
        id_pedido INT, 
        id_obra INT,
        cantidad_reservada DECIMAL(10, 2) NOT NULL,
        fecha_reserva DATETIME DEFAULT GETDATE(),
        estado_reserva VARCHAR(50) DEFAULT 'activa',
        CONSTRAINT FK_reservas_materiales_perfil FOREIGN KEY (id_perfil) REFERENCES inventario_perfiles(id) ON DELETE SET NULL, -- Cambiado a SET NULL
        CONSTRAINT FK_reservas_materiales_pedido FOREIGN KEY (id_pedido) REFERENCES pedidos(id) ON DELETE NO ACTION,
        CONSTRAINT FK_reservas_materiales_obra FOREIGN KEY (id_obra) REFERENCES obras(id) ON DELETE NO ACTION
    );
    PRINT 'Tabla reservas_materiales creada.';
END
ELSE
BEGIN
    PRINT 'Tabla reservas_materiales ya existe. Verificando columnas...';
    IF COL_LENGTH('reservas_materiales', 'id_item') IS NOT NULL AND COL_LENGTH('reservas_materiales', 'id_perfil') IS NULL
    BEGIN
        EXEC sp_rename 'reservas_materiales.id_item', 'id_perfil', 'COLUMN';
        PRINT 'Columna id_item renombrada a id_perfil en reservas_materiales.';
    END
    ELSE IF COL_LENGTH('reservas_materiales', 'id_perfil') IS NULL
    BEGIN
        ALTER TABLE reservas_materiales ADD id_perfil INT;
        PRINT 'Columna id_perfil añadida a reservas_materiales.';
    END
    -- Eliminar la FK anterior si existe y tiene un ON DELETE CASCADE problemático
    IF EXISTS (SELECT * FROM sys.foreign_keys WHERE name = 'FK_reservas_materiales_perfil' AND parent_object_id = OBJECT_ID('reservas_materiales'))
    BEGIN
        DECLARE @constraint_name NVARCHAR(256)
        SELECT @constraint_name = name FROM sys.foreign_keys WHERE name = 'FK_reservas_materiales_perfil' AND parent_object_id = OBJECT_ID('reservas_materiales')
        IF @constraint_name IS NOT NULL
        BEGIN
            -- Verificar si la FK existente tiene ON DELETE CASCADE
            DECLARE @delete_referential_action_desc NVARCHAR(60)
            SELECT @delete_referential_action_desc = delete_referential_action_desc 
            FROM sys.foreign_keys 
            WHERE name = @constraint_name AND parent_object_id = OBJECT_ID('reservas_materiales');

            IF @delete_referential_action_desc = 'CASCADE'
            BEGIN
                EXEC('ALTER TABLE reservas_materiales DROP CONSTRAINT ' + @constraint_name);
                PRINT 'FK FK_reservas_materiales_perfil con ON DELETE CASCADE eliminada de reservas_materiales.';
                -- Volver a crear la FK con ON DELETE SET NULL
                ALTER TABLE reservas_materiales ADD CONSTRAINT FK_reservas_materiales_perfil FOREIGN KEY (id_perfil) REFERENCES inventario_perfiles(id) ON DELETE SET NULL;
                PRINT 'FK FK_reservas_materiales_perfil recreada con ON DELETE SET NULL en reservas_materiales.';
            END
            ELSE IF @delete_referential_action_desc != 'SET_NULL' -- Si no es CASCADE y tampoco es SET_NULL, la recreamos
            BEGIN
                 EXEC('ALTER TABLE reservas_materiales DROP CONSTRAINT ' + @constraint_name);
                 ALTER TABLE reservas_materiales ADD CONSTRAINT FK_reservas_materiales_perfil FOREIGN KEY (id_perfil) REFERENCES inventario_perfiles(id) ON DELETE SET NULL;
                 PRINT 'FK FK_reservas_materiales_perfil existente actualizada a ON DELETE SET NULL en reservas_materiales.';
            END
        END
    END
    ELSE IF COL_LENGTH('reservas_materiales', 'id_perfil') IS NOT NULL -- Si la columna existe pero no la FK
    BEGIN
        ALTER TABLE reservas_materiales ADD CONSTRAINT FK_reservas_materiales_perfil FOREIGN KEY (id_perfil) REFERENCES inventario_perfiles(id) ON DELETE SET NULL;
        PRINT 'FK FK_reservas_materiales_perfil creada con ON DELETE SET NULL en reservas_materiales.';
    END
END
GO

IF NOT EXISTS (SELECT * FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_NAME = 'perfiles_por_obra')
BEGIN
    CREATE TABLE perfiles_por_obra (
        id INT IDENTITY(1,1) PRIMARY KEY,
        id_obra INT,
        id_perfil INT, -- Correcto, referencia a inventario_perfiles
        cantidad_reservada DECIMAL(18,2), -- Unificado a DECIMAL
        estado NVARCHAR(50)
    );
END
GO

IF NOT EXISTS (SELECT * FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_NAME = 'materiales')
BEGIN
    CREATE TABLE materiales (
        id INT IDENTITY(1,1) PRIMARY KEY,
        codigo NVARCHAR(50),
        descripcion NVARCHAR(255),
        cantidad DECIMAL(18,2), -- Unificado a DECIMAL
        ubicacion NVARCHAR(100),
        fecha_ingreso DATETIME DEFAULT GETDATE(), -- Añadido basado en BD actual
        observaciones NVARCHAR(255),
        rowversion ROWVERSION
    );
END
GO

IF NOT EXISTS (SELECT * FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_NAME = 'obras')
BEGIN
    CREATE TABLE obras (
        id INT IDENTITY(1,1) PRIMARY KEY,
        nombre NVARCHAR(100),
        cliente NVARCHAR(100),
        estado NVARCHAR(50),
        fecha DATETIME,
        cantidad_aberturas INT,
        pago_completo BIT,
        pago_porcentaje DECIMAL(5,2),
        monto_usd DECIMAL(18,2),
        monto_ars DECIMAL(18,2),
        fecha_medicion DATETIME,
        dias_entrega INT,
        fecha_entrega DATETIME,
        usuario_creador NVARCHAR(100),
        rowversion ROWVERSION
    );
END
GO

IF NOT EXISTS (SELECT * FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_NAME = 'cronograma_obras')
BEGIN
    CREATE TABLE cronograma_obras (
        id INT IDENTITY(1,1) PRIMARY KEY,
        id_obra INT,
        etapa NVARCHAR(100),
        fecha_inicio DATETIME,
        fecha_fin DATETIME,
        estado NVARCHAR(50),
        fecha_programada DATETIME,
        fecha_realizada DATETIME,
        observaciones NVARCHAR(255),
        responsable NVARCHAR(100)
    );
END
GO

-- Sincronizar tabla materiales_por_obra
IF OBJECT_ID('materiales_por_obra', 'U') IS NULL
BEGIN
    CREATE TABLE materiales_por_obra (
        id INT PRIMARY KEY IDENTITY(1,1),
        id_obra INT, -- FK a obras.id
        id_perfil INT, -- FK a inventario_perfiles.id
        cantidad_requerida DECIMAL(10, 2),
        cantidad_utilizada DECIMAL(10, 2),
        CONSTRAINT FK_materiales_obra_obra FOREIGN KEY (id_obra) REFERENCES obras(id) ON DELETE CASCADE,
        CONSTRAINT FK_materiales_obra_perfil FOREIGN KEY (id_perfil) REFERENCES inventario_perfiles(id) ON DELETE CASCADE
    );
    PRINT 'Tabla materiales_por_obra creada.';
END
ELSE
BEGIN
    PRINT 'Tabla materiales_por_obra ya existe. Verificando columnas...';
    IF COL_LENGTH('materiales_por_obra', 'id_item') IS NOT NULL AND COL_LENGTH('materiales_por_obra', 'id_perfil') IS NULL
    BEGIN
        EXEC sp_rename 'materiales_por_obra.id_item', 'id_perfil', 'COLUMN';
        PRINT 'Columna id_item renombrada a id_perfil en materiales_por_obra.';
    END
    ELSE IF COL_LENGTH('materiales_por_obra', 'id_perfil') IS NULL
    BEGIN
        ALTER TABLE materiales_por_obra ADD id_perfil INT;
        PRINT 'Columna id_perfil añadida a materiales_por_obra.';
    END
    IF NOT EXISTS (SELECT * FROM sys.foreign_keys WHERE name = 'FK_materiales_obra_perfil' AND parent_object_id = OBJECT_ID('materiales_por_obra'))
    BEGIN
        ALTER TABLE materiales_por_obra ADD CONSTRAINT FK_materiales_obra_perfil FOREIGN KEY (id_perfil) REFERENCES inventario_perfiles(id) ON DELETE CASCADE;
        PRINT 'FK FK_materiales_obra_perfil creada en materiales_por_obra.';
    END
END
GO

IF NOT EXISTS (SELECT * FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_NAME = 'pedidos')
BEGIN
    CREATE TABLE pedidos (
        id INT IDENTITY(1,1) PRIMARY KEY,
        id_obra INT,
        fecha_emision DATETIME DEFAULT GETDATE(),
        estado NVARCHAR(50),
        total_estimado DECIMAL(18,2),
        usuario NVARCHAR(100),
        rowversion ROWVERSION
    );
END
GO

IF NOT EXISTS (SELECT * FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_NAME = 'pedidos_compra')
BEGIN
    CREATE TABLE pedidos_compra (
        id INT IDENTITY(1,1) PRIMARY KEY,
        id_obra INT,
        fecha DATETIME DEFAULT GETDATE(),
        estado NVARCHAR(50),
        usuario NVARCHAR(100),
        total_usd DECIMAL(18,2),
        total_ars DECIMAL(18,2),
        rowversion ROWVERSION
    );
END
GO

IF NOT EXISTS (SELECT * FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_NAME = 'pedidos_por_obra')
BEGIN
    CREATE TABLE pedidos_por_obra (
        id INT IDENTITY(1,1) PRIMARY KEY,
        id_pedido INT,
        id_obra INT,
        id_item INT, -- Revisar si debe ser id_perfil
        tipo_item NVARCHAR(50),
        cantidad_requerida DECIMAL(18,2) -- Unificado a DECIMAL
    );
END
GO

-- Agregar columnas faltantes a tablas existentes y ajustar tipos si es necesario

-- Para inventario_perfiles (asegurar columnas de la BD actual y tipos)
IF COL_LENGTH('inventario_perfiles', 'tipo') IS NULL ALTER TABLE inventario_perfiles ADD tipo NVARCHAR(100);
IF COL_LENGTH('inventario_perfiles', 'acabado') IS NULL ALTER TABLE inventario_perfiles ADD acabado NVARCHAR(100);
IF COL_LENGTH('inventario_perfiles', 'numero') IS NULL ALTER TABLE inventario_perfiles ADD numero NVARCHAR(50);
IF COL_LENGTH('inventario_perfiles', 'vs') IS NULL ALTER TABLE inventario_perfiles ADD vs NVARCHAR(50);
IF COL_LENGTH('inventario_perfiles', 'proveedor') IS NULL ALTER TABLE inventario_perfiles ADD proveedor NVARCHAR(100);
IF COL_LENGTH('inventario_perfiles', 'longitud') IS NULL ALTER TABLE inventario_perfiles ADD longitud NVARCHAR(50);
IF COL_LENGTH('inventario_perfiles', 'ancho') IS NULL ALTER TABLE inventario_perfiles ADD ancho NVARCHAR(50);
IF COL_LENGTH('inventario_perfiles', 'alto') IS NULL ALTER TABLE inventario_perfiles ADD alto NVARCHAR(50);
IF COL_LENGTH('inventario_perfiles', 'necesarias') IS NULL ALTER TABLE inventario_perfiles ADD necesarias DECIMAL(18,2);
ELSE ALTER TABLE inventario_perfiles ALTER COLUMN necesarias DECIMAL(18,2);
IF COL_LENGTH('inventario_perfiles', 'stock') IS NULL ALTER TABLE inventario_perfiles ADD stock DECIMAL(18,2);
ELSE ALTER TABLE inventario_perfiles ALTER COLUMN stock DECIMAL(18,2); -- Parece redundante con stock_actual
IF COL_LENGTH('inventario_perfiles', 'faltan') IS NULL ALTER TABLE inventario_perfiles ADD faltan DECIMAL(18,2);
ELSE ALTER TABLE inventario_perfiles ALTER COLUMN faltan DECIMAL(18,2);
IF COL_LENGTH('inventario_perfiles', 'ped_min') IS NULL ALTER TABLE inventario_perfiles ADD ped_min DECIMAL(18,2);
ELSE ALTER TABLE inventario_perfiles ALTER COLUMN ped_min DECIMAL(18,2);
IF COL_LENGTH('inventario_perfiles', 'emba') IS NULL ALTER TABLE inventario_perfiles ADD emba NVARCHAR(50);
IF COL_LENGTH('inventario_perfiles', 'pedido') IS NULL ALTER TABLE inventario_perfiles ADD pedido NVARCHAR(100);
IF COL_LENGTH('inventario_perfiles', 'importe') IS NULL ALTER TABLE inventario_perfiles ADD importe DECIMAL(18,2);
ELSE ALTER TABLE inventario_perfiles ALTER COLUMN importe DECIMAL(18,2);
IF COL_LENGTH('inventario_perfiles', 'fecha_creacion') IS NULL ALTER TABLE inventario_perfiles ADD fecha_creacion DATETIME DEFAULT GETDATE();
IF COL_LENGTH('inventario_perfiles', 'fecha_actualizacion') IS NULL ALTER TABLE inventario_perfiles ADD fecha_actualizacion DATETIME DEFAULT GETDATE();
IF COL_LENGTH('inventario_perfiles', 'rowversion') IS NULL ALTER TABLE inventario_perfiles ADD rowversion ROWVERSION;
-- Ajustar tipos de stock_actual y stock_minimo si existen y son INT
IF EXISTS (SELECT 1 FROM INFORMATION_SCHEMA.COLUMNS WHERE TABLE_NAME = 'inventario_perfiles' AND COLUMN_NAME = 'stock_actual' AND DATA_TYPE = 'int')
    ALTER TABLE inventario_perfiles ALTER COLUMN stock_actual DECIMAL(18,2);
IF EXISTS (SELECT 1 FROM INFORMATION_SCHEMA.COLUMNS WHERE TABLE_NAME = 'inventario_perfiles' AND COLUMN_NAME = 'stock_minimo' AND DATA_TYPE = 'int')
    ALTER TABLE inventario_perfiles ALTER COLUMN stock_minimo DECIMAL(18,2);
GO

-- Para movimientos_stock
IF COL_LENGTH('movimientos_stock', 'id_perfil') IS NULL AND COL_LENGTH('movimientos_stock', 'id_item') IS NOT NULL
BEGIN
    -- Renombrar id_item a id_perfil si existe y id_perfil no
    EXEC sp_rename 'movimientos_stock.id_item', 'id_perfil', 'COLUMN';
END
ELSE IF COL_LENGTH('movimientos_stock', 'id_perfil') IS NULL
    ALTER TABLE movimientos_stock ADD id_perfil INT; -- Asumiendo que referencia a inventario_perfiles
IF EXISTS (SELECT 1 FROM INFORMATION_SCHEMA.COLUMNS WHERE TABLE_NAME = 'movimientos_stock' AND COLUMN_NAME = 'cantidad' AND DATA_TYPE = 'int')
    ALTER TABLE movimientos_stock ALTER COLUMN cantidad DECIMAL(18,2);
IF COL_LENGTH('movimientos_stock', 'referencia') IS NULL ALTER TABLE movimientos_stock ADD referencia NVARCHAR(255);
ELSE IF EXISTS (SELECT 1 FROM INFORMATION_SCHEMA.COLUMNS WHERE TABLE_NAME = 'movimientos_stock' AND COLUMN_NAME = 'referencia' AND CHARACTER_MAXIMUM_LENGTH < 255)
    ALTER TABLE movimientos_stock ALTER COLUMN referencia NVARCHAR(255);
GO

-- Sincronizar tabla movimientos_stock
-- (Ya se maneja el renombramiento de id_item a id_perfil y la adición de id_perfil si no existe en la versión anterior del script)
-- Asegurar la FK a inventario_perfiles
IF OBJECT_ID('movimientos_stock', 'U') IS NOT NULL
BEGIN
    IF COL_LENGTH('movimientos_stock', 'id_perfil') IS NOT NULL AND NOT EXISTS (SELECT * FROM sys.foreign_keys WHERE name = 'FK_movimientos_stock_perfil' AND parent_object_id = OBJECT_ID('movimientos_stock'))
    BEGIN
        ALTER TABLE movimientos_stock ADD CONSTRAINT FK_movimientos_stock_perfil FOREIGN KEY (id_perfil) REFERENCES inventario_perfiles(id) ON DELETE CASCADE;
        PRINT 'FK FK_movimientos_stock_perfil creada en movimientos_stock.';
    END
END
GO

-- Sincronizar tabla reservas_materiales
IF OBJECT_ID('reservas_materiales', 'U') IS NULL
BEGIN
    CREATE TABLE reservas_materiales (
        id INT PRIMARY KEY IDENTITY(1,1),
        id_perfil INT, -- FK a inventario_perfiles.id
        id_pedido INT, 
        id_obra INT,
        cantidad_reservada DECIMAL(10, 2) NOT NULL,
        fecha_reserva DATETIME DEFAULT GETDATE(),
        estado_reserva VARCHAR(50) DEFAULT 'activa',
        CONSTRAINT FK_reservas_materiales_perfil FOREIGN KEY (id_perfil) REFERENCES inventario_perfiles(id) ON DELETE SET NULL, -- Cambiado a SET NULL
        CONSTRAINT FK_reservas_materiales_pedido FOREIGN KEY (id_pedido) REFERENCES pedidos(id) ON DELETE NO ACTION,
        CONSTRAINT FK_reservas_materiales_obra FOREIGN KEY (id_obra) REFERENCES obras(id) ON DELETE NO ACTION
    );
    PRINT 'Tabla reservas_materiales creada.';
END
ELSE
BEGIN
    PRINT 'Tabla reservas_materiales ya existe. Verificando columnas...';
    IF COL_LENGTH('reservas_materiales', 'id_item') IS NOT NULL AND COL_LENGTH('reservas_materiales', 'id_perfil') IS NULL
    BEGIN
        EXEC sp_rename 'reservas_materiales.id_item', 'id_perfil', 'COLUMN';
        PRINT 'Columna id_item renombrada a id_perfil en reservas_materiales.';
    END
    ELSE IF COL_LENGTH('reservas_materiales', 'id_perfil') IS NULL
    BEGIN
        ALTER TABLE reservas_materiales ADD id_perfil INT;
        PRINT 'Columna id_perfil añadida a reservas_materiales.';
    END
    -- Eliminar la FK anterior si existe y tiene un ON DELETE CASCADE problemático
    IF EXISTS (SELECT * FROM sys.foreign_keys WHERE name = 'FK_reservas_materiales_perfil' AND parent_object_id = OBJECT_ID('reservas_materiales'))
    BEGIN
        DECLARE @constraint_name NVARCHAR(256)
        SELECT @constraint_name = name FROM sys.foreign_keys WHERE name = 'FK_reservas_materiales_perfil' AND parent_object_id = OBJECT_ID('reservas_materiales')
        IF @constraint_name IS NOT NULL
        BEGIN
            -- Verificar si la FK existente tiene ON DELETE CASCADE
            DECLARE @delete_referential_action_desc NVARCHAR(60)
            SELECT @delete_referential_action_desc = delete_referential_action_desc 
            FROM sys.foreign_keys 
            WHERE name = @constraint_name AND parent_object_id = OBJECT_ID('reservas_materiales');

            IF @delete_referential_action_desc = 'CASCADE'
            BEGIN
                EXEC('ALTER TABLE reservas_materiales DROP CONSTRAINT ' + @constraint_name);
                PRINT 'FK FK_reservas_materiales_perfil con ON DELETE CASCADE eliminada de reservas_materiales.';
                -- Volver a crear la FK con ON DELETE SET NULL
                ALTER TABLE reservas_materiales ADD CONSTRAINT FK_reservas_materiales_perfil FOREIGN KEY (id_perfil) REFERENCES inventario_perfiles(id) ON DELETE SET NULL;
                PRINT 'FK FK_reservas_materiales_perfil recreada con ON DELETE SET NULL en reservas_materiales.';
            END
            ELSE IF @delete_referential_action_desc != 'SET_NULL' -- Si no es CASCADE y tampoco es SET_NULL, la recreamos
            BEGIN
                 EXEC('ALTER TABLE reservas_materiales DROP CONSTRAINT ' + @constraint_name);
                 ALTER TABLE reservas_materiales ADD CONSTRAINT FK_reservas_materiales_perfil FOREIGN KEY (id_perfil) REFERENCES inventario_perfiles(id) ON DELETE SET NULL;
                 PRINT 'FK FK_reservas_materiales_perfil existente actualizada a ON DELETE SET NULL en reservas_materiales.';
            END
        END
    END
    ELSE IF COL_LENGTH('reservas_materiales', 'id_perfil') IS NOT NULL -- Si la columna existe pero no la FK
    BEGIN
        ALTER TABLE reservas_materiales ADD CONSTRAINT FK_reservas_materiales_perfil FOREIGN KEY (id_perfil) REFERENCES inventario_perfiles(id) ON DELETE SET NULL;
        PRINT 'FK FK_reservas_materiales_perfil creada con ON DELETE SET NULL en reservas_materiales.';
    END
END
GO

-- Para reservas_materiales
IF COL_LENGTH('reservas_materiales', 'codigo_reserva') IS NULL ALTER TABLE reservas_materiales ADD codigo_reserva NVARCHAR(100);
IF COL_LENGTH('reservas_materiales', 'fecha_reserva') IS NULL ALTER TABLE reservas_materiales ADD fecha_reserva DATETIME DEFAULT GETDATE();
IF EXISTS (SELECT 1 FROM INFORMATION_SCHEMA.COLUMNS WHERE TABLE_NAME = 'reservas_materiales' AND COLUMN_NAME = 'cantidad_reservada' AND DATA_TYPE = 'int')
    ALTER TABLE reservas_materiales ALTER COLUMN cantidad_reservada DECIMAL(18,2);
-- Considerar renombrar id_item a id_perfil si aplica
GO

-- Para perfiles_por_obra
IF EXISTS (SELECT 1 FROM INFORMATION_SCHEMA.COLUMNS WHERE TABLE_NAME = 'perfiles_por_obra' AND COLUMN_NAME = 'cantidad_reservada' AND DATA_TYPE = 'int')
    ALTER TABLE perfiles_por_obra ALTER COLUMN cantidad_reservada DECIMAL(18,2);
GO

-- Para materiales
IF EXISTS (SELECT 1 FROM INFORMATION_SCHEMA.COLUMNS WHERE TABLE_NAME = 'materiales' AND COLUMN_NAME = 'cantidad' AND DATA_TYPE = 'int')
    ALTER TABLE materiales ALTER COLUMN cantidad DECIMAL(18,2);
IF COL_LENGTH('materiales', 'fecha_ingreso') IS NULL ALTER TABLE materiales ADD fecha_ingreso DATETIME DEFAULT GETDATE();
GO

-- Para materiales_por_obra
IF EXISTS (SELECT 1 FROM INFORMATION_SCHEMA.COLUMNS WHERE TABLE_NAME = 'materiales_por_obra' AND COLUMN_NAME = 'cantidad_necesaria' AND DATA_TYPE = 'int')
    ALTER TABLE materiales_por_obra ALTER COLUMN cantidad_necesaria DECIMAL(18,2);
IF EXISTS (SELECT 1 FROM INFORMATION_SCHEMA.COLUMNS WHERE TABLE_NAME = 'materiales_por_obra' AND COLUMN_NAME = 'cantidad_reservada' AND DATA_TYPE = 'int')
    ALTER TABLE materiales_por_obra ALTER COLUMN cantidad_reservada DECIMAL(18,2);
GO

-- Para detalle_pedido
IF EXISTS (SELECT 1 FROM INFORMATION_SCHEMA.COLUMNS WHERE TABLE_NAME = 'detalle_pedido' AND COLUMN_NAME = 'cantidad' AND DATA_TYPE = 'int')
    ALTER TABLE detalle_pedido ALTER COLUMN cantidad DECIMAL(18,2);
GO

-- Para pedidos_por_obra
IF EXISTS (SELECT 1 FROM INFORMATION_SCHEMA.COLUMNS WHERE TABLE_NAME = 'pedidos_por_obra' AND COLUMN_NAME = 'cantidad_requerida' AND DATA_TYPE = 'int')
    ALTER TABLE pedidos_por_obra ALTER COLUMN cantidad_requerida DECIMAL(18,2);
GO

-- Columnas que ya estaban en el script original para añadir si faltaban (revisadas)
IF COL_LENGTH('movimientos_stock', 'usuario') IS NULL
    ALTER TABLE movimientos_stock ADD usuario NVARCHAR(100);
-- IF COL_LENGTH('reservas_stock', 'id_obra') IS NULL -- Tabla eliminada
--     ALTER TABLE reservas_stock ADD id_obra INT;
IF COL_LENGTH('perfiles_por_obra', 'id_obra') IS NULL
    ALTER TABLE perfiles_por_obra ADD id_obra INT;
IF COL_LENGTH('cronograma_obras', 'fecha_inicio') IS NULL
    ALTER TABLE cronograma_obras ADD fecha_inicio DATETIME;
IF COL_LENGTH('pedidos', 'id_obra') IS NULL
    ALTER TABLE pedidos ADD id_obra INT;
IF COL_LENGTH('pedidos_por_obra', 'id_pedido') IS NULL
    ALTER TABLE pedidos_por_obra ADD id_pedido INT;
GO

-- Considerar eliminar la tabla 'inventario_items' si 'inventario_perfiles' la cubre completamente.
-- PRINT 'Revisar: La tabla inventario_items podría ser redundante con inventario_perfiles. Considere eliminarla tras análisis.';
-- IF OBJECT_ID('inventario_items', 'U') IS NOT NULL
--     DROP TABLE inventario_items;
-- GO

-- Considerar eliminar la columna 'stock' de 'inventario_perfiles' si es redundante con 'stock_actual'.
-- PRINT 'Revisar: La columna inventario_perfiles.stock podría ser redundante con inventario_perfiles.stock_actual. Considere eliminarla tras análisis.';
-- IF COL_LENGTH('inventario_perfiles', 'stock') IS NOT NULL AND COL_LENGTH('inventario_perfiles', 'stock_actual') IS NOT NULL
--     ALTER TABLE inventario_perfiles DROP COLUMN stock;
-- GO

-- Considerar la eliminación de la tabla inventario_items si es redundante
PRINT ''
PRINT '---------------------------------------------------------------------'
PRINT 'ADVERTENCIA: La tabla inventario_items parece ser redundante.'
PRINT 'La tabla principal de inventario es inventario_perfiles.'
PRINT 'Si inventario_items no se utiliza o su funcionalidad ha sido absorbida por inventario_perfiles,'
PRINT 'considere eliminarla manualmente después de una revisión cuidadosa:'
PRINT '-- DROP TABLE inventario_items;'
PRINT 'Asegúrese de que ninguna otra tabla o proceso dependa de inventario_items antes de eliminarla.'
PRINT '---------------------------------------------------------------------'
GO

-- Considerar la eliminación de la columna stock en inventario_perfiles si es redundante
PRINT ''
PRINT '---------------------------------------------------------------------'
PRINT 'ADVERTENCIA: La columna stock en la tabla inventario_perfiles podría ser redundante.'
PRINT 'Existe la columna stock_actual que parece cumplir la misma función.'
PRINT 'Si stock es efectivamente redundante con stock_actual,'
PRINT 'considere eliminarla manualmente después de una revisión cuidadosa:'
PRINT '-- ALTER TABLE inventario_perfiles DROP COLUMN stock;\';
