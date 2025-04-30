import pandas as pd
from fpdf import FPDF

class LogisticaModel:
    def __init__(self, db_connection):
        self.db = db_connection

    def obtener_entregas(self):
        query = "SELECT * FROM entregas_obras"
        return self.db.ejecutar_query(query)

    def obtener_entregas_por_estado(self, estado):
        query = "SELECT * FROM entregas_obras WHERE estado = ?"
        return self.db.ejecutar_query(query, (estado,))

    def actualizar_estado_entrega(self, id_entrega, nuevo_estado):
        query = "UPDATE entregas_obras SET estado = ? WHERE id = ?"
        self.db.ejecutar_query(query, (nuevo_estado, id_entrega))

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

    def exportar_historial_entregas(self, formato):
        query = """
        SELECT id, id_obra, fecha_programada, fecha_realizada, estado, vehiculo_asignado, chofer_asignado, observaciones
        FROM entregas_obras
        """
        datos = self.db.ejecutar_query(query)

        if formato == "excel":
            df = pd.DataFrame(datos, columns=["ID", "Obra", "Fecha Programada", "Fecha Realizada", "Estado", "Vehículo", "Chofer", "Observaciones"])
            df.to_excel("historial_entregas.xlsx", index=False)
            return "Historial de entregas exportado a Excel."

        elif formato == "pdf":
            pdf = FPDF()
            pdf.add_page()
            pdf.set_font("Arial", size=12)
            pdf.cell(200, 10, txt="Historial de Entregas", ln=True, align="C")
            for row in datos:
                pdf.cell(200, 10, txt=str(row), ln=True)
            pdf.output("historial_entregas.pdf")
            return "Historial de entregas exportado a PDF."

        return "Formato no soportado."

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
        pdf.cell(200, 10, txt=f"Acta de Entrega - ID {entrega[0]}", ln=True, align="C")
        pdf.cell(200, 10, txt=f"Obra: {entrega[1]}", ln=True)
        pdf.cell(200, 10, txt=f"Fecha Programada: {entrega[2]}", ln=True)
        pdf.cell(200, 10, txt=f"Fecha Realizada: {entrega[3]}", ln=True)
        pdf.cell(200, 10, txt=f"Estado: {entrega[4]}", ln=True)
        pdf.cell(200, 10, txt=f"Vehículo Asignado: {entrega[5]}", ln=True)
        pdf.cell(200, 10, txt=f"Chofer Asignado: {entrega[6]}", ln=True)
        pdf.cell(200, 10, txt=f"Observaciones: {entrega[7]}", ln=True)

        # Exportar checklist asociado
        query_checklist = """
        SELECT item, estado_item, observaciones
        FROM checklist_entrega
        WHERE id_entrega = ?
        """
        checklist = self.db.ejecutar_query(query_checklist, (id_entrega,))
        pdf.cell(200, 10, txt="Checklist:", ln=True)
        for item in checklist:
            pdf.cell(200, 10, txt=f"- {item[0]}: {item[1]} ({item[2]})", ln=True)

        pdf.output(f"acta_entrega_{id_entrega}.pdf")
        return f"Acta de entrega exportada como acta_entrega_{id_entrega}.pdf."

    def programar_entrega(self, id_obra, fecha_programada, vehiculo_asignado, chofer_asignado):
        query = "INSERT INTO entregas_obras (id_obra, fecha_programada, vehiculo_asignado, chofer_asignado) VALUES (?, ?, ?, ?)"
        self.db.ejecutar_query(query, (id_obra, fecha_programada, vehiculo_asignado, chofer_asignado))

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
