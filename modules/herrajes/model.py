from core.database import InventarioDatabaseConnection

class HerrajesModel:
    """
    Modelo de Herrajes que utiliza InventarioDatabaseConnection (hereda de BaseDatabaseConnection) para conexión persistente y segura.
    """
    def __init__(self, db_connection=None):
        self.db = db_connection or InventarioDatabaseConnection()

    def crear_tabla_materiales(self):
        query = """
        IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='materiales' AND xtype='U')
        CREATE TABLE materiales (
            id INT IDENTITY(1,1) PRIMARY KEY,
            codigo VARCHAR(50) NOT NULL,
            descripcion VARCHAR(255),
            cantidad INT NOT NULL,
            ubicacion VARCHAR(100),
            fecha_ingreso DATETIME DEFAULT GETDATE(),
            observaciones TEXT
        );
        """
        self.db.ejecutar_query(query)

    def agregar_material(self, codigo, descripcion, cantidad, ubicacion, observaciones):
        query = """
        INSERT INTO materiales (codigo, descripcion, cantidad, ubicacion, observaciones)
        VALUES (?, ?, ?, ?, ?);
        """
        self.db.ejecutar_query(query, (codigo, descripcion, cantidad, ubicacion, observaciones))

    def obtener_materiales(self):
        query = "SELECT * FROM materiales;"
        return self.db.ejecutar_query(query)

    def actualizar_material(self, id_material, codigo, descripcion, cantidad, ubicacion, observaciones):
        query = """
        UPDATE materiales
        SET codigo = ?, descripcion = ?, cantidad = ?, ubicacion = ?, observaciones = ?
        WHERE id = ?;
        """
        self.db.ejecutar_query(query, (codigo, descripcion, cantidad, ubicacion, observaciones, id_material))

    def eliminar_material(self, id_material):
        query = "DELETE FROM materiales WHERE id = ?;"
        self.db.ejecutar_query(query, (id_material,))

    def reservar_herraje(self, usuario, id_obra, id_herraje, cantidad):
        """
        Reserva cantidad de herraje para una obra, actualiza stock y movimientos, y registra auditoría.
        """
        if cantidad is None or cantidad <= 0:
            raise ValueError("Cantidad inválida")
        stock = self.db.ejecutar_query("SELECT stock_actual FROM herrajes WHERE id_herraje = ?", (id_herraje,))
        if not stock or stock[0][0] is None:
            raise ValueError("Herraje no encontrado")
        if cantidad > stock[0][0]:
            raise ValueError("Stock insuficiente")
        with self.db.transaction(timeout=30, retries=2):
            self.db.ejecutar_query("UPDATE herrajes SET stock_actual = stock_actual - ? WHERE id_herraje = ?", (cantidad, id_herraje))
            res = self.db.ejecutar_query("SELECT cantidad_reservada FROM herrajes_por_obra WHERE id_obra=? AND id_herraje=?", (id_obra, id_herraje))
            if res:
                nueva = res[0][0] + cantidad
                self.db.ejecutar_query("UPDATE herrajes_por_obra SET cantidad_reservada=?, estado='Reservado' WHERE id_obra=? AND id_herraje=?", (nueva, id_obra, id_herraje))
            else:
                self.db.ejecutar_query("INSERT INTO herrajes_por_obra (id_obra, id_herraje, cantidad_reservada, estado) VALUES (?, ?, ?, 'Reservado')", (id_obra, id_herraje, cantidad))
            self.db.ejecutar_query("INSERT INTO movimientos_herrajes (id_herraje, tipo_movimiento, cantidad, fecha, usuario) VALUES (?, 'Egreso', ?, CURRENT_TIMESTAMP, ?)", (id_herraje, cantidad, usuario or ""))
            if usuario:
                self.db.ejecutar_query("INSERT INTO auditorias_sistema (usuario, modulo, accion, fecha) VALUES (?, ?, ?, CURRENT_TIMESTAMP)", (usuario, "Herrajes", f"Reservó {cantidad} del herraje {id_herraje} para obra {id_obra}",))
        return True

    def devolver_herraje(self, usuario, id_obra, id_herraje, cantidad):
        """
        Devuelve cantidad de herraje a inventario, actualiza stock y movimientos, y registra auditoría.
        """
        if cantidad is None or cantidad <= 0:
            raise ValueError("Cantidad inválida")
        self.db.ejecutar_query("UPDATE herrajes SET stock_actual = stock_actual + ? WHERE id_herraje = ?", (cantidad, id_herraje))
        res = self.db.ejecutar_query("SELECT cantidad_reservada FROM herrajes_por_obra WHERE id_obra=? AND id_herraje=?", (id_obra, id_herraje))
        if not res or res[0][0] is None or res[0][0] == 0:
            raise ValueError("No hay reserva previa")
        cantidad_reservada = res[0][0]
        if cantidad > cantidad_reservada:
            raise ValueError("No se puede devolver más de lo reservado")
        with self.db.transaction(timeout=30, retries=2):
            nueva = cantidad_reservada - cantidad
            if nueva > 0:
                self.db.ejecutar_query("UPDATE herrajes_por_obra SET cantidad_reservada=?, estado='Reservado' WHERE id_obra=? AND id_herraje=?", (nueva, id_obra, id_herraje))
            else:
                self.db.ejecutar_query("UPDATE herrajes_por_obra SET cantidad_reservada=0, estado='Liberado' WHERE id_obra=? AND id_herraje=?", (id_obra, id_herraje))
            self.db.ejecutar_query("INSERT INTO movimientos_herrajes (id_herraje, tipo_movimiento, cantidad, fecha, usuario) VALUES (?, 'Ingreso', ?, CURRENT_TIMESTAMP, ?)", (id_herraje, cantidad, usuario or ""))
            if usuario:
                self.db.ejecutar_query("INSERT INTO auditorias_sistema (usuario, modulo, accion, fecha) VALUES (?, ?, ?, CURRENT_TIMESTAMP)", (usuario, "Herrajes", f"Devolvió {cantidad} del herraje {id_herraje} de la obra {id_obra}",))
        return True

    def ajustar_stock_herraje(self, usuario, id_herraje, nueva_cantidad):
        """
        Ajusta el stock de un herraje a un nuevo valor, registra movimiento y auditoría.
        """
        if nueva_cantidad < 0:
            raise ValueError("Cantidad inválida")
        stock_ant = self.db.ejecutar_query("SELECT stock_actual FROM herrajes WHERE id_herraje = ?", (id_herraje,))
        if not stock_ant or stock_ant[0][0] is None:
            raise ValueError("Herraje no encontrado")
        stock_anterior = stock_ant[0][0]
        with self.db.transaction(timeout=30, retries=2):
            self.db.ejecutar_query("UPDATE herrajes SET stock_actual = ? WHERE id_herraje = ?", (nueva_cantidad, id_herraje))
            self.db.ejecutar_query("INSERT INTO movimientos_herrajes (id_herraje, tipo_movimiento, cantidad, fecha, usuario) VALUES (?, 'Ajuste', ?, CURRENT_TIMESTAMP, ?)", (id_herraje, abs(nueva_cantidad - stock_anterior), usuario or ""))
            if usuario:
                self.db.ejecutar_query("INSERT INTO auditorias_sistema (usuario, modulo, accion, fecha) VALUES (?, ?, ?, CURRENT_TIMESTAMP)", (usuario, "Herrajes", f"Ajustó stock del herraje {id_herraje} de {stock_anterior} a {nueva_cantidad}",))
        return True

    def obtener_estado_pedido_por_obra(self, id_obra):
        """
        Devuelve el estado del pedido de herrajes para una obra dada.
        Retorna un string: 'pendiente', 'pedido', 'en proceso', 'entregado', etc.
        """
        try:
            query = "SELECT estado FROM pedidos_herrajes WHERE id_obra = ? ORDER BY fecha DESC LIMIT 1"
            resultado = self.db.ejecutar_query(query, (id_obra,))
            if resultado and resultado[0]:
                return resultado[0][0]
            return 'pendiente'
        except Exception as e:
            return f"Error: {e}"
