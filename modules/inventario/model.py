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

    def registrar_movimiento(self, id_item, cantidad, tipo, referencia):
        query = """
        INSERT INTO movimientos_stock (id_item, cantidad, tipo_movimiento, fecha, referencia)
        VALUES (?, ?, ?, GETDATE(), ?)
        """
        self.db.ejecutar_query(query, (id_item, cantidad, tipo, str(referencia)))

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
            query = "SELECT id, codigo, nombre, tipo_material, unidad, stock_actual, stock_minimo, ubicacion, descripcion, qr, imagen_referencia FROM inventario_perfiles WHERE codigo = ?"
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
        query_reserva = "SELECT id_item, cantidad_reservada, estado FROM reservas_materiales WHERE id = ?"
        reserva = self.db.ejecutar_query(query_reserva, (id_reserva,))
        if not reserva:
            return False  # No se encontró la reserva
        id_item, cantidad_reservada, estado = reserva[0]
        if estado != 'activa':
            return False  # Solo se puede entregar reservas activas
        # Validar stock suficiente
        query_stock = "SELECT stock_actual FROM inventario_perfiles WHERE id = ?"
        stock_row = self.db.ejecutar_query(query_stock, (id_item,))
        if not stock_row or stock_row[0][0] < cantidad_reservada:
            return False  # Stock insuficiente
        # Actualizar el stock del ítem
        query_actualizar_stock = "UPDATE inventario_perfiles SET stock_actual = stock_actual - ? WHERE id = ?"
        self.db.ejecutar_query(query_actualizar_stock, (cantidad_reservada, id_item))
        # Cambiar el estado de la reserva a 'entregada'
        query_actualizar_reserva = "UPDATE reservas_materiales SET estado = 'entregada' WHERE id = ?"
        self.db.ejecutar_query(query_actualizar_reserva, (id_reserva,))
        # Registrar auditoría si está disponible (formato unificado)
        auditoria_model = getattr(self, 'auditoria_model', None)
        if auditoria_model:
            usuario = getattr(self, 'usuario_actual', None)
            ip = usuario.get('ip', '') if usuario else ''
            auditoria_model.registrar_evento(
                usuario,
                'inventario',
                f'Reserva entregada: {id_reserva}',
                ip_origen=ip,
                resultado='éxito'
            )
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
        Ejemplo de descripción: "Marco 64 Euro-Design 60 Mar-Rob/Rob Pres. 5,8 m."
        Devuelve: tipo, acabado, longitud
        """
        tipo = ""
        acabado = ""
        longitud = ""
        # Buscar tipo (ej: "Marco 64")
        tipo_match = re.search(r"^(.*?)\s*Euro-Design", descripcion, re.IGNORECASE)
        if tipo_match:
            tipo = tipo_match.group(1).strip()
        # Buscar acabado (ej: "Mar-Rob/Rob")
        acabado_match = re.search(r"Euro-Design\s*\d+\s*([\w\-/]+)", descripcion, re.IGNORECASE)
        if acabado_match:
            acabado = acabado_match.group(1).strip()
        # Buscar longitud (ej: "5,8 m" o "5.8 m")
        longitud_match = re.search(r"([\d,.]+)\s*m", descripcion)
        if longitud_match:
            longitud = longitud_match.group(1).replace(",", ".")
        return tipo, acabado, longitud

    def actualizar_qr_y_campos_por_descripcion(self):
        """
        Recorre todos los perfiles, extrae tipo, acabado y longitud de la descripción,
        y actualiza la tabla inventario_perfiles con esos datos y el QR.
        """
        perfiles = self.db.ejecutar_query("SELECT id, codigo, descripcion FROM inventario_perfiles")
        for perfil in perfiles:
            id_item = perfil[0]
            codigo = perfil[1]
            descripcion = perfil[2] or ""
            tipo, acabado, longitud = self.extraer_datos_descripcion(descripcion)
            qr = f"QR-{codigo}" if codigo else None
            query = """
                UPDATE inventario_perfiles
                SET tipo = ?, acabado = ?, longitud = ?, qr = ?
                WHERE id = ?
            """
            self.db.ejecutar_query(query, (tipo, acabado, longitud, qr, id_item))

    def test_y_corregir_campos_tipo_acabado_longitud(self):
        """
        Verifica cuántos registros de inventario_perfiles tienen tipo, acabado o longitud vacíos o nulos.
        Si encuentra registros incompletos, los corrige usando extraer_datos_descripcion y actualiza la tabla.
        Devuelve la cantidad de registros corregidos.
        """
        perfiles = self.db.ejecutar_query("SELECT id, descripcion, tipo, acabado, longitud, codigo FROM inventario_perfiles")
        faltantes = []
        for perfil in perfiles:
            id_item, descripcion, tipo, acabado, longitud, codigo = perfil
            if not tipo or not acabado or not longitud:
                tipo_n, acabado_n, longitud_n = self.extraer_datos_descripcion(descripcion or "")
                qr = f"QR-{codigo}" if codigo else None
                query = """
                    UPDATE inventario_perfiles
                    SET tipo = ?, acabado = ?, longitud = ?, qr = ?
                    WHERE id = ?
                """
                self.db.ejecutar_query(query, (tipo_n, acabado_n, longitud_n, qr, id_item))
                faltantes.append(id_item)
        return len(faltantes)

    def obtener_stock_item(self, id_item):
        """Devuelve el stock actual de un ítem/material por su id."""
        query = "SELECT stock_actual FROM inventario_perfiles WHERE id = ?"
        res = self.db.ejecutar_query(query, (id_item,))
        return res[0][0] if res and len(res[0]) > 0 else 0

    def reservar_stock(self, id_item, cantidad, id_obra):
        """Reserva stock de un ítem/material, actualizando stock_actual y registrando la reserva."""
        stock_actual = self.obtener_stock_item(id_item)
        if stock_actual < cantidad:
            raise Exception("Stock insuficiente para reservar.")
        # Descontar stock
        query_update = "UPDATE inventario_perfiles SET stock_actual = stock_actual - ? WHERE id = ?"
        self.db.ejecutar_query(query_update, (cantidad, id_item))
        # Registrar reserva
        query_reserva = """
        INSERT INTO reservas_materiales (id_item, cantidad_reservada, referencia_obra, estado)
        VALUES (?, ?, ?, ?)
        """
        self.db.ejecutar_query(query_reserva, (id_item, cantidad, str(id_obra), 'activa'))
        return True
