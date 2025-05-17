import pandas as pd
from fpdf import FPDF
from core.database import AuditoriaDatabaseConnection  # Importar la clase correcta

class AuditoriaModel:
    def __init__(self, db_connection):
        self.db = db_connection

    def obtener_auditorias(self, filtros=None):
        query = "SELECT * FROM auditorias_sistema"
        campos_validos = {"modulo_afectado", "usuario_id", "tipo_evento", "detalle", "ip_origen", "fecha_hora"}
        if filtros:
            # Solo aplicar filtros válidos
            filtros_validos = {k: v for k, v in filtros.items() if k in campos_validos}
            if filtros_validos:
                query += " WHERE " + " AND ".join([f"{campo} = ?" for campo in filtros_validos.keys()])
                result = self.db.ejecutar_query(query, tuple(filtros_validos.values()))
                return result if result is not None else []
            # Si no hay filtros válidos, devolver todos los resultados
        result = self.db.ejecutar_query(query)
        return result if result is not None else []

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

    def registrar_evento(self, usuario, modulo, accion, ip_origen=None):
        query = """
        INSERT INTO auditorias_sistema (usuario_id, modulo_afectado, tipo_evento, detalle, ip_origen)
        VALUES (?, ?, ?, ?, ?)
        """
        usuario_id = usuario['id'] if usuario and 'id' in usuario else None
        self.db.ejecutar_query(query, (usuario_id, modulo, 'accion', accion, ip_origen))

    def registrar_evento_obra(self, usuario, detalle, ip_origen=None):
        """Registra un evento de auditoría para acciones sobre obras."""
        modulo_afectado = 'obras'
        tipo_evento = 'asociar_material_a_obra'
        usuario_id = usuario['id'] if usuario and 'id' in usuario else None
        query = "INSERT INTO auditorias_sistema (usuario_id, modulo_afectado, tipo_evento, detalle, ip_origen) VALUES (?, ?, ?, ?, ?)"
        self.db.ejecutar_query(query, (usuario_id, modulo_afectado, tipo_evento, detalle, ip_origen))

    def obtener_logs(self, modulo_afectado):
        query = "SELECT * FROM auditorias_sistema WHERE modulo_afectado = ?"
        result = self.db.ejecutar_query(query, (modulo_afectado,))
        return result if result is not None else []

    def consultar_auditoria(self, fecha_inicio, fecha_fin, usuario):
        query = "SELECT * FROM auditoria WHERE fecha >= ? AND fecha <= ? AND usuario LIKE ?"
        parametros = (fecha_inicio, fecha_fin, f"%{usuario}%")
        resultados = self.db.ejecutar_query(query, parametros)
        return resultados
