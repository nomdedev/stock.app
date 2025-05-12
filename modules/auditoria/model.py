import pandas as pd
from fpdf import FPDF
from core.database import AuditoriaDatabaseConnection  # Importar la clase correcta

class AuditoriaModel:
    def __init__(self, db_connection):
        self.db = db_connection

    def obtener_auditorias(self, filtros=None):
        query = "SELECT * FROM auditorias_sistema"
        if filtros:
            query += " WHERE " + " AND ".join([f"{campo} = ?" for campo in filtros.keys()])
            return self.db.ejecutar_query(query, tuple(filtros.values()))
        return self.db.ejecutar_query(query)

    def obtener_errores(self, filtros=None):
        query = "SELECT * FROM errores_sistema"
        if filtros:
            query += " WHERE " + " AND ".join([f"{campo} = ?" for campo in filtros.keys()])
            return self.db.ejecutar_query(query, tuple(filtros.values()))
        return self.db.ejecutar_query(query)

    def exportar_auditorias(self, formato):
        query = """
        SELECT fecha_hora, usuario_id, modulo_afectado, tipo_evento, detalle, ip_origen
        FROM auditorias_sistema
        """
        datos = self.db.ejecutar_query(query)

        if formato == "excel":
            df = pd.DataFrame(datos, columns=["Fecha", "Usuario", "Módulo", "Evento", "Detalle", "IP"])
            df.to_excel("auditorias.xlsx", index=False)
            return "Auditorías exportadas a Excel."

        elif formato == "pdf":
            pdf = FPDF()
            pdf.add_page()
            pdf.set_font("Arial", size=12)
            pdf.cell(200, 10, txt="Auditorías del Sistema", ln=True, align="C")
            for row in datos:
                pdf.cell(200, 10, txt=str(row), ln=True)
            pdf.output("auditorias.pdf")
            return "Auditorías exportadas a PDF."

        return "Formato no soportado."

    def exportar_logs(self, formato):
        query = """
        SELECT fecha_hora, usuario_id, modulo_afectado, tipo_evento, detalle, ip_origen
        FROM auditorias_sistema
        """
        datos = self.db.ejecutar_query(query)

        if formato == "excel":
            df = pd.DataFrame(datos, columns=["Fecha", "Usuario", "Módulo", "Evento", "Detalle", "IP"])
            df.to_excel("logs_auditoria.xlsx", index=False)
            return "Logs exportados a Excel."

        elif formato == "pdf":
            pdf = FPDF()
            pdf.add_page()
            pdf.set_font("Arial", size=12)
            pdf.cell(200, 10, txt="Logs de Auditoría", ln=True, align="C")
            for row in datos:
                pdf.cell(200, 10, txt=str(row), ln=True)
            pdf.output("logs_auditoria.pdf")
            return "Logs exportados a PDF."

        return "Formato no soportado."

    def registrar_evento(self, modulo_afectado, tipo_evento, detalle, ip_origen):
        query = "INSERT INTO auditorias_sistema (modulo_afectado, tipo_evento, detalle, ip_origen) VALUES (?, ?, ?, ?)"
        self.db.ejecutar_query(query, (modulo_afectado, tipo_evento, detalle, ip_origen))

    def obtener_logs(self, modulo_afectado):
        query = "SELECT * FROM auditorias_sistema WHERE modulo_afectado = ?"
        return self.db.ejecutar_query(query, (modulo_afectado,))

    def consultar_auditoria(self, fecha_inicio, fecha_fin, usuario):
        query = "SELECT * FROM auditoria WHERE fecha >= ? AND fecha <= ? AND usuario LIKE ?"
        parametros = (fecha_inicio, fecha_fin, f"%{usuario}%")
        resultados = self.db.ejecutar_query(query, parametros)
        return resultados
