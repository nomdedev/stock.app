import csv
from PyQt6.QtWidgets import QTableWidgetItem

class AuditoriaController:
    def __init__(self, model, view):
        self.model = model
        self.view = view
        self.view.boton_filtrar.clicked.connect(self.aplicar_filtros)  # Conectar el botón al método
        self.view.boton_exportar.clicked.connect(self.exportar_logs)
        self.view.boton_exportar_excel.clicked.connect(lambda: self.exportar_auditorias("excel"))
        self.view.boton_exportar_pdf.clicked.connect(lambda: self.exportar_auditorias("pdf"))

    def aplicar_filtros(self):
        # Leer los filtros desde la vista
        fecha_inicio = self.view.fecha_inicio.text()  # Ajustar según los widgets reales
        fecha_fin = self.view.fecha_fin.text()
        usuario = self.view.campo_usuario.text()
        # Consultar la base de datos con los filtros
        resultados = self.model.consultar_auditoria(fecha_inicio, fecha_fin, usuario)
        # Actualizar la tabla con los resultados
        self.view.actualizar_tabla(resultados)

    def exportar_logs(self):
        logs = self.model.obtener_auditorias()
        with open("logs_auditoria.csv", "w", newline="") as file:
            writer = csv.writer(file)
            writer.writerow(["Usuario", "Módulo", "Evento", "Detalle", "Fecha"])
            writer.writerows(logs)
        self.view.label.setText("Logs exportados exitosamente.")

    def exportar_auditorias(self, formato):
        mensaje = self.model.exportar_auditorias(formato)
        self.view.label.setText(mensaje)

    def exportar_logs(self, formato):
        mensaje = self.model.exportar_logs(formato)
        self.view.label.setText(mensaje)
