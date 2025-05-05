from PyQt6.QtWidgets import QTableWidgetItem

class LogisticaController:
    def __init__(self, model, view):
        self.model = model
        self.view = view
        self.view.boton_agregar.clicked.connect(self.agregar_entrega)
        self.view.boton_actualizar_estado.clicked.connect(self.actualizar_estado_entrega)
        self.view.boton_agregar_checklist.clicked.connect(self.agregar_item_checklist)
        self.cargar_datos_entregas()

    def cargar_datos_entregas(self):
        """Carga los datos de la tabla de entregas en la vista de logística."""
        try:
            datos = self.model.obtener_datos_entregas()
            self.view.tabla_entregas.setRowCount(len(datos))
            for row_idx, row_data in enumerate(datos):
                for col_idx, value in enumerate(row_data):
                    self.view.tabla_entregas.setItem(row_idx, col_idx, QTableWidgetItem(str(value)))
        except Exception as e:
            self.view.label.setText(f"Error al cargar datos: {e}")

    def agregar_entrega(self):
        destino = self.view.destino_input.text()
        fecha_programada = self.view.fecha_programada_input.text()
        estado = self.view.estado_input.text()
        vehiculo = self.view.vehiculo_input.text()
        chofer = self.view.chofer_input.text()

        if destino and fecha_programada and estado and vehiculo and chofer:
            self.model.agregar_entrega((destino, fecha_programada, estado, vehiculo, chofer, ""))
            self.view.label.setText("Entrega agregada exitosamente.")
        else:
            self.view.label.setText("Por favor, complete todos los campos.")

    def actualizar_estado_entrega(self):
        fila_seleccionada = self.view.tabla_entregas.currentRow()
        if fila_seleccionada != -1:
            id_entrega = self.view.tabla_entregas.item(fila_seleccionada, 0).text()
            nuevo_estado = "en ruta"  # Ejemplo, debería obtenerse dinámicamente
            self.model.actualizar_estado_entrega(id_entrega, nuevo_estado)
            self.view.label.setText(f"Estado de la entrega {id_entrega} actualizado a {nuevo_estado}.")

    def agregar_item_checklist(self):
        fila_seleccionada = self.view.tabla_entregas.currentRow()
        if fila_seleccionada != -1:
            id_entrega = self.view.tabla_entregas.item(fila_seleccionada, 0).text()
            item = "Nuevo Ítem"  # Ejemplo, debería obtenerse dinámicamente
            estado_item = "pendiente"
            observaciones = "Sin observaciones"
            self.model.agregar_item_checklist((id_entrega, item, estado_item, observaciones))
            self.view.label.setText(f"Ítem agregado al checklist de la entrega {id_entrega}.")

    def registrar_firma_entrega(self, id_entrega, firma_digital):
        self.model.registrar_firma_entrega(id_entrega, firma_digital)
        self.view.label.setText("Firma digital registrada exitosamente.")

    def verificar_entregas_vencidas(self):
        entregas_vencidas = self.model.obtener_entregas_por_estado("pendiente")
        if entregas_vencidas:
            mensaje = f"Hay {len(entregas_vencidas)} entregas vencidas."
            self.notificaciones_controller.enviar_notificacion_automatica(mensaje, "logística")
            self.view.label.setText(mensaje)

    def generar_hoja_de_ruta(self, id_vehiculo):
        hoja_de_ruta = self.model.generar_hoja_de_ruta(id_vehiculo)
        if isinstance(hoja_de_ruta, str):  # Mensaje de error
            self.view.label.setText(hoja_de_ruta)
        else:
            self.view.mostrar_hoja_de_ruta(hoja_de_ruta)

    def exportar_historial_entregas(self, formato):
        mensaje = self.model.exportar_historial_entregas(formato)
        self.view.label.setText(mensaje)

    def exportar_acta_entrega(self, id_entrega):
        mensaje = self.model.exportar_acta_entrega(id_entrega)
        self.view.label.setText(mensaje)
