import csv
from PyQt6.QtWidgets import QTableWidgetItem

class AuditoriaController:
    def __init__(self, model, view):
        self.model = model
        self.view = view
        self.view.boton_filtrar.clicked.connect(self.aplicar_filtros)
        self.view.boton_exportar.clicked.connect(self.exportar_logs)
        self.view.boton_exportar_excel.clicked.connect(lambda: self.exportar_auditorias("excel"))
        self.view.boton_exportar_pdf.clicked.connect(lambda: self.exportar_auditorias("pdf"))

    def aplicar_filtros(self):
        filtros = {}
        if self.view.filtro_usuario.text():
            filtros["usuario_id"] = self.view.filtro_usuario.text()
        if self.view.filtro_modulo.text():
            filtros["modulo_afectado"] = self.view.filtro_modulo.text()
        if self.view.filtro_fecha.text():
            filtros["fecha_hora"] = self.view.filtro_fecha.text()

        auditorias = self.model.obtener_auditorias(filtros)
        self.view.tabla_auditorias.setRowCount(len(auditorias))
        for row, auditoria in enumerate(auditorias):
            for col, value in enumerate(auditoria):
                self.view.tabla_auditorias.setItem(row, col, QTableWidgetItem(str(value)))

        errores = self.model.obtener_errores(filtros)
        self.view.tabla_errores.setRowCount(len(errores))
        for row, error in enumerate(errores):
            for col, value in enumerate(error):
                self.view.tabla_errores.setItem(row, col, QTableWidgetItem(str(value)))

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
