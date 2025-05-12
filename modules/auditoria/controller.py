import csv
from PyQt6.QtWidgets import QTableWidgetItem

class AuditoriaController:
    def __init__(self, model, view, db_connection, usuario_actual=None):
        self.model = model
        self.view = view
        self.usuario_actual = usuario_actual

    def ejecutar_accion(self):
        try:
            # Lógica centralizada para manejar la acción del botón
            print("Acción ejecutada desde el módulo Auditoría")
            # Aquí puedes implementar la lógica deseada, como aplicar filtros o exportar datos
        except Exception as e:
            print(f"Error al ejecutar la acción: {e}")

    def aplicar_filtros(self):
        try:
            # Implementar la lógica para aplicar filtros si es necesario
            fecha_inicio = self.view.fecha_inicio.text()  # Ajustar según los widgets reales
            fecha_fin = self.view.fecha_fin.text()
            usuario = self.view.campo_usuario.text()
            # Consultar la base de datos con los filtros
            resultados = self.model.consultar_auditoria(fecha_inicio, fecha_fin, usuario)
            # Actualizar la tabla con los resultados
            self.view.actualizar_tabla(resultados)
        except Exception as e:
            print(f"Error al aplicar filtros: {e}")

    def exportar_logs(self):
        try:
            logs = self.model.obtener_auditorias()
            with open("logs_auditoria.csv", "w", newline="") as file:
                writer = csv.writer(file)
                writer.writerow(["Usuario", "Módulo", "Evento", "Detalle", "Fecha"])
                writer.writerows(logs)
            self.view.label.setText("Logs exportados exitosamente.")
        except Exception as e:
            print(f"Error al exportar logs: {e}")

    def exportar_auditorias(self, formato):
        try:
            mensaje = self.model.exportar_auditorias(formato)
            self.view.label.setText(mensaje)
        except Exception as e:
            print(f"Error al exportar auditorías: {e}")
