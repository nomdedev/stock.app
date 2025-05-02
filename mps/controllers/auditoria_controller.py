import os
import csv
from datetime import datetime
from mps.services.database import AuditoriaDatabaseConnection

class AuditoriaController:
    LOCAL_LOG_FILE = "auditoria_local.log"

    @staticmethod
    def registrar_reconexion(base, usuario):
        """Registra un evento de reconexión en la auditoría."""
        db = AuditoriaDatabaseConnection()
        query = """
        INSERT INTO auditoria (tipo, modulo, usuario, fecha_hora, descripcion)
        VALUES (%s, %s, %s, %s, %s)
        """
        descripcion = f"Se reestableció la conexión con la base '{base}' desde Configuración."
        db.ejecutar_query(query, ("RECONEXIÓN", base, usuario, datetime.now().isoformat(), descripcion))

    @staticmethod
    def log_local_si_falla(base, usuario, descripcion, exito: bool):
        """Registra auditorías en la base de datos o localmente si falla la conexión."""
        try:
            if exito:
                db = AuditoriaDatabaseConnection()
                query = """
                INSERT INTO auditoria (tipo, modulo, usuario, fecha_hora, descripcion)
                VALUES (%s, %s, %s, %s, %s)
                """
                db.ejecutar_query(query, ("LOG", base, usuario, datetime.now().isoformat(), descripcion))
            else:
                with open(AuditoriaController.LOCAL_LOG_FILE, mode="a", newline="", encoding="utf-8") as file:
                    writer = csv.writer(file)
                    writer.writerow([datetime.now().isoformat(), usuario, "LOG", base, descripcion, "FALLIDO"])
        except Exception as e:
            print(f"Error al registrar auditoría: {e}")

    @staticmethod
    def sincronizar_auditorias_pendientes():
        """Sincroniza auditorías locales pendientes con la base de datos."""
        if not os.path.exists(AuditoriaController.LOCAL_LOG_FILE):
            return

        try:
            db = AuditoriaDatabaseConnection()
            with open(AuditoriaController.LOCAL_LOG_FILE, mode="r", encoding="utf-8") as file:
                reader = csv.reader(file)
                for row in reader:
                    fecha, usuario, tipo, modulo, descripcion, estado = row
                    if estado == "FALLIDO":
                        query = """
                        INSERT INTO auditoria (tipo, modulo, usuario, fecha_hora, descripcion)
                        VALUES (%s, %s, %s, %s, %s)
                        """
                        db.ejecutar_query(query, (tipo, modulo, usuario, fecha, descripcion))
            os.remove(AuditoriaController.LOCAL_LOG_FILE)
        except Exception as e:
            print(f"Error al sincronizar auditorías pendientes: {e}")
