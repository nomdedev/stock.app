-- Crear tabla pedidos para SQL Server
CREATE TABLE pedidos (
    id INT IDENTITY(1,1) PRIMARY KEY,
    obra NVARCHAR(100) NOT NULL, -- Obra asociada al pedido
    fecha DATE NOT NULL, -- Fecha del pedido
    materiales NVARCHAR(MAX) NOT NULL, -- Lista de materiales solicitados
    observaciones NVARCHAR(MAX), -- Observaciones adicionales
    estado NVARCHAR(20) DEFAULT 'Pendiente' -- Estado del pedido (Pendiente, Aprobado, Rechazado)
);

-- Crear tabla auditoria_pedidos para SQL Server
CREATE TABLE auditoria_pedidos (
    id INT IDENTITY(1,1) PRIMARY KEY,
    pedido_id INT NOT NULL, -- ID del pedido asociado
    accion NVARCHAR(50) NOT NULL, -- Acción realizada (Aprobado, Rechazado, Creado, etc.)
    usuario NVARCHAR(100) NOT NULL, -- Usuario que realizó la acción
    fecha DATETIME DEFAULT GETDATE(), -- Fecha y hora de la acción
    FOREIGN KEY (pedido_id) REFERENCES pedidos(id) ON DELETE CASCADE
);
