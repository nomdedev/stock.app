-- Script para crear la tabla auditorias_sistema
CREATE TABLE auditorias_sistema (
    id_auditoria INT IDENTITY(1,1) PRIMARY KEY,
    usuario NVARCHAR(255) NOT NULL,
    accion NVARCHAR(255) NOT NULL,
    fecha DATETIME DEFAULT GETDATE(),
    detalles NVARCHAR(MAX)
);
