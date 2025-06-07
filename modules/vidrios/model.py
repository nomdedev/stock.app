class VidriosModel:
    def __init__(self, db_connection):
        self.db = db_connection

    def obtener_vidrios(self):
        query = "SELECT * FROM vidrios"
        return self.db.ejecutar_query(query)

    def agregar_vidrio(self, datos):
        query = """
        INSERT INTO vidrios (tipo, ancho, alto, cantidad, proveedor, fecha_entrega)
        VALUES (?, ?, ?, ?, ?, ?)
        """
        self.db.ejecutar_query(query, datos)

    def asignar_a_obra(self, id_vidrio, id_obra):
        query = """
        INSERT INTO vidrios_obras (id_vidrio, id_obra)
        VALUES (?, ?)
        """
        self.db.ejecutar_query(query, (id_vidrio, id_obra))

    def reservar_vidrio(self, usuario, id_obra, id_vidrio, cantidad):
        if cantidad <= 0:
            raise ValueError("Cantidad inválida")
        with self.db.transaction():
            stock = self.db.ejecutar_query("SELECT stock_actual FROM vidrios WHERE id_vidrio = ?", (id_vidrio,))
            if not stock:
                raise ValueError("Vidrio no encontrado")
            stock_actual = stock[0][0]
            if cantidad > stock_actual:
                raise ValueError("Stock insuficiente")
            self.db.ejecutar_query("UPDATE vidrios SET stock_actual = stock_actual - ? WHERE id_vidrio = ?", (cantidad, id_vidrio))
            reserva = self.db.ejecutar_query("SELECT cantidad_reservada FROM vidrios_por_obra WHERE id_obra = ? AND id_vidrio = ?", (id_obra, id_vidrio))
            if reserva:
                nueva_cantidad = reserva[0][0] + cantidad
                self.db.ejecutar_query("UPDATE vidrios_por_obra SET cantidad_reservada = ?, estado = 'Reservado' WHERE id_obra = ? AND id_vidrio = ?", (nueva_cantidad, id_obra, id_vidrio))
            else:
                self.db.ejecutar_query("INSERT INTO vidrios_por_obra (id_obra, id_vidrio, cantidad_reservada, estado) VALUES (?, ?, ?, 'Reservado')", (id_obra, id_vidrio, cantidad))
            self.db.ejecutar_query("INSERT INTO movimientos_vidrios (id_vidrio, tipo_movimiento, cantidad, fecha, usuario) VALUES (?, 'Egreso', ?, CURRENT_TIMESTAMP, ?)", (id_vidrio, cantidad, usuario or ""))
            self.db.ejecutar_query("INSERT INTO auditorias_sistema (usuario, modulo, accion, fecha) VALUES (?, ?, ?, CURRENT_TIMESTAMP)", (usuario, "Vidrios", f"Reservó {cantidad} del vidrio {id_vidrio} para obra {id_obra}"))
        return True

    def devolver_vidrio(self, usuario, id_obra, id_vidrio, cantidad):
        if cantidad <= 0:
            raise ValueError("Cantidad inválida")
        with self.db.transaction():
            self.db.ejecutar_query("UPDATE vidrios SET stock_actual = stock_actual + ? WHERE id_vidrio = ?", (cantidad, id_vidrio))
            reserva = self.db.ejecutar_query("SELECT cantidad_reservada FROM vidrios_por_obra WHERE id_obra = ? AND id_vidrio = ?", (id_obra, id_vidrio))
            if not reserva:
                raise ValueError("No hay reserva previa")
            cantidad_reservada = reserva[0][0]
            if cantidad > cantidad_reservada:
                raise ValueError("No se puede devolver más de lo reservado")
            nueva_cantidad = cantidad_reservada - cantidad
            self.db.ejecutar_query("UPDATE vidrios_por_obra SET cantidad_reservada = ?, estado = 'Reservado' WHERE id_obra = ? AND id_vidrio = ?", (nueva_cantidad, id_obra, id_vidrio))
            self.db.ejecutar_query("INSERT INTO movimientos_vidrios (id_vidrio, tipo_movimiento, cantidad, fecha, usuario) VALUES (?, 'Ingreso', ?, CURRENT_TIMESTAMP, ?)", (id_vidrio, cantidad, usuario or ""))
            self.db.ejecutar_query("INSERT INTO auditorias_sistema (usuario, modulo, accion, fecha) VALUES (?, ?, ?, CURRENT_TIMESTAMP)", (usuario, "Vidrios", f"Devolvió {cantidad} del vidrio {id_vidrio} de la obra {id_obra}"))
        return True

    def ajustar_stock_vidrio(self, usuario, id_vidrio, nueva_cantidad):
        if nueva_cantidad < 0:
            raise ValueError("Cantidad inválida")
        with self.db.transaction():
            stock = self.db.ejecutar_query("SELECT stock_actual FROM vidrios WHERE id_vidrio = ?", (id_vidrio,))
            if not stock:
                raise ValueError("Vidrio no encontrado")
            stock_anterior = stock[0][0]
            self.db.ejecutar_query("UPDATE vidrios SET stock_actual = ? WHERE id_vidrio = ?", (nueva_cantidad, id_vidrio))
            self.db.ejecutar_query("INSERT INTO movimientos_vidrios (id_vidrio, tipo_movimiento, cantidad, fecha, usuario) VALUES (?, 'Ajuste', ?, CURRENT_TIMESTAMP, ?)", (id_vidrio, abs(nueva_cantidad - stock_anterior), usuario or ""))
            self.db.ejecutar_query("INSERT INTO auditorias_sistema (usuario, modulo, accion, fecha) VALUES (?, ?, ?, CURRENT_TIMESTAMP)", (usuario, "Vidrios", f"Ajustó stock del vidrio {id_vidrio} de {stock_anterior} a {nueva_cantidad}"))
        return True
