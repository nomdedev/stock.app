"""
FLUJO PASO A PASO DEL MÓDULO LOGÍSTICA

1. Programar entrega: programar_entrega(id_obra, fecha_programada, vehiculo_asignado, chofer_asignado)
2. Visualizar entregas y su estado: obtener_datos_entregas(), obtener_entregas(), obtener_entregas_por_estado(estado)
3. Actualizar estado de entrega: actualizar_estado_entrega(id_entrega, nuevo_estado)
4. Checklist de entrega: obtener_checklist_por_entrega(id_entrega), agregar_item_checklist(datos)
5. Registrar firma digital: registrar_firma_entrega(id_entrega, firma_digital)
6. Generar hoja de ruta: generar_hoja_de_ruta(id_vehiculo)
7. Exportar historial y acta de entrega: exportar_historial_entregas(formato), exportar_acta_entrega(id_entrega)
8. Eliminar entrega: eliminar_entrega(id_entrega)
9. Estadísticas de entregas: obtener_estadisticas_entregas()
10. Auditoría: todas las acciones relevantes quedan registradas (controlador)
11. Decorador de permisos aplicado en el controlador
12. Checklist funcional y visual cubierto
"""

import pandas as pd
from fpdf import FPDF
from core.database import InventarioDatabaseConnection  # Importar la clase correcta

class LogisticaModel:
    def __init__(self, db_connection):
        self.db = db_connection

    def obtener_datos_entregas(self):
        """Obtiene los datos de la tabla de entregas desde la base de datos."""
        query = "SELECT destino, fecha_programada, estado, vehiculo, chofer FROM entregas"
        return self.db.ejecutar_query(query)

    def obtener_entregas(self):
        query = "SELECT * FROM entregas_obras"
        return self.db.ejecutar_query(query)

    def obtener_entregas_por_estado(self, estado):
        query = "SELECT * FROM entregas_obras WHERE estado = ?"
        return self.db.ejecutar_query(query, (estado,))

    def actualizar_estado_entrega(self, id_entrega, nuevo_estado):
        """Actualiza el estado de una entrega."""
        try:
            query = "UPDATE entregas_obras SET estado = ? WHERE id = ?"
            self.db.ejecutar_query(query, (nuevo_estado, id_entrega))
        except Exception as e:
            print(f"Error al actualizar estado de entrega: {e}")
            raise

    def obtener_checklist_por_entrega(self, id_entrega):
        query = "SELECT * FROM checklist_entrega WHERE id_entrega = ?"
        return self.db.ejecutar_query(query, (id_entrega,))

    def agregar_item_checklist(self, datos):
        query = """
        INSERT INTO checklist_entrega (id_entrega, item, estado_item, observaciones)
        VALUES (?, ?, ?, ?)
        """
        self.db.ejecutar_query(query, datos)

    def registrar_firma_entrega(self, id_entrega, firma_digital):
        query = "UPDATE entregas_obras SET firma_receptor = ? WHERE id = ?"
        self.db.ejecutar_query(query, (firma_digital, id_entrega))

    def generar_hoja_de_ruta(self, id_vehiculo):
        query = """
        SELECT id, id_obra, fecha_programada, estado, chofer_asignado
        FROM entregas_obras
        WHERE vehiculo_asignado = ? AND estado = 'pendiente'
        """
        entregas = self.db.ejecutar_query(query, (id_vehiculo,))
        if not entregas:
            return "No hay entregas pendientes para este vehículo."

        hoja_de_ruta = []
        for entrega in entregas:
            hoja_de_ruta.append({
                "ID Entrega": entrega[0],
                "ID Obra": entrega[1],
                "Fecha Programada": entrega[2],
                "Estado": entrega[3],
                "Chofer Asignado": entrega[4]
            })
        return hoja_de_ruta

    def exportar_historial_entregas(self, formato: str) -> str:
        """
        Exporta el historial de entregas en el formato solicitado ('excel' o 'pdf').
        Si no hay datos, retorna un mensaje de advertencia.
        Si ocurre un error, retorna un mensaje de error.
        El nombre del archivo incluye fecha y hora para evitar sobrescritura.
        """
        query = """
        SELECT id, id_obra, fecha_programada, fecha_realizada, estado, vehiculo_asignado, chofer_asignado, observaciones
        FROM entregas_obras
        """
        try:
            datos = self.db.ejecutar_query(query) or []
            if not datos:
                return "No hay datos de entregas para exportar."
            formato = (formato or '').lower().strip()
            if formato not in ("excel", "pdf"):
                return "Formato no soportado. Use 'excel' o 'pdf'."
            fecha_str = pd.Timestamp.now().strftime("%Y%m%d_%H%M%S")
            columnas = ["ID", "Obra", "Fecha Programada", "Fecha Realizada", "Estado", "Vehículo", "Chofer", "Observaciones"]
            if formato == "excel":
                nombre_archivo = f"historial_entregas_{fecha_str}.xlsx"
                try:
                    df = pd.DataFrame(datos, columns=columnas)
                    df.to_excel(nombre_archivo, index=False)
                    return f"Historial de entregas exportado a Excel: {nombre_archivo}"
                except Exception as e:
                    return f"Error al exportar a Excel: {e}"
            elif formato == "pdf":
                nombre_archivo = f"historial_entregas_{fecha_str}.pdf"
                try:
                    pdf = FPDF()
                    pdf.add_page()
                    pdf.set_font("Arial", size=12)
                    pdf.cell(200, 10, "Historial de Entregas", ln=True, align="C")
                    for row in datos:
                        pdf.cell(200, 10, str(row), ln=True)
                    pdf.output(nombre_archivo)
                    return f"Historial de entregas exportado a PDF: {nombre_archivo}"
                except Exception as e:
                    return f"Error al exportar a PDF: {e}"
        except Exception as e:
            return f"Error al exportar el historial de entregas: {e}"

    def exportar_acta_entrega(self, id_entrega):
        query = """
        SELECT id, id_obra, fecha_programada, fecha_realizada, estado, vehiculo_asignado, chofer_asignado, observaciones
        FROM entregas_obras
        WHERE id = ?
        """
        datos = self.db.ejecutar_query(query, (id_entrega,))
        if not datos:
            return "Entrega no encontrada."

        entrega = datos[0]
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Arial", size=12)
        pdf.cell(200, 10, f"Acta de Entrega - ID {entrega[0]}", ln=True, align="C")
        pdf.cell(200, 10, f"Obra: {entrega[1]}", ln=True)
        pdf.cell(200, 10, f"Fecha Programada: {entrega[2]}", ln=True)
        pdf.cell(200, 10, f"Fecha Realizada: {entrega[3]}", ln=True)
        pdf.cell(200, 10, f"Estado: {entrega[4]}", ln=True)
        pdf.cell(200, 10, f"Vehículo Asignado: {entrega[5]}", ln=True)
        pdf.cell(200, 10, f"Chofer Asignado: {entrega[6]}", ln=True)
        pdf.cell(200, 10, f"Observaciones: {entrega[7]}", ln=True)

        # Exportar checklist asociado
        query_checklist = """
        SELECT item, estado_item, observaciones
        FROM checklist_entrega
        WHERE id_entrega = ?
        """
        checklist = self.db.ejecutar_query(query_checklist, (id_entrega,))
        pdf.cell(200, 10, "Checklist:", ln=True)
        for item in checklist:
            pdf.cell(200, 10, f"- {item[0]}: {item[1]} ({item[2]})", ln=True)

        pdf.output(f"acta_entrega_{id_entrega}.pdf")
        return f"Acta de entrega exportada como acta_entrega_{id_entrega}.pdf."

    def programar_entrega(self, id_obra, fecha_programada, vehiculo_asignado, chofer_asignado, control_subida=None, fecha_llegada=None):
        # Nuevo: registrar quién lo llevó, quién lo controló y cuándo se llevó
        query = """
        INSERT INTO entregas_obras (id_obra, fecha_programada, vehiculo_asignado, chofer_asignado, control_subida, fecha_llegada)
        VALUES (?, ?, ?, ?, ?, ?)
        """
        self.db.ejecutar_query(query, (id_obra, fecha_programada, vehiculo_asignado, chofer_asignado, control_subida, fecha_llegada))

    def generar_acta_entrega(self, id_entrega):
        query = "SELECT id, id_obra, fecha_programada, estado FROM entregas_obras WHERE id = ?"
        entrega = self.db.ejecutar_query(query, (id_entrega,))
        if not entrega:
            return "Entrega no encontrada."

        entrega = entrega[0]
        return f"Acta de entrega generada para la obra {entrega[1]}"

    def eliminar_entrega(self, id_entrega):
        query = "DELETE FROM entregas_obras WHERE id = ?"
        self.db.ejecutar_query(query, (id_entrega,))

    def obtener_estadisticas_entregas(self):
        query = """
        SELECT estado, COUNT(*) as total
        FROM entregas_obras
        GROUP BY estado
        """
        return self.db.ejecutar_query(query)

    def obtener_datos_inventario(self):
        """Obtiene los datos de la tabla de inventario desde la base de datos."""
        query = "SELECT * FROM inventario_perfiles"
        return self.db.ejecutar_query(query)

    def agregar_entrega(self, datos):
        """Agrega una nueva entrega a la base de datos."""
        try:
            query = """
            INSERT INTO entregas_obras (destino, fecha_programada, estado, vehiculo_asignado, chofer_asignado, observaciones)
            VALUES (?, ?, ?, ?, ?, ?)
            """
            self.db.ejecutar_query(query, datos)
        except Exception as e:
            print(f"Error al agregar entrega: {e}")
            raise
