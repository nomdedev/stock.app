from mps.services.app_state import AppState
from PyQt6.QtWidgets import QTabWidget, QWidget, QVBoxLayout, QLabel, QTableWidget, QTableWidgetItem
import csv

class ConfiguracionBDWidget:
    def __init__(self, model, view):
        self.model = model
        self.view = view

    def obtener_usuario_activo(self):
        # Método para obtener el usuario actual
        return AppState.get_usuario_activo()

    def probar_conexion(self):
        usuario_activo = self.obtener_usuario_activo()  # Método para obtener el usuario actual
        bases = ["inventario", "usuarios", "auditoria"]
        for base in bases:
            try:
                self.model.probar_conexion(base)
                AppState.set_db_status(base, True, usuario=usuario_activo)
                self.view.mostrar_mensaje_exito(f"Conexión exitosa con la base '{base}'.")
            except Exception as e:
                AppState.set_db_status(base, False, usuario=usuario_activo)
                self.view.mostrar_mensaje_error(f"Error al conectar con '{base}': {str(e)}")

    def inicializar_pestana_auditoria(self):
        """Agrega una pestaña para mostrar auditorías del sistema."""
        auditoria_tab = QWidget()
        layout = QVBoxLayout()

        # Tabla para auditorías locales pendientes
        tabla_local = QTableWidget()
        tabla_local.setColumnCount(5)
        tabla_local.setHorizontalHeaderLabels(["Fecha", "Usuario", "Tipo", "Módulo", "Descripción"])
        layout.addWidget(QLabel("Auditorías Locales Pendientes"))
        layout.addWidget(tabla_local)

        # Cargar datos locales
        try:
            with open("auditoria_local.log", mode="r", encoding="utf-8") as file:
                reader = csv.reader(file)
                for row in reader:
                    tabla_local.insertRow(tabla_local.rowCount())
                    for col, value in enumerate(row[:5]):
                        tabla_local.setItem(tabla_local.rowCount() - 1, col, QTableWidgetItem(value))
        except FileNotFoundError:
            pass

        auditoria_tab.setLayout(layout)
        self.view.tabs.addTab(auditoria_tab, "Auditoría del Sistema")