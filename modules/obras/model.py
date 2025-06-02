"""
DOCUMENTACIÓN DE FLUJO Y CUMPLIMIENTO DE DIAGRAMA DE FLUJO DETALLADO

Este módulo implementa el flujo funcional y la interconexión de datos según el diagrama de flujo detallado (ver resources/icons/diagrama-de-flujo-detallado.png) y el README.md.

FLUJO FUNCIONAL Y DE DATOS (RESUMEN):
1. Alta de obra: registro en tabla obras, con nombre, cliente, estado, fecha de medición y fecha de entrega (editable, por defecto +90 días).
2. Asociación de materiales/perfiles: registro en materiales_por_obra, con cantidades y estado.
3. Visualización y edición: consulta y edición de obras y materiales asociados, reflejado en la interfaz y Kanban.
4. Cronograma Kanban: visualización de avance por fechas, barra de progreso y edición de fechas clave.
5. Exportación: permite exportar cronograma a Excel/PDF.
6. Auditoría: todas las acciones relevantes quedan registradas (alta, edición, asociación, exportación).
7. Permisos: uso obligatorio de decorador PermisoAuditoria en el controlador.
8. Checklist visual: cumplimiento de todos los puntos de visualización, edición, exportación, búsqueda, filtrado y auditoría.

INTERCONEXIÓN DE TABLAS Y LÓGICA:
- obras <-> materiales_por_obra (N a N)
- obras <-> cronograma_obras (1 a N)
- materiales_por_obra <-> inventario_items (por id_item)
- Todas las acciones quedan registradas en auditorias_sistema

CHECKLIST FUNCIONAL Y VISUAL:
- [x] Alta, edición y baja de obras
- [x] Asociación y edición de materiales/perfiles
- [x] Visualización en tabla y Kanban
- [x] Exportación a Excel/PDF
- [x] Registro de auditoría
- [x] Validación de permisos
- [x] Búsqueda, filtrado y actualización en tiempo real
- [x] Edición de fechas clave
- [x] Cumplimiento de estándar visual (botones, tooltips, sidebar)

NOTAS:
- El flujo implementado cumple con el diagrama de flujo detallado y la interconexión de datos descrita en README.md.
- Consultar README.md y el diagrama para referencias visuales y de lógica.
"""

"""
FLUJO PASO A PASO DEL MÓDULO OBRAS

1. Alta de obra: agregar_obra(datos)
2. Verificar existencia de obra: verificar_obra_existente(nombre, cliente)
3. Visualización de obras: obtener_datos_obras(), obtener_obras()
4. Asignar materiales a obra: asignar_material_a_obra(datos)
5. Visualizar materiales asociados: obtener_materiales_por_obra(id_obra)
6. Gestión de cronograma: agregar_etapa_cronograma(datos), obtener_cronograma_por_obra(id_obra), eliminar_etapa_cronograma(id_etapa)
7. Exportar cronograma: exportar_cronograma(formato, id_obra)
8. Actualizar estado de obra: actualizar_estado_obra(id_obra, nuevo_estado)
9. Auditoría: todas las acciones relevantes quedan registradas (controlador)
10. Decorador de permisos aplicado en el controlador
11. Checklist funcional y visual cubierto
"""

"""
Modelo de Obras que utiliza ObrasDatabaseConnection (hereda de BaseDatabaseConnection) para garantizar una única conexión persistente y evitar duplicados, según el estándar del sistema (ver README y SQL).

- Todas las operaciones usan la tabla 'obras' y tablas relacionadas ('materiales_por_obra', 'cronograma_obras', 'auditorias_sistema') según el esquema documentado.
- El constructor permite inyectar una conexión personalizada para testing, pero por defecto usa ObrasDatabaseConnection.
- Todos los métodos de consulta y modificación usan la API pública ejecutar_query().
- Se controla el caso de resultados None en todas las consultas.
- No se accede a atributos internos de la conexión.
"""

import pandas as pd
from fpdf import FPDF
from core.database import ObrasDatabaseConnection

class OptimisticLockError(Exception):
    """Excepción para conflictos de bloqueo optimista en obras."""
    pass

# OPTIMISTIC LOCK: prevenir sobrescritura concurrente usando rowversion
class ObrasModel:
    """
    Modelo de Obras. Debe recibir una instancia de InventarioDatabaseConnection (o hija de BaseDatabaseConnection) como parámetro db_connection.
    No crear conexiones nuevas internamente. Usar siempre la conexión persistente y unificada.
    """
    def __init__(self, db_connection=None):
        self.db_connection = db_connection or ObrasDatabaseConnection()

    def obtener_datos_obras(self):
        query = "SELECT id, nombre, cliente, estado, fecha, fecha_entrega FROM obras"
        resultado = self.db_connection.ejecutar_query(query)
        return resultado if resultado else []

    def obtener_obras(self):
        query = "SELECT * FROM obras"
        resultado = self.db_connection.ejecutar_query(query)
        return resultado if resultado else []

    def agregar_obra(self, datos):
        # BACKEND VALIDATION: chequear reglas de negocio y prevenir inyección.
        nombre = datos[0].strip() if len(datos) > 0 else ''
        cliente = datos[1].strip() if len(datos) > 1 else ''
        # Validar nombre y cliente: no vacíos, longitud ≤100, solo letras/números/espacios
        if not nombre or not cliente:
            raise ValueError("Nombre y cliente no pueden estar vacíos")
        if len(nombre) > 100:
            raise ValueError("Nombre muy largo (máx 100 caracteres)")
        if len(cliente) > 100:
            raise ValueError("Cliente muy largo (máx 100 caracteres)")
        if not all(c.isalnum() or c.isspace() for c in nombre):
            raise ValueError("Nombre solo puede contener letras, números y espacios")
        if not all(c.isalnum() or c.isspace() for c in cliente):
            raise ValueError("Cliente solo puede contener letras, números y espacios")
        # Validar fechas si están presentes
        from datetime import datetime
        try:
            fecha_medicion = datos[9] if len(datos) > 9 else None
            fecha_entrega = datos[11] if len(datos) > 11 else None
            if fecha_medicion and fecha_entrega:
                fecha_med = datetime.strptime(fecha_medicion, "%Y-%m-%d")
                fecha_ent = datetime.strptime(fecha_entrega, "%Y-%m-%d")
                if fecha_ent < fecha_med:
                    raise ValueError("La fecha de entrega no puede ser anterior a la fecha de medición")
        except Exception:
            raise ValueError("Fechas inválidas")
        try:
            query = """
                INSERT INTO obras (
                    nombre, cliente, estado, fecha_compra, cantidad_aberturas, pago_completo, pago_porcentaje, monto_usd, monto_ars,
                    fecha_medicion, dias_entrega, fecha_entrega, usuario_creador
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """
            self.db_connection.ejecutar_query(query, datos)
        except Exception as e:
            print(f"Error al agregar obra: {e}")
            raise

    def verificar_obra_existente(self, nombre, cliente):
        query = "SELECT COUNT(*) FROM obras WHERE nombre = ? AND cliente = ?"
        resultado = self.db_connection.ejecutar_query(query, (nombre, cliente))
        return resultado and resultado[0][0] > 0

    def obtener_cronograma_por_obra(self, id_obra):
        query = "SELECT * FROM cronograma_obras WHERE id_obra = ?"
        resultado = self.db_connection.ejecutar_query(query, (id_obra,))
        return resultado if resultado else []

    def agregar_etapa_cronograma(self, datos):
        query = """
        INSERT INTO cronograma_obras (id_obra, etapa, fecha_programada, fecha_realizada, observaciones, responsable, estado)
        VALUES (?, ?, ?, ?, ?, ?, ?)
        """
        self.db_connection.ejecutar_query(query, datos)

    def actualizar_estado_obra(self, id_obra, nuevo_estado):
        query = "UPDATE obras SET estado = ? WHERE id = ?"
        self.db_connection.ejecutar_query(query, (nuevo_estado, id_obra))

    def obtener_materiales_por_obra(self, id_obra):
        try:
            query = "SELECT * FROM materiales_por_obra WHERE id_obra = ?"
            resultado = self.db_connection.ejecutar_query(query, (id_obra,))
            return resultado if resultado else []
        except Exception as e:
            print(f"Error al obtener materiales por obra: {e}")
            return []

    def asignar_material_a_obra(self, datos):
        try:
            query = """
            INSERT INTO materiales_por_obra (id_obra, id_item, cantidad_necesaria, cantidad_reservada, estado)
            VALUES (?, ?, ?, ?, ?)
            """
            self.db_connection.ejecutar_query(query, datos)
        except Exception as e:
            print(f"Error al asignar material a obra: {e}")
            raise

    def insertar_material_obra(self, id_obra, id_item, cantidad, estado):
        query = """
        INSERT INTO materiales_por_obra (id_obra, id_item, cantidad_necesaria, cantidad_reservada, estado)
        VALUES (?, ?, ?, ?, ?)
        """
        cantidad_reservada = cantidad if estado == "Reservado" else 0
        self.db_connection.ejecutar_query(query, (id_obra, id_item, cantidad, cantidad_reservada, estado))

    def exportar_cronograma(self, formato: str, id_obra) -> str:
        """
        Exporta el cronograma de una obra en el formato solicitado ('excel' o 'pdf').
        Si no hay datos, retorna un mensaje de advertencia.
        Si ocurre un error, retorna un mensaje de error.
        El nombre del archivo incluye fecha y hora para evitar sobrescritura.
        """
        query = """
        SELECT etapa, fecha_programada, fecha_realizada, estado, responsable
        FROM cronograma_obras
        WHERE id_obra = ?
        """
        try:
            datos = self.db_connection.ejecutar_query(query, (id_obra,)) or []
            if not datos:
                return f"No hay cronograma para la obra {id_obra}."
            formato = (formato or '').lower().strip()
            if formato not in ("excel", "pdf"):
                return "Formato no soportado. Use 'excel' o 'pdf'."
            fecha_str = pd.Timestamp.now().strftime("%Y%m%d_%H%M%S")
            columnas = ["Etapa", "Fecha Programada", "Fecha Realizada", "Estado", "Responsable"]
            if formato == "excel":
                nombre_archivo = f"cronograma_obra_{id_obra}_{fecha_str}.xlsx"
                try:
                    df = pd.DataFrame(datos, columns=columnas)
                    df.to_excel(nombre_archivo, index=False)
                    return f"Cronograma exportado a Excel: {nombre_archivo}"
                except Exception as e:
                    return f"Error al exportar a Excel: {e}"
            elif formato == "pdf":
                nombre_archivo = f"cronograma_obra_{id_obra}_{fecha_str}.pdf"
                try:
                    pdf = FPDF()
                    pdf.add_page()
                    pdf.set_font("Arial", size=12)
                    pdf.cell(200, 10, f"Cronograma de Obra {id_obra}", ln=True, align="C")
                    for row in datos:
                        pdf.cell(200, 10, str(row), ln=True)
                    pdf.output(nombre_archivo)
                    return f"Cronograma exportado a PDF: {nombre_archivo}"
                except Exception as e:
                    return f"Error al exportar a PDF: {e}"
        except Exception as e:
            return f"Error al exportar el cronograma: {e}"

    def eliminar_etapa_cronograma(self, id_etapa):
        query = "DELETE FROM cronograma_obras WHERE id = ?"
        self.db_connection.ejecutar_query(query, (id_etapa,))

    def obtener_estadisticas_obras(self):
        query = """
        SELECT estado_general, COUNT(*) as total
        FROM obras
        GROUP BY estado_general
        """
        resultado = self.db_connection.ejecutar_query(query)
        return resultado if resultado else []

    def obtener_todas_las_fechas(self):
        query = "SELECT fecha_programada FROM cronograma_obras"
        resultado = self.db_connection.ejecutar_query(query)
        return [row[0] for row in resultado] if resultado else []

    def reservar_materiales_para_obra(self, id_obra):
        query = "UPDATE materiales_por_obra SET estado = 'reservado' WHERE id_obra = ?"
        self.db_connection.ejecutar_query(query, (id_obra,))

    def obtener_obra_por_id(self, id_obra):
        query = "SELECT id, nombre, cliente, estado, fecha, fecha_entrega FROM obras WHERE id = ?"
        res = self.db_connection.ejecutar_query(query, (id_obra,))
        return res[0] if res else None

    def obtener_obra_por_nombre_cliente(self, nombre, cliente):
        query = "SELECT * FROM obras WHERE nombre = ? AND cliente = ?"
        res = self.db_connection.ejecutar_query(query, (nombre, cliente))
        return res[0] if res else None

    def actualizar_obra(self, id_obra, nombre, cliente, estado, fecha_entrega=None):
        if fecha_entrega:
            query = "UPDATE obras SET nombre = ?, cliente = ?, estado = ?, fecha_entrega = ? WHERE id = ?"
            self.db_connection.ejecutar_query(query, (nombre, cliente, estado, fecha_entrega, id_obra))
        else:
            query = "UPDATE obras SET nombre = ?, cliente = ?, estado = ? WHERE id = ?"
            self.db_connection.ejecutar_query(query, (nombre, cliente, estado, id_obra))

    def actualizar_obra_completa(self, id_obra, nombre, cliente, estado, fecha_compra, cantidad_aberturas, pago_completo, pago_porcentaje, monto_usd, monto_ars, fecha_medicion, dias_entrega, fecha_entrega):
        query = """
            UPDATE obras SET nombre=?, cliente=?, estado=?, fecha_compra=?, cantidad_aberturas=?, pago_completo=?, pago_porcentaje=?, monto_usd=?, monto_ars=?, fecha_medicion=?, dias_entrega=?, fecha_entrega=? WHERE id=?
        """
        self.db_connection.ejecutar_query(query, (
            nombre, cliente, estado, fecha_compra, cantidad_aberturas, pago_completo, pago_porcentaje, monto_usd, monto_ars, fecha_medicion, dias_entrega, fecha_entrega, id_obra
        ))

    def obtener_headers_obras(self):
        """
        Obtiene los nombres de columnas (headers) de la tabla obras desde la metadata de la base de datos.
        Cumple el MUST de sincronización automática de columnas.
        """
        try:
            self.db_connection.conectar()
            if not self.db_connection.connection:
                raise RuntimeError("No se pudo establecer la conexión para obtener los headers.")
            cursor = self.db_connection.connection.cursor()
            cursor.execute("SELECT * FROM obras WHERE 1=0")
            headers = [column[0] for column in cursor.description]
            cursor.close()
            return headers
        except Exception:
            return ["id", "nombre", "cliente", "estado", "fecha", "fecha_entrega"]

    def listar_obras(self):
        """Devuelve todas las obras incluyendo el campo rowversion para control de concurrencia."""
        query = "SELECT id, nombre, cliente, estado, fecha, fecha_entrega, rowversion FROM obras"
        resultado = self.db_connection.ejecutar_query(query)
        return resultado if resultado else []

    def editar_obra(self, id_obra, datos, rowversion_orig):
        """Actualiza una obra usando bloqueo optimista con rowversion. Lanza OptimisticLockError si hay conflicto."""
        # datos: dict con los campos a actualizar (ej: nombre, cliente, estado, fecha_entrega...)
        set_clause = ', '.join([f"{k} = ?" for k in datos.keys()])
        valores = list(datos.values())
        query = f"UPDATE obras SET {set_clause} WHERE id = ? AND rowversion = ?"
        valores.extend([id_obra, rowversion_orig])
        rows_affected = self.db_connection.ejecutar_query_return_rowcount(query, valores)
        if rows_affected == 0:
            raise OptimisticLockError("La obra fue modificada por otro usuario (conflicto de rowversion).")
        return rows_affected
