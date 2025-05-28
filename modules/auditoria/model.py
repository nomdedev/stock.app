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

    def exportar_auditorias(self, formato="excel", filename=None):
        """
        Exporta los registros de auditoría a Excel o PDF.
        Args:
            formato (str): 'excel' o 'pdf'.
            filename (str): Nombre de archivo opcional.
        Returns:
            str: Mensaje de resultado.
        """
        query = """
        SELECT fecha_hora, usuario_id, modulo_afectado, tipo_evento, detalle, ip_origen
        FROM auditorias_sistema
        """
        datos = self.db.ejecutar_query(query)
        columnas = ["Fecha/Hora", "Usuario", "Módulo", "Evento", "Detalle", "IP"]
        if formato not in ("excel", "pdf"):
            return "Formato no soportado. Usa 'excel' o 'pdf'."
        if not datos or len(datos) == 0:
            return "No hay datos de auditoría para exportar."
        if not filename:
            filename = "auditorias.xlsx" if formato == "excel" else "auditorias.pdf"
        if formato == "excel":
            try:
                import pandas as pd
                df = pd.DataFrame(datos, columns=columnas)
                df.to_excel(filename, index=False)
                return f"Auditorías exportadas a Excel: {filename}"
            except Exception as e:
                return f"Error al exportar a Excel: {e}"
        elif formato == "pdf":
            try:
                from fpdf import FPDF
                pdf = FPDF()
                pdf.add_page()
                pdf.set_font("Arial", size=10)
                pdf.cell(200, 10, "Auditorías del Sistema", ln=True, align="C")
                for row in datos:
                    fila = " | ".join([str(x) for x in row])
                    pdf.cell(0, 8, fila, ln=True)
                pdf.output(filename)
                return f"Auditorías exportadas a PDF: {filename}"
            except Exception as e:
                return f"Error al exportar a PDF: {e}"
        return "Formato no soportado. Usa 'excel' o 'pdf'."

    def registrar_evento(self, usuario_id, modulo, tipo_evento, detalle, ip_origen):
        """
        Registra un evento en la tabla auditorias_sistema.
        Args:
            usuario_id (int): ID del usuario (obligatorio).
            modulo (str): Nombre del módulo afectado.
            tipo_evento (str): Tipo de evento.
            detalle (str): Detalle del evento.
            ip_origen (str): IP de origen (opcional).
        Returns:
            bool: True si se registró correctamente, False si hubo error.
        """
        if usuario_id is None or not modulo or not tipo_evento:
            try:
                from core.logger import log_error
                log_error(f"registrar_evento: Argumentos faltantes: usuario_id={usuario_id}, modulo={modulo}, tipo_evento={tipo_evento}")
            except Exception:
                pass
            return False
        query = """
        INSERT INTO auditorias_sistema (usuario_id, modulo_afectado, tipo_evento, detalle, ip_origen)
        VALUES (?, ?, ?, ?, ?)
        """
        try:
            self.db.ejecutar_query(query, (usuario_id, modulo, tipo_evento, detalle, ip_origen))
            return True
        except Exception as e:
            try:
                from core.logger import log_error
                log_error(f"Error en registrar_evento: {e}")
            except Exception:
                pass
            return False

    def registrar_evento_obra(self, usuario, detalle, ip_origen=None):
        """
        Registra un evento de auditoría para acciones sobre obras.
        Args:
            usuario (dict): Debe contener 'id'.
            detalle (str): Descripción del evento.
            ip_origen (str): IP de origen (opcional).
        Returns:
            bool: True si se registró correctamente, False si hubo error.
        """
        modulo_afectado = 'obras'
        tipo_evento = 'asociar_material_a_obra'
        usuario_id = usuario['id'] if usuario and 'id' in usuario else None
        if usuario_id is None:
            try:
                from core.logger import log_error
                log_error(f"registrar_evento_obra: usuario sin id: {usuario}")
            except Exception:
                pass
            return False
        query = "INSERT INTO auditorias_sistema (usuario_id, modulo_afectado, tipo_evento, detalle, ip_origen) VALUES (?, ?, ?, ?, ?)"
        try:
            self.db.ejecutar_query(query, (usuario_id, modulo_afectado, tipo_evento, detalle, ip_origen))
            return True
        except Exception as e:
            try:
                from core.logger import log_error
                log_error(f"Error en registrar_evento_obra: {e}")
            except Exception:
                pass
            return False

    def obtener_logs(self, modulo_afectado):
        query = "SELECT * FROM auditorias_sistema WHERE modulo_afectado = ?"
        result = self.db.ejecutar_query(query, (modulo_afectado,))
        # Si hay más de un resultado, devolver todos los eventos del módulo solicitado
        return result if result is not None else []

    def consultar_auditoria(self, fecha_inicio, fecha_fin, usuario_id=None):
        """
        Consulta auditorías filtrando por fecha y usuario_id (opcional).
        Args:
            fecha_inicio (str): Fecha inicio (YYYY-MM-DD).
            fecha_fin (str): Fecha fin (YYYY-MM-DD).
            usuario_id (int, opcional): ID del usuario. Si es None, no filtra por usuario.
        Returns:
            list: Resultados de la consulta.
        """
        if usuario_id:
            query = """
            SELECT * FROM auditorias_sistema WHERE fecha_hora >= ? AND fecha_hora <= ? AND usuario_id = ?
            """
            parametros = (fecha_inicio, fecha_fin, usuario_id)
        else:
            query = """
            SELECT * FROM auditorias_sistema WHERE fecha_hora >= ? AND fecha_hora <= ?
            """
            parametros = (fecha_inicio, fecha_fin)
        resultados = self.db.ejecutar_query(query, parametros)
        return resultados if resultados is not None else []
