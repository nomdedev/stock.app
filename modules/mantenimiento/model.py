import pandas as pd
from fpdf import FPDF

class MantenimientoModel:
    """
    Modelo de Mantenimiento. Debe recibir una instancia de MantenimientoDatabaseConnection (o hija de BaseDatabaseConnection) como parámetro db_connection.
    No crear conexiones nuevas internamente. Usar siempre la conexión persistente y unificada.
    """
    def __init__(self, db_connection):
        self.db = db_connection

    def obtener_herramientas(self):
        query = "SELECT * FROM herramientas"
        return self.db.ejecutar_query(query)

    def obtener_vehiculos(self):
        query = "SELECT * FROM vehiculos"
        return self.db.ejecutar_query(query)

    def agregar_mantenimiento(self, datos):
        # Alias de registrar_mantenimiento para compatibilidad
        return self.registrar_mantenimiento(datos)

    def registrar_mantenimiento(self, datos):
        """
        Registra un nuevo mantenimiento.
        datos: (tipo_objeto, id_objeto, tipo_mantenimiento, fecha_realizacion, realizado_por, observaciones, firma_digital)
        """
        query = """
        INSERT INTO mantenimientos (tipo_objeto, id_objeto, tipo_mantenimiento, fecha_realizacion, realizado_por, observaciones, firma_digital)
        VALUES (?, ?, ?, ?, ?, ?, ?)
        """
        self.db.ejecutar_query(query, datos)
        return True

    def obtener_mantenimientos(self):
        query = "SELECT * FROM mantenimientos"
        return self.db.ejecutar_query(query)

    def obtener_checklist(self, id_mantenimiento):
        query = "SELECT * FROM checklists_mantenimiento WHERE id_mantenimiento = ?"
        return self.db.ejecutar_query(query, (id_mantenimiento,))

    def agregar_checklist_item(self, datos):
        # datos: (id_mantenimiento, item, estado, observaciones)
        query = """
        INSERT INTO checklists_mantenimiento (id_mantenimiento, item, estado, observaciones)
        VALUES (?, ?, ?, ?)
        """
        self.db.ejecutar_query(query, datos)
        return True

    def obtener_tareas_recurrentes(self):
        query = "SELECT * FROM tareas_recurrentes WHERE proxima_fecha <= CURRENT_DATE"
        return self.db.ejecutar_query(query)

    def agregar_tarea_recurrente(self, datos):
        # datos: (tipo_objeto, id_objeto, descripcion, frecuencia_dias, proxima_fecha, responsable)
        query = """
        INSERT INTO tareas_recurrentes (tipo_objeto, id_objeto, descripcion, frecuencia_dias, proxima_fecha, responsable)
        VALUES (?, ?, ?, ?, ?, ?)
        """
        self.db.ejecutar_query(query, datos)
        return True

    def actualizar_tarea_recurrente(self, id_tarea, nueva_fecha):
        query = "UPDATE tareas_recurrentes SET proxima_fecha = ? WHERE id = ?"
        self.db.ejecutar_query(query, (nueva_fecha, id_tarea))
        return True

    def eliminar_tarea_recurrente(self, id_tarea):
        query = "DELETE FROM tareas_recurrentes WHERE id = ?"
        self.db.ejecutar_query(query, (id_tarea,))
        return True

    def exportar_reporte_mantenimiento(self, formato: str) -> str:
        """
        Exporta el reporte de mantenimientos en el formato solicitado.
        Soporta 'excel' y 'pdf'.
        Si no hay datos, retorna un mensaje de advertencia.
        Si ocurre un error, retorna un mensaje de error.
        El nombre del archivo incluye fecha y hora para evitar sobrescritura.
        """
        query = (
            """
            SELECT tipo_mantenimiento, fecha_realizacion, realizado_por, observaciones, firma_digital
            FROM mantenimientos
            """
        )
        try:
            datos = self.db.ejecutar_query(query) or []
            if not datos:
                return "No hay datos de mantenimiento para exportar."
            formato = (formato or '').lower().strip()
            if formato not in ("excel", "pdf"):
                return "Formato no soportado. Use 'excel' o 'pdf'."
            fecha_str = pd.Timestamp.now().strftime("%Y%m%d_%H%M%S")
            if formato == "excel":
                nombre_archivo = f"reporte_mantenimiento_{fecha_str}.xlsx"
                try:
                    df = pd.DataFrame(datos, columns=["Tipo", "Fecha", "Realizado Por", "Observaciones", "Firma Digital"])
                    df.to_excel(nombre_archivo, index=False)
                    return f"Reporte de mantenimiento exportado a Excel: {nombre_archivo}"
                except Exception as e:
                    return f"Error al exportar a Excel: {e}"
            elif formato == "pdf":
                nombre_archivo = f"reporte_mantenimiento_{fecha_str}.pdf"
                try:
                    pdf = FPDF()
                    pdf.add_page()
                    pdf.set_font("Arial", size=12)
                    pdf.cell(200, 10, "Reporte de Mantenimiento", ln=True, align="C")
                    for row in datos:
                        pdf.cell(200, 10, str(row), ln=True)
                    pdf.output(nombre_archivo)
                    return f"Reporte de mantenimiento exportado a PDF: {nombre_archivo}"
                except Exception as e:
                    return f"Error al exportar a PDF: {e}"
        except Exception as e:
            return f"Error al exportar el reporte: {e}"

    def exportar_historial_mantenimientos(self, formato: str) -> str:
        """
        Exporta el historial de mantenimientos en el formato solicitado.
        Soporta 'excel' y 'pdf'.
        Si no hay datos, retorna un mensaje de advertencia.
        Si ocurre un error, retorna un mensaje de error.
        El nombre del archivo incluye fecha y hora para evitar sobrescritura.
        """
        query = (
            """
            SELECT tipo_mantenimiento, fecha_realizacion, realizado_por, observaciones, firma_digital
            FROM mantenimientos
            """
        )
        try:
            datos = self.db.ejecutar_query(query) or []
            if not datos:
                return "No hay historial de mantenimientos para exportar."
            formato = (formato or '').lower().strip()
            if formato not in ("excel", "pdf"):
                return "Formato no soportado. Use 'excel' o 'pdf'."
            fecha_str = pd.Timestamp.now().strftime("%Y%m%d_%H%M%S")
            if formato == "excel":
                nombre_archivo = f"historial_mantenimientos_{fecha_str}.xlsx"
                try:
                    df = pd.DataFrame(datos, columns=["Tipo", "Fecha", "Realizado Por", "Observaciones", "Firma Digital"])
                    df.to_excel(nombre_archivo, index=False)
                    return f"Historial de mantenimientos exportado a Excel: {nombre_archivo}"
                except Exception as e:
                    return f"Error al exportar a Excel: {e}"
            elif formato == "pdf":
                nombre_archivo = f"historial_mantenimientos_{fecha_str}.pdf"
                try:
                    pdf = FPDF()
                    pdf.add_page()
                    pdf.set_font("Arial", size=12)
                    pdf.cell(200, 10, "Historial de Mantenimientos", ln=True, align="C")
                    for row in datos:
                        pdf.cell(200, 10, str(row), ln=True)
                    pdf.output(nombre_archivo)
                    return f"Historial de mantenimientos exportado a PDF: {nombre_archivo}"
                except Exception as e:
                    return f"Error al exportar a PDF: {e}"
        except Exception as e:
            return f"Error al exportar el historial: {e}"

    def obtener_historial_mantenimientos(self, id_objeto):
        query = "SELECT * FROM mantenimientos WHERE id_objeto = ?"
        return self.db.ejecutar_query(query, (id_objeto,))

    def obtener_estadisticas_mantenimientos(self):
        query = """
        SELECT tipo_mantenimiento, COUNT(*) as total
        FROM mantenimientos
        GROUP BY tipo_mantenimiento
        """
        return self.db.ejecutar_query(query)
