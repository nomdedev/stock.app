import pandas as pd  # Asegúrate de tener pandas instalado
from fpdf import FPDF  # Asegúrate de tener fpdf instalado

class InventarioModel:
    def __init__(self, db_connection):
        self.db = db_connection

    def obtener_items(self):
        query = """
        SELECT id, codigo, descripcion, proveedor, necesarias, stock, faltan, ped_min, emba, pedido, importe
        FROM inventario
        """
        return self.db.ejecutar_query(query)

    def obtener_items_por_lotes(self, offset=0, limite=500):
        query = """
        SELECT id, codigo, descripcion, proveedor, necesarias, stock, faltan, ped_min, emba, pedido, importe
        FROM inventario
        ORDER BY id
        OFFSET ? ROWS
        FETCH NEXT ? ROWS ONLY
        """
        return self.db.ejecutar_query(query, (offset, limite))

    def agregar_item(self, datos):
        try:
            query = """
            INSERT INTO inventario_items (codigo, nombre, tipo_material, unidad, stock_actual, stock_minimo, ubicacion, descripcion, qr_code, imagen_referencia)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """
            self.db.ejecutar_query(query, datos)
        except Exception as e:
            print(f"Error al agregar ítem: {e}")
            raise

    def registrar_movimiento(self, datos):
        query = """
        INSERT INTO movimientos_stock (id_item, tipo_movimiento, cantidad, realizado_por, observaciones, referencia)
        VALUES (?, ?, ?, ?, ?, ?)
        """
        self.db.ejecutar_query(query, datos)

    def registrar_reserva(self, datos):
        query = """
        INSERT INTO reservas_stock (id_item, cantidad_reservada, referencia_obra, estado)
        VALUES (?, ?, ?, ?)
        """
        self.db.ejecutar_query(query, datos)

    def obtener_movimientos(self, id_item):
        query = "SELECT * FROM movimientos_stock WHERE id_item = ?"
        return self.db.ejecutar_query(query, (id_item,))

    def obtener_reservas(self, id_item):
        query = "SELECT * FROM reservas_stock WHERE id_item = ?"
        return self.db.ejecutar_query(query, (id_item,))

    def obtener_item_por_codigo(self, codigo):
        try:
            query = "SELECT * FROM inventario_items WHERE codigo = ?"
            return self.db.ejecutar_query(query, (codigo,))
        except Exception as e:
            print(f"Error al obtener ítem por código: {e}")
            return None

    def actualizar_stock(self, id_item, cantidad):
        query = "UPDATE inventario_items SET stock_actual = stock_actual + ? WHERE id = ?"
        self.db.ejecutar_query(query, (cantidad, id_item))

    def obtener_items_bajo_stock(self):
        try:
            query = "SELECT * FROM inventario_items WHERE stock_actual < stock_minimo"
            return self.db.ejecutar_query(query)
        except Exception as e:
            print(f"Error al obtener ítems bajo stock: {e}")
            return []

    def generar_qr(self, id_item):
        query = "SELECT codigo FROM inventario_items WHERE id = ?"
        codigo = self.db.ejecutar_query(query, (id_item,))
        if (codigo and len(codigo[0]) > 0):  # Asegurarse de que el resultado no esté vacío
            qr_code = f"QR-{codigo[0][0]}"
            update_query = "UPDATE inventario_items SET qr_code = ? WHERE id = ?"
            print(f"DEBUG: Ejecutando actualización con qr_code={qr_code} y id_item={id_item}")
            self.db.ejecutar_query(update_query, (qr_code, id_item))
            return qr_code
        print("DEBUG: Código no encontrado o vacío para id_item={id_item}")
        return None

    def exportar_inventario(self, formato):
        query = "SELECT * FROM inventario_items"
        datos = self.db.ejecutar_query(query)

        if formato == "excel":
            df = pd.DataFrame(datos, columns=["ID", "Código", "Nombre", "Tipo", "Unidad", "Stock Actual", "Stock Mínimo", "Ubicación", "Descripción", "QR", "Imagen"])
            df.to_excel("inventario.xlsx", index=False)
            return "Inventario exportado a Excel."

        elif formato == "pdf":
            pdf = FPDF()
            pdf.add_page()
            pdf.set_font("Arial", size=12)
            pdf.cell(200, 10, txt="Inventario General", ln=True, align="C")
            for row in datos:
                pdf.cell(200, 10, txt=str(row), ln=True)
            pdf.output("inventario.pdf")
            return "Inventario exportado a PDF."

        return "Formato no soportado."

    def transformar_reserva_en_entrega(self, id_reserva):
        # Obtener datos de la reserva
        query_reserva = "SELECT id_item, cantidad_reservada FROM reservas_stock WHERE id = ? AND estado = 'activa'"
        reserva = self.db.ejecutar_query(query_reserva, (id_reserva,))

        if not reserva:
            return False  # No se encontró la reserva activa

        id_item, cantidad_reservada = reserva[0]

        # Actualizar el stock del ítem
        query_actualizar_stock = "UPDATE inventario_items SET stock_actual = stock_actual - ? WHERE id = ?"
        self.db.ejecutar_query(query_actualizar_stock, (cantidad_reservada, id_item))

        # Cambiar el estado de la reserva a 'entregada'
        query_actualizar_reserva = "UPDATE reservas_stock SET estado = 'entregada' WHERE id = ?"
        self.db.ejecutar_query(query_actualizar_reserva, (id_reserva,))

        return True
