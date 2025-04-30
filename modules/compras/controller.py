from PyQt6.QtWidgets import QTableWidgetItem, QMessageBox
import os
from datetime import datetime

class ComprasController:
    def __init__(self, model, view):
        self.model = model
        self.view = view
        self.setup_view_signals()

    def setup_view_signals(self):
        if hasattr(self.view, 'boton_guardar'):
            self.view.boton_guardar.clicked.connect(self.guardar_pedido)
        if hasattr(self.view, 'boton_buscar'):
            self.view.boton_buscar.clicked.connect(self.buscar_pedido)
        if hasattr(self.view, 'boton_eliminar'):
            self.view.boton_eliminar.clicked.connect(self.eliminar_pedido)
        if hasattr(self.view, 'boton_comparar'):
            # usar ID desde la vista al comparar presupuestos
            self.view.boton_comparar.clicked.connect(
                lambda: self.comparar_presupuestos(self.view.obtener_id_pedido())
            )

    def guardar_pedido(self):
        pedido = self.view.obtener_datos_pedido()
        resultado = self.model.guardar_pedido(pedido)
        if isinstance(resultado, str):  # Mensaje de error
            self.view.label.setText(resultado)
        else:
            self.view.limpiar_formulario()
            self.view.label.setText("Pedido guardado con éxito")

    def buscar_pedido(self):
        id_pedido = self.view.obtener_id_pedido()
        pedido = self.model.buscar_pedido(id_pedido)
        if isinstance(pedido, str):  # Mensaje de error
            self.view.label.setText(pedido)
        else:
            self.view.mostrar_datos_pedido(pedido)

    def eliminar_pedido(self):
        id_pedido = self.view.obtener_id_pedido()
        resultado = self.model.eliminar_pedido(id_pedido)
        if isinstance(resultado, str):  # Mensaje de error
            self.view.label.setText(resultado)
        else:
            self.view.limpiar_formulario()
            self.view.label.setText("Pedido eliminado con éxito")

    def comparar_presupuestos(self, id_pedido):
        presupuestos = self.model.obtener_comparacion_presupuestos(id_pedido)
        if isinstance(presupuestos, str):  # Mensaje de error
            self.view.label.setText(presupuestos)
        else:
            self.view.mostrar_comparacion_presupuestos(presupuestos)