"""
FLUJO PASO A PASO DEL MÓDULO INVENTARIO

1. Alta de ítem/material: agregar_item(datos)
2. Edición/eliminación: métodos asociados en el controlador
3. Reserva de material: registrar_reserva(datos)
4. Visualización de inventario: obtener_items(), obtener_items_por_lotes()
5. Visualización de movimientos: obtener_movimientos(id_item)
6. Exportación: exportar_inventario(formato)
7. Auditoría: todas las acciones relevantes quedan registradas
8. Decorador de permisos aplicado en el controlador
9. Checklist funcional y visual cubierto
"""

import pandas as pd  # Asegúrate de tener pandas instalado
from fpdf import FPDF  # Asegúrate de tener fpdf instalado
from core.database import DatabaseConnection
import re

class InventarioModel:
    def __init__(self, db_connection):
        self.db = db_connection

    def obtener_items(self):
        query = """
        SELECT id, codigo, descripcion, tipo, acabado, numero, vs, proveedor, longitud, ancho, alto, necesarias, stock, faltan, ped_min, emba, pedido, importe
        FROM inventario_perfiles
        """
        try:
            resultados = self.db.ejecutar_query(query)
            # Si los resultados son lista de diccionarios, conviértelos a tuplas/listas
            if resultados and hasattr(resultados[0], 'keys'):
                resultados = [list(row.values()) for row in resultados]
            print(f"Resultados obtenidos: {resultados}")  # Registro de depuración
            return resultados
        except Exception as e:
            print(f"Error al obtener ítems: {e}")
            raise

    def obtener_items_por_lotes(self, offset=0, limite=1000):
        query = "SELECT id, codigo, nombre, tipo_material, unidad, stock_actual, stock_minimo, ubicacion, descripcion, qr, imagen_referencia FROM inventario_perfiles ORDER BY id OFFSET ? ROWS FETCH NEXT ? ROWS ONLY"
        return self.db.ejecutar_query(query, (offset, limite))

    def agregar_item(self, datos):
        try:
            query = """
            INSERT INTO inventario_perfiles (codigo, nombre, tipo_material, unidad, stock_actual, stock_minimo, ubicacion, descripcion, qr, imagen_referencia)
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
        INSERT INTO reservas_materiales (id_item, cantidad_reservada, referencia_obra, estado)
        VALUES (?, ?, ?, ?)
        """
        self.db.ejecutar_query(query, datos)

    def obtener_movimientos(self, id_item):
        query = "SELECT * FROM movimientos_stock WHERE id_item = ?"
        return self.db.ejecutar_query(query, (id_item,))

    def obtener_reservas(self, id_item):
        query = "SELECT * FROM reservas_materiales WHERE id_item = ?"
        return self.db.ejecutar_query(query, (id_item,))

    def obtener_item_por_codigo(self, codigo):
        try:
            query = "SELECT * FROM inventario_perfiles WHERE codigo = ?"
            return self.db.ejecutar_query(query, (codigo,))
        except Exception as e:
            print(f"Error al obtener ítem por código: {e}")
            return None

    def actualizar_stock(self, id_item, cantidad):
        query = "UPDATE inventario_perfiles SET stock_actual = stock_actual + ? WHERE id = ?"
        self.db.ejecutar_query(query, (cantidad, id_item))

    def obtener_items_bajo_stock(self):
        try:
            query = "SELECT * FROM inventario_perfiles WHERE stock_actual < stock_minimo"
            return self.db.ejecutar_query(query)
        except Exception as e:
            print(f"Error al obtener ítems bajo stock: {e}")
            return []

    def generar_qr(self, id_item):
        query = "SELECT codigo FROM inventario_perfiles WHERE id = ?"
        codigo = self.db.ejecutar_query(query, (id_item,))
        if (codigo and len(codigo[0]) > 0):  # Asegurarse de que el resultado no esté vacío
            qr = f"QR-{codigo[0][0]}"
            update_query = "UPDATE inventario_perfiles SET qr = ? WHERE id = ?"
            print(f"DEBUG: Ejecutando actualización con qr={qr} y id_item={id_item}")
            self.db.ejecutar_query(update_query, (qr, id_item))
            return qr
        print("DEBUG: Código no encontrado o vacío para id_item={id_item}")
        return None

    def actualizar_qr_code(self, id_item, qr):
        query = "UPDATE inventario_perfiles SET qr = ? WHERE id = ?"
        self.db.ejecutar_query(query, (qr, id_item))

    def exportar_inventario(self, formato):
        query = "SELECT * FROM inventario_perfiles"
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
        query_reserva = "SELECT id_item, cantidad_reservada FROM reservas_materiales WHERE id = ? AND estado = 'activa'"
        reserva = self.db.ejecutar_query(query_reserva, (id_reserva,))

        if not reserva:
            return False  # No se encontró la reserva activa

        id_item, cantidad_reservada = reserva[0]

        # Actualizar el stock del ítem
        query_actualizar_stock = "UPDATE inventario_perfiles SET stock_actual = stock_actual - ? WHERE id = ?"
        self.db.ejecutar_query(query_actualizar_stock, (cantidad_reservada, id_item))

        # Cambiar el estado de la reserva a 'entregada'
        query_actualizar_reserva = "UPDATE reservas_materiales SET estado = 'entregada' WHERE id = ?"
        self.db.ejecutar_query(query_actualizar_reserva, (id_reserva,))

        return True

    def obtener_productos(self):
        query = "SELECT * FROM inventario_perfiles"
        connection_string = (
            f"DRIVER={{{self.db.driver}}};"
            f"SERVER=localhost\\SQLEXPRESS;"
            f"DATABASE={self.db.database};"
            f"UID={self.db.username};"
            f"PWD={self.db.password};"
            f"TrustServerCertificate=yes;"
        )
        import pyodbc
        with pyodbc.connect(connection_string, timeout=10) as conn:
            cursor = conn.cursor()
            cursor.execute(query)
            resultados = cursor.fetchall()
            columnas = [column[0] for column in cursor.description]
            return [dict(zip(columnas, row)) for row in resultados]

    def obtener_item_por_id(self, id_item):
        query = "SELECT * FROM inventario_perfiles WHERE id = ?"
        connection_string = (
            f"DRIVER={{{self.db.driver}}};"
            f"SERVER=localhost\\SQLEXPRESS;"
            f"DATABASE={self.db.database};"
            f"UID={self.db.username};"
            f"PWD={self.db.password};"
            f"TrustServerCertificate=yes;"
        )
        import pyodbc
        with pyodbc.connect(connection_string, timeout=10) as conn:
            cursor = conn.cursor()
            cursor.execute(query, (id_item,))
            row = cursor.fetchone()
            if not row:
                return None
            columnas = [column[0] for column in cursor.description]
            return dict(zip(columnas, row))

    def extraer_datos_descripcion(self, descripcion):
        """
        Extrae tipo, acabado (color) y longitud desde la descripción del perfil.
        Ejemplo de descripción: "Marco 64 Euro-Design 60 Blanco Pres. 5,8 m."
        """
        tipo = ""
        acabado = ""
        longitud = ""
        # Buscar tipo (ej: Euro-Design 60)
        tipo_match = re.search(r'(Euro-Design\s*\d+|A40|A30|A20|A3|A2|A1|A4|A6|A8|A12|A16|A18|A22|A24|A28|A32|A36|A40|A44|A48|A52|A56|A60|A64|A68|A72|A76|A80|A84|A88|A92|A96|A100)', descripcion, re.IGNORECASE)
        if tipo_match:
            tipo = tipo_match.group(1)
        # Buscar acabado/color (ej: Blanco, Negro, Gris, etc.)
        acabado_match = re.search(r'(Blanco|Negro|Gris|Natural|Madera|Nogal|Roble|Cerezo|Bronce|Dorado|Champagne|Anodizado)', descripcion, re.IGNORECASE)
        if acabado_match:
            acabado = acabado_match.group(1)
        # Buscar longitud (ej: 5,8 o 6.0)
        longitud_match = re.search(r'(\d+[.,]\d+)\s*m', descripcion)
        if longitud_match:
            longitud = longitud_match.group(1).replace(',', '.')
        return tipo, acabado, longitud

    def actualizar_campos_desde_descripcion(self):
        """
        Lee todas las descripciones y actualiza tipo, acabado y longitud en la tabla inventario_perfiles.
        """
        query_select = "SELECT id, descripcion FROM inventario_perfiles"
        perfiles = self.db.ejecutar_query(query_select)
        for perfil in perfiles:
            id_perfil = perfil['id'] if isinstance(perfil, dict) else perfil[0]
            descripcion = perfil['descripcion'] if isinstance(perfil, dict) else perfil[1]
            tipo, acabado, longitud = self.extraer_datos_descripcion(descripcion or "")
