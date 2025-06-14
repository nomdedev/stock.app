-- Script para la base de datos: obras
-- Contiene tablas de obras, cronograma, aberturas, etapas y entregas

-- =====================
-- TABLA obras
-- =====================
IF OBJECT_ID('obras', 'U') IS NOT NULL DROP TABLE obras;
CREATE TABLE obras (
    id INT IDENTITY(1,1) PRIMARY KEY,
    nombre NVARCHAR(100),
    usuario_creador INT,
    cliente NVARCHAR(100),
    estado NVARCHAR(30),
    fecha_medicion DATETIME,
    fecha_entrega DATETIME
);

-- =====================
-- TABLA cronograma_obras
-- =====================
IF OBJECT_ID('cronograma_obras', 'U') IS NOT NULL DROP TABLE cronograma_obras;
CREATE TABLE cronograma_obras (
    id INT IDENTITY(1,1) PRIMARY KEY,
    id_obra INT FOREIGN KEY REFERENCES obras(id) ON DELETE CASCADE,
    fecha DATETIME,
    estado NVARCHAR(30)
);

-- =====================
-- TABLA aberturas
-- =====================
IF OBJECT_ID('aberturas', 'U') IS NOT NULL DROP TABLE aberturas;
CREATE TABLE aberturas (
    id INT IDENTITY(1,1) PRIMARY KEY,
    fecha_entrega_estimada DATE,
    id_obra INT FOREIGN KEY REFERENCES obras(id)
);

-- =====================
-- TABLA etapas_fabricacion
-- =====================
IF OBJECT_ID('etapas_fabricacion', 'U') IS NOT NULL DROP TABLE etapas_fabricacion;
CREATE TABLE etapas_fabricacion (
    id INT IDENTITY(1,1) PRIMARY KEY,
    id_abertura INT FOREIGN KEY REFERENCES aberturas(id) ON DELETE CASCADE,
    observaciones NVARCHAR(MAX)
);

-- =====================
-- TABLA entregas_obras
-- =====================
IF OBJECT_ID('entregas_obras', 'U') IS NOT NULL DROP TABLE entregas_obras;
CREATE TABLE entregas_obras (
    id INT IDENTITY(1,1) PRIMARY KEY,
    id_obra INT FOREIGN KEY REFERENCES obras(id) ON DELETE CASCADE,
    fecha_entrega DATETIME,
    firma_receptor NVARCHAR(255)
);

-- =====================
-- TABLA checklist_entrega
-- =====================
IF OBJECT_ID('checklist_entrega', 'U') IS NOT NULL DROP TABLE checklist_entrega;
CREATE TABLE checklist_entrega (
    id INT IDENTITY(1,1) PRIMARY KEY,
    id_entrega INT FOREIGN KEY REFERENCES entregas_obras(id) ON DELETE CASCADE,
    observaciones NVARCHAR(MAX)
);
