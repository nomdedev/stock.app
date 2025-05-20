import pandas as pd
from fpdf import FPDF
import hashlib

class ContabilidadModel:
    """
    Modelo de Contabilidad. Debe recibir una instancia de ContabilidadDatabaseConnection (o hija de BaseDatabaseConnection) como parámetro db_connection.
    No crear conexiones nuevas internamente. Usar siempre la conexión persistente y unificada.
    """
    def __init__(self, db_connection):
        self.db = db_connection

    def obtener_reportes(self):
        query = "SELECT * FROM reportes"
        return self.db.ejecutar_query(query)

    def agregar_reporte(self, datos):
        query = "INSERT INTO reportes (titulo, fecha, total) VALUES (?, ?, ?)"
        self.db.ejecutar_query(query, datos)

    def obtener_recibos(self):
        query = "SELECT * FROM recibos"
        return self.db.ejecutar_query(query)

    def agregar_recibo(self, datos):
        query = """
        INSERT INTO recibos (fecha_emision, obra_id, monto_total, concepto, destinatario, firma_digital, usuario_emisor, estado, archivo_pdf)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """
        self.db.ejecutar_query(query, datos)

    def obtener_movimientos_contables(self):
        query = "SELECT * FROM movimientos_contables"
        return self.db.ejecutar_query(query)

    def agregar_movimiento_contable(self, datos):
        query = """
        INSERT INTO movimientos_contables (fecha, tipo_movimiento, monto, concepto, referencia_recibo, observaciones)
        VALUES (?, ?, ?, ?, ?, ?)
        """
        self.db.ejecutar_query(query, datos)

    def anular_recibo(self, id_recibo):
        query = "UPDATE recibos SET estado = 'anulado' WHERE id = ?"
        self.db.ejecutar_query(query, (id_recibo,))

    def exportar_balance(self, formato: str, datos_balance) -> str:
        """
        Exporta el balance contable en el formato solicitado ('excel' o 'pdf').
        Si no hay datos, retorna un mensaje de advertencia.
        Si ocurre un error, retorna un mensaje de error.
        El nombre del archivo incluye fecha y hora para evitar sobrescritura.
        """
        if not datos_balance:
            return "No hay datos de balance para exportar."
        formato = (formato or '').lower().strip()
        if formato not in ("excel", "pdf"):
            return "Formato no soportado. Use 'excel' o 'pdf'."
        fecha_str = pd.Timestamp.now().strftime("%Y%m%d_%H%M%S")
        columnas = ["Fecha", "Tipo", "Monto", "Concepto", "Referencia", "Observaciones"]
        if formato == "excel":
            nombre_archivo = f"balance_contable_{fecha_str}.xlsx"
            try:
                df = pd.DataFrame(datos_balance, columns=columnas)
                df.to_excel(nombre_archivo, index=False)
                return f"Balance exportado a Excel: {nombre_archivo}"
            except Exception as e:
                return f"Error al exportar a Excel: {e}"
        elif formato == "pdf":
            nombre_archivo = f"balance_contable_{fecha_str}.pdf"
            try:
                pdf = FPDF()
                pdf.add_page()
                pdf.set_font("Arial", size=12)
                pdf.cell(200, 10, "Balance Contable", ln=True, align="C")
                for row in datos_balance:
                    pdf.cell(200, 10, str(row), ln=True)
                pdf.output(nombre_archivo)
                return f"Balance exportado a PDF: {nombre_archivo}"
            except Exception as e:
                return f"Error al exportar a PDF: {e}"

    def generar_recibo_pdf(self, id_recibo):
        query = """
        SELECT fecha_emision, obra_id, monto_total, concepto, destinatario, firma_digital
        FROM recibos
        WHERE id = ?
        """
        datos = self.db.ejecutar_query(query, (id_recibo,))
        if not datos:
            return "Recibo no encontrado."

        recibo = datos[0]
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Arial", size=12)
        pdf.cell(200, 10, f"Recibo - ID {id_recibo}", ln=True, align="C")
        pdf.cell(200, 10, f"Fecha de Emisión: {recibo[0]}", ln=True)
        pdf.cell(200, 10, f"Obra ID: {recibo[1]}", ln=True)
        pdf.cell(200, 10, f"Monto Total: {recibo[2]}", ln=True)
        pdf.cell(200, 10, f"Concepto: {recibo[3]}", ln=True)
        pdf.cell(200, 10, f"Destinatario: {recibo[4]}", ln=True)
        pdf.cell(200, 10, f"Firma Digital: {recibo[5]}", ln=True)

        pdf.output(f"recibo_{id_recibo}.pdf")
        return f"Recibo exportado como recibo_{id_recibo}.pdf."

    def generar_firma_digital(self, datos_recibo):
        """
        Genera una firma digital basada en los datos del recibo.
        """
        datos_concatenados = "|".join(map(str, datos_recibo))
        firma = hashlib.sha256(datos_concatenados.encode()).hexdigest()
        return firma

    def verificar_firma_digital(self, id_recibo):
        """
        Verifica si la firma digital almacenada coincide con los datos del recibo.
        """
        query = """
        SELECT fecha_emision, obra_id, monto_total, concepto, destinatario, firma_digital
        FROM recibos
        WHERE id = ?
        """
        datos = self.db.ejecutar_query(query, (id_recibo,))
        if not datos:
            return "Recibo no encontrado."

        recibo = datos[0]
        firma_calculada = self.generar_firma_digital(recibo[:-1])  # Excluye la firma almacenada
        return firma_calculada == recibo[-1]

    def generar_recibo(self, obra_id, monto_total, concepto, destinatario):
        query = "INSERT INTO recibos (obra_id, monto_total, concepto, destinatario) VALUES (?, ?, ?, ?)"
        self.db.ejecutar_query(query, (obra_id, monto_total, concepto, destinatario))

    def obtener_balance(self, fecha_inicio, fecha_fin):
        query = "SELECT * FROM movimientos_contables WHERE fecha BETWEEN ? AND ?"
        return self.db.ejecutar_query(query, (fecha_inicio, fecha_fin))
