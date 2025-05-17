import pandas as pd
from fpdf import FPDF

class MantenimientoModel:
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

    def exportar_reporte_mantenimiento(self, formato):
        """
        Exporta el reporte de mantenimientos en el formato solicitado.
        """
        query = """
        SELECT tipo_mantenimiento, fecha_realizacion, realizado_por, observaciones, firma_digital
        FROM mantenimientos
        """
        datos = self.db.ejecutar_query(query)

        if formato == "excel":
            df = pd.DataFrame(datos, columns=["Tipo", "Fecha", "Realizado Por", "Observaciones", "Firma Digital"])
            df.to_excel("reporte_mantenimiento.xlsx", index=False)
            return "Reporte de mantenimiento exportado a Excel."

        elif formato == "pdf":
            pdf = FPDF()
            pdf.add_page()
            pdf.set_font("Arial", size=12)
            pdf.cell(200, 10, txt="Reporte de Mantenimiento", ln=True, align="C")
            for row in datos:
                pdf.cell(200, 10, txt=str(row), ln=True)
            pdf.output("reporte_mantenimiento.pdf")
            return "Reporte de mantenimiento exportado a PDF."

        return "Formato no soportado."

    def registrar_repuesto_utilizado(self, datos):
        # datos: (id_mantenimiento, id_item, cantidad_utilizada)
        query = """
        INSERT INTO repuestos_usados (id_mantenimiento, id_item, cantidad_utilizada)
        VALUES (?, ?, ?)
        """
        self.db.ejecutar_query(query, datos)
        return True

    def exportar_historial_mantenimientos(self, formato):
        """
        Exporta el historial de mantenimientos en el formato solicitado.
        """
        query = """
        SELECT tipo_mantenimiento, fecha_realizacion, realizado_por, observaciones, firma_digital
        FROM mantenimientos
        """
        datos = self.db.ejecutar_query(query)

        if formato == "excel":
            df = pd.DataFrame(datos, columns=["Tipo", "Fecha", "Realizado Por", "Observaciones", "Firma Digital"])
            df.to_excel("historial_mantenimientos.xlsx", index=False)
            return "Historial de mantenimientos exportado a Excel."

        elif formato == "pdf":
            pdf = FPDF()
            pdf.add_page()
            pdf.set_font("Arial", size=12)
            pdf.cell(200, 10, txt="Historial de Mantenimientos", ln=True, align="C")
            for row in datos:
                pdf.cell(200, 10, txt=str(row), ln=True)
            pdf.output("historial_mantenimientos.pdf")
            return "Historial de mantenimientos exportado a PDF."

        return "Formato no soportado."

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
