import csv
from PyQt6.QtWidgets import QTableWidgetItem

class AuditoriaController:
    def __init__(self, model, view, db_connection, usuario_actual=None):
        self.model = model
        self.view = view
        self.usuario_actual = usuario_actual

    def ejecutar_accion(self):
        try:
            print(f"[LOG ACCIÓN] Ejecutando acción 'ejecutar_accion' en módulo 'auditoria' por usuario: {getattr(self.usuario_actual, 'username', 'desconocido')}")
            # Lógica centralizada para manejar la acción del botón
            print("Acción ejecutada desde el módulo Auditoría")
            # Aquí puedes implementar la lógica deseada, como aplicar filtros o exportar datos
            print("[LOG ACCIÓN] Acción 'ejecutar_accion' en módulo 'auditoria' finalizada con éxito.")
        except Exception as e:
            print(f"[LOG ACCIÓN] Error en acción 'ejecutar_accion' en módulo 'auditoria': {e}")

    def aplicar_filtros(self):
        try:
            print(f"[LOG ACCIÓN] Ejecutando acción 'aplicar_filtros' en módulo 'auditoria' por usuario: {getattr(self.usuario_actual, 'username', 'desconocido')}")
            # Implementar la lógica para aplicar filtros si es necesario
            fecha_inicio = self.view.fecha_inicio.text()  # Ajustar según los widgets reales
            fecha_fin = self.view.fecha_fin.text()
            usuario = self.view.campo_usuario.text()
            # Consultar la base de datos con los filtros
            resultados = self.model.consultar_auditoria(fecha_inicio, fecha_fin, usuario)
            # Actualizar la tabla con los resultados
            self.view.actualizar_tabla(resultados)
            print("[LOG ACCIÓN] Acción 'aplicar_filtros' en módulo 'auditoria' finalizada con éxito.")
        except Exception as e:
            print(f"[LOG ACCIÓN] Error en acción 'aplicar_filtros' en módulo 'auditoria': {e}")

    def exportar_logs(self):
        try:
            print(f"[LOG ACCIÓN] Ejecutando acción 'exportar_logs' en módulo 'auditoria' por usuario: {getattr(self.usuario_actual, 'username', 'desconocido')}")
            logs = self.model.obtener_auditorias()
            with open("logs_auditoria.csv", "w", newline="") as file:
                writer = csv.writer(file)
                writer.writerow(["Usuario", "Módulo", "Evento", "Detalle", "Fecha"])
                writer.writerows(logs)
            self.view.label.setText("Logs exportados exitosamente.")
            print("[LOG ACCIÓN] Acción 'exportar_logs' en módulo 'auditoria' finalizada con éxito.")
        except Exception as e:
            print(f"[LOG ACCIÓN] Error en acción 'exportar_logs' en módulo 'auditoria': {e}")

    def exportar_auditorias(self, formato):
        try:
            print(f"[LOG ACCIÓN] Ejecutando acción 'exportar_auditorias' en módulo 'auditoria' por usuario: {getattr(self.usuario_actual, 'username', 'desconocido')}")
            mensaje = self.model.exportar_auditorias(formato)
            self.view.label.setText(mensaje)
            print("[LOG ACCIÓN] Acción 'exportar_auditorias' en módulo 'auditoria' finalizada con éxito.")
        except Exception as e:
            print(f"[LOG ACCIÓN] Error en acción 'exportar_auditorias' en módulo 'auditoria': {e}")
