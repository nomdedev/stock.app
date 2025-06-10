class ProduccionModel:
    def __init__(self, db_connection):
        self.db = db_connection

    def obtener_etapas(self):
        query = "SELECT * FROM etapas_fabricacion"
        return self.db.ejecutar_query(query)

    def agregar_etapa(self, datos):
        """Agrega una nueva etapa de fabricación."""
        try:
            query = """
            INSERT INTO etapas_fabricacion (id_abertura, etapa, estado, fecha_inicio, fecha_fin)
            VALUES (?, ?, ?, ?, ?)
            """
            self.db.ejecutar_query(query, datos)
        except Exception as e:
            print(f"Error al agregar etapa: {e}")
            raise

    def obtener_aberturas(self):
        query = "SELECT * FROM aberturas"
        return self.db.ejecutar_query(query)

    def actualizar_estado_abertura(self, id_abertura, nuevo_estado):
        query = "UPDATE aberturas SET estado_general = ? WHERE id = ?"
        self.db.ejecutar_query(query, (nuevo_estado, id_abertura))

    def obtener_etapas_por_abertura(self, id_abertura):
        query = "SELECT * FROM etapas_fabricacion WHERE id_abertura = ?"
        return self.db.ejecutar_query(query, (id_abertura,))

    def finalizar_etapa(self, id_etapa, fecha_fin, tiempo_real):
        """Finaliza una etapa de fabricación."""
        try:
            query = """
            UPDATE etapas_fabricacion
            SET estado = 'finalizada', fecha_fin = ?, tiempo_real = ?
            WHERE id = ?
            """
            self.db.ejecutar_query(query, (fecha_fin, tiempo_real, id_etapa))
        except Exception as e:
            print(f"Error al finalizar etapa: {e}")
            raise

    def obtener_etapas_fabricacion(self):
        query = """
        SELECT id_abertura, etapa, estado
        FROM etapas_fabricacion
        WHERE estado != 'finalizada'
        """
        return self.db.ejecutar_query(query)

    def iniciar_etapa_fabricacion(self, id_abertura, etapa, fecha_inicio):
        query = "UPDATE etapas_fabricacion SET estado = 'en proceso', fecha_inicio = ? WHERE id = ? AND etapa = ?"
        self.db.ejecutar_query(query, (fecha_inicio, id_abertura, etapa))

    def finalizar_etapa_fabricacion(self, id_abertura, etapa, fecha_fin):
        query = "UPDATE etapas_fabricacion SET estado = 'finalizada', fecha_fin = ? WHERE id = ? AND etapa = ?"
        self.db.ejecutar_query(query, (fecha_fin, id_abertura, etapa))

    def obtener_estado_abertura(self, id_abertura):
        query = "SELECT etapa, estado FROM etapas_fabricacion WHERE id = ?"
        return self.db.ejecutar_query(query, (id_abertura,))

    def obtener_abertura_por_id(self, id_abertura):
        query = "SELECT * FROM aberturas WHERE id = ?"
        return self.db.ejecutar_query(query, (id_abertura,))

    def eliminar_etapa_fabricacion(self, id_etapa):
        query = "DELETE FROM etapas_fabricacion WHERE id = ?"
        self.db.ejecutar_query(query, (id_etapa,))

    def pedidos_realizados_y_pagados(self, id_obra):
        """
        Devuelve True si todos los pedidos de Inventario, Vidrios y Herrajes para la obra están realizados y pagados.
        """
        from modules.inventario.model import InventarioModel
        from modules.vidrios.model import VidriosModel
        from modules.herrajes.model import HerrajesModel
        from modules.contabilidad.model import ContabilidadModel
        inventario_model = InventarioModel(self.db)
        vidrios_model = VidriosModel(self.db)
        herrajes_model = HerrajesModel(self.db)
        contabilidad_model = ContabilidadModel(self.db)
        pedidos_inv = inventario_model.obtener_pedidos_por_obra(id_obra) or []
        pedidos_vid = vidrios_model.obtener_pedidos_por_obra(id_obra) if hasattr(vidrios_model, 'obtener_pedidos_por_obra') else []
        pedidos_her = herrajes_model.obtener_pedidos_por_obra(id_obra) or []
        for pedido in pedidos_inv:
            id_pedido = pedido[0]
            estado_pago = contabilidad_model.obtener_estado_pago_pedido(id_pedido, 'Inventario')
            if estado_pago != 'pagado':
                return False
        for pedido in pedidos_vid:
            id_pedido = pedido[0]
            estado_pago = contabilidad_model.obtener_estado_pago_pedido(id_pedido, 'Vidrios')
            if estado_pago != 'pagado':
                return False
        for pedido in pedidos_her:
            id_pedido = pedido[0]
            estado_pago = contabilidad_model.obtener_estado_pago_pedido(id_pedido, 'Herrajes')
            if estado_pago != 'pagado':
                return False
        return True
